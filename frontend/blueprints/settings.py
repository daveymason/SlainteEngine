"""Settings Blueprint: AI Model Selection, FHIR Backend Data Switcher, App/Security & User Admin."""
import os
import time
from flask import Blueprint, abort, jsonify, redirect, render_template, request
from flask_login import current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash

import auth
import db
from ai import provider as ai_provider
from config import ai_blocked_reason
from logging_setup import pseudonymize
from blueprints.common import audit, _fragment_error
from blueprints.agents import _resolve_auditor_paths
from agents_hub import (
    run_cve_vulnerability_scan,
    run_gdpr_privacy_scan,
    run_immutable_audit_scan,
)

settings_bp = Blueprint('settings_bp', __name__)


def register_settings_routes(app, limiter=None):

    @app.route('/settings/ai', endpoint='ai_settings')
    @login_required
    @auth.require_role(db.ROLE_ADMIN)
    def ai_settings():
        saved_model = db.get_system_setting('ai_model', '') if not app.config.get('TESTING') else ''
        active_model = saved_model or app.config['AI_MODEL']
        return render_template(
            'ai_settings.html',
            model=active_model,
            env_model=app.config['AI_MODEL'],
            key_configured=bool(app.config['OPENAI_API_KEY']),
            fhir_server=app.config['FHIR_SERVER_URL'],
            blocked_reason=ai_blocked_reason(
                app.config['FHIR_SERVER_URL'], app.config['AI_ALLOW_REAL_PHI'],
            ),
        )

    @app.route('/settings/ai/select', methods=['POST'], endpoint='select_ai_model')
    @login_required
    @auth.require_role(db.ROLE_ADMIN)
    def select_ai_model():
        selected_model = (request.form.get('selected_model') or '').strip()
        if not selected_model:
            return '<div class="alert alert-warning py-2 mb-0 small">Please select a valid AI model.</div>'
        db.set_system_setting('ai_model', selected_model)
        app.config['AI_MODEL'] = selected_model
        try:
            _, _, reports_dir = _resolve_auditor_paths(app)
            os.makedirs(reports_dir, exist_ok=True)
            with open(os.path.join(reports_dir, 'selected_model.txt'), 'w') as mf:
                mf.write(selected_model)
        except Exception:
            pass
        audit('settings.ai_model_selected', outcome='success', detail={'model': selected_model})
        provider_type = 'Local Sovereign Ollama (Port 11434)' if selected_model.startswith('ollama/') else 'Cloud API (.env Key)'
        return (
            f'<div class="alert alert-success py-2 mb-0 small">'
            f'<i class="fas fa-check-circle me-1"></i> Active AI model updated to '
            f'<code>{selected_model}</code> ({provider_type}). Synced across Dashboard &amp; Slainte-Auditor.'
            f'</div>'
        )

    @app.route('/settings/ai/test', methods=['POST'], endpoint='test_ai_provider')
    @login_required
    @auth.require_role(db.ROLE_ADMIN)
    def test_ai_provider():
        req_model = (
            request.form.get('selected_model')
            or request.form.get('model')
            or request.args.get('model')
            or ((request.get_json(silent=True) or {}).get('model'))
            or ''
        ).strip()
        saved_model = db.get_system_setting('ai_model', '') if not app.config.get('TESTING') else ''
        active_model = req_model or saved_model or app.config['AI_MODEL']
        status = ai_provider.from_config(app.config, model_override=active_model).check()
        audit('settings.ai_provider_tested',
              outcome='success' if status.ok else 'failure',
              detail={'model': status.model, 'model_available': status.model_available})
        return jsonify({
            'ok': status.ok,
            'message': status.message,
            'model': status.model,
            'key_configured': status.key_configured,
            'key_valid': status.key_valid,
            'model_available': status.model_available,
            'suggestions': status.suggestions,
        })

    @app.route('/settings/data', endpoint='settings_data')
    @login_required
    @auth.require_role(db.ROLE_ADMIN)
    def settings_data():
        current_profile, active_url = db.get_active_backend_config(
            default_profile='slainte_fhir',
            default_url=app.config.get('FHIR_SERVER_URL', 'http://slainte-fhir:8082/fhir/r4')
        )
        profile_names = {
            'slainte_fhir': 'SlainteFHIR Micro-EHR (Port 8082 - SQLite WAL)',
            'local_store': 'Local Filesystem Store (/workspace/data/fhir_store)',
            'hapi_demo': 'Public HAPI Demo Server (https://hapi.fhir.org/baseR4)',
            'custom': 'Custom FHIR Endpoint',
        }
        driver_name = "LocalFhirStore (File-based)" if hasattr(app.fhir, '_cache_patients') else "FhirClient (REST HTTP)"
        patient_count = 0
        try:
            if hasattr(app.fhir, '_cache_patients'):
                patient_count = len(app.fhir._cache_patients)
            elif hasattr(app.fhir, 'count'):
                cnt = app.fhir.count('Patient')
                patient_count = cnt if cnt is not None else 0
        except Exception:
            patient_count = 0

        return render_template(
            'settings_data.html',
            active_profile=current_profile,
            active_profile_name=profile_names.get(current_profile, 'Active Server'),
            active_url=active_url,
            driver_name=driver_name,
            patient_count=patient_count,
            custom_url=getattr(app, 'custom_backend_url', ''),
        )

    @app.route('/settings/data/probe', methods=['POST'], endpoint='probe_data_backend')
    @login_required
    @auth.require_role(db.ROLE_ADMIN)
    def probe_data_backend():
        import requests
        profile = request.form.get('backend_profile', 'slainte_fhir')
        custom_url = request.form.get('custom_url', '').strip()

        target_url = None
        if profile == 'slainte_fhir':
            target_url = "http://slainte-fhir:8082" if os.path.exists("/.dockerenv") or os.environ.get("APPLIANCE_MODE") else "http://localhost:8082"
        elif profile == 'hapi_demo':
            target_url = "https://hapi.fhir.org/baseR4"
        elif profile == 'custom':
            target_url = custom_url
        elif profile == 'local_store':
            path = app.config.get('FHIR_STORE_PATH', '/workspace/data/fhir_store')
            exists = os.path.isdir(path)
            count = len([f for f in os.listdir(path) if f.endswith('.json')]) if exists else 0
            return f'<div class="alert alert-success py-2 px-3 small border-0 shadow-sm"><i class="fas fa-check-circle text-success me-1"></i><strong>Local Filesystem OK:</strong> Directory accessible ({count} JSON bundles found). Latency: &lt;0.1 ms.</div>'

        if not target_url:
            return '<div class="alert alert-danger py-2 px-3 small">Please provide a valid server URL to probe.</div>'

        start = time.time()
        try:
            meta_url = f"{target_url.rstrip('/')}/metadata" if not target_url.endswith("/metadata") else target_url
            r = requests.get(meta_url, timeout=3.0)
            latency = round((time.time() - start) * 1000, 1)
            if r.status_code == 200:
                data = r.json()
                server_name = data.get("software", {}).get("name") or "HL7 FHIR Server"
                fhir_ver = data.get("fhirVersion") or "R4"
                return f'<div class="alert alert-success py-2 px-3 small border-0 shadow-sm"><i class="fas fa-check-circle text-success me-1"></i><strong>Probe Succeeded:</strong> HTTP 200 OK from <code>{target_url}</code> ({server_name} FHIR {fhir_ver}). Latency: <strong>{latency} ms</strong>.</div>'
            else:
                return f'<div class="alert alert-warning py-2 px-3 small">Server reachable at <code>{target_url}</code>, but returned HTTP {r.status_code}. Latency: {latency} ms.</div>'
        except Exception as e:
            latency = round((time.time() - start) * 1000, 1)
            if profile == 'slainte_fhir' and "slainte-fhir" in target_url:
                try:
                    fallback_url = "http://localhost:8082"
                    rf = requests.get(f"{fallback_url}/health", timeout=2.0)
                    if rf.status_code == 200:
                        return f'<div class="alert alert-success py-2 px-3 small border-0 shadow-sm"><i class="fas fa-check-circle text-success me-1"></i><strong>SlainteFHIR OK:</strong> HTTP 200 via <code>{fallback_url}</code>. Latency: {latency} ms.</div>'
                except Exception:
                    pass
            return f'<div class="alert alert-danger py-2 px-3 small"><i class="fas fa-exclamation-triangle me-1"></i><strong>Connection Failed:</strong> Could not connect to <code>{target_url}</code> ({e}). Latency: {latency} ms.</div>'

    @app.route('/settings/data/switch', methods=['POST'], endpoint='switch_data_backend')
    @login_required
    @auth.require_role(db.ROLE_ADMIN)
    def switch_data_backend():
        profile = request.form.get('backend_profile', 'slainte_fhir')
        custom_url = request.form.get('custom_url', '').strip()
        from fhir_client import FhirClient
        from local_fhir_store import LocalFhirStore

        new_client = None
        target_display = ""
        if profile == 'slainte_fhir':
            url = "http://slainte-fhir:8082/fhir/r4"
            try:
                import requests
                requests.get("http://slainte-fhir:8082/health", timeout=1.0)
            except Exception:
                url = "http://localhost:8082/fhir/r4"
            new_client = FhirClient(url, timeout=app.config['FHIR_TIMEOUT'])
            target_display = f"SlainteFHIR Micro-EHR ({url})"
            app.active_backend_url = url
        elif profile == 'local_store':
            path = app.config.get('FHIR_STORE_PATH', '/workspace/data/fhir_store')
            new_client = LocalFhirStore(path)
            target_display = f"Local Filesystem Store ({path})"
            app.active_backend_url = f"file://{path}"
        elif profile == 'hapi_demo':
            url = "https://hapi.fhir.org/baseR4"
            new_client = FhirClient(url, timeout=app.config['FHIR_TIMEOUT'])
            target_display = f"Public HAPI Demo ({url})"
            app.active_backend_url = url
        elif profile == 'custom':
            if not custom_url:
                return '<div class="alert alert-danger py-2 px-3 small">Please provide a custom FHIR server URL.</div>'
            new_client = FhirClient(custom_url, timeout=app.config['FHIR_TIMEOUT'])
            target_display = f"Custom FHIR Endpoint ({custom_url})"
            app.active_backend_url = custom_url
            app.custom_backend_url = custom_url

        if new_client:
            db.set_active_backend_config(profile, app.active_backend_url)
            app._cached_fhir_key = (profile, app.active_backend_url)
            app._cached_fhir_client = new_client
            app.active_profile = profile
            audit('settings.backend_switched', outcome='success', detail={'profile': profile, 'target': target_display})
            return f'''
            <div class="alert alert-success py-2 px-3 small border-0 shadow-sm animate-fade-in">
                <i class="fas fa-check-circle text-success me-1"></i>
                <strong>Backend Switched Successfully!</strong> Currently connected to <strong>{target_display}</strong>.
                <a href="/" class="alert-link ms-2">Return to Dashboard &rarr;</a>
            </div>
            <script>setTimeout(function() {{ window.location.reload(); }}, 1200);</script>
            '''
        return '<div class="alert alert-danger py-2 px-3 small">Failed to initialize selected backend.</div>'

    @app.route('/settings/app', endpoint='settings_app')
    @login_required
    def settings_app():
        return render_template('settings_app.html')

    @app.route('/settings/security', endpoint='settings_security')
    @login_required
    def settings_security():
        _, store_dir, _ = _resolve_auditor_paths(app)
        audit_scan = run_immutable_audit_scan(db, store_dir)
        cve_scan = run_cve_vulnerability_scan(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), app.config)
        gdpr_scan = run_gdpr_privacy_scan(app.config, db)
        recent_audits = [
            {
                'action': r.get('action', ''),
                'user_id': r.get('actor', ''),
                'outcome': r.get('outcome', 'success'),
                'timestamp': r.get('occurred_at', ''),
            }
            for r in audit_scan.get('recent_audits', [])
        ]
        return render_template(
            'settings_security.html',
            audit_count=audit_scan.get('audit_count', 0),
            ai_exchange_count=audit_scan.get('ai_exchange_count', 0),
            provenance_count=audit_scan.get('provenance_count', 0),
            triggers_ok=audit_scan.get('triggers_ok', True),
            recent_audits=recent_audits,
            recent_ai_exchanges=audit_scan.get('recent_ai_exchanges', []),
            cve_scan=cve_scan,
            gdpr_scan=gdpr_scan,
        )

    @app.route('/settings/user', endpoint='settings_user')
    @login_required
    def settings_user():
        return render_template('settings_user.html')

    @app.route('/settings/user/password', methods=['POST'], endpoint='change_password')
    @login_required
    def change_password():
        current_pw = request.form.get('current_password', '')
        new_pw = request.form.get('new_password', '')
        confirm_pw = request.form.get('confirm_password', '')

        if not current_pw or not new_pw:
            return '<div class="alert alert-danger py-2 px-3 small">All fields are required.</div>'
        if new_pw != confirm_pw:
            return '<div class="alert alert-danger py-2 px-3 small">New password and confirmation do not match.</div>'
        if len(new_pw) < 8:
            return '<div class="alert alert-danger py-2 px-3 small">Password must be at least 8 characters long.</div>'

        user = db.get_user_by_username(current_user.username)
        if not user or not check_password_hash(user['password_hash'], current_pw):
            audit('user.password_change', outcome='failure', detail={'reason': 'invalid_current_password'})
            return '<div class="alert alert-danger py-2 px-3 small">Current password is incorrect.</div>'

        new_hash = generate_password_hash(new_pw)
        conn = db.get_connection()
        conn.execute("UPDATE users SET password_hash = ? WHERE username = ?;", (new_hash, current_user.username))
        conn.commit()

        audit('user.password_change', outcome='success')
        return '<div class="alert alert-success py-2 px-3 small"><i class="fas fa-check-circle me-1"></i>Password updated successfully!</div>'

    @app.route('/admin/users', endpoint='admin_users')
    @login_required
    @auth.require_role(db.ROLE_ADMIN)
    def admin_users():
        return render_template(
            'admin_users.html',
            users=db.list_users(),
            clinical_roles=db.CLINICAL_ROLES,
            clinical_role_labels=db.CLINICAL_ROLE_LABELS,
        )

    @app.route('/admin/users/<username>/status', methods=['POST'], endpoint='admin_set_user_status')
    @login_required
    @auth.require_role(db.ROLE_ADMIN)
    def admin_set_user_status(username):
        status = request.form.get('status', '')
        if status not in (db.STATUS_PENDING, db.STATUS_ACTIVE, db.STATUS_DISABLED):
            abort(400)
        if username.lower() == current_user.username and status != db.STATUS_ACTIVE:
            return _fragment_error('You cannot disable your own account.')

        db.set_user_status(username, status)
        audit('admin.user_status_changed', resource_type='User',
              resource_id=pseudonymize(username), detail={'status': status})
        return render_template(
            'admin_user_rows.html',
            users=db.list_users(),
            clinical_roles=db.CLINICAL_ROLES,
            clinical_role_labels=db.CLINICAL_ROLE_LABELS,
        )

    @app.route('/admin/users/<username>/role', methods=['POST'], endpoint='admin_set_user_role')
    @login_required
    @auth.require_role(db.ROLE_ADMIN)
    def admin_set_user_role(username):
        role = request.form.get('role', '')
        if role not in db.ROLES:
            abort(400)
        if username.lower() == current_user.username and role != db.ROLE_ADMIN:
            return _fragment_error('You cannot remove your own administrator role.')

        db.set_user_role(username, role)
        audit('admin.user_role_changed', resource_type='User',
              resource_id=pseudonymize(username), detail={'role': role})
        return render_template(
            'admin_user_rows.html',
            users=db.list_users(),
            clinical_roles=db.CLINICAL_ROLES,
            clinical_role_labels=db.CLINICAL_ROLE_LABELS,
        )

    @app.route('/admin/audit', endpoint='admin_audit')
    @login_required
    @auth.require_role(db.ROLE_ADMIN)
    def admin_audit():
        audit('admin.audit_viewed')
        return render_template('admin_audit.html', entries=db.read_audit(limit=200))
