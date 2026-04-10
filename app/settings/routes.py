from flask import render_template, request, redirect, url_for, flash, send_file, jsonify, make_response
from flask_login import current_user
from app.settings import bp
from app.models import GrupoTarefas, TipoLista, GrupoItem, Tarefa, Lista, ItemLista
from app import db
from app.services.backup_service import export_data, import_data
import json
from datetime import datetime
from io import BytesIO

@bp.route('/backup/export', methods=['GET'])
def backup_export():
    try:
        data = export_data()
        json_str = json.dumps(data, indent=4)
        
        filename = f"backup_app_personal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        response = make_response(json_str)
        response.headers['Content-Type'] = 'application/json'
        # Adiciona aspas ao redor do nome do arquivo para evitar problemas com espaços ou caracteres especiais (mesmo que não haja agora)
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    except Exception as e:
        flash(f'Erro ao gerar backup: {str(e)}', 'danger')
        return redirect(url_for('settings.index'))

@bp.route('/backup/import', methods=['POST'])
def backup_import():
    if 'backup_file' not in request.files:
        return jsonify({'success': False, 'message': 'Nenhum arquivo enviado.'}), 400
        
    file = request.files['backup_file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado.'}), 400
        
    try:
        json_data = json.load(file)
        success, message = import_data(json_data)
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao ler arquivo: {str(e)}'})

@bp.route('/alterar_senha', methods=['GET', 'POST'])
def alterar_senha():
    if request.method == 'POST':
        senha_atual = request.form.get('senha_atual')
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')
        
        if not current_user.check_password(senha_atual):
            flash('Senha atual incorreta.', 'danger')
            return redirect(url_for('settings.alterar_senha'))
        
        if nova_senha != confirmar_senha:
            flash('As novas senhas não coincidem.', 'danger')
            return redirect(url_for('settings.alterar_senha'))
            
        current_user.set_password(nova_senha)
        db.session.commit()
        flash('Senha alterada com sucesso!', 'success')
        return redirect(url_for('settings.index'))
        
    return render_template('settings/change_password.html')

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
