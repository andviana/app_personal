import traceback
from flask import render_template, current_app, request
from app import db
from app.blueprints.errors import bp
from app.exceptions import NotFoundError
from app.services.log_service import LogService

@bp.app_errorhandler(400)
def bad_request_error(error):
    return render_template('errors/400.html'), 400

@bp.app_errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(NotFoundError)
def domain_not_found_error(error):
    """Traduz a exceção de domínio levantada pelos repositórios (ver
    `BaseRepository.get_or_404`) para a mesma página 404 acima. Mantém a
    camada de dados desacoplada do Flask."""
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(PermissionError)
def permission_error(error):
    """Rede de segurança para checagens de autorização (`PermissionError`,
    levantada pelos services) que não foram capturadas explicitamente pela
    view — evita que uma falta de permissão vire um 500 genérico."""
    return render_template('errors/403.html'), 403

@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    tb = traceback.format_exc()
    LogService.log_action('System', 'ERROR_500', f"URL: {request.url} | Details: {str(error)}\n{tb}")
    return render_template('errors/500.html'), 500

@bp.app_errorhandler(Exception)
def unhandled_exception(error):
    db.session.rollback()
    tb = traceback.format_exc()
    LogService.log_action('System', 'UNHANDLED_EXCEPTION', f"URL: {request.url} | Details: {str(error)}\n{tb}")
    # Em modo local (DEBUG=True), re-eleva o erro para depuração
    if current_app.debug:
        raise error
    # Em homologação e produção, renderiza a página 500 sem expor o stack trace ao usuário
    return render_template('errors/500.html'), 500
