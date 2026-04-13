from flask import render_template, request, redirect, url_for, Response
from app.tasks import bp
from app.models import Tarefa, GrupoTarefas, StatusTarefas
from app import db
from datetime import datetime, timezone
from app.services.pdf_service import build_tasks_pdf
from app.services.log_service import LogService
from flask_login import current_user

def init_defaults():
    # Ensure default Statuses and Group exist
    changed = False
    status_pendente = StatusTarefas.query.filter_by(denominacao='PENDENTE').first()
    if not status_pendente:
        status_pendente = StatusTarefas(denominacao='PENDENTE')
        db.session.add(status_pendente)
        changed = True

    status_iniciado = StatusTarefas.query.filter_by(denominacao='INICIADO').first()
    if not status_iniciado:
        status_iniciado = StatusTarefas(denominacao='INICIADO')
        db.session.add(status_iniciado)
        changed = True

    status_finalizado = StatusTarefas.query.filter_by(denominacao='FINALIZADO').first()
    if not status_finalizado:
        status_finalizado = StatusTarefas(denominacao='FINALIZADO')
        db.session.add(status_finalizado)
        changed = True

    grupo_comum = GrupoTarefas.query.filter_by(denominacao='COMUM').first()
    if not grupo_comum:
        grupo_comum = GrupoTarefas(denominacao='COMUM')
        db.session.add(grupo_comum)
        changed = True

    if changed:
        db.session.commit()
    
    return status_pendente, status_iniciado, status_finalizado, grupo_comum

@bp.route('/')
def index():
    init_defaults()
    grupos = GrupoTarefas.query.order_by(GrupoTarefas.denominacao).all()
    # We will pass 'grupos' directly. Each group has 'tarefas' relationship.
    # To ensure we get all tasks, we just rely on group.tarefas in the template.
    # Wait, what if a task has no group? The model says nullable=False, so they all have a group.
    return render_template('tasks/index.html', grupos=grupos)

@bp.route('/add', methods=['POST'])
def add():
    status_pendente, _, _, grupo_comum = init_defaults()
    descricao = request.form.get('descricao')
    grupo_id = request.form.get('grupo_id')
    
    if descricao:
        nova_tarefa = Tarefa(
            descricao=descricao,
            grupo_id=grupo_id if grupo_id else grupo_comum.id,
            status_id=status_pendente.id
        )
        db.session.add(nova_tarefa)
        db.session.commit()
        LogService.log_action(current_user, 'TASK_CREATED', f'ID: {nova_tarefa.id} | DESCRIPTION: {descricao}')
    return redirect(url_for('tasks.index'))

@bp.route('/edit/<int:id>', methods=['POST'])
def edit(id):
    tarefa = Tarefa.query.get_or_404(id)
    descricao = request.form.get('descricao')
    grupo_id = request.form.get('grupo_id')
    if descricao:
        tarefa.descricao = descricao
    if grupo_id:
        tarefa.grupo_id = grupo_id
    db.session.commit()
    LogService.log_action(current_user, 'TASK_EDITED', f'ID: {id} | NEW_DESCRIPTION: {descricao}')
    return redirect(url_for('tasks.index'))

@bp.route('/iniciar/<int:id>', methods=['POST'])
def iniciar(id):
    tarefa = Tarefa.query.get_or_404(id)
    _, status_iniciado, _, _ = init_defaults()
    tarefa.status_id = status_iniciado.id
    db.session.commit()
    LogService.log_action(current_user, 'TASK_STARTED', f'ID: {id}')
    return redirect(url_for('tasks.index'))

@bp.route('/concluir/<int:id>', methods=['POST'])
def concluir(id):
    tarefa = Tarefa.query.get_or_404(id)
    _, _, status_finalizado, _ = init_defaults()
    tarefa.status_id = status_finalizado.id
    tarefa.data_executado = datetime.now(timezone.utc)
    db.session.commit()
    LogService.log_action(current_user, 'TASK_COMPLETED', f'ID: {id}')
    return redirect(url_for('tasks.index'))

@bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    tarefa = Tarefa.query.get_or_404(id)
    db.session.delete(tarefa)
    db.session.commit()
    LogService.log_action(current_user, 'TASK_DELETED', f'ID: {id} | DESCRIPTION: {tarefa.descricao}')
    return redirect(url_for('tasks.index'))

@bp.route('/add_grupo', methods=['POST'])
def add_grupo():
    denominacao = request.form.get('denominacao')
    if denominacao:
        novo_grupo = GrupoTarefas(denominacao=denominacao.upper())
        db.session.add(novo_grupo) 
        db.session.commit()
        LogService.log_action(current_user, 'TASK_GROUP_CREATED', f'NAME: {denominacao.upper()}')
    return redirect(url_for('tasks.index'))

@bp.route('/export_pdf')
def export_pdf():
    tarefas = Tarefa.query.all()
    pdf_bytes = build_tasks_pdf(tarefas)
    return Response(pdf_bytes, mimetype='application/pdf', headers={'Content-Disposition': 'attachment;filename=tarefas.pdf'})
