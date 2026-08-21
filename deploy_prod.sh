#!/usr/bin/env bash
set -e

echo "=========================================="
echo "🚀 INICIANDO DEPLOY DE PRODUÇÃO - DAYLOG"
echo "=========================================="

# 1. Puxar as últimas alterações do repositório
echo "📥 Atualizando código-fonte a partir do Git..."
git pull origin main || git pull

# 2. Verificar existência do arquivo .env
if [ ! -f .env ]; then
    echo "⚠️ Arquivo .env não encontrado! Copiando modelo de .env.example..."
    cp .env.example .env
fi

# 3. Garantir a existência da rede externa do Traefik
echo "🌐 Verificando rede compartilhada 'traefik_net'..."
docker network create traefik_net 2>/dev/null || true

# 4. Fazer o build das imagens Docker e subir em detached mode
echo "🐳 Executando build e subindo containers com Docker Compose..."
if command -v docker-compose &> /dev/null; then
    docker-compose up -d --build
else
    docker compose up -d --build
fi

# 5. Executar migrações do banco de dados e seed inicial
echo "🗄️ Executando migrações e seed de dados..."
if command -v docker-compose &> /dev/null; then
    docker-compose exec -T web flask db upgrade
    docker-compose exec -T web python scripts/seed_users.py
else
    docker compose exec -T web flask db upgrade
    docker compose exec -T web python scripts/seed_users.py
fi

echo "=========================================="
echo "✅ DEPLOY CONCLUÍDO COM SUCESSO!"
echo "=========================================="
