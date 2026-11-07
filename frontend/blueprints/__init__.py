"""Slainte-Engine Domain Blueprints Package.

Modularizes frontend routes into clean domain blueprints:
- auth: Authentication, registration, lockout, session management
- patients: Patient roster, search, clinical detail, writes, charts, and bedside AI copilots
- verticals: 8-vertical specialty cockpits (ED, GP, Psych, Dental, Pharmacy, EMS, Sports, Astro)
- agents: Master 11-agent hub, dedicated agent dashboards, runners, settings, SARIF export
- intake: Manchester Triage Queue, dropzone telemetry, manual intake & multimodal batch upload
- settings: AI model picker, FHIR data backend switcher, app/security settings, user administration
"""
import logging
from flask import jsonify, render_template, request, session
import db
from verticals import get_active_vertical, get_vertical_list
from blueprints.common import _fragment_error
from blueprints.auth import register_auth_routes, auth_bp
from blueprints.verticals import register_verticals_routes, verticals_bp
from blueprints.agents import register_agents_routes, agents_bp
from blueprints.intake import register_intake_routes, intake_bp
from blueprints.settings import register_settings_routes, settings_bp
from blueprints.patients import register_patients_routes, patients_bp

logger = logging.getLogger(__name__)


def register_all_blueprints(app, csrf, limiter=None):
    """Register all domain routes, context processors, and error handlers."""
    fhir = app.fhir

    # 1. Context Processor for active vertical branding across templates
    @app.context_processor
    def inject_vertical_and_fleet():
        return {
            'active_vertical': get_active_vertical(session, db),
            'all_verticals': get_vertical_list(),
        }

    # 2. Public health probe routes
    @app.route('/health', endpoint='health_check')
    def health_check():
        payload = {'status': 'ok'}
        if app.config.get('HEALTH_SHOW_BACKEND'):
            _, active_url = db.get_active_backend_config(
                default_profile='slainte_fhir',
                default_url=app.config.get('FHIR_SERVER_URL', 'http://slainte-fhir:8082/fhir/r4')
            )
            payload['fhir_server'] = active_url
        return jsonify(payload)

    @app.route('/health/ready', endpoint='readiness_check')
    def readiness_check():
        reachable = fhir.capability_ok()
        return jsonify({'status': 'ok' if reachable else 'degraded',
                        'fhir_reachable': reachable}), (200 if reachable else 503)

    # 3. Register Domain Route Modules
    register_auth_routes(app, limiter)
    register_patients_routes(app)
    register_verticals_routes(app)
    register_agents_routes(app)
    register_intake_routes(app, csrf)
    register_settings_routes(app, limiter)

    # 4. Global Error Handlers
    @app.errorhandler(403)
    def handle_forbidden(_error):
        if request.headers.get('HX-Request'):
            return _fragment_error('You do not have permission to view this.'), 403
        return render_template('error.html', code=403,
                               message='You do not have permission to view this.'), 403

    @app.errorhandler(404)
    def handle_not_found(_error):
        if request.headers.get('HX-Request'):
            return _fragment_error('Not found.'), 404
        return render_template('error.html', code=404,
                               message='That page could not be found.'), 404

    @app.errorhandler(500)
    def handle_server_error(error):
        logger.exception('Unhandled error: %s', error)
        if request.headers.get('HX-Request'):
            return _fragment_error('Something went wrong loading this section.'), 500
        return render_template('error.html', code=500,
                               message='Something went wrong.'), 500


__all__ = [
    'register_all_blueprints',
    'auth_bp',
    'patients_bp',
    'verticals_bp',
    'agents_bp',
    'intake_bp',
    'settings_bp',
]
