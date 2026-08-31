#!/usr/bin/env sh
# Ponto de entrada do container de produção.
#
# Aplica as migrações do banco de dados automaticamente a cada deploy, antes
# de subir o servidor — sem isso, um deploy que inclua uma migração nova
# (ex: nova coluna) sobe o código novo com o schema antigo e a aplicação
# quebra em runtime com erros como "column ... does not exist".
set -e

echo "Aplicando migrações do banco de dados..."
flask db upgrade

echo "Iniciando o servidor..."
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --threads 2 run:app
