# Guia de Deploy: Render + Supabase (PostgreSQL)

Este guia descreve como configurar sua aplicação para usar o **Supabase** como banco de dados PostgreSQL e como realizar o deploy no **Render**.

## 1. Configurando o Banco de Dados no Supabase

1.  Acesse [supabase.com](https://supabase.com/) e crie uma conta (ou faça login).
2.  Clique em **New Project** e selecione sua organização.
3.  Preencha os detalhes do projeto:
    *   **Name:** Escolha um nome para seu projeto (ex: `app-personal-db`).
    *   **Database Password:** Clique em "Generate a password" e **COPIE E GUARDE ESTA SENHA**. Você precisará dela depois.
    *   **Region:** Escolha uma região próxima aos servidores do Render (ex: `South America (São Paulo)` se seu público for no Brasil, ou `US East (N. Virginia)`).
4.  Clique em **Create New Project** e aguarde alguns minutos até o banco ser provisionado.

### Obtendo a String de Conexão (DATABASE_URL)

1.  No painel do Supabase, vá em **Project Settings** (ícone de engrenagem no menu lateral).
2.  Selecione **Database**.
3.  Role até a seção **Connection string**.
4.  Selecione a aba **URI**.
5.  A URL será algo como: 
    `postgresql://postgres:[YOUR-PASSWORD]@db.xxxx.supabase.co:5432/postgres`
6.  **Substitua** `[YOUR-PASSWORD]` pela senha que você salvou no passo anterior.
7.  **IMPORTANTE:** Certifique-se de que a senha não contenha caracteres especiais que precisem de encoding (ou use encoding se necessário).

---

## 2. Configurando a Aplicação no Render

1.  Acesse [dashboard.render.com](https://dashboard.render.com/).
2.  Clique em **New +** e selecione **Web Service**.
3.  Conecte seu repositório do GitHub.
4.  Configure os detalhes do serviço:
    *   **Name:** `app-personal`
    *   **Environment:** `Python 3`
    *   **Build Command:** `./render-build.sh`
    *   **Start Command:** `gunicorn run:app`
5.  Clique em **Advanced** e vá na seção **Environment Variables**.
6.  Adicione as seguintes variáveis:
    *   `SECRET_KEY`: Gerada por você (ex: `minha-chave-super-secreta-123`).
    *   `DATABASE_URL`: Cole a URI que você obteve no Supabase (já com a senha).
    *   `FLASK_APP`: `run.py`
    *   `FLASK_ENV`: `production` (ou `development` se desejar modo debug).

---

## 3. Verificando o Deploy

1.  Clique em **Create Web Service**.
2.  O Render iniciará o processo de build.
3.  O arquivo `render-build.sh` executará automaticamente o comando `flask db upgrade`, que criará todas as tabelas necessárias no seu banco de dados do Supabase.
4.  Acompanhe os logs. Se o build terminar com "Your service is live!", sua aplicação está pronta!

> [!TIP]
> **Dica de Segurança:** Nunca versione seu arquivo `.env` com senhas reais. Sempre use o `.env.example` como referência e preencha as variáveis reais diretamente no painel do Render.

> [!IMPORTANT]
> Se você encontrar erros de conexão, verifique se o Supabase não está bloqueando conexões externas ou se a senha na `DATABASE_URL` está correta.
