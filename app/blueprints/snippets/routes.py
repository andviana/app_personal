from flask import render_template, request, redirect, url_for, jsonify
from app.blueprints.snippets import bp
from app.services.snippet_service import SnippetService
from flask_login import current_user

@bp.route('/')
def index():
    search = request.args.get('search', '')
    snippets = SnippetService.get_all_snippets(search)
    return render_template('snippets/index.html', snippets=snippets, search=search)

@bp.route('/novo')
def novo():
    return render_template('snippets/new.html')

@bp.route('/<int:id>')
def view(id):
    snippet = SnippetService.get_snippet_by_id(id)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'id': snippet.id,
            'titulo': snippet.titulo,
            'conteudo': snippet.conteudo,
            'linguagem': snippet.linguagem,
            'html': snippet.conteudo # In a real app we'd convert markdown/code to HTML
        })
    return render_template('snippets/view.html', snippet=snippet)

@bp.route('/editar/<int:id>')
def editar(id):
    snippet = SnippetService.get_snippet_by_id(id)
    return render_template('snippets/edit.html', snippet=snippet)

@bp.route('/add', methods=['POST'])
def add():
    SnippetService.create_snippet(request.form, current_user)
    return redirect(url_for('snippets.index'))

@bp.route('/edit/<int:id>', methods=['POST'])
def edit(id):
    SnippetService.update_snippet(id, request.form, current_user)
    return redirect(url_for('snippets.index'))

@bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    SnippetService.delete_snippet(id, current_user)
    return redirect(url_for('snippets.index'))

# Fallback for old template names if needed, but better to fix templates
@bp.route('/<int:id>/deletar', methods=['POST'])
def deletar(id):
    return delete(id)
