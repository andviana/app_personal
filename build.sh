#!/usr/bin/env bash
# ==============================================================================
# DAYLOG - SCRIPT DE DEPLOY EM PRODUÇÃO (Hostinger VPS + Docker + Traefik)
#
# Diferente do deploy em Homologação (Render, via render-build.sh, que roda
# num buildpack Python sem Docker), a Produção roda inteiramente em
# containers Docker atrás do Traefik. Este script deve ser executado no VPS,
# dentro do diretório do projeto (onde está o docker-compose.yml) — via SSH
# manual ou por um webhook/cron que dispare o deploy.
#
# O que ele faz, em ordem:
#   1. Atualiza o código-fonte (git pull)
#   2. Reconstrói a imagem do container "web" (instala deps Python/Node e
#      recompila o CSS — tudo isso já acontece dentro do Dockerfile)
#   3. Sobe os containers (web + db, se necessário)
#   4. Confirma que o container subiu e ficou de pé (as migrações do banco
#      rodam automaticamente dentro do container, via entrypoint.sh, antes do
#      Gunicorn iniciar — se uma migração falhar, o container não sobe, e
#      este script detecta isso e para com erro em vez de reportar sucesso)
#   5. Confirma que as migrações estão em dia (checagem explícita adicional)
#   6. Limpa imagens Docker antigas para não acumular lixo em disco
# ==============================================================================

set -o errexit

# Garante que o script opera a partir do diretório onde ele está,
# independentemente de onde foi chamado (ex: via cron ou caminho absoluto).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "--- INICIANDO DEPLOY EM PRODUÇÃO (HOSTINGER VPS) ---"

# 1. Atualizar o código-fonte a partir do repositório remoto
echo "Atualizando código-fonte (git pull origin main)..."
git pull origin main

# 2. Construir a nova imagem Docker do serviço "web"
#    (instala requirements.txt, roda "npm run build:css" — tudo já
#    definido no Dockerfile em 2 estágios)
echo "Construindo a imagem Docker (web)..."
docker compose build web

# 3. Subir os serviços em segundo plano
#    (o "db" só é (re)criado se ainda não estiver rodando; a imagem dele não
#    muda a cada deploy, então não é reconstruída)
echo "Subindo os serviços (web + db)..."
docker compose up -d web

# 4. Aguardar o container inicializar e confirmar que ele ficou de pé
#    (as migrações do banco — flask db upgrade — rodam automaticamente
#    dentro do entrypoint.sh do container, antes do Gunicorn subir; se
#    falharem, o container encerra e este passo detecta isso)
echo "Aguardando o container 'web' inicializar..."
sleep 6

WEB_CID="$(docker compose ps -q web)"
WEB_STATUS="$(docker inspect -f '{{.State.Status}}' "$WEB_CID")"

if [ "$WEB_STATUS" != "running" ]; then
    echo "ERRO: o container 'web' não está em execução (status: $WEB_STATUS)."
    echo "Últimos logs do container:"
    docker compose logs --tail=80 web
    exit 1
fi

# 5. Confirmação explícita de que as migrações foram aplicadas
echo "Confirmando estado das migrações do banco de dados..."
docker compose exec -T web flask db current

# 6. Checagem fim-a-fim: a aplicação responde de dentro do próprio container
echo "Verificando se a aplicação está respondendo..."
HTTP_STATUS="$(docker compose exec -T web curl -fsS -o /dev/null -w '%{http_code}' http://localhost:5000/auth/login || true)"
if [ "$HTTP_STATUS" != "200" ]; then
    echo "ERRO: a aplicação não respondeu como esperado (HTTP $HTTP_STATUS)."
    docker compose logs --tail=80 web
    exit 1
fi

# 7. Limpar imagens Docker antigas/não utilizadas (libera espaço em disco)
echo "Limpando imagens Docker não utilizadas..."
docker image prune -f

echo "--- DEPLOY CONCLUÍDO COM SUCESSO ---"
