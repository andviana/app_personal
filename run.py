from app import create_app, db
from app.models import Tarefa, GrupoTarefas, StatusTarefas, Lista, TipoLista, ItemLista, GrupoItem

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Tarefa': Tarefa, 'GrupoTarefas': GrupoTarefas, 'StatusTarefas': StatusTarefas, 'Lista': Lista, 'TipoLista': TipoLista, 'ItemLista': ItemLista, 'GrupoItem': GrupoItem}
