from flask import render_template, request, redirect, url_for, Response, jsonify, flash
from app.blueprints.tasks import bp
from app.services.pdf_service import build_tasks_pdf
from app.services.task_service import TaskService
from app.repositories.user_repository import UserRepository
from flask_login import current_user, login_required

@bp.route('/')
@login_required
def index():
    view = request.args.get('view')
    grupo_id = request.args.get('grupo_id', type=int)
    show_archived = request.args.get('archived') == 'true' or view == 'archived'
    is_active = not show_archived
    
    users = UserRepository().list_all_users()
    
    if show_archived:
        grupos = TaskService.get_tasks_data(current_user, is_active=False)
        return render_template('tasks/index.html', grupos=grupos, view='all', is_archived_view=True, users=users)
    elif view == 'all':
        grupos = TaskService.get_tasks_data(current_user, is_active=True)
        return render_template('tasks/index.html', grupos=grupos, view='all', is_archived_view=False, users=users)
    elif grupo_id:
        grupo = TaskService.get_group_detail(grupo_id, current_user, is_active=True)
        grupos = TaskService.get_all_groups(current_user, is_active=True)
        return render_template('tasks/index.html', grupos=grupos, grupo_selecionado=grupo, view='detail', is_archived_view=False, users=users)
    else:
        grupos = TaskService.get_all_groups(current_user, is_active=True)
        return render_template('tasks/index.html', grupos=grupos, view='groups', is_archived_view=False, users=users)

@bp.route('/add', methods=['POST'])
@login_required
def add():
    descricao = request.form.get('descricao')
    grupo_id = request.form.get('grupo_id')
    TaskService.create_task(descricao, grupo_id, current_user)
    return redirect(request.referrer or url_for('tasks.index'))

@bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    try:
        descricao = request.form.get('descricao')
        grupo_id = request.form.get('grupo_id')
        status_nome = request.form.get('status_nome')
        TaskService.update_task_basic(id, descricao, grupo_id, status_nome, current_user)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {
                'success': True,
                'task': {
                    'id': id,
                    'descricao': descricao,
                    'grupo_id': int(grupo_id) if grupo_id else None,
                    'status': status_nome
                }
            }
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'success': False, 'error': str(e)}, 403
        flash(str(e), 'danger')
    return redirect(request.referrer or url_for('tasks.index'))

@bp.route('/iniciar/<int:id>', methods=['POST'])
@login_required
def iniciar(id):
    try:
        TaskService.start_task(id, current_user)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'success': True, 'status': 'INICIADO'}
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'success': False, 'error': str(e)}, 403
        flash(str(e), 'danger')
    return redirect(request.referrer or url_for('tasks.index'))

@bp.route('/concluir/<int:id>', methods=['POST'])
@login_required
def concluir(id):
    try:
        TaskService.complete_task(id, current_user)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'success': True, 'status': 'FINALIZADO'}
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'success': False, 'error': str(e)}, 403
        flash(str(e), 'danger')
    return redirect(request.referrer or url_for('tasks.index'))

@bp.route('/archive/<int:id>', methods=['POST'])
@login_required
def archive(id):
    try:
        TaskService.archive_task(id, current_user)
        flash('Tarefa desativada com sucesso.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(request.referrer or url_for('tasks.index'))

@bp.route('/reactivate/<int:id>', methods=['POST'])
@login_required
def reactivate(id):
    try:
        TaskService.reactivate_task(id, current_user)
        flash('Tarefa reativada com sucesso.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(request.referrer or url_for('tasks.index', archived='true'))

@bp.route('/share/<int:id>', methods=['POST'])
@login_required
def share(id):
    try:
        user_ids = request.form.getlist('user_ids', type=int)
        TaskService.share_task(id, user_ids, current_user)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Compartilhamento atualizado!'})
        flash('Compartilhamento atualizado com sucesso!', 'success')
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)}), 403
        flash(str(e), 'danger')
    return redirect(request.referrer or url_for('tasks.index'))

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    try:
        TaskService.delete_task(id, current_user)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'success': True}
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'success': False, 'error': str(e)}, 403
        flash(str(e), 'danger')
    return redirect(request.referrer or url_for('tasks.index'))

@bp.route('/add_grupo', methods=['POST'])
@login_required
def add_grupo():
    denominacao = request.form.get('denominacao')
    TaskService.create_group(denominacao, current_user)
    return redirect(request.referrer or url_for('tasks.index'))

@bp.route('/group/archive/<int:id>', methods=['POST'])
@login_required
def archive_grupo(id):
    try:
        TaskService.archive_group(id, current_user)
        flash('Grupo de tarefas desativado com sucesso.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(request.referrer or url_for('tasks.index'))

@bp.route('/group/reactivate/<int:id>', methods=['POST'])
@login_required
def reactivate_grupo(id):
    try:
        TaskService.reactivate_group(id, current_user)
        flash('Grupo de tarefas reativado com sucesso.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(request.referrer or url_for('tasks.index', archived='true'))

@bp.route('/group/share/<int:id>', methods=['POST'])
@login_required
def share_grupo(id):
    try:
        user_ids = request.form.getlist('user_ids', type=int)
        TaskService.share_group(id, user_ids, current_user)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Compartilhamento do grupo atualizado!'})
        flash('Compartilhamento do grupo atualizado com sucesso!', 'success')
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)}), 403
        flash(str(e), 'danger')
    return redirect(request.referrer or url_for('tasks.index'))

@bp.route('/group/delete/<int:id>', methods=['POST'])
@login_required
def delete_grupo(id):
    try:
        TaskService.delete_group(id, current_user)
        flash('Grupo excluído com sucesso.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('tasks.index'))

@bp.route('/export_pdf')
@login_required
def export_pdf():
    tarefas = TaskService.get_all_tasks(current_user, is_active=True)
    pdf_bytes = build_tasks_pdf(tarefas)
    return Response(pdf_bytes, mimetype='application/pdf', headers={'Content-Disposition': 'attachment;filename=tarefas.pdf'})

