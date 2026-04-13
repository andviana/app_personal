from flask import render_template, request, redirect, url_for, Response
from app.lists import bp
from app.models import Lista, TipoLista, GrupoItem, ItemLista
from app import db
from app.services.pdf_service import build_lists_pdf
from app.services.log_service import LogService
from flask_login import current_user

@bp.route('/')
def index():
    listas = Lista.query.all()
    tipos = TipoLista.query.all()
    return render_template('lists/index.html', listas=listas, tipos=tipos)

@bp.route('/add', methods=['POST'])
def add():
    denominacao = request.form.get('denominacao')
    tipo_id = request.form.get('tipo_id')
    if denominacao and tipo_id:
        nova_lista = Lista(denominacao=denominacao, tipo_id=tipo_id)
        db.session.add(nova_lista)
        db.session.commit()
        LogService.log_action(current_user, 'LIST_CREATED', f'ID: {nova_lista.id} | NAME: {denominacao}')
    return redirect(url_for('lists.index'))

@bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    lista = Lista.query.get_or_404(id)
    db.session.delete(lista)
    db.session.commit()
    LogService.log_action(current_user, 'LIST_DELETED', f'ID: {id} | NAME: {lista.denominacao}')
    return redirect(url_for('lists.index'))

@bp.route('/<int:id>')
def detail(id):
    lista = Lista.query.get_or_404(id)
    grupos = GrupoItem.query.all()
    return render_template('lists/detail.html', lista=lista, grupos=grupos)

@bp.route('/<int:id>/add_item', methods=['POST'])
def add_item(id):
    item = request.form.get('item')
    grupo_id = request.form.get('grupo_id')
    valor = request.form.get('valor')
    
    if item:
        # Forçar Caixa Alta
        item = item.upper()
        
        # Categoria Padrão: OUTROS
        if not grupo_id:
            grupo_outros = GrupoItem.query.filter(GrupoItem.denominacao.ilike('OUTROS')).first()
            if not grupo_outros:
                grupo_outros = GrupoItem(denominacao='OUTROS')
                db.session.add(grupo_outros)
                db.session.commit()
            grupo_id = grupo_outros.id
            
        try:
            v_float = float(valor) if valor else None
        except ValueError:
            v_float = None
            
        novo_item = ItemLista(
            lista_id=id,
            item=item,
            grupo_id=grupo_id,
            valor=v_float
        )
        db.session.add(novo_item)
        db.session.commit()
        LogService.log_action(current_user, 'LIST_ITEM_ADDED', f'LIST_ID: {id} | ITEM: {item}')
    return redirect(url_for('lists.detail', id=id))

@bp.route('/item/<int:item_id>/toggle', methods=['POST'])
def toggle_item(item_id):
    item = ItemLista.query.get_or_404(item_id)
    item.status = not item.status
    db.session.commit()
    LogService.log_action(current_user, 'LIST_ITEM_TOGGLED', f'ITEM_ID: {item_id} | STATUS: {item.status}')
    return redirect(url_for('lists.detail', id=item.lista_id))

@bp.route('/item/<int:item_id>/delete', methods=['POST'])
def delete_item(item_id):
    item = ItemLista.query.get_or_404(item_id)
    lista_id = item.lista_id
    db.session.delete(item)
    db.session.commit()
    LogService.log_action(current_user, 'LIST_ITEM_DELETED', f'ITEM_ID: {item_id} | ITEM: {item.item}')
    return redirect(url_for('lists.detail', id=lista_id))

@bp.route('/item/<int:item_id>/edit', methods=['POST'])
def edit_item(item_id):
    item = ItemLista.query.get_or_404(item_id)
    
    descricao = request.form.get('item')
    grupo_id = request.form.get('grupo_id')
    valor = request.form.get('valor')
    
    if descricao:
        item.item = descricao.upper() # Forçar Caixa Alta
    
    if grupo_id:
        item.grupo_id = grupo_id
    else:
        # Fallback para OUTROS se esvaziar a categoria
        grupo_outros = GrupoItem.query.filter(GrupoItem.denominacao.ilike('OUTROS')).first()
        if not grupo_outros:
            grupo_outros = GrupoItem(denominacao='OUTROS')
            db.session.add(grupo_outros)
            db.session.commit()
        item.grupo_id = grupo_outros.id
    
    try:
        v_float = float(valor) if valor else None
        item.valor = v_float
    except ValueError:
        item.valor = None

    item.link = request.form.get('link')

    db.session.commit()
    return redirect(url_for('lists.detail', id=item.lista_id))

@bp.route('/add_tipo', methods=['POST'])
def add_tipo():
    denominacao = request.form.get('denominacao')
    if denominacao:
        db.session.add(TipoLista(denominacao=denominacao))
        db.session.commit()
        LogService.log_action(current_user, 'LIST_TYPE_CREATED', f'NAME: {denominacao}')
    return redirect(url_for('lists.index'))

@bp.route('/<int:id>/add_grupo_item', methods=['POST'])
def add_grupo_item(id):
    denominacao = request.form.get('denominacao')
    if denominacao:
        db.session.add(GrupoItem(denominacao=denominacao))
        db.session.commit()
        LogService.log_action(current_user, 'LIST_ITEM_GROUP_CREATED', f'NAME: {denominacao}')
    return redirect(url_for('lists.detail', id=id))

@bp.route('/<int:id>/export_pdf')
def export_pdf(id):
    lista = Lista.query.get_or_404(id)
    pdf_bytes = build_lists_pdf(lista)
    return Response(pdf_bytes, mimetype='application/pdf', headers={'Content-Disposition': f'attachment;filename=lista_{id}.pdf'})
