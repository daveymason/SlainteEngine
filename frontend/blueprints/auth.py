"""Authentication Blueprint: Login, Registration, Logout, and Session Management."""
from flask import Blueprint, current_app, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
import auth
import db
from logging_setup import pseudonymize
from blueprints.common import audit
from config import MIN_PASSWORD_LENGTH, MIN_USERNAME_LENGTH, MAX_USERNAME_LENGTH, is_valid_username
from verticals import VERTICALS_CATALOG

auth_bp = Blueprint('auth', __name__)


def register_auth_routes(app, limiter=None):
    if limiter is None:
        limiter = getattr(app, 'limiter', None)
    auth_limit = app.config.get('RATELIMIT_AUTH', '10 per minute')

    def _apply_limit(view_fn):
        if limiter and hasattr(limiter, 'limit'):
            return limiter.limit(auth_limit, methods=['POST'])(view_fn)
        return view_fn

    @app.route('/login', methods=['GET', 'POST'], endpoint='login')
    @_apply_limit
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        if request.method == 'GET':
            notice = None
            if request.args.get('registered'):
                notice = ('Account created. An administrator must approve it '
                          'before you can sign in.')
            return render_template('login.html', notice=notice)

        username = (request.form.get('username') or '').strip().lower()
        password = request.form.get('password') or ''
        if not username or not password:
            return render_template('login.html', error='Enter your username and password.'), 400

        locked, locked_until = db.is_account_locked(username)
        if locked:
            audit('login.locked', outcome='denied', resource_type='User',
                  resource_id=pseudonymize(username), detail={'reason': 'account_locked', 'locked_until': locked_until})
            return render_template('login.html',
                                   error='Account is temporarily locked due to multiple failed login attempts. Please try again later.'), 403

        record = auth.verify_credentials(username, password)
        if record is None:
            attempts, locked_until = db.record_failed_login(username)
            detail = {'reason': 'bad_credentials', 'failed_attempts': attempts}
            if locked_until:
                detail['locked_until'] = locked_until
            audit('login.denied', outcome='failure', resource_type='User',
                  resource_id=pseudonymize(username), detail=detail)
            if locked_until:
                from enterprise_engine import dispatch_siem_event
                dispatch_siem_event(
                    db_module=db,
                    app_config=app.config,
                    event_type='SECURITY_ACCOUNT_LOCKOUT',
                    severity='HIGH',
                    actor=username,
                    detail={'failed_attempts': attempts, 'locked_until': locked_until},
                )
                return render_template('login.html',
                                       error='Account has been temporarily locked due to 5 consecutive failed login attempts. Please try again in 15 minutes.'), 403
            return render_template('login.html', error='Incorrect username or password.'), 401

        if record['status'] != db.STATUS_ACTIVE:
            audit('login.denied', outcome='denied', resource_type='User',
                  resource_id=pseudonymize(username),
                  detail={'reason': f"account_{record['status']}"})
            message = ('Your account is awaiting administrator approval.'
                       if record['status'] == db.STATUS_PENDING
                       else 'This account has been disabled.')
            return render_template('login.html', error=message), 403

        login_user(auth.User(record))
        db.record_login(username)
        selected_vertical = (request.form.get('vertical_key') or '').strip().lower()
        if selected_vertical in VERTICALS_CATALOG:
            session['active_vertical'] = selected_vertical
            db.set_system_setting('default_vertical', selected_vertical)
        audit('login.success', resource_type='User', resource_id=pseudonymize(username),
              detail={'vertical': selected_vertical or 'ed'})
        return redirect(url_for('index'))

    @app.route('/register', methods=['GET', 'POST'], endpoint='register')
    @_apply_limit
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        if request.method == 'GET':
            return render_template('register.html')

        username = (request.form.get('username') or '').strip().lower()
        password = request.form.get('password') or ''
        confirm = request.form.get('confirm_password') or ''

        error = None
        if not is_valid_username(username):
            error = (f'Choose a username of {MIN_USERNAME_LENGTH}-{MAX_USERNAME_LENGTH} '
                     'characters: letters, numbers, dots, hyphens or underscores.')
        elif len(password) < MIN_PASSWORD_LENGTH:
            error = f'Choose a password of at least {MIN_PASSWORD_LENGTH} characters.'
        elif password != confirm:
            error = 'Passwords do not match.'
        elif db.get_user(username) is not None:
            error = 'That username is already taken.'

        if error:
            return render_template('register.html', error=error, username=username), 400

        db.register_pending_user(username, auth.hash_password(password))
        audit('register.pending', resource_type='User', resource_id=pseudonymize(username))
        return redirect(url_for('login', registered=1))

    @app.route('/logout', endpoint='logout')
    @login_required
    def logout():
        audit('logout')
        logout_user()
        session.clear()
        return redirect(url_for('login'))
