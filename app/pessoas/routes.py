from flask import render_template, redirect, url_for, flash, request
from app import db
from app.models import Pessoa, Endereco, Telefone, PessoaArquivo
from app.pessoas import bp
from app.services.log_service import LogService
from flask_login import current_user
from datetime import datetime
import re

def sanitize_url(url):
    if not url:
        return ""
    # Garantir que comece com http/https
    if not (url.startswith('http://') or url.startswith('https://')):
        return f"https://{url}"
    return url

@bp.route('/')
def index():
    search = request.args.get('search', '')
    if search:
        pessoas = Pessoa.query.filter(Pessoa.nome_completo.ilike(f'%{search}%')).all()
    else:
        pessoas = Pessoa.query.order_by(Pessoa.nome_completo).all()
    return render_template('pessoas/index.html', pessoas=pessoas, search=search)

@bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        try:
            # Dados básicos
            rg_data = request.form.get('rg_data_expedicao')
            nasc_data = request.form.get('data_nascimento')
            
            pessoa = Pessoa(
                nome_completo=request.form.get('nome_completo'),
                rg_numero=request.form.get('rg_numero'),
                rg_orgao=request.form.get('rg_orgao'),
                rg_data_expedicao=datetime.strptime(rg_data, '%Y-%m-%d') if rg_data else None,
                cpf=request.form.get('cpf'),
                pis=request.form.get('pis'),
                data_nascimento=datetime.strptime(nasc_data, '%Y-%m-%d') if nasc_data else None,
                foto_url=request.form.get('foto_url')
            )
            db.session.add(pessoa)
            db.session.flush() # Para pegar o ID

            # Endereços
            enderecos = request.form.getlist('enderecos[]')
            for end in enderecos:
                if end.strip():
                    db.session.add(Endereco(pessoa_id=pessoa.id, descricao=end.strip()))

            # Telefones
            telefones = request.form.getlist('telefones[]')
            for tel in telefones:
                if tel.strip():
                    db.session.add(Telefone(pessoa_id=pessoa.id, numero=tel.strip()))

            # Arquivos/Links
            titulos = request.form.getlist('arquivo_titulos[]')
            urls = request.form.getlist('arquivo_urls[]')
            for t, u in zip(titulos, urls):
                if t.strip() and u.strip():
                    db.session.add(PessoaArquivo(
                        pessoa_id=pessoa.id, 
                        titulo=t.strip(), 
                        url=sanitize_url(u.strip())
                    ))

            db.session.commit()
            LogService.log_action(current_user.username, "PESSOA_CREATED", f"NOME: {pessoa.nome_completo}")
            flash('Pessoa cadastrada com sucesso!', 'success')
            return redirect(url_for('pessoas.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar: {str(e)}', 'danger')
            
    return render_template('pessoas/form.html', pessoa=None)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    pessoa = Pessoa.query.get_or_404(id)
    if request.method == 'POST':
        try:
            rg_data = request.form.get('rg_data_expedicao')
            nasc_data = request.form.get('data_nascimento')
            
            pessoa.nome_completo = request.form.get('nome_completo')
            pessoa.rg_numero = request.form.get('rg_numero')
            pessoa.rg_orgao = request.form.get('rg_orgao')
            pessoa.rg_data_expedicao = datetime.strptime(rg_data, '%Y-%m-%d') if rg_data else None
            pessoa.cpf = request.form.get('cpf')
            pessoa.pis = request.form.get('pis')
            pessoa.data_nascimento = datetime.strptime(nasc_data, '%Y-%m-%d') if nasc_data else None
            pessoa.foto_url = request.form.get('foto_url')

            # Limpar relacionados para reinserir (simplificação)
            Endereco.query.filter_by(pessoa_id=pessoa.id).delete()
            Telefone.query.filter_by(pessoa_id=pessoa.id).delete()
            PessoaArquivo.query.filter_by(pessoa_id=pessoa.id).delete()

            # Endereços
            enderecos = request.form.getlist('enderecos[]')
            for end in enderecos:
                if end.strip():
                    db.session.add(Endereco(pessoa_id=pessoa.id, descricao=end.strip()))

            # Telefones
            telefones = request.form.getlist('telefones[]')
            for tel in telefones:
                if tel.strip():
                    db.session.add(Telefone(pessoa_id=pessoa.id, numero=tel.strip()))

            # Arquivos/Links
            titulos = request.form.getlist('arquivo_titulos[]')
            urls = request.form.getlist('arquivo_urls[]')
            for t, u in zip(titulos, urls):
                if t.strip() and u.strip():
                    db.session.add(PessoaArquivo(
                        pessoa_id=pessoa.id, 
                        titulo=t.strip(), 
                        url=sanitize_url(u.strip())
                    ))

            db.session.commit()
            LogService.log_action(current_user.username, "PESSOA_UPDATED", f"NOME: {pessoa.nome_completo}")
            flash('Dados atualizados com sucesso!', 'success')
            return redirect(url_for('pessoas.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar: {str(e)}', 'danger')
            
    return render_template('pessoas/form.html', pessoa=pessoa)

@bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    pessoa = Pessoa.query.get_or_404(id)
    nome = pessoa.nome_completo
    db.session.delete(pessoa)
    db.session.commit()
    LogService.log_action(current_user.username, "PESSOA_DELETED", f"NOME: {nome}")
    flash('Pessoa removida com sucesso!', 'success')
    return redirect(url_for('pessoas.index'))
