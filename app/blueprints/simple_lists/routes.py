from flask import render_template, request, redirect, url_for, jsonify, flash
from app.blueprints.simple_lists import bp
from app.services.simple_list_service import SimpleListService
from app.repositories.user_repository import UserRepository
from flask_login import current_user, login_required

@bp.route('/')
@login_required
def index():
    show_archived = request.args.get('archived') == 'true'
    listas = SimpleListService.get_all_lists(current_user, is_active=not show_archived)
    users = UserRepository().list_all_users()
    return render_template('simple_lists/index.html', listas=listas, is_archived_view=show_archived, users=users)

@bp.route('/add', methods=['POST'])
@login_required
def add():
    nome = request.form.get('nome')
    if not nome:
        flash('O nome da lista é obrigatório.', 'danger')
        return redirect(url_for('simple_lists.index'))
    
    success, message = SimpleListService.create_list(nome, current_user)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('simple_lists.index'))

@bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    nome = request.form.get('nome')
    if not nome:
        flash('O nome da lista é obrigatório.', 'danger')
        return redirect(url_for('simple_lists.index'))
    
    success, message = SimpleListService.update_list(id, nome, current_user)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('simple_lists.index'))

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    success, message = SimpleListService.delete_list(id, current_user)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('simple_lists.index'))

@bp.route('/archive/<int:id>', methods=['POST'])
@login_required
def archive(id):
    success, message = SimpleListService.archive_list(id, current_user)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('simple_lists.index'))

@bp.route('/reactivate/<int:id>', methods=['POST'])
@login_required
def reactivate(id):
    success, message = SimpleListService.reactivate_list(id, current_user)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('simple_lists.index', archived='true'))

@bp.route('/share/<int:id>', methods=['POST'])
@login_required
def share(id):
    user_ids = request.form.getlist('user_ids', type=int)
    success, message = SimpleListService.share_list(id, user_ids, current_user)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': success, 'message': message if success else None, 'error': None if success else message}), (200 if success else 403)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('simple_lists.index'))

@bp.route('/<int:id>')
@login_required
def detail(id):
    lista = SimpleListService.get_list_by_id(id, current_user)
    if not lista:
        flash('Lista não encontrada ou acesso negado.', 'danger')
        return redirect(url_for('simple_lists.index'))
    users = UserRepository().list_all_users()
    return render_template('simple_lists/detail.html', lista=lista, users=users)

@bp.route('/<int:lista_id>/item/add', methods=['POST'])
@login_required
def add_item(lista_id):
    nome = request.form.get('nome')
    link = request.form.get('link')
    if not nome:
        flash('O nome do item é obrigatório.', 'danger')
        return redirect(url_for('simple_lists.detail', id=lista_id))
    
    success, message = SimpleListService.create_item(lista_id, nome, link, current_user)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('simple_lists.detail', id=lista_id))

@bp.route('/<int:lista_id>/item/batch', methods=['POST'])
@login_required
def add_batch(lista_id):
    batch_text = request.form.get('batch_text')
    if not batch_text:
        flash('Nenhum texto informado para o lote.', 'danger')
        return redirect(url_for('simple_lists.detail', id=lista_id))
    
    success, message = SimpleListService.create_items_batch(lista_id, batch_text, current_user)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('simple_lists.detail', id=lista_id))

@bp.route('/item/edit/<int:item_id>', methods=['POST'])
@login_required
def edit_item(item_id):
    nome = request.form.get('nome')
    link = request.form.get('link')
    lista_id = request.form.get('lista_id')
    
    if not nome:
        flash('O nome do item é obrigatório.', 'danger')
        return redirect(url_for('simple_lists.detail', id=lista_id))
    
    success, message = SimpleListService.update_item(item_id, nome, link, current_user)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('simple_lists.detail', id=lista_id))

@bp.route('/item/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    lista_id = request.form.get('lista_id')
    success, message = SimpleListService.delete_item(item_id, current_user)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('simple_lists.detail', id=lista_id))

@bp.route('/item/toggle/<int:item_id>', methods=['POST'])
@login_required
def toggle_item(item_id):
    data = request.get_json() or {}
    checked = data.get('checked', False)
    success, new_status = SimpleListService.toggle_item(item_id, checked, current_user)
    return jsonify({'success': success, 'status': new_status})

