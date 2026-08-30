from flask import render_template, request, redirect, url_for, flash
from app.blueprints.perfumes import bp
from app.decorators import flash_service_errors
from app.services.perfume_service import PerfumeService
from flask_login import current_user, login_required

@bp.route('/')
@login_required
def index():
    perfumes = PerfumeService.get_all_perfumes()
    return render_template('perfumes/index.html', perfumes=perfumes)

@bp.route('/add', methods=['POST'])
@login_required
@flash_service_errors('perfumes.index', error_prefix='Erro ao cadastrar')
def add():
    PerfumeService.create_perfume(request.form, current_user)
    flash('Perfume cadastrado com sucesso!', 'success')
    return redirect(url_for('perfumes.index'))

@bp.route('/edit/<int:id>', methods=['POST'])
@login_required
@flash_service_errors('perfumes.index', error_prefix='Erro ao atualizar')
def edit(id):
    PerfumeService.update_perfume(id, request.form, current_user)
    flash('Perfume atualizado com sucesso!', 'success')
    return redirect(url_for('perfumes.index'))

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@flash_service_errors('perfumes.index', error_prefix='Erro ao excluir')
def delete(id):
    PerfumeService.delete_perfume(id, current_user)
    flash('Perfume excluído com sucesso!', 'success')
    return redirect(url_for('perfumes.index'))
