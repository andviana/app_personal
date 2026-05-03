from flask import render_template, request, redirect, url_for, jsonify, flash
from app.blueprints.simple_lists import bp
from app.services.simple_list_service import SimpleListService
from flask_login import current_user

@bp.route('/')
def index():
    listas = SimpleListService.get_all_lists()
    return render_template('simple_lists/index.html', listas=listas)

@bp.route('/add', methods=['POST'])
def add():
    nome = request.form.get('nome')
    if not nome:
        flash('O nome da lista é obrigatório.', 'danger')
        return redirect(url_for('simple_lists.index'))
    
    success, message = SimpleListService.create_list(nome)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('simple_lists.index'))

@bp.route('/edit/<int:id>', methods=['POST'])
def edit(id):
    nome = request.form.get('nome')
    if not nome:
        flash('O nome da lista é obrigatório.', 'danger')
        return redirect(url_for('simple_lists.index'))
    
    success, message = SimpleListService.update_list(id, nome)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('simple_lists.index'))

@bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    success, message = SimpleListService.delete_list(id)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('simple_lists.index'))

@bp.route('/<int:id>')
def detail(id):
    lista = SimpleListService.get_list_by_id(id)
    if not lista:
        flash('Lista não encontrada.', 'danger')
        return redirect(url_for('simple_lists.index'))
    return render_template('simple_lists/detail.html', lista=lista)

@bp.route('/<int:lista_id>/item/add', methods=['POST'])
def add_item(lista_id):
    nome = request.form.get('nome')
    link = request.form.get('link')
    if not nome:
        flash('O nome do item é obrigatório.', 'danger')
        return redirect(url_for('simple_lists.detail', id=lista_id))
    
    success, message = SimpleListService.create_item(lista_id, nome, link)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('simple_lists.detail', id=lista_id))

@bp.route('/<int:lista_id>/item/batch', methods=['POST'])
def add_batch(lista_id):
    batch_text = request.form.get('batch_text')
    if not batch_text:
        flash('Nenhum texto informado para o lote.', 'danger')
        return redirect(url_for('simple_lists.detail', id=lista_id))
    
    success, message = SimpleListService.create_items_batch(lista_id, batch_text)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('simple_lists.detail', id=lista_id))

@bp.route('/item/edit/<int:item_id>', methods=['POST'])
def edit_item(item_id):
    nome = request.form.get('nome')
    link = request.form.get('link')
    lista_id = request.form.get('lista_id')
    
    if not nome:
        flash('O nome do item é obrigatório.', 'danger')
        return redirect(url_for('simple_lists.detail', id=lista_id))
    
    success, message = SimpleListService.update_item(item_id, nome, link)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('simple_lists.detail', id=lista_id))

@bp.route('/item/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    lista_id = request.form.get('lista_id')
    success, message = SimpleListService.delete_item(item_id)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('simple_lists.detail', id=lista_id))

@bp.route('/item/toggle/<int:item_id>', methods=['POST'])
def toggle_item(item_id):
    data = request.get_json()
    checked = data.get('checked', False)
    success, new_status = SimpleListService.toggle_item(item_id, checked)
    return jsonify({'success': success, 'status': new_status})
