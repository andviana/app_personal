"""
Decorators de view — centralizam o padrão de tratamento de erro repetido em
várias rotas dos blueprints (checagem de permissão + flash/redirect, ou
resposta JSON quando a requisição vem via AJAX).

Antes: cada rota que chamava um service com checagem de dono/compartilhamento
reimplementava o mesmo bloco try/except (ver histórico de `tasks/routes.py`,
`lists/routes.py`). Isso divergia com o tempo (algumas rotas tratavam AJAX,
outras não; mensagens de fallback diferentes) e — por capturar
`Exception` de forma ampla — escondia bugs reais atrás de uma mensagem
genérica de "erro" sem nenhum log.

Agora: a exceção de negócio (`PermissionError`, levantada pelos services
como `TaskService`/`ListService` quando o usuário não é dono/colaborador)
é tratada em um único lugar. Qualquer outra exceção não prevista continua
subindo para o error handler global (`errors/handlers.py`), que loga via
`LogService` e mostra a página 500 — em vez de ser mascarada como uma
mensagem de formulário.
"""
import functools
from flask import flash, jsonify, redirect, request, url_for


def _wants_json() -> bool:
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def handle_permission_error(fallback_endpoint: str, **fallback_kwargs):
    """
    Envolve uma view que chama um service capaz de levantar `PermissionError`.

    - Requisição AJAX: responde JSON `{"success": False, "error": <msg>}` com
      status 403.
    - Requisição normal: usa `flash(..., 'danger')` e redireciona de volta
      para `request.referrer`, ou para `fallback_endpoint` se não houver.

    Uso:
        @bp.route('/archive/<int:id>', methods=['POST'])
        @login_required
        @handle_permission_error('tasks.index')
        def archive(id):
            TaskService.archive_task(id, current_user)
            flash('Tarefa desativada com sucesso.', 'success')
            return redirect(request.referrer or url_for('tasks.index'))
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            try:
                return view_func(*args, **kwargs)
            except PermissionError as e:
                if _wants_json():
                    return jsonify({'success': False, 'error': str(e)}), 403
                flash(str(e), 'danger')
                return redirect(request.referrer or url_for(fallback_endpoint, **fallback_kwargs))
        return wrapper
    return decorator


def flash_service_errors(fallback_endpoint: str, error_prefix: str = 'Erro', **fallback_kwargs):
    """
    Envolve uma view de criar/editar/excluir que não tem um modelo de
    permissão próprio (ex.: Perfumes, Pessoas — recursos compartilhados
    entre todos os usuários do app, sem dono). Qualquer exceção levantada
    pelo service é exibida ao usuário como flash message, prefixada por
    `error_prefix` (ex.: "Erro ao cadastrar").

    Uso:
        @bp.route('/add', methods=['POST'])
        @flash_service_errors('perfumes.index', error_prefix='Erro ao cadastrar')
        def add():
            PerfumeService.create_perfume(request.form, current_user)
            flash('Perfume cadastrado com sucesso!', 'success')
            return redirect(url_for('perfumes.index'))
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            try:
                return view_func(*args, **kwargs)
            except Exception as e:
                flash(f'{error_prefix}: {str(e)}', 'danger')
                return redirect(url_for(fallback_endpoint, **fallback_kwargs))
        return wrapper
    return decorator
