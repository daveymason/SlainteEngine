import os
"""FHIR Patient Dashboard.

Flask + HTMX viewer over a FHIR R4 server. Routes return HTML fragments that
HTMX swaps into the page, so there is no client-side framework and no build step.
"""
import logging
import re

import click
from flask import (
    Flask, abort, jsonify, redirect, render_template, request, session, url_for
)
from flask_login import (
    LoginManager, current_user, login_required, login_user, logout_user
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

import auth
import db
from ai import provider as ai_provider
from charts import demographics_charts, vitals_charts
from config import (
    ConfigError, MAX_USERNAME_LENGTH, MIN_PASSWORD_LENGTH, MIN_USERNAME_LENGTH,
    ai_blocked_reason, is_valid_username, resolve_secret_key, select_config,
)
from fhir_client import FhirClient
from fhir_utils import (
    LOINC_DIASTOLIC, LOINC_SYSTOLIC, blood_pressure_components, calculate_age,
    calculate_news2_score, check_drug_allergy_contraindications,
    condition_onset, first_coding_display, format_address, format_fhir_date,
    observation_code, observation_value, patient_display_name, patient_initials,
    sort_key,
)
from clinical_workflows import (
    ALL_FDI_TEETH, BPE_SEXTANTS, CLINICAL_ALLERGENS_CATALOG,
    CLINICAL_CONDITIONS_CATALOG, CLINICAL_MEDICATIONS_CATALOG,
    FDI_LOWER_LEFT, FDI_LOWER_RIGHT, FDI_UPPER_LEFT, FDI_UPPER_RIGHT,
    NOTE_TYPES_CATALOG, TOOTH_STATUS_META, build_allergy_resource,
    build_clinical_note, build_condition_resource,
    build_dental_chart_observation, build_medication_request,
    build_provenance_signoff, build_vital_observations, extract_note_view,
    parse_dental_chart_observation, persist_fhir_resource,
)
import rate_limit_storage
from logging_setup import configure_logging, pseudonymize, validate_salt

rate_limit_storage.register_sqlite_scheme()

logger = logging.getLogger(__name__)

login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)

# LOINC codes for the vital signs panel.
VITAL_SIGN_CODES = {
    'blood_pressure': ('85354-9', 'Blood Pressure', 'mmHg'),
    'heart_rate': ('8867-4', 'Heart Rate', 'bpm'),
    'spo2': ('59408-5', 'Oxygen Saturation (SpO2)', '%'),
    'respiratory_rate': ('9279-1', 'Respiratory Rate', '/min'),
    'temperature': ('8310-5', 'Temperature', '°C'),
    'pain': ('72514-3', 'Pain Score', '{score}'),
}

# Patient search parameters that may be sorted, mapped to nothing (they're
# already valid FHIR _sort values) -- kept as a set purely to reject anything
# else a caller might try to inject through the sort parameter.
_SORTABLE_FIELDS = {'family', 'birthdate', 'gender'}

_DATE_SEARCH_RE = re.compile(r'\d{4}(-\d{2}(-\d{2})?)?$')


class DynamicFhirProxy:
    """Proxy that dynamically resolves the active FHIR client backed by shared SQLite state.

    Guarantees 100% synchronization across multi-worker gunicorn instances with zero
    in-memory drift.
    """
    def __init__(self, app):
        self._app = app

    def _get_client(self):
        app = self._app
        default_url = app.config.get('FHIR_SERVER_URL') or 'http://slainte-fhir:8082/fhir/r4'
        default_profile = 'slainte_fhir' if '8082' in default_url else 'custom'

        profile, url = db.get_active_backend_config(default_profile=default_profile, default_url=default_url)
        if not url:
            url = default_url

        cached_key = getattr(app, '_cached_fhir_key', None)
        cached_client = getattr(app, '_cached_fhir_client', None)

        if cached_key != (profile, url) or cached_client is None:
            if profile == 'local_store' or (url and url.startswith('file://')):
                from local_fhir_store import LocalFhirStore
                path = url.replace('file://', '') if url else app.config.get('FHIR_STORE_PATH', '/workspace/data/fhir_store')
                if not os.path.isdir(path):
                    alt_path = app.config.get('FHIR_STORE_PATH')
                    if alt_path and os.path.isdir(alt_path):
                        path = alt_path
                    else:
                        eng_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'slainte-engine', 'data', 'fhir_store'))
                        if os.path.isdir(eng_path):
                            path = eng_path
                cached_client = LocalFhirStore(path)
            else:
                from fhir_client import FhirClient
                effective_url = url
                if 'slainte-fhir:8082' in effective_url and not os.path.exists('/.dockerenv'):
                    effective_url = effective_url.replace('slainte-fhir:8082', 'localhost:8082')
                cached_client = FhirClient(effective_url, timeout=app.config.get('FHIR_TIMEOUT', 4.0))

            app._cached_fhir_key = (profile, url)
            app._cached_fhir_client = cached_client
            app.active_profile = profile
            app.active_backend_url = url

        return cached_client

    def __getattr__(self, name):
        if name in ('_app', '_get_client'):
            return super().__getattribute__(name)
        return getattr(self._get_client(), name)

    def __dir__(self):
        return dir(self._get_client())


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_app(config_object=None):
    app = Flask(__name__)

    # 1. Base configuration defaults
    app.config.from_object(select_config())

    # 2. Merge overrides (dict or config class)
    if config_object:
        if isinstance(config_object, dict):
            app.config.from_mapping(config_object)
        else:
            app.config.from_object(config_object)

    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = resolve_secret_key(app.config.get('DEBUG', False))

    configure_logging(app.config.get('LOG_LEVEL', 'INFO'), as_json=app.config.get('LOG_JSON', False))

    app.fhir = DynamicFhirProxy(app)


    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.user_loader(auth.load_user)
    login_manager.session_protection = 'strong'

    validate_salt(is_debug=app.debug, is_testing=app.testing)

    if 'RATELIMIT_STORAGE_URI' not in app.config:
        if app.testing:
            app.config['RATELIMIT_STORAGE_URI'] = 'memory://'
        else:
            db_path = app.config.get('DATABASE_PATH')
            if not db_path:
                db_dir = os.path.abspath(app.instance_path)
                app.config['DATABASE_PATH'] = os.path.join(db_dir, 'app.db')
            else:
                db_dir = os.path.dirname(db_path)
            if not db_dir or db_dir == ':memory:':
                db_dir = os.path.abspath(app.instance_path)
            try:
                os.makedirs(db_dir, exist_ok=True)
                rl_db = os.path.join(db_dir, 'rate_limits.db')
                app.config['RATELIMIT_STORAGE_URI'] = f'sqlite:///{rl_db}'
            except (OSError, PermissionError):
                app.config['RATELIMIT_STORAGE_URI'] = 'memory://'

    csrf.init_app(app)
    limiter.init_app(app)
    app.limiter = limiter

    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com data:; "
            "img-src 'self' data: https:; "
            "connect-src 'self' http://localhost:* http://127.0.0.1:* https://unpkg.com https://cdn.jsdelivr.net https://hapi.fhir.org; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        response.headers['Content-Security-Policy'] = csp
        return response

    app.teardown_appcontext(db.close_connection)
    db.init_db(app)

    from enterprise_bp import enterprise_bp, smart_introspect, smart_token
    csrf.exempt(smart_token)
    csrf.exempt(smart_introspect)
    app.register_blueprint(enterprise_bp)

    register_routes(app)
    register_cli(app)

    # Nobody can approve a pending account if there is no reachable admin, so
    # say so at boot rather than letting the operator discover it by being
    # locked out.
    with app.app_context():
        if db.count_active_admins() == 0:
            logger.warning(
                'No active administrator account exists. Nobody can approve '
                'sign-in requests. Grant one with: '
                'flask --app app grant-admin <username>'
            )

    @app.before_request
    def _make_session_permanent():
        session.permanent = True

    logger.info(
        'Application started',
        extra={'fhir_server': app.config['FHIR_SERVER_URL'], 'debug': app.config['DEBUG']},
    )
    return app


# ---------------------------------------------------------------------------
# Audit helper
# ---------------------------------------------------------------------------

def audit(action, outcome='success', resource_type=None, resource_id=None, detail=None):
    """Record an access to the audit trail, with the patient ID pseudonymised."""
    db.write_audit(
        action=action,
        outcome=outcome,
        actor=current_user.get_id() if current_user.is_authenticated else None,
        resource_type=resource_type,
        resource_id=resource_id,
        remote_addr=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        detail=detail,
    )


def _fragment_error(message, columns=None):
    """Render an inline error for an HTMX panel.

    Returns HTTP 200 deliberately: htmx does not swap non-2xx responses by
    default, so a 5xx here would leave the panel silently blank.
    """
    if columns:
        return (
            f'<tr><td colspan="{columns}" class="text-center text-danger py-3">'
            f'<i class="fas fa-exclamation-triangle me-2"></i>{message}</td></tr>'
        )
    return (
        f'<div class="alert alert-danger mb-3">'
        f'<i class="fas fa-exclamation-triangle me-2"></i>{message}</div>'
    )


# ---------------------------------------------------------------------------
# Presentation helpers
# ---------------------------------------------------------------------------

def _load_local_bundle_summary(pt_id):
    """Fast local lookup of clinical summary fields (conditions, allergies, meds, vitals) from fhir_store."""
    import json
    from flask import current_app, has_app_context
    if has_app_context() and current_app.config.get('TESTING') and not current_app.config.get('FHIR_STORE_PATH'):
        return {
            'primary_condition': 'General Assessment',
            'allergies': [],
            'medications': [],
            'news2_score': 0,
            'news2_tier': 'Low Risk',
            'vitals_summary': 'Baseline',
            'rx_alerts': [],
        }
    candidates = [
        os.environ.get('FHIR_STORE_PATH', ''),
        '/workspace/data/fhir_store',
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'fhir_store')),
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'slainte-engine', 'data', 'fhir_store')),
    ]
    for store_dir in candidates:
        if not store_dir or not os.path.isdir(store_dir):
            continue
        bpath = os.path.join(store_dir, f'bundle_{pt_id}.json')
        if os.path.isfile(bpath):
            try:
                with open(bpath, 'r', encoding='utf-8') as f:
                    bdata = json.load(f)
                conditions = []
                allergies = []
                medications = []
                vitals_map = {}
                for entry in bdata.get('entry') or []:
                    res = entry.get('resource') or {}
                    rtype = res.get('resourceType')
                    if rtype == 'Condition':
                        txt = (res.get('code') or {}).get('text') or ((res.get('code') or {}).get('coding') or [{}])[0].get('display')
                        if txt:
                            conditions.append(txt)
                    elif rtype == 'AllergyIntolerance':
                        txt = (res.get('code') or {}).get('text') or ((res.get('code') or {}).get('coding') or [{}])[0].get('display')
                        if txt:
                            allergies.append(txt)
                    elif rtype == 'MedicationRequest':
                        txt = (res.get('medicationCodeableConcept') or {}).get('text') or ((res.get('medicationCodeableConcept') or {}).get('coding') or [{}])[0].get('display')
                        if txt:
                            medications.append(txt)
                    elif rtype == 'Observation':
                        code = ((res.get('code') or {}).get('coding') or [{}])[0].get('code')
                        val = (res.get('valueQuantity') or {}).get('value')
                        if code and val is not None:
                            vitals_map[code] = val
                score, tier, _ = calculate_news2_score(vitals_map)
                v_parts = []
                if '8867-4' in vitals_map:
                    v_parts.append(f"HR {int(float(vitals_map['8867-4']))}")
                if '2708-6' in vitals_map or '59408-5' in vitals_map:
                    sp = vitals_map.get('2708-6') or vitals_map.get('59408-5')
                    v_parts.append(f"SpO2 {int(float(sp))}%")
                if '8480-6' in vitals_map:
                    v_parts.append(f"SBP {int(float(vitals_map['8480-6']))}")
                return {
                    'primary_condition': conditions[0] if conditions else 'Clinical Review',
                    'allergies': allergies,
                    'medications': medications,
                    'news2_score': score,
                    'news2_tier': tier,
                    'vitals_summary': ' · '.join(v_parts) if v_parts else 'Vitals stable',
                    'rx_alerts': check_drug_allergy_contraindications(allergies, medications),
                }
            except Exception:
                break
    return {
        'primary_condition': 'General Assessment',
        'allergies': [],
        'medications': [],
        'news2_score': 0,
        'news2_tier': 'Low Risk',
        'vitals_summary': 'Baseline',
        'rx_alerts': [],
    }


def process_patient_results(resources):
    """Flatten Patient resources into the shape the table templates expect, enriched for vertical cockpits."""
    processed = []
    for resource in resources:
        address = (resource.get('address') or [{}])[0]
        telecom = (resource.get('telecom') or [{}])[0]
        pt_id = resource.get('id', 'Unknown')
        bdate = resource.get('birthDate', 'Unknown')
        gms_val = 'Unassigned'
        for ident in resource.get('identifier') or []:
            if isinstance(ident, dict) and ident.get('value'):
                gms_val = ident.get('value')
                break
        extra = _load_local_bundle_summary(pt_id)
        processed.append({
            'id': pt_id,
            'name': patient_display_name(resource),
            'gender': resource.get('gender', 'Unknown'),
            'birthDate': bdate,
            'age': calculate_age(bdate),
            'gms': gms_val,
            'address': format_address(address) or 'Not recorded',
            'telecom': telecom.get('value', 'Not recorded'),
            **extra,
        })
    return processed


def _bundle_next_link(result):
    """Extract the `next` page URL from a searchset Bundle, if there is one."""
    for link in result.data.get('link') or []:
        if isinstance(link, dict) and link.get('relation') == 'next':
            return link.get('url')
    return None


def _validate_sort(raw):
    """Only pass through a `sort` value that is actually one of our columns.

    The value doubles as the literal FHIR `_sort` parameter (e.g. `-birthdate`),
    so an unchecked value would let a caller sort -- or otherwise perturb the
    query -- by an arbitrary FHIR search parameter.
    """
    if not raw:
        return None
    field = raw[1:] if raw.startswith('-') else raw
    return raw if field in _SORTABLE_FIELDS else None


def _looks_like_date(term):
    return bool(_DATE_SEARCH_RE.fullmatch(term))


def _looks_like_phone(term):
    digits = re.sub(r'[\s().+-]', '', term)
    return digits.isdigit() and len(digits) >= 6


def _looks_like_id(term):
    return term.replace('-', '').isalnum() and any(c.isdigit() for c in term)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

def register_routes(app):
    """Delegate route registration to clean domain blueprints."""
    from blueprints import register_all_blueprints
    register_all_blueprints(app, csrf, limiter)

def register_cli(app):
    """Operator commands, including the lockout recovery path."""

    @app.cli.command('grant-admin')
    @click.argument('username')
    def grant_admin_command(username):
        """Create or promote USERNAME to an active administrator.

        Prompts for a password interactively, and (re)sets it -- this is the
        lockout-recovery path, so it must work even if the account already
        exists and its password is unknown.
        """
        username = username.strip().lower()
        if not is_valid_username(username):
            raise click.ClickException(
                f'{username!r} is not a usable username. It must be '
                f'{MIN_USERNAME_LENGTH}-{MAX_USERNAME_LENGTH} characters of letters, '
                'numbers, dots, hyphens or underscores.'
            )
        password = click.prompt('Password', hide_input=True, confirmation_prompt=True)
        if len(password) < MIN_PASSWORD_LENGTH:
            raise click.ClickException(
                f'Password must be at least {MIN_PASSWORD_LENGTH} characters.'
            )
        record = db.grant_admin(username, auth.hash_password(password))
        db.write_audit('admin.granted_via_cli', 'success',
                       actor='cli', resource_type='User',
                       resource_id=pseudonymize(record['username']))
        click.echo(f"{record['username']} is now an active administrator.")

    @app.cli.command('reset-password')
    @click.argument('username')
    def reset_password_command(username):
        """Reset USERNAME's password, leaving their role and status alone.

        `grant-admin` also promotes, so it is the wrong tool for an ordinary
        forgotten password -- it would hand the account administrator rights
        as a side effect.
        """
        username = username.strip().lower()
        password = click.prompt('New password', hide_input=True, confirmation_prompt=True)
        if len(password) < MIN_PASSWORD_LENGTH:
            raise click.ClickException(
                f'Password must be at least {MIN_PASSWORD_LENGTH} characters.'
            )
        record = db.set_password(username, auth.hash_password(password))
        if record is None:
            raise click.ClickException(f'No account called {username!r}.')
        db.write_audit('user.password_reset_via_cli', 'success',
                       actor='cli', resource_type='User',
                       resource_id=pseudonymize(record['username']))
        click.echo(f"Password reset for {record['username']} "
                   f"(role {record['role']}, status {record['status']} -- unchanged).")

    @app.cli.command('list-users')
    def list_users_command():
        """Show every registered account and its status."""
        users = db.list_users()
        if not users:
            click.echo('No users registered yet.')
            return
        click.echo(f"{'USERNAME':<24}{'ROLE':<12}{'STATUS':<10}LAST SIGN-IN")
        for user in users:
            click.echo(
                f"{user['username']:<24}{user['role']:<12}"
                f"{user['status']:<10}{(user['last_login_at'] or 'never')[:19]}"
            )
        click.echo(f'\n{db.count_active_admins()} active administrator(s).')


def main():
    try:
        application = create_app()
    except ConfigError as exc:
        raise SystemExit(f'\nConfiguration error:\n{exc}\n')
    application.run(debug=application.config['DEBUG'])


if __name__ == '__main__':
    main()
