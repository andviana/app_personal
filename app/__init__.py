import os
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_wtf.csrf import CSRFProtect
from flask_compress import Compress
from authlib.integrations.flask_client import OAuth
from werkzeug.middleware.proxy_fix import ProxyFix

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
csrf = CSRFProtect()
oauth = OAuth()
login.login_view = 'auth.login'
login.login_message = 'Por favor, faça login para acessar esta página.'
login.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(
        __name__,
        static_folder=config_class.STATIC_FOLDER,
        static_url_path='/static'
    )
    app.config.from_object(config_class)

    # Confia em 1 hop de proxy reverso (Traefik, em produção) para o esquema
    # (http/https), host e IP originais da requisição — sem isso, URLs geradas
    # com _external=True (ex: redirect_uri do login com Google) saem como
    # http:// mesmo atrás de um proxy HTTPS, e os logs registram o IP interno
    # do proxy em vez do IP real do cliente.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # Garantir que o diretório de mídia (caminho absoluto) exista
    if 'MEDIA_FOLDER' in app.config:
        os.makedirs(app.config['MEDIA_FOLDER'], exist_ok=True)

    # 1. Ativa compressão Gzip/Brotli automática para arquivos estáticos (CSS, JS)
    app.config['COMPRESS_ALGORITHM_STREAMING'] = ['br', 'gzip']
    Compress(app)

    # 2. Configura o cache do navegador para 1 ano (em segundos) em produção
    # O navegador guardará o CSS localmente e não fará requisições repetidas ao Render/Hostinger
    if app.debug:
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    else:
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000

    db.init_app(app)
    migrate.init_app(app, db)

    login.init_app(app)
    csrf.init_app(app)

    # Login com Google (OAuth 2.0 / OpenID Connect) — só registra o provedor
    # se as credenciais estiverem configuradas (ver README, seção Google Login).
    oauth.init_app(app)
    if app.config.get('GOOGLE_CLIENT_ID') and app.config.get('GOOGLE_CLIENT_SECRET'):
        oauth.register(
            name='google',
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'},
        )

    @app.route('/media/<path:filename>')
    def serve_media(filename):
        from flask import send_from_directory
        return send_from_directory(app.config['MEDIA_FOLDER'], filename)

    @login.user_loader
    def load_user(id):
        from app.models import User
        return db.session.get(User, int(id))

    @app.before_request
    def validate_host():
        from flask import request, abort
        from app.services.log_service import LogService
        
        # Em ambiente local, permite qualquer host dev
        if app.config.get('ENVIRONMENT') == 'local':
            return

        allowed = app.config.get('ALLOWED_HOSTS', [])
        if '*' in allowed:
            return

        host = request.host.split(':')[0]
        if host not in allowed:
            LogService.log_action('Security', 'UNAUTHORIZED_HOST', f"Host não permitido tentou acesso: {host}")
            abort(400, description="Host não autorizado.")

    @app.before_request
    def require_login():
        from flask import request
        from flask_login import current_user
        
        # Excluir rotas de autenticação, estáticas, mídia e o próprio login
        if not current_user.is_authenticated:
            if request.endpoint and \
               'auth.' not in request.endpoint and \
               'snippets.shared' not in request.endpoint and \
               'static' != request.endpoint and \
               'serve_media' != request.endpoint:
                
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

    @app.after_request
    def set_security_and_cors_headers(response):
        from flask import request
        origin = request.headers.get('Origin')
        allowed_origins = app.config.get('CORS_ALLOWED_ORIGINS', [])

        if origin and origin in allowed_origins:
            # Origem explicitamente confiável: pode receber cookies de sessão.
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, X-CSRFToken'
        elif origin and '*' in allowed_origins:
            # Curinga: nunca combinar com credentials, senão qualquer site
            # poderia ler respostas autenticadas do usuário via fetch/XHR.
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, X-CSRFToken'

        # Cabeçalhos de Segurança HTTP recomendados em Produção
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    @app.context_processor
    def utility_processor():
        def get_file_version(filename):
            try:
                # Retorna a data de modificação do arquivo como versão
                path = os.path.join(current_app.root_path, '..', filename)
                return int(os.path.getmtime(path))
            except OSError:
                return 1
        google_login_enabled = bool(app.config.get('GOOGLE_CLIENT_ID') and app.config.get('GOOGLE_CLIENT_SECRET'))
        return dict(get_file_version=get_file_version, google_login_enabled=google_login_enabled)

    return app
