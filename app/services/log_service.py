import logging
import sys
from datetime import datetime
from flask import current_app

class LogService:
    _logger = None

    @classmethod
    def _get_logger(cls):
        if cls._logger is None:
            # Em ambientes como Render, logar para stdout é a prática recomendada
            cls._logger = logging.getLogger('DayLog')
            cls._logger.setLevel(logging.INFO)
            
            # Impedir adição de múltiplos handlers se o logger for reutilizado
            if not cls._logger.handlers:
                # Usar sys.stdout em vez de FileHandler para evitar problemas de permissão em disco
                handler = logging.StreamHandler(sys.stdout)
                formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
                handler.setFormatter(formatter)
                cls._logger.addHandler(handler)
        
        return cls._logger

    @classmethod
    def log_action(cls, user, action, details=None):
        """
        Logs a user action.
        :param user: User object or string 'System'
        :param action: String describing the action (e.g., 'LOGIN', 'TASK_CREATED')
        :param details: Optional additional context
        """
        try:
            username = user.username if hasattr(user, 'username') else str(user)
            message = f"USER: {username} | ACTION: {action}"
            if details:
                message += f" | DETAILS: {details}"
            
            cls._get_logger().info(message)
        except Exception as e:
            # Log falhou (ex: erro de buffer, thread, etc). 
            # NÃO derrubar a aplicação por causa disso.
            print(f"CRITICAL LOGGING ERROR: {str(e)}")

    @classmethod
    def get_log_path(cls):
        # Retorna dummy path já que não estamos usando arquivo literal
        return "stdout"
