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

    @staticmethod
    def authenticate_google_user(email, ip_address=None):
        """
        Autentica um usuário já cadastrado a partir do e-mail confirmado pelo Google.

        Não cria contas automaticamente: o Google apenas prova que o usuário é
        dono daquele e-mail. Se nenhum cadastro local tiver esse e-mail, o
        login é recusado — quem tem acesso ao sistema continua sendo definido
        apenas pelos usuários já cadastrados (ver Configurações > Perfil).
        """
        if not email:
            LogService.log_action('Google', 'GOOGLE_LOGIN_FAILED', 'E-mail não informado pelo Google')
            return None, 'O Google não retornou um e-mail válido.'

        repo = UserRepository()
        user = repo.find_by_email(email)

        if user is None:
            LogService.log_action(email, 'GOOGLE_LOGIN_UNAUTHORIZED', f'Attempt from IP: {ip_address}')
            return None, 'Este e-mail não está cadastrado no sistema.'

        login_user(user)
        LogService.log_action(user, 'GOOGLE_LOGIN_SUCCESS')
        return user, None
