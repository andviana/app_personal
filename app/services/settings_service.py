import json
import os
from datetime import datetime
from app.repositories.base_repository import BaseRepository
from app.models import GrupoTarefas, TipoLista, GrupoItem, User, Tarefa, Lista, ItemLista
from app.services.log_service import LogService
from app.services.backup_service import export_data, import_data
from flask import make_response, send_file

class SettingsService:
    @staticmethod
    def update_password(current_user, form_data):
        senha_atual = form_data.get('senha_atual')
        nova_senha = form_data.get('nova_senha')
        confirmar_senha = form_data.get('confirmar_senha')
        
        if not current_user.check_password(senha_atual):
            return False, 'Senha atual incorreta.'
        
        if nova_senha != confirmar_senha:
            return False, 'As novas senhas não coincidem.'
            
        repo = BaseRepository(User)
        user = repo.get_by_id(current_user.id)
        user.set_password(nova_senha)
        repo.commit()
        LogService.log_action(current_user.username, 'PASSWORD_CHANGED')
        return True, 'Senha alterada com sucesso!'

    @staticmethod
    def get_index_data():
        return {
            'grupos_tarefas': BaseRepository(GrupoTarefas).list_all(order_by=GrupoTarefas.denominacao),
            'tipos_listas': BaseRepository(TipoLista).list_all(order_by=TipoLista.denominacao),
            'grupos_itens': BaseRepository(GrupoItem).list_all(order_by=GrupoItem.denominacao)
        }

    @staticmethod
    def create_entity(entity_type, denominacao, current_user):
        model_map = {
            'grupo_tarefa': GrupoTarefas,
            'tipo_lista': TipoLista,
            'grupo_item': GrupoItem
        }
        model = model_map.get(entity_type)
        if model and denominacao:
            repo = BaseRepository(model)
            nova_entidade = model(denominacao=denominacao.upper())
            repo.add(nova_entidade)
            repo.commit()
            LogService.log_action(current_user.username, f'{entity_type.upper()}_CREATED', f'NAME: {denominacao}')
            return True
        return False

    @staticmethod
    def update_entity(entity_type, id, denominacao, current_user):
        model_map = {
            'grupo_tarefa': GrupoTarefas,
            'tipo_lista': TipoLista,
            'grupo_item': GrupoItem
        }
        model = model_map.get(entity_type)
        if model and denominacao:
            repo = BaseRepository(model)
            entidade = repo.get_or_404(id)
            entidade.denominacao = denominacao.upper()
            repo.commit()
            LogService.log_action(current_user.username, f'{entity_type.upper()}_UPDATED', f'ID: {id} | NEW_NAME: {denominacao}')
            return True
        return False

    @staticmethod
    def delete_entity(entity_type, id, current_user):
        model_map = {
            'grupo_tarefa': (GrupoTarefas, Tarefa, 'grupo_id'),
            'tipo_lista': (TipoLista, Lista, 'tipo_id'),
            'grupo_item': (GrupoItem, ItemLista, 'grupo_id')
        }
        config = model_map.get(entity_type)
        if config:
            model, related_model, fk_field = config
            repo = BaseRepository(model)
            entidade = repo.get_or_404(id)
            
            # Check for dependencies
            if related_model.query.filter_by(**{fk_field: id}).first():
                return False, "Existem registros vinculados a esta categoria."
                
            repo.delete(entidade)
            repo.commit()
            LogService.log_action(current_user.username, f'{entity_type.upper()}_DELETED', f'ID: {id}')
            return True, "Removido com sucesso."
        return False, "Tipo de entidade inválido."

    @staticmethod
    def export_backup_response(current_user):
        data = export_data()
        json_str = json.dumps(data, indent=4)
        filename = f"backup_app_personal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        response = make_response(json_str)
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        LogService.log_action(current_user.username, 'BACKUP_EXPORTED', f'Filename: {filename}')
        return response

    @staticmethod
    def import_backup_action(file, current_user):
        if not file or file.filename == '':
            return False, 'Arquivo inválido.'
        try:
            json_data = json.load(file)
            success, message = import_data(json_data)
            if success:
                LogService.log_action(current_user.username, 'BACKUP_IMPORTED', f'File: {file.filename}')
            else:
                LogService.log_action(current_user.username, 'BACKUP_IMPORT_FAILED', message)
            return success, message
        except Exception as e:
            LogService.log_action(current_user.username, 'BACKUP_IMPORT_ERROR', str(e))
            return False, f'Erro ao ler arquivo: {str(e)}'

    @staticmethod
    def get_logs_response(current_user):
        path = LogService.get_log_path()
        if not os.path.exists(path):
            LogService.log_action('System', 'LOG_FILE_INITIALIZED')
        
        LogService.log_action(current_user.username, 'LOG_DOWNLOADED')
        return send_file(path, as_attachment=True, download_name='daylog_system.log')
