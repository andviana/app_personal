import json
import sqlalchemy
from datetime import datetime, date
from app import db
from app.repositories.base_repository import BaseRepository
from app.models import (
    User, GrupoTarefas, StatusTarefas, Tarefa,
    TipoLista, GrupoItem, Lista, ItemLista, 
    Snippet, Perfume, Pessoa, Endereco, 
    Telefone, PessoaArquivo, Tag, SnippetTag,
    Bookmark, BookmarkCategory, BookmarkAssociation
)

# Ordem de restauração (respeitando chaves estrangeiras)
MODELS_ORDER = [
    User,
    GrupoTarefas,
    StatusTarefas,
    TipoLista,
    GrupoItem,
    Tag,
    Snippet,
    Perfume,
    Pessoa,
    Tarefa,
    Lista,
    ItemLista,
    Endereco,
    Telefone,
    PessoaArquivo,
    SnippetTag,
    BookmarkCategory,
    Bookmark,
    BookmarkAssociation
]

def export_data():
    """Exporta todos os dados do banco para um dicionário JSON"""
    data = {}
    
    for model in MODELS_ORDER:
        table_name = model.__tablename__
        repo = BaseRepository(model)
        records = repo.list_all()
        
        data[table_name] = []
        for record in records:
            # Converte o objeto do modelo para dicionário
            record_dict = {}
            for column in record.__table__.columns:
                value = getattr(record, column.name)
                
                # Trata campos de data e data/hora
                if isinstance(value, (datetime, date)):
                    value = value.isoformat()
                
                record_dict[column.name] = value
            
            data[table_name].append(record_dict)
            
    return data

def import_data(json_data):
    """Restaura dados a partir de um dicionário JSON (Limpa antes de inserir)"""
    try:
        # 1. Limpa os dados em ordem inversa para evitar erros de FK
        for model in reversed(MODELS_ORDER):
            db.session.query(model).delete()
        
        # Garante que as deleções sejam processadas antes de novas inserções
        db.session.flush()
        
        # 2. Insere os dados na ordem correta
        for model in MODELS_ORDER:
            table_name = model.__tablename__
            if table_name in json_data:
                for row in json_data[table_name]:
                    # Trata as datas na volta
                    for column in model.__table__.columns:
                        col_name = column.name
                        
                        # Verifica de forma robusta se a coluna é do tipo datetime/date
                        is_datetime = False
                        if hasattr(column.type, 'python_type') and column.type.python_type in (datetime, date):
                            is_datetime = True
                        elif type(column.type).__name__.upper() in ('DATETIME', 'DATE'):
                            is_datetime = True
                            
                        if col_name in row and row[col_name] and is_datetime:
                            try:
                                # Tenta analisar o formato ISO
                                dt_val = datetime.fromisoformat(str(row[col_name]).replace('Z', '+00:00'))
                                
                                # Se a coluna for apenas Date, converte o datetime para date
                                if hasattr(column.type, 'python_type') and column.type.python_type == date:
                                    row[col_name] = dt_val.date()
                                elif 'DATE' in type(column.type).__name__.upper() and 'DATETIME' not in type(column.type).__name__.upper():
                                    row[col_name] = dt_val.date()
                                else:
                                    row[col_name] = dt_val
                            except (ValueError, TypeError):
                                pass
                    
                    obj = model(**row)
                    db.session.add(obj)
                
                # IMPORTANTE: Flush após cada tipo de modelo para garantir que 
                # as chaves estrangeiras existam antes de serem referenciadas
                db.session.flush()
        
        db.session.commit()

        # 3. Sincroniza as sequências do Postgres (se aplicável)
        try:
            reset_postgres_sequences()
        except Exception as seq_err:
            print(f"Aviso ao sincronizar sequências: {seq_err}")
            # Não falha a importação por causa das sequências, mas avisa no log
            
        return True, "Restauração concluída com sucesso!"
    except Exception as e:
        db.session.rollback()
        return False, f"Erro na restauração: {str(e)}"

def reset_postgres_sequences():
    """Sincroniza os contadores (SERIAL/IDENTITY) do Postgres com os IDs importados."""
    # Verifica se estamos usando Postgres
    if 'postgresql' not in str(db.engine.url):
        return

    for model in MODELS_ORDER:
        table_name = model.__tablename__
        # Apenas para tabelas que possuem coluna 'id'
        if hasattr(model, 'id'):
            # SQL para resetar a sequência do ID para o valor máximo atual
            # SELECT setval(pg_get_serial_sequence('table', 'id'), coalesce(max(id), 1), max(id) IS NOT null) FROM table;
            sql = sqlalchemy.text(f"""
                SELECT setval(
                    pg_get_serial_sequence('{table_name}', 'id'), 
                    COALESCE(MAX(id), 1), 
                    MAX(id) IS NOT NULL
                ) FROM "{table_name}"
            """)
            try:
                db.session.execute(sql)
            except Exception:
                # Algumas tabelas podem não ter sequências ou ter nomes diferentes
                db.session.rollback()
                continue
    
    db.session.commit()
