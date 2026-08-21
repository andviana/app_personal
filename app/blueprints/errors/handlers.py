import traceback
from flask import render_template, current_app, request
from app import db
from app.blueprints.errors import bp
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
