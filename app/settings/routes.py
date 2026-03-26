from flask import render_template, request, redirect, url_for, flash
from app.settings import bp
from app.models import GrupoTarefas, TipoLista, GrupoItem, Tarefa, Lista, ItemLista
from app import db

@bp.route('/')
def index():
    grupos_tarefas = GrupoTarefas.query.order_by(GrupoTarefas.denominacao).all()
    tipos_listas = TipoLista.query.order_by(TipoLista.denominacao).all()
    grupos_itens = GrupoItem.query.order_by(GrupoItem.denominacao).all()
    return render_template('settings/index.html', 
                           grupos_tarefas=grupos_tarefas, 
                           tipos_listas=tipos_listas, 
                           grupos_itens=grupos_itens)

# --- CRUD GrupoTarefas ---
@bp.route('/grupo_tarefa/add', methods=['POST'])
def add_grupo_tarefa():
    denominacao = request.form.get('denominacao')
    if denominacao:
        db.session.add(GrupoTarefas(denominacao=denominacao.upper()))
        db.session.commit()
    return redirect(url_for('settings.index'))

@bp.route('/grupo_tarefa/edit/<int:id>', methods=['POST'])
def edit_grupo_tarefa(id):
    grupo = GrupoTarefas.query.get_or_404(id)
    denominacao = request.form.get('denominacao')
    if denominacao:
        grupo.denominacao = denominacao.upper()
        db.session.commit()
    return redirect(url_for('settings.index'))

@bp.route('/grupo_tarefa/delete/<int:id>', methods=['POST'])
def delete_grupo_tarefa(id):
    grupo = GrupoTarefas.query.get_or_404(id)
    # Check if there are tasks linked
    if Tarefa.query.filter_by(grupo_id=id).first():
        # Ideally we'd show a flash message here, but redirecting for simplicity as per existing pattern
        pass
    else:
        db.session.delete(grupo)
        db.session.commit()
    return redirect(url_for('settings.index'))

# --- CRUD TipoLista (Categorias) ---
@bp.route('/tipo_lista/add', methods=['POST'])
def add_tipo_lista():
    denominacao = request.form.get('denominacao')
    if denominacao:
        db.session.add(TipoLista(denominacao=denominacao.upper()))
        db.session.commit()
    return redirect(url_for('settings.index'))

@bp.route('/tipo_lista/edit/<int:id>', methods=['POST'])
def edit_tipo_lista(id):
    tipo = TipoLista.query.get_or_404(id)
    denominacao = request.form.get('denominacao')
    if denominacao:
        tipo.denominacao = denominacao.upper()
        db.session.commit()
    return redirect(url_for('settings.index'))

@bp.route('/tipo_lista/delete/<int:id>', methods=['POST'])
def delete_tipo_lista(id):
    tipo = TipoLista.query.get_or_404(id)
    if Lista.query.filter_by(tipo_id=id).first():
        pass
    else:
        db.session.delete(tipo)
        db.session.commit()
    return redirect(url_for('settings.index'))

# --- CRUD GrupoItem ---
@bp.route('/grupo_item/add', methods=['POST'])
def add_grupo_item():
    denominacao = request.form.get('denominacao')
    if denominacao:
        db.session.add(GrupoItem(denominacao=denominacao.upper()))
        db.session.commit()
    return redirect(url_for('settings.index'))

@bp.route('/grupo_item/edit/<int:id>', methods=['POST'])
def edit_grupo_item(id):
    grupo = GrupoItem.query.get_or_404(id)
    denominacao = request.form.get('denominacao')
    if denominacao:
        grupo.denominacao = denominacao.upper()
        db.session.commit()
    return redirect(url_for('settings.index'))

@bp.route('/grupo_item/delete/<int:id>', methods=['POST'])
def delete_grupo_item(id):
    grupo = GrupoItem.query.get_or_404(id)
    if ItemLista.query.filter_by(grupo_id=id).first():
        pass
    else:
        db.session.delete(grupo)
        db.session.commit()
    return redirect(url_for('settings.index'))
