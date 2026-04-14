from flask import render_template, redirect, url_for, flash, request
from app.blueprints.pessoas import bp
from app.services.pessoa_service import PessoaService
from flask_login import current_user

@bp.route('/')
def index():
    search = request.args.get('search', '')
    pessoas = PessoaService.get_all_pessoas(search)
    return render_template('pessoas/index.html', pessoas=pessoas, search=search)

@bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        try:
            PessoaService.create_pessoa(request.form, current_user.username)
            flash('Pessoa cadastrada com sucesso!', 'success')
            return redirect(url_for('pessoas.index'))
        except Exception as e:
            flash(f'Erro ao cadastrar: {str(e)}', 'danger')
            
    return render_template('pessoas/form.html', pessoa=None)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'POST':
        try:
            PessoaService.update_pessoa(id, request.form, current_user.username)
            flash('Dados atualizados com sucesso!', 'success')
            return redirect(url_for('pessoas.index'))
        except Exception as e:
            flash(f'Erro ao atualizar: {str(e)}', 'danger')
            
    from app.repositories.pessoa_repository import PessoaRepository
    pessoa = PessoaRepository().get_or_404(id)
    return render_template('pessoas/form.html', pessoa=pessoa)

@bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    try:
        PessoaService.delete_pessoa(id, current_user.username)
        flash('Pessoa removida com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao remover: {str(e)}', 'danger')
    return redirect(url_for('pessoas.index'))
