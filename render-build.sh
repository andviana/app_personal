#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Executar migrações do banco de dados
flask db upgrade
