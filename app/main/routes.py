from flask import render_template
from app.main import bp
from app.models import Tarefa, Lista

@bp.route('/')
def index():
    # Consider "pending" any task without data_executado
    tarefas_pendentes = Tarefa.query.filter_by(data_executado=None).count()
    
    listas_ativas = Lista.query.count()
    
    return render_template('dashboard.html', tarefas_pendentes=tarefas_pendentes, listas_ativas=listas_ativas)
