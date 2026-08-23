from app.repositories.user_repository import UserRepository
from app.services.log_service import LogService
from flask_login import login_user

class AuthService:
    @staticmethod
    def authenticate_user(username, password, remember=False, ip_address=None):
        repo = UserRepository()
        user = repo.find_by_username(username)
        
        if user is None or not user.check_password(password):
            LogService.log_action(username, 'LOGIN_FAILED', f'Attempt from IP: {ip_address}')
            return None, 'Credenciais inválidas.'
        
        login_user(user, remember=remember)
        LogService.log_action(user, 'LOGIN_SUCCESS')
        return user, None
