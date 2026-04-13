import logging
import os
from datetime import datetime
from flask import current_app

class LogService:
    _logger = None

    @classmethod
    def _get_logger(cls):
        if cls._logger is None:
            # Ensure logs directory exists
            log_dir = os.path.join(current_app.root_path, '..', 'logs')
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            log_path = os.path.join(log_dir, 'app.log')
            
            cls._logger = logging.getLogger('DayLog')
            cls._logger.setLevel(logging.INFO)
            
            # Prevent adding multiple handlers if the logger is reused
            if not cls._logger.handlers:
                handler = logging.FileHandler(log_path, encoding='utf-8')
                formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
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
        username = user.username if hasattr(user, 'username') else str(user)
        message = f"USER: {username} | ACTION: {action}"
        if details:
            message += f" | DETAILS: {details}"
        
        cls._get_logger().info(message)

    @classmethod
    def get_log_path(cls):
        return os.path.join(current_app.root_path, '..', 'logs', 'app.log')
