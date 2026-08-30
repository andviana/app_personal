from flask import render_template, request, redirect, url_for, jsonify, flash
from app.blueprints.bookmarks import bp
from app.services.bookmark_service import BookmarkService
from app.repositories.user_repository import UserRepository
from flask_login import current_user, login_required

@bp.route('/')
@login_required
def index():
    show_archived = request.args.get('archived') == 'true'
    bookmarks = BookmarkService.get_all_bookmarks(current_user, is_active=not show_archived)
    categories = BookmarkService.get_all_categories()
    users = UserRepository().list_all_users()
    return render_template(
        'bookmarks/index.html',
        bookmarks=bookmarks,
        categories=categories,
        users=users,
        is_archived_view=show_archived
    )

@bp.route('/scrape', methods=['POST'])
@login_required
def scrape():
    url = request.json.get('url')
    if not url:
        return jsonify({'success': False, 'error': 'URL não fornecida'})
    
    result = BookmarkService.scrape_url(url)
    return jsonify(result)

@bp.route('/add', methods=['POST'])
@login_required
def add():
    titulo = request.form.get('titulo')
    url = request.form.get('url')
    descricao = request.form.get('descricao')
    image_url = request.form.get('image_url')
    category_ids = request.form.getlist('category_ids')
    
    success, message = BookmarkService.create_bookmark(titulo, url, descricao, category_ids, image_url, current_user)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('bookmarks.index'))

@bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    titulo = request.form.get('titulo')
    url = request.form.get('url')
    descricao = request.form.get('descricao')
    image_url = request.form.get('image_url')
    category_ids = request.form.getlist('category_ids')
    
    success, message = BookmarkService.update_bookmark(id, titulo, url, descricao, category_ids, image_url, current_user)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('bookmarks.index'))

@bp.route('/archive/<int:id>', methods=['POST'])
@login_required
def archive(id):
    success, message = BookmarkService.archive_bookmark(id, current_user)
    flash(message, 'success' if success else 'danger')
    return redirect(request.referrer or url_for('bookmarks.index'))

@bp.route('/reactivate/<int:id>', methods=['POST'])
@login_required
def reactivate(id):
    success, message = BookmarkService.reactivate_bookmark(id, current_user)
    flash(message, 'success' if success else 'danger')
    return redirect(request.referrer or url_for('bookmarks.index', archived='true'))

@bp.route('/share/<int:id>', methods=['POST'])
@login_required
def share(id):
    user_ids = request.form.getlist('user_ids', type=int)
    success, message = BookmarkService.share_bookmark(id, user_ids, current_user)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': success, 'message': message}), 200 if success else 403
    flash(message, 'success' if success else 'danger')
    return redirect(request.referrer or url_for('bookmarks.index'))

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    success, message = BookmarkService.delete_bookmark(id, current_user)
    flash(message, 'success' if success else 'danger')
    return redirect(request.referrer or url_for('bookmarks.index'))

@bp.route('/batch', methods=['POST'])
@login_required
def batch_add():
    batch_text = request.form.get('batch_text')
    category_ids = request.form.getlist('category_ids')
    
    if not batch_text:
        flash('Nenhum texto informado para o lote.', 'danger')
        return redirect(url_for('bookmarks.index'))
    
    success, message = BookmarkService.create_batch_bookmarks(batch_text, category_ids, current_user)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('bookmarks.index'))

@bp.route('/category/add', methods=['POST'])
@login_required
def category_add():
    nome = request.form.get('nome')
    success, message = BookmarkService.create_category(nome)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('bookmarks.index'))

@bp.route('/category/edit/<int:id>', methods=['POST'])
@login_required
def category_edit(id):
    nome = request.form.get('nome')
    success, message = BookmarkService.update_category(id, nome)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('bookmarks.index'))

@bp.route('/category/delete/<int:id>', methods=['POST'])
@login_required
def category_delete(id):
    success, message = BookmarkService.delete_category(id)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('bookmarks.index'))
