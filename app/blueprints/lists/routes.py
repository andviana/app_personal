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
    denominacao = request.form.get('denominacao')
    tipo_id = request.form.get('tipo_id')
    ListService.create_list(denominacao, tipo_id, current_user)
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
    item_nome = request.form.get('item')
    grupo_id = request.form.get('grupo_id')
    valor = request.form.get('valor')
    link = request.form.get('link')
    ListService.create_list_item(lista_id, item_nome, grupo_id, valor, link, current_user)
    return redirect(url_for('lists.detail', id=lista_id))

@bp.route('/item/<int:item_id>/edit', methods=['POST'])
def edit_item(item_id):
    item_nome = request.form.get('item')
    grupo_id = request.form.get('grupo_id')
    valor = request.form.get('valor')
    link = request.form.get('link')
    item = ListService.update_list_item(item_id, item_nome, grupo_id, valor, link, current_user)
    if item:
        return redirect(url_for('lists.detail', id=item.lista_id))
    return redirect(url_for('lists.index'))

@bp.route('/item/toggle/<int:item_id>', methods=['POST'])
def toggle_item(item_id):
    data = request.get_json(silent=True)
    # Handle both JSON (from JS) and Form (from fallback)
    if data and 'checked' in data:
        checked = data['checked']
    elif 'checked' in request.form:
        checked = request.form.get('checked') == 'true'
    else:
        # Default toggle behavior if no explicit state is provided
        checked = None
        
    item = ListService.toggle_item_check(item_id, checked, current_user)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'status': item.status})
    return redirect(url_for('lists.detail', id=item.lista_id))

@bp.route('/item/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    lista_id = request.form.get('lista_id')
    ListService.delete_item(item_id, current_user)
    return redirect(url_for('lists.detail', id=lista_id))

@bp.route('/tipo/add', methods=['POST'])
def add_tipo():
    denominacao = request.form.get('denominacao')
    ListService.create_list_type(denominacao, current_user)
    return redirect(url_for('lists.index'))

@bp.route('/grupo/add/<int:id>', methods=['POST'])
def add_grupo_item(id):
    denominacao = request.form.get('denominacao')
    ListService.create_item_group(denominacao, current_user)
    return redirect(url_for('lists.detail', id=id))

@bp.route('/scrape/<int:list_id>', methods=['POST'])
def scrape_add(list_id):
    url = request.form.get('url')
    # Use the ScraperService if available, otherwise fallback
    from app.services.scraper_service import ScraperService
    ScraperService.scrape_and_add(url, list_id, current_user)
    return redirect(url_for('lists.detail', id=list_id))

@bp.route('/export/<int:id>')
def export_pdf(id):
    from app.services.pdf_service import PDFService
    return PDFService.generate_list_pdf(id)
