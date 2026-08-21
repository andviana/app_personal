import os
import sys

# Adicionar o diretório raiz ao path para importar a app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from decouple import config
from app import create_app, db
from app.models import User

def seed():
    app = create_app()
    with app.app_context():
        # Criar as tabelas caso não existam
        db.create_all()
        
        admin_username = config('SEED_ADMIN_USER', default='admin')
        admin_password = config('SEED_ADMIN_PASSWORD', default='admin')
        
        users_to_create = [
            {'username': admin_username, 'password': admin_password}
        ]
        
        for u_data in users_to_create:
            existing = User.query.filter_by(username=u_data['username']).first()
            if existing:
                print(f"Usuário {u_data['username']} já existe. Atualizando senha...")
                existing.set_password(u_data['password'])
            else:
                print(f"Criando usuário {u_data['username']}...")
                user = User(username=u_data['username'])
                user.set_password(u_data['password'])
                db.session.add(user)
        
        db.session.commit()
        print("População de usuários concluída com sucesso!")

if __name__ == '__main__':
    seed()
