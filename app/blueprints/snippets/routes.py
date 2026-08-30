from flask import render_template, request, redirect, url_for, jsonify
from app.blueprints.snippets import bp
from app.services.snippet_service import SnippetService
from app.services.markdown_renderer import render_markdown
from flask_login import current_user, login_required

@bp.route('/')
@login_required
def index():
    search = request.args.get('search', '')
    snippets = SnippetService.get_all_snippets(search)

    # Pre-render Markdown content for mobile accordion
    for s in snippets:
        s.html = render_markdown(s.conteudo)

    return render_template('snippets/index.html', snippets=snippets, search=search)

@bp.route('/novo')
@login_required
def novo():
    return render_template('snippets/new.html')

@bp.route('/<int:id>')
@login_required
def view(id):
    snippet = SnippetService.get_snippet_by_id(id)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'id': snippet.id,
            'uuid': snippet.uuid,
            'titulo': snippet.titulo,
            'conteudo': snippet.conteudo,
            'descricao': snippet.descricao,
            'html': render_markdown(snippet.conteudo),
            'tags': [{'id': t.id, 'denominacao': t.denominacao, 'cor': t.cor} for t in snippet.tags],
            'share_url': url_for('snippets.shared', uuid=snippet.uuid, _external=True)
        })

    return render_template('snippets/view.html', snippet=snippet, snippet_html=render_markdown(snippet.conteudo))

@bp.route('/tags/list')
@login_required
def list_tags():
    tags = SnippetService.get_all_tags()
    return jsonify([{'id': t.id, 'denominacao': t.denominacao, 'cor': t.cor} for t in tags])

@bp.route('/tags/add', methods=['POST'])
@login_required
def add_tag():
    denominacao = request.form.get('denominacao')
    cor = request.form.get('cor')
    tag = SnippetService.create_tag(denominacao, cor, current_user)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'tag': {'id': tag.id, 'denominacao': tag.denominacao, 'cor': tag.cor}})
        
    return redirect(url_for('snippets.index'))

@bp.route('/tags/delete/<int:id>', methods=['POST'])
@login_required
def delete_tag(id):
    SnippetService.delete_tag(id, current_user)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})

    return redirect(url_for('snippets.index'))

@bp.route('/<int:snippet_id>/tags/toggle', methods=['POST'])
@login_required
def toggle_tag(snippet_id):
    tag_id = request.form.get('tag_id')
    SnippetService.toggle_snippet_tag(snippet_id, tag_id, current_user)
    return jsonify({'success': True})

@bp.route('/shared/<string:uuid>')
def shared(uuid):
    snippet = SnippetService.get_snippet_by_uuid(uuid)
    return render_template('snippets/public_view.html',
                          snippet=snippet,
                          snippet_html=render_markdown(snippet.conteudo))

@bp.route('/editar/<int:id>')
@login_required
def editar(id):
    snippet = SnippetService.get_snippet_by_id(id)
    return render_template('snippets/edit.html', snippet=snippet)

@bp.route('/add', methods=['POST'])
@login_required
def add():
    SnippetService.create_snippet(request.form, current_user)
    return redirect(url_for('snippets.index'))

@bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    SnippetService.update_snippet(id, request.form, current_user)
    return redirect(url_for('snippets.index'))

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    SnippetService.delete_snippet(id, current_user)
    return redirect(url_for('snippets.index'))
