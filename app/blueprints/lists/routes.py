from flask import render_template, request, redirect, url_for, jsonify
from app.blueprints.lists import bp
from app.services.list_service import ListService
from flask_login import current_user

@bp.route('/')
def index():
    listas, tipos = ListService.get_lists_data()
    return render_template('lists/index.html', listas=listas, tipos=tipos)

@bp.route('/add', methods=['POST'])
def add():
    titulo = request.form.get('titulo')
    tipo_id = request.form.get('tipo_id')
    ListService.create_list(titulo, tipo_id, current_user)
    return redirect(url_for('lists.index'))

@bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    ListService.delete_list(id, current_user)
    return redirect(url_for('lists.index'))

@bp.route('/<int:id>')
def detail(id):
    lista, grupos = ListService.get_list_detail(id)
    return render_template('lists/detail.html', lista=lista, grupos=grupos)

@bp.route('/<int:lista_id>/item/add', methods=['POST'])
def add_item(lista_id):
    descricao = request.form.get('descricao')
    grupo_id = request.form.get('grupo_id')
    valor = request.form.get('valor')
    url = request.form.get('url')
    ListService.create_list_item(lista_id, descricao, grupo_id, valor, url, current_user)
    return redirect(url_for('lists.detail', id=lista_id))

@bp.route('/item/check/<int:item_id>', methods=['POST'])
def check_item(item_id):
    data = request.json
    item = ListService.toggle_item_check(item_id, data.get('checked', False), current_user)
    return jsonify({'success': True, 'comprado': item.comprado})

@bp.route('/item/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    lista_id = request.form.get('lista_id')
    ListService.delete_item(item_id, current_user)
    return redirect(url_for('lists.detail', id=lista_id))
