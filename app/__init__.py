from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_wtf.csrf import CSRFProtect
from flask_compress import Compress

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
csrf = CSRFProtect()
login.login_view = 'auth.login'
login.login_message = 'Por favor, faça login para acessar esta página.'
login.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 1. Ativa compressão Gzip/Brotli automática para arquivos estáticos (CSS, JS)
    app.config['COMPRESS_ALGORITHM_STREAMING'] = ['br', 'gzip']
    Compress(app)

    # 2. Configura o cache do navegador para 1 ano (em segundos) em produção
    # O navegador guardará o CSS localmente e não fará requisições repetidas ao Render
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000

    db.init_app(app)
    migrate.init_app(app, db)

    login.init_app(app)
    csrf.init_app(app)

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
               'snippets.shared' not in request.endpoint and \
               'static' != request.endpoint:
                
                # Se for a home page, redireciona silenciosamente sem mensagem de erro
                if request.endpoint == 'main.index':
                    from flask import redirect, url_for
                    return redirect(url_for('auth.login'))
                    
                return login.unauthorized()



    from app.blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.blueprints.tasks import bp as tasks_bp
    app.register_blueprint(tasks_bp, url_prefix='/tasks')

    from app.blueprints.lists import bp as lists_bp
    app.register_blueprint(lists_bp, url_prefix='/lists')

    from app.blueprints.settings import bp as settings_bp
    app.register_blueprint(settings_bp, url_prefix='/settings')

    from app.blueprints.snippets import bp as snippets_bp
    app.register_blueprint(snippets_bp, url_prefix='/snippets')

    from app.blueprints.simple_lists import bp as simple_lists_bp
    app.register_blueprint(simple_lists_bp, url_prefix='/simple_lists')

    from app.blueprints.bookmarks import bp as bookmarks_bp
    app.register_blueprint(bookmarks_bp, url_prefix='/bookmarks')

    from app.blueprints.perfumes import bp as perfumes_bp
    app.register_blueprint(perfumes_bp, url_prefix='/perfumes')

    from app.blueprints.pessoas import bp as pessoas_bp
    app.register_blueprint(pessoas_bp, url_prefix='/pessoas')

    from app.blueprints.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    return app
