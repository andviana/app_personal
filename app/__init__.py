from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Por favor, faça login para acessar esta página.'
login.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    @login.user_loader
    def load_user(id):
        from app.models import User
        return db.session.get(User, int(id))

    @app.before_request
    def require_login():
        from flask import request
        from flask_login import current_user
        
        # Excluir rotas de autenticação, estáticas e o próprio login
        if not current_user.is_authenticated:
            if request.endpoint and \
               'auth.' not in request.endpoint and \
               'static' != request.endpoint:
                return login.unauthorized()

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.tasks import bp as tasks_bp
    app.register_blueprint(tasks_bp, url_prefix='/tasks')

    from app.lists import bp as lists_bp
    app.register_blueprint(lists_bp, url_prefix='/lists')

    from app.settings import bp as settings_bp
    app.register_blueprint(settings_bp, url_prefix='/settings')

    from app.snippets import bp as snippets_bp
    app.register_blueprint(snippets_bp, url_prefix='/snippets')

    return app
