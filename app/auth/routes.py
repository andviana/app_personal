from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlsplit
from app import db
from app.auth import bp
from app.models import User
from app.services.log_service import LogService

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            LogService.log_action(username, 'LOGIN_FAILED', f'Attempt from IP: {request.remote_addr}')
            flash('Credenciais inválidas.', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=remember)
        LogService.log_action(user, 'LOGIN_SUCCESS')
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
