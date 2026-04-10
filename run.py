from app import create_app, db
from app.models import User, Tarefa, GrupoTarefas, StatusTarefas, Lista, TipoLista, ItemLista, GrupoItem

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Tarefa': Tarefa, 'GrupoTarefas': GrupoTarefas, 'StatusTarefas': StatusTarefas, 'Lista': Lista, 'TipoLista': TipoLista, 'ItemLista': ItemLista, 'GrupoItem': GrupoItem}
