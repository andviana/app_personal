from flask import render_template, request, redirect, url_for, Response
from app.blueprints.tasks import bp

from app.services.pdf_service import build_tasks_pdf
from app.services.task_service import TaskService
from flask_login import current_user

@bp.route('/')
def index():
    view = request.args.get('view')
    grupo_id = request.args.get('grupo_id', type=int)
    
    if view == 'all':
        grupos = TaskService.get_tasks_data()
        return render_template('tasks/index.html', grupos=grupos, view='all')
    elif grupo_id:
        grupo = TaskService.get_group_detail(grupo_id)
        grupos = TaskService.get_all_groups()
        return render_template('tasks/index.html', grupos=grupos, grupo_selecionado=grupo, view='detail')
    else:
        grupos = TaskService.get_all_groups()
        return render_template('tasks/index.html', grupos=grupos, view='groups')

@bp.route('/add', methods=['POST'])
def add():
    descricao = request.form.get('descricao')
    grupo_id = request.form.get('grupo_id')
    TaskService.create_task(descricao, grupo_id, current_user)
    return redirect(request.referrer or url_for('tasks.index'))

@bp.route('/edit/<int:id>', methods=['POST'])
def edit(id):
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
    return redirect(request.referrer or url_for('tasks.index'))

@bp.route('/iniciar/<int:id>', methods=['POST'])
def iniciar(id):
    TaskService.start_task(id, current_user)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return {'success': True, 'status': 'INICIADO'}
    return redirect(request.referrer or url_for('tasks.index'))

@bp.route('/concluir/<int:id>', methods=['POST'])
def concluir(id):
    TaskService.complete_task(id, current_user)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return {'success': True, 'status': 'FINALIZADO'}
    return redirect(request.referrer or url_for('tasks.index'))

@bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    TaskService.delete_task(id, current_user)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return {'success': True}
    return redirect(request.referrer or url_for('tasks.index'))

@bp.route('/add_grupo', methods=['POST'])
def add_grupo():
    denominacao = request.form.get('denominacao')
    TaskService.create_group(denominacao, current_user)
    return redirect(request.referrer or url_for('tasks.index'))

@bp.route('/export_pdf')
def export_pdf():
    tarefas = TaskService.get_all_tasks()
    pdf_bytes = build_tasks_pdf(tarefas)
    return Response(pdf_bytes, mimetype='application/pdf', headers={'Content-Disposition': 'attachment;filename=tarefas.pdf'})
