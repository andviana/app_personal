from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import logout_user, current_user
from urllib.parse import urlsplit
from app.blueprints.auth import bp
from app.services.auth_service import AuthService
from app.services.log_service import LogService

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user, error = AuthService.authenticate_user(
            username=username,
            password=password,
            remember=remember,
            ip_address=request.remote_addr
        )
        
        if error:
            flash(error, 'danger')
            return redirect(url_for('auth.login'))
        
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    if current_user.is_authenticated:
        LogService.log_action(current_user, 'LOGOUT')
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/google/login')
def google_login():
    from app import oauth
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if not current_app.config.get('GOOGLE_CLIENT_ID'):
        flash('Login com Google não está configurado neste ambiente.', 'danger')
        return redirect(url_for('auth.login'))

    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@bp.route('/google/callback')
def google_callback():
    from app import oauth
    try:
        token = oauth.google.authorize_access_token()
    except Exception:
        LogService.log_action('Google', 'GOOGLE_LOGIN_ERROR', 'Falha ao trocar o código de autorização com o Google')
        flash('Não foi possível concluir o login com o Google. Tente novamente.', 'danger')
        return redirect(url_for('auth.login'))

    userinfo = token.get('userinfo') or {}
    email = userinfo.get('email')

    # Só aceita e-mails que o próprio Google confirma pertencer ao usuário.
    if not userinfo.get('email_verified'):
        email = None

    user, error = AuthService.authenticate_google_user(email, ip_address=request.remote_addr)

    if error:
        return render_template('auth/unauthorized.html', email=email), 403

    next_page = request.args.get('next')
    if not next_page or urlsplit(next_page).netloc != '':
        next_page = url_for('main.index')
    return redirect(next_page)
