from datetime import datetime
from app.repositories.pessoa_repository import PessoaRepository
from app.models import Pessoa, Endereco, Telefone, PessoaArquivo
from app.services.log_service import LogService

class PessoaService:
    @staticmethod
    def sanitize_url(url):
        if not url:
            return ""
        if not (url.startswith('http://') or url.startswith('https://')):
            return f"https://{url}"
        return url

    @staticmethod
    def get_all_pessoas(search=None):
        repo = PessoaRepository()
        if search:
            return repo.search_by_name(search)
        return repo.list_all(order_by=Pessoa.nome_completo)

    @staticmethod
    def create_pessoa(form_data, current_user):
        repo = PessoaRepository()
        rg_data = form_data.get('rg_data_expedicao')
        nasc_data = form_data.get('data_nascimento')

        pessoa = Pessoa(
            nome_completo=form_data.get('nome_completo', '').strip(),
            rg_numero=form_data.get('rg_numero', '').strip() or None,
            rg_orgao=form_data.get('rg_orgao', '').strip() or None,
            rg_data_expedicao=datetime.strptime(rg_data, '%Y-%m-%d') if rg_data else None,
            cpf=form_data.get('cpf', '').strip() or None,
            pis=form_data.get('pis', '').strip() or None,
            data_nascimento=datetime.strptime(nasc_data, '%Y-%m-%d') if nasc_data else None,
            foto_url=form_data.get('foto_url', '').strip() or None
        )
        repo.add(pessoa)
        repo.flush()

        # Endereços
        enderecos = form_data.getlist('enderecos[]')
        for end in enderecos:
            if end.strip():
                repo.add(Endereco(pessoa_id=pessoa.id, descricao=end.strip()))

        # Telefones
        telefones = form_data.getlist('telefones[]')
        for tel in telefones:
            if tel.strip():
                repo.add(Telefone(pessoa_id=pessoa.id, numero=tel.strip()))

        # Arquivos/Links
        titulos = form_data.getlist('arquivo_titulos[]')
        urls = form_data.getlist('arquivo_urls[]')
        for t, u in zip(titulos, urls):
            if t.strip() and u.strip():
                repo.add(PessoaArquivo(
                    pessoa_id=pessoa.id,
                    titulo=t.strip(),
                    url=PessoaService.sanitize_url(u.strip())
                ))

        repo.commit()
        LogService.log_action(current_user.username, "PESSOA_CREATED", f"NOME: {pessoa.nome_completo}")
        return pessoa

    @staticmethod
    def update_pessoa(id, form_data, current_user):
        repo = PessoaRepository()
        pessoa = repo.get_or_404(id)
        rg_data = form_data.get('rg_data_expedicao')
        nasc_data = form_data.get('data_nascimento')

        pessoa.nome_completo = form_data.get('nome_completo', '').strip()
        pessoa.rg_numero = form_data.get('rg_numero', '').strip() or None
        pessoa.rg_orgao = form_data.get('rg_orgao', '').strip() or None
        pessoa.rg_data_expedicao = datetime.strptime(rg_data, '%Y-%m-%d') if rg_data else None
        pessoa.cpf = form_data.get('cpf', '').strip() or None
        pessoa.pis = form_data.get('pis', '').strip() or None
        pessoa.data_nascimento = datetime.strptime(nasc_data, '%Y-%m-%d') if nasc_data else None
        pessoa.foto_url = form_data.get('foto_url', '').strip() or None

        # Limpar relacionados para reinserir
        repo.delete_related(id)

        # Endereços
        enderecos = form_data.getlist('enderecos[]')
        for end in enderecos:
            if end.strip():
                repo.add(Endereco(pessoa_id=pessoa.id, descricao=end.strip()))

        # Telefones
        telefones = form_data.getlist('telefones[]')
        for tel in telefones:
            if tel.strip():
                repo.add(Telefone(pessoa_id=pessoa.id, numero=tel.strip()))

        # Arquivos/Links
        titulos = form_data.getlist('arquivo_titulos[]')
        urls = form_data.getlist('arquivo_urls[]')
        for t, u in zip(titulos, urls):
            if t.strip() and u.strip():
                repo.add(PessoaArquivo(
                    pessoa_id=pessoa.id,
                    titulo=t.strip(),
                    url=PessoaService.sanitize_url(u.strip())
                ))

        repo.commit()
        LogService.log_action(current_user.username, "PESSOA_UPDATED", f"NOME: {pessoa.nome_completo}")
        return pessoa

    @staticmethod
    def delete_pessoa(id, current_user):
        repo = PessoaRepository()
        pessoa = repo.get_or_404(id)
        nome = pessoa.nome_completo
        repo.delete(pessoa)
        repo.commit()
        LogService.log_action(current_user.username, "PESSOA_DELETED", f"NOME: {nome}")
        return nome

    @staticmethod
    def get_pessoa_by_id(id):
        repo = PessoaRepository()
        return repo.get_or_404(id)

