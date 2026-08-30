"""
Exceções de domínio da aplicação.

Mantém a camada de repositórios/serviços independente do Flask: em vez de
chamar `flask.abort(...)` diretamente (o que acopla a persistência de dados
à camada web), o repositório levanta uma exceção de domínio e a tradução
para uma resposta HTTP acontece em um único lugar
(`app/blueprints/errors/handlers.py`).

`PermissionError` (built-in do Python) continua sendo usada nos services
para falhas de autorização — é o padrão já adotado em todo o projeto
(ver `TaskService`, `ListService`) e não há motivo para reinventar uma
exceção equivalente.
"""


class NotFoundError(Exception):
    """Levantada pelos repositórios quando um registro não é encontrado."""
    pass
