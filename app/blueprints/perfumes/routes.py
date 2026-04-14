from flask import render_template, request, redirect, url_for, flash
from app.blueprints.perfumes import bp
from app.services.perfume_service import PerfumeService
from flask_login import current_user

@bp.route('/')
def index():
    perfumes = PerfumeService.get_all_perfumes()
    return render_template('perfumes/index.html', perfumes=perfumes)

@bp.route('/add', methods=['POST'])
def add():
    try:
        PerfumeService.create_perfume(request.form, current_user)
        flash('Perfume cadastrado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao cadastrar: {str(e)}', 'danger')
    return redirect(url_for('perfumes.index'))

@bp.route('/edit/<int:id>', methods=['POST'])
def edit(id):
    try:
        PerfumeService.update_perfume(id, request.form, current_user)
        flash('Perfume atualizado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao atualizar: {str(e)}', 'danger')
    return redirect(url_for('perfumes.index'))

@bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    try:
        PerfumeService.delete_perfume(id, current_user)
        flash('Perfume excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir: {str(e)}', 'danger')
    return redirect(url_for('perfumes.index'))
