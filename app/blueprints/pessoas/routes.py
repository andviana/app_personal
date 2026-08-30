from flask import render_template, redirect, url_for, flash, request
from app.blueprints.pessoas import bp
from app.decorators import flash_service_errors
from app.services.pessoa_service import PessoaService
from flask_login import current_user, login_required

@bp.route('/')
@login_required
def index():
    search = request.args.get('search', '')
    pessoas = PessoaService.get_all_pessoas(search)
    return render_template('pessoas/index.html', pessoas=pessoas, search=search)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        try:
            PessoaService.create_pessoa(request.form, current_user)
            flash('Pessoa cadastrada com sucesso!', 'success')
            return redirect(url_for('pessoas.index'))
        except Exception as e:
            flash(f'Erro ao cadastrar: {str(e)}', 'danger')

    return render_template('pessoas/form.html', pessoa=None)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if request.method == 'POST':
        try:
            PessoaService.update_pessoa(id, request.form, current_user)
            flash('Dados atualizados com sucesso!', 'success')
            return redirect(url_for('pessoas.index'))
        except Exception as e:
            flash(f'Erro ao atualizar: {str(e)}', 'danger')

    pessoa = PessoaService.get_pessoa_by_id(id)
    return render_template('pessoas/form.html', pessoa=pessoa)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@flash_service_errors('pessoas.index', error_prefix='Erro ao remover')
def delete(id):
    PessoaService.delete_pessoa(id, current_user)
    flash('Pessoa removida com sucesso!', 'success')
    return redirect(url_for('pessoas.index'))
