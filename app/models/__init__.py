from app.models.user import User
from app.models.tasks import GrupoTarefas, StatusTarefas, Tarefa
from app.models.lists import TipoLista, GrupoItem, Lista, ItemLista
from app.models.catalog import Snippet, Perfume
from app.models.persona import Pessoa, Endereco, Telefone, PessoaArquivo

__all__ = [
    'User',
    'GrupoTarefas', 'StatusTarefas', 'Tarefa',
    'TipoLista', 'GrupoItem', 'Lista', 'ItemLista',
    'Snippet', 'Perfume',
    'Pessoa', 'Endereco', 'Telefone', 'PessoaArquivo'
]
