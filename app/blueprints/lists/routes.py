from flask import render_template, request, redirect, url_for, jsonify, flash
from app.blueprints.lists import bp
from app.services.list_service import ListService
from app.repositories.user_repository import UserRepository
from flask_login import current_user, login_required

@bp.route('/')
@login_required
def index():
    show_archived = request.args.get('archived') == 'true'
    listas, tipos = ListService.get_lists_data(current_user, is_active=not show_archived)
    users = UserRepository().list_all_users()
    return render_template('lists/index.html', listas=listas, tipos=tipos, is_archived_view=show_archived, users=users)

@bp.route('/add', methods=['POST'])
@login_required
def add():
    denominacao = request.form.get('denominacao')
    tipo_id = request.form.get('tipo_id')
    ListService.create_list(denominacao, tipo_id, current_user)
    return redirect(url_for('lists.index'))

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    try:
        ListService.delete_list(id, current_user)
        flash('Lista excluída com sucesso.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('lists.index'))

@bp.route('/archive/<int:id>', methods=['POST'])
@login_required
def archive(id):
    try:
        ListService.archive_list(id, current_user)
        flash('Lista desativada com sucesso.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('lists.index'))

@bp.route('/reactivate/<int:id>', methods=['POST'])
@login_required
def reactivate(id):
    try:
        ListService.reactivate_list(id, current_user)
        flash('Lista reativada com sucesso.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('lists.index', archived='true'))

@bp.route('/share/<int:id>', methods=['POST'])
@login_required
def share(id):
    try:
        user_ids = request.form.getlist('user_ids', type=int)
        ListService.share_list(id, user_ids, current_user)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Compartilhamento atualizado!'})
        flash('Compartilhamento atualizado com sucesso!', 'success')
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)}), 403
        flash(str(e), 'danger')
    return redirect(url_for('lists.index'))

@bp.route('/<int:id>')
@login_required
def detail(id):
    try:
        lista, grupos = ListService.get_list_detail(id, current_user)
        users = UserRepository().list_all_users()
        return render_template('lists/detail.html', lista=lista, grupos=grupos, users=users)
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('lists.index'))

@bp.route('/<int:lista_id>/item/add', methods=['POST'])
@login_required
def add_item(lista_id):
    try:
        item_nome = request.form.get('item')
        grupo_id = request.form.get('grupo_id')
        valor = request.form.get('valor')
        link = request.form.get('link')
        ListService.create_list_item(lista_id, item_nome, grupo_id, valor, link, current_user)
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('lists.detail', id=lista_id))

@bp.route('/item/<int:item_id>/edit', methods=['POST'])
@login_required
def edit_item(item_id):
    try:
        item_nome = request.form.get('item')
        grupo_id = request.form.get('grupo_id')
        valor = request.form.get('valor')
        link = request.form.get('link')
        item = ListService.update_list_item(item_id, item_nome, grupo_id, valor, link, current_user)
        if item:
            return redirect(url_for('lists.detail', id=item.lista_id))
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('lists.index'))

@bp.route('/item/toggle/<int:item_id>', methods=['POST'])
@login_required
def toggle_item(item_id):
    data = request.get_json(silent=True)
    if data and 'checked' in data:
        checked = data['checked']
    elif 'checked' in request.form:
        checked = request.form.get('checked') == 'true'
    else:
        checked = None
        
    try:
        item = ListService.toggle_item_check(item_id, checked, current_user)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'status': item.status})
        return redirect(url_for('lists.detail', id=item.lista_id))
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)}), 403
        flash(str(e), 'danger')
        return redirect(url_for('lists.index'))

@bp.route('/item/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    lista_id = request.form.get('lista_id')
    try:
        ListService.delete_item(item_id, current_user)
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('lists.detail', id=lista_id))

@bp.route('/tipo/add', methods=['POST'])
@login_required
def add_tipo():
    denominacao = request.form.get('denominacao')
    ListService.create_list_type(denominacao, current_user)
    return redirect(url_for('lists.index'))

@bp.route('/grupo/add/<int:id>', methods=['POST'])
@login_required
def add_grupo_item(id):
    denominacao = request.form.get('denominacao')
    ListService.create_item_group(denominacao, current_user)
    return redirect(url_for('lists.detail', id=id))

@bp.route('/scrape/<int:list_id>', methods=['POST'])
@login_required
def scrape_add(list_id):
    url = request.form.get('url')
    from app.services.scraper_service import ScraperService
    ScraperService.scrape_and_add(url, list_id, current_user)
    return redirect(url_for('lists.detail', id=list_id))

@bp.route('/export/<int:id>')
@login_required
def export_pdf(id):
    from app.services.pdf_service import PDFService
    return PDFService.generate_list_pdf(id)

