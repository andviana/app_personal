import os
from decouple import config

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # 1. Leitura do Ambiente de Execução: 'local', 'homologation', 'production'
    ENVIRONMENT = config('ENVIRONMENT', default='local').strip().lower()

    # 2. Validação estrita do modo DEBUG: estritamente False quando ENVIRONMENT != local
    if ENVIRONMENT == 'local':
        DEBUG = config('DEBUG', default=True, cast=bool)
    else:
        DEBUG = False

    SECRET_KEY = config('SECRET_KEY', default='you-will-never-guess')

    # 3. Configuração de Allowed Hosts & CORS
    # Em produção, o ALLOWED_HOSTS inclui daylog.institutoviva.digital por padrão
    ALLOWED_HOSTS = config(
        'ALLOWED_HOSTS',
        default='daylog.institutoviva.digital,localhost,127.0.0.1',
        cast=lambda v: [s.strip() for s in v.split(',') if s.strip()]
    )

    CORS_ALLOWED_ORIGINS = config(
        'CORS_ALLOWED_ORIGINS',
        default='https://daylog.institutoviva.digital,http://localhost:5000,http://127.0.0.1:5000',
        cast=lambda v: [s.strip() for s in v.split(',') if s.strip()]
    )

    # 3.1 Login com Google (OAuth 2.0 / OpenID Connect)
    # Client ID e Secret vêm do Google Cloud Console (ver README para o passo a passo).
    # Deixe em branco para manter o botão "Continuar com Google" desativado.
    GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')
    GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET', default='')

    # 4. Seleção de Banco de Dados conforme o cenário/ambiente
    if ENVIRONMENT == 'homologation':
        # Homologação: Supabase PostgreSQL (Deploy no Render)
        db_url = config('DATABASE_URL', default=config('SUPABASE_DATABASE_URL', default=''))
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        if not db_url:
            raise ValueError("DATABASE_URL ou SUPABASE_DATABASE_URL deve ser definida para o ambiente de homologação.")
        SQLALCHEMY_DATABASE_URI = db_url

    elif ENVIRONMENT == 'production':
        # Produção: PostgreSQL interno via Docker na Hostinger
        pg_user = config('POSTGRES_USER', default='postgres')
        pg_pass = config('POSTGRES_PASSWORD', default='postgres')
        pg_host = config('POSTGRES_HOST', default='db')
        pg_port = config('POSTGRES_PORT', default='5432')
        pg_db = config('POSTGRES_DB', default='daylog')
        
        db_url = config('DATABASE_URL', default='')
        # Se POSTGRES_PASSWORD for especificado no .env, usa diretamente para garantir sincronia com o container db
        if db_url and not config('POSTGRES_PASSWORD', default=''):
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
            SQLALCHEMY_DATABASE_URI = db_url
        else:
            SQLALCHEMY_DATABASE_URI = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"

    else:
        # Local (padrão): Banco de dados SQLite nativo
        sqlite_name = config('SQLITE_DB_NAME', default='app.db')
        sqlite_path = os.path.join(basedir, sqlite_name)
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{sqlite_path}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 5. Configuração de Caminhos Absolutos para Arquivos Estáticos e Mídia
    STATIC_FOLDER = os.path.abspath(config('STATIC_FOLDER', default=os.path.join(basedir, 'app', 'static')))
    MEDIA_FOLDER = os.path.abspath(config('MEDIA_FOLDER', default=os.path.join(basedir, 'app', 'media')))
    UPLOAD_FOLDER = MEDIA_FOLDER

    # 6. Segurança e Cookies
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False if ENVIRONMENT == 'local' else config('SESSION_COOKIE_SECURE', default=True, cast=bool)
