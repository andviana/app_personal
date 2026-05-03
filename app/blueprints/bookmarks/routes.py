from flask import render_template, request, redirect, url_for, jsonify, flash
from app.blueprints.bookmarks import bp
from app.services.bookmark_service import BookmarkService
from flask_login import current_user

@bp.route('/')
def index():
    bookmarks = BookmarkService.get_all_bookmarks()
    categories = BookmarkService.get_all_categories()
    return render_template('bookmarks/index.html', bookmarks=bookmarks, categories=categories)

@bp.route('/scrape', methods=['POST'])
def scrape():
    url = request.json.get('url')
    if not url:
        return jsonify({'success': False, 'error': 'URL não fornecida'})
    
    result = BookmarkService.scrape_url(url)
    return jsonify(result)

@bp.route('/add', methods=['POST'])
def add():
    titulo = request.form.get('titulo')
    url = request.form.get('url')
    descricao = request.form.get('descricao')
    image_url = request.form.get('image_url')
    category_ids = request.form.getlist('category_ids')
    
    success, message = BookmarkService.create_bookmark(titulo, url, descricao, category_ids, image_url)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('bookmarks.index'))

@bp.route('/edit/<int:id>', methods=['POST'])
def edit(id):
    titulo = request.form.get('titulo')
    url = request.form.get('url')
    descricao = request.form.get('descricao')
    image_url = request.form.get('image_url')
    category_ids = request.form.getlist('category_ids')
    
    success, message = BookmarkService.update_bookmark(id, titulo, url, descricao, category_ids, image_url)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('bookmarks.index'))

@bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    success, message = BookmarkService.delete_bookmark(id)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('bookmarks.index'))

@bp.route('/batch', methods=['POST'])
def batch_add():
    batch_text = request.form.get('batch_text')
    category_ids = request.form.getlist('category_ids')
    
    if not batch_text:
        flash('Nenhum texto informado para o lote.', 'danger')
        return redirect(url_for('bookmarks.index'))
    
    success, message = BookmarkService.create_batch_bookmarks(batch_text, category_ids)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('bookmarks.index'))

@bp.route('/category/add', methods=['POST'])
def category_add():
    nome = request.form.get('nome')
    success, message = BookmarkService.create_category(nome)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('bookmarks.index'))

@bp.route('/category/edit/<int:id>', methods=['POST'])
def category_edit(id):
    nome = request.form.get('nome')
    success, message = BookmarkService.update_category(id, nome)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('bookmarks.index'))

@bp.route('/category/delete/<int:id>', methods=['POST'])
def category_delete(id):
    success, message = BookmarkService.delete_category(id)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('bookmarks.index'))
