import logging
import sys
import os
from datetime import datetime
from flask import current_app

class LogService:
    _logger = None
    _log_file = 'app.log'
    _log_dir = 'logs'

    @classmethod
    def _get_logger(cls):
        if cls._logger is None:
            cls._logger = logging.getLogger('DayLog')
            cls._logger.setLevel(logging.INFO)
            
            if not cls._logger.handlers:
                # 1. StreamHandler (stdout) - Essencial para Render/Docker
                stream_handler = logging.StreamHandler(sys.stdout)
                formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
                stream_handler.setFormatter(formatter)
                cls._logger.addHandler(stream_handler)

                # 2. FileHandler - Necessário para a função de download de logs
                try:
                    if not os.path.exists(cls._log_dir):
                        os.makedirs(cls._log_dir)
                    
                    file_path = os.path.join(cls._log_dir, cls._log_file)
                    file_handler = logging.FileHandler(file_path, encoding='utf-8')
                    file_handler.setFormatter(formatter)
                    cls._logger.addHandler(file_handler)
                except Exception as e:
                    print(f"FAILED TO INITIALIZE FILE LOGGING: {str(e)}")
        
        return cls._logger

    @classmethod
    def log_action(cls, user, action, details=None):
        """
        Logs a user action.
        """
        try:
            username = user.username if hasattr(user, 'username') else str(user)
            message = f"USER: {username} | ACTION: {action}"
            if details:
                message += f" | DETAILS: {details}"
            
            cls._get_logger().info(message)
        except Exception as e:
            print(f"CRITICAL LOGGING ERROR: {str(e)}")

    @classmethod
    def get_log_path(cls) -> str:
        """Retorna o caminho absoluto do arquivo de log."""
        # Garantir que o diretório existe (caso seja chamado antes do primeiro log)
        if not os.path.exists(cls._log_dir):
            os.makedirs(cls._log_dir)
        return os.path.abspath(os.path.join(cls._log_dir, cls._log_file))
