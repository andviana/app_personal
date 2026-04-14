from app.repositories.base_repository import BaseRepository
from app.models import Pessoa, Endereco, Telefone, PessoaArquivo

class PessoaRepository(BaseRepository):
    def __init__(self):
        super().__init__(Pessoa)

    def search_by_name(self, name):
        return self.model.query.filter(Pessoa.nome_completo.ilike(f'%{name}%')).all()

    def get_related_counts(self):
        # Example of specialized method if needed
        pass

    def delete_related(self, pessoa_id):
        Endereco.query.filter_by(pessoa_id=pessoa_id).delete()
        Telefone.query.filter_by(pessoa_id=pessoa_id).delete()
        PessoaArquivo.query.filter_by(pessoa_id=pessoa_id).delete()
