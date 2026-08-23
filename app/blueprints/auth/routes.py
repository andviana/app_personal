from flask import render_template, redirect, url_for, flash, request
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
