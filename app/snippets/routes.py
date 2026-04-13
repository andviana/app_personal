from flask import render_template, request, redirect, url_for, flash, jsonify
from app.snippets import bp
from app.models import Snippet
from app import db
from app.services.markdown_renderer import render_markdown
from app.services.log_service import LogService
from flask_login import current_user

@bp.route('/')
def index():
    query = request.args.get('q', '')
    if query:
        snippets = Snippet.query.filter(
            (Snippet.titulo.ilike(f'%{query}%')) | 
            (Snippet.descricao.ilike(f'%{query}%'))
        ).order_by(Snippet.data_criacao.desc()).all()
    else:
        snippets = Snippet.query.order_by(Snippet.data_criacao.desc()).all()
    
    # Processamos o markdown para o mobile (acordeão) no servidor também para manter consistência
    rendered_snippets = []
    for s in snippets:
        rendered_snippets.append({
            'id': s.id,
            'titulo': s.titulo,
            'descricao': s.descricao,
            'html': render_markdown(s.conteudo)
        })
    
    return render_template('snippets/index.html', snippets=rendered_snippets, query=query)

@bp.route('/novo', methods=['GET', 'POST'])
def novo():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descricao = request.form.get('descricao')
        conteudo = request.form.get('conteudo')
        
        if not titulo or not conteudo:
            flash('Título e conteúdo são obrigatórios.', 'danger')
            return redirect(url_for('snippets.novo'))
        
        snippet = Snippet(titulo=titulo, descricao=descricao, conteudo=conteudo)
        db.session.add(snippet)
        db.session.commit()
        LogService.log_action(current_user, 'SNIPPET_CREATED', f'ID: {snippet.id} | TITLE: {titulo}')
        flash('Snippet cadastrado com sucesso!', 'success')
        return redirect(url_for('snippets.index'))
    
    return render_template('snippets/new.html')

@bp.route('/<int:id>')
def view(id):
    snippet = Snippet.query.get_or_404(id)
    snippet_html = render_markdown(snippet.conteudo)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'id': snippet.id,
            'titulo': snippet.titulo,
            'descricao': snippet.descricao,
            'conteudo': snippet.conteudo, # Markdown original para cópia
            'html': snippet_html
        })
    
    return render_template('snippets/view.html', snippet=snippet, snippet_html=snippet_html)

@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def editar(id):
    snippet = Snippet.query.get_or_404(id)
    if request.method == 'POST':
        snippet.titulo = request.form.get('titulo')
        snippet.descricao = request.form.get('descricao')
        snippet.conteudo = request.form.get('conteudo')
        
        if not snippet.titulo or not snippet.conteudo:
            flash('Título e conteúdo são obrigatórios.', 'danger')
            return redirect(url_for('snippets.editar', id=id))
        
        db.session.commit()
        LogService.log_action(current_user, 'SNIPPET_EDITED', f'ID: {id} | NEW_TITLE: {snippet.titulo}')
        flash('Snippet atualizado com sucesso!', 'success')
        return redirect(url_for('snippets.index'))
    
    return render_template('snippets/edit.html', snippet=snippet)

@bp.route('/<int:id>/deletar', methods=['POST'])
def deletar(id):
    snippet = Snippet.query.get_or_404(id)
    db.session.delete(snippet)
    db.session.commit()
    LogService.log_action(current_user, 'SNIPPET_DELETED', f'ID: {id} | TITLE: {snippet.titulo}')
    flash('Snippet removido com sucesso!', 'success')
    return redirect(url_for('snippets.index'))
