#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Instalar dependências de frontend otimizada e buildar CSS minificado
npm ci
npm run build:css

# Executar migrações do banco de dados
flask db upgrade

# Garantir criação de tabelas e usuários iniciais
python scripts/seed_users.py
