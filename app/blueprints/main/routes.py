from flask import render_template
from app.blueprints.main import bp
from app.models import Tarefa, Lista, Perfume, Pessoa, Snippet, ItemLista

@bp.route('/')
def index():
    # Consider "pending" any task without data_executado
    tarefas_pendentes = Tarefa.query.filter_by(data_executado=None).count()
    
    listas_ativas = Lista.query.count()
    
    # New totals for dashboard
    perfumes_count = Perfume.query.count()
    pessoas_count = Pessoa.query.count()
    snippets_count = Snippet.query.count()
    itens_count = ItemLista.query.count()
    
    return render_template('dashboard.html', 
                          tarefas_pendentes=tarefas_pendentes, 
                          listas_ativas=listas_ativas,
                          perfumes_count=perfumes_count,
                          pessoas_count=pessoas_count,
                          snippets_count=snippets_count,
                          itens_count=itens_count)
