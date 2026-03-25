# Guia de Deploy no Render - AppPessoal

Siga estes passos para colocar sua aplicação online:

## 1. Prepare seu Repositório Git
Certifique-se de que todos os arquivos (incluindo `render-build.sh`, `Procfile` e as atualizações no `config.py`) foram commitados e enviados para o seu GitHub.

```bash
git add .
git commit -m "Configurações para deploy no Render"
git push origin master
```

## 2. No Painel do Render (dashboard.render.com)
1. Clique em **New +** e selecione **Web Service**.
2. Conecte seu repositório do GitHub.
3. Configure os detalhes do serviço:
   - **Name:** `app-personal` (ou o nome que preferir)
   - **Environment:** `Python 3`
   - **Build Command:** `./render-build.sh`
   - **Start Command:** `gunicorn run:app` (ou deixe o Render ler do `Procfile`)

## 3. Variáveis de Ambiente (Environment Variables)
No menu **Environment**, adicione as seguintes chaves:
- `SECRET_KEY`: Uma string aleatória e segura.
- `DATABASE_URL`: Se você criou um banco de dados PostgreSQL no Render, ele preencherá isso automaticamente se você conectar os serviços. Caso contrário, cole a URL interna do banco.
- `PYTHON_VERSION`: `3.12.0` (opcional, dependendo do ambiente).

## 4. Persistência (Importante para SQLite)
> [!WARNING]
> Se você optar por NÃO usar PostgreSQL e manter o SQLite (`app.db`), você deve adicionar um **Disk** (Persistent Storage) ao seu serviço no Render montado em `/home/anderson/workspace/antigravity/app_personal/` (ou ajuste conforme o path raiz do app no Render) para não perder os dados. **O plano gratuito não suporta Disks.**

## 5. Build e Deploy
Clique em **Create Web Service**. O Render executará o `render-build.sh`, instalará as dependências, rodará as migrações e iniciará o servidor.
