from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from app.blueprints.settings import bp
from app.services.settings_service import SettingsService

@bp.route('/')
def index():
    data = SettingsService.get_index_data()
    return render_template('settings/index.html', **data)

@bp.route('/backup/export', methods=['GET'])
def backup_export():
    try:
        return SettingsService.export_backup_response(current_user)
    except Exception as e:
        flash(f'Erro ao gerar backup: {str(e)}', 'danger')
        return redirect(url_for('settings.index'))

@bp.route('/backup/import', methods=['POST'])
def backup_import():
    file = request.files.get('backup_file')
    success, message = SettingsService.import_backup_action(file, current_user)
    return jsonify({'success': success, 'message': message})

@bp.route('/alterar_senha', methods=['GET', 'POST'])
def alterar_senha():
    if request.method == 'POST':
        success, message = SettingsService.update_password(current_user, request.form)
        flash(message, 'success' if success else 'danger')
        if success:
            return redirect(url_for('settings.index'))
        return redirect(url_for('settings.alterar_senha'))
    return render_template('settings/change_password.html')

# --- CRUD Genérico para Configurações ---
@bp.route('/<entity_type>/add', methods=['POST'])
def add_entity(entity_type):
    denominacao = request.form.get('denominacao')
    SettingsService.create_entity(entity_type, denominacao, current_user)
    return redirect(url_for('settings.index'))

@bp.route('/<entity_type>/edit/<int:id>', methods=['POST'])
def edit_entity(entity_type, id):
    denominacao = request.form.get('denominacao')
    SettingsService.update_entity(entity_type, id, denominacao, current_user)
    return redirect(url_for('settings.index'))

@bp.route('/<entity_type>/delete/<int:id>', methods=['POST'])
def delete_entity(entity_type, id):
    success, message = SettingsService.delete_entity(entity_type, id, current_user)
    if not success:
        flash(message, 'warning')
    return redirect(url_for('settings.index'))

@bp.route('/download_logs')
def download_logs():
    try:
        return SettingsService.get_logs_response(current_user)
    except Exception as e:
        flash(f'Erro ao baixar logs: {str(e)}', 'danger')
        return redirect(url_for('settings.index'))
