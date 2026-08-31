# DayLog - AppPessoal

Sistema de gerenciamento pessoal para tarefas, listas, pessoas, perfumes e snippets. Desenvolvido com Flask, seguindo uma arquitetura em camadas (Blueprints → Services → Repositories → Models) e uma interface minimalista, responsiva e mobile-first construída com Tailwind CSS.

## 🚀 Funcionalidades

- **Dashboard**: Visão geral do sistema.
- **Tarefas**: Gerenciamento de afazeres com grupos e status.
- **Listas**: Listas de compras ou desejos com importação automática (Scraper).
- **Snippets**: Armazenamento de trechos de código ou texto.
- **Perfumes**: Catálogo pessoal de fragrâncias.
- **Pessoas**: Cadastro de contatos, documentos e arquivos.
- **Segurança**: Autenticação com Flask-Login e proteção CSRF com Flask-WTF. Login opcional com Google (OAuth 2.0).

---

## 🛠️ Requisitos

- **Python 3.8+**
- **Node.js 18+ & npm** (para processamento do CSS)

### Instale as dependências do sistema

Para compilar `psycopg2-binary` e demais dependências nativas, instale o `libpq-dev` (que fornece o `pg_config`) e os compiladores necessários:

```bash
sudo apt update && sudo apt install -y libpq-dev build-essential python3-dev
```

## 💻 Instalação Local

1. **Clone o repositório**:
   ```bash
   git clone <url-do-repositorio>
   cd app_personal
   ```

2. **Crie um ambiente virtual e instale as dependências**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Instale e compile o frontend (Tailwind CSS)**:
   ```bash
   npm install
   npm run build:css
   ```

4. **Configure as variáveis de ambiente**:
   Crie um arquivo `.env` baseado no arquivo `.env.example`.

5. **Inicie o banco de dados**:
   ```bash
   flask db upgrade
   ```

6. **Execute a aplicação**:
   ```bash
   python run.py
   ```

---

## 🏗️ Arquitetura

O back-end segue uma arquitetura em camadas para manter regras de negócio, acesso a dados e rotas HTTP desacoplados:

- **Blueprints (`app/blueprints/`)**: rotas Flask — validam entrada, chamam a camada de serviço e traduzem o resultado em respostas HTTP (redirect, JSON, template).
- **Services (`app/services/`)**: regras de negócio, autorização (multi-tenant, compartilhamento, arquivamento) e orquestração entre repositórios.
- **Repositories (`app/repositories/`)**: acesso a dados via SQLAlchemy, através de um `BaseRepository` genérico reutilizado por todos os módulos.
- **Models (`app/models/`)**: entidades SQLAlchemy.

Erros de autorização são sinalizados pelos services com `PermissionError` e centralizados nas rotas por decorators reutilizáveis (`app/decorators.py`); registros não encontrados na camada de repositório levantam `NotFoundError` (`app/exceptions.py`), traduzida para HTTP 404 por um error handler global — mantendo a camada de dados independente do Flask. Requisições a URLs externas (scraper de links) passam por uma verificação de segurança (`app/services/url_safety.py`) que bloqueia acesso a endereços privados/internos (proteção contra SSRF).

---

## 🎨 Desenvolvimento de Frontend

A aplicação utiliza **Tailwind CSS** com um processo de build local.

- **Compilação em Tempo Real (Watch)**: Use durante o desenvolvimento para que o CSS seja atualizado automaticamente ao salvar arquivos HTML.
  ```bash
  npm run watch:css
  ```
- **Build de Produção**: Gera um arquivo CSS minificado e otimizado.
  ```bash
  npm run build:css
  ```

Os arquivos fonte ficam em `app/static/css/input.css` e o resultado compilado em `app/static/css/output.css`.

---

## 🌐 Deploy no Render

Siga estes passos para colocar sua aplicação online usando o **Render** e o **Supabase** (PostgreSQL).

### 1. Banco de Dados (Supabase)

1. Acesse [supabase.com](https://supabase.com/) e crie um projeto.
2. Em **Project Settings > Database**, obtenha a **Connection String (URI)**.
3. Substitua `[YOUR-PASSWORD]` pela senha do banco que você definiu.

### 2. Configurações no Render

1. No [Render Dashboard](https://dashboard.render.com/), clique em **New + > Web Service**.
2. Conecte seu repositório do GitHub.
3. Configure os detalhes:
   - **Name:** `app-personal`
   - **Environment:** `Python 3`
   - **Build Command:** `./render-build.sh`
   - **Start Command:** `gunicorn run:app`
4. Em **Environment Variables**, adicione:
   - `ENVIRONMENT`: `homologation` (ou `production` em servidor próprio)
   - `SECRET_KEY`: Uma chave segura e aleatória.
   - `DATABASE_URL`: A URI obtida no Supabase (Homologação) ou Docker Postgres (Produção).
   - `FLASK_APP`: `run.py`

---

## ⚙️ Cenários de Ambiente (`ENVIRONMENT`)

A aplicação suporta 3 cenários configuráveis via variável `ENVIRONMENT` em um único arquivo `.env`:

| Cenário | Valor de `ENVIRONMENT` | Banco de Dados | Modo `DEBUG` |
| :--- | :--- | :--- | :--- |
| **Local** | `local` | SQLite nativo (`app.db`) | Configurável (`True` por padrão) |
| **Homologação** | `homologation` | PostgreSQL do Supabase (Render) | Estritamente `False` |
| **Produção** | `production` | PostgreSQL via Docker (Hostinger) | Estritamente `False` |

---

### 3. Considerações Importantes

- O arquivo `render-build.sh` executa automaticamente a instalação das dependências (Python e npm), o build do CSS e as migrações do banco de dados (`flask db upgrade`).
- O Render detecta automaticamente o arquivo `package.json` e configura o ambiente Node.js necessário.
- Se preferir usar SQLite (não recomendado para o plano gratuito do Render), você precisará configurar um **Persistent Disk**.

---

## 🔐 Login com Google (OAuth)

A tela de login tem um botão opcional "Continuar com Google". Ele só aparece
quando `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` estão configurados — sem
isso, o app funciona normalmente só com usuário/senha.

**Como funciona:** o Google apenas confirma a identidade (e-mail) de quem
está logando — ele **não cria contas**. No callback, o DayLog procura um
usuário já cadastrado cujo campo `email` (em *Configurações > Perfil*) bata
com o e-mail confirmado pelo Google. Se encontrar, libera o acesso; se não
encontrar, mostra uma tela de "Acesso não autorizado" e não cria nada.

### 1. Criar as credenciais no Google Cloud Console

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/) e crie um projeto (ou reutilize um existente).
2. Em **APIs e Serviços > Tela de consentimento OAuth**, configure como "Externo", preencha nome do app/e-mail de suporte e publique (ou mantenha em "Testing" e adicione os e-mails autorizados como *test users* — suficiente para uso pessoal/familiar).
3. Em **APIs e Serviços > Credenciais > Criar Credenciais > ID do cliente OAuth**, escolha **Aplicativo da Web**.
4. Em **URIs de redirecionamento autorizados**, cadastre uma URI para cada ambiente que for usar:
   - Local: `http://localhost:5000/auth/google/callback`
   - Produção (Hostinger): `https://daylog.institutoviva.digital/auth/google/callback`
5. Salve e copie o **Client ID** e o **Client Secret** gerados.

### 2. Configurar as variáveis de ambiente

Adicione ao `.env` (local) ou ao `.env` do servidor (produção — é o mesmo
arquivo que o `docker-compose.yml` já carrega via `env_file`):

```bash
GOOGLE_CLIENT_ID=xxxxxxxxxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
```

Depois de editar o `.env` no VPS, suba o container novamente para aplicar:

```bash
docker compose up -d --build web
```

### 3. Rodar a migração e cadastrar o e-mail dos usuários

O login com Google casa pelo e-mail, então cada usuário precisa ter um
e-mail salvo (*Configurações > Perfil*). Depois de atualizar o código no
servidor, rode a migração que adiciona a coluna `email`:

```bash
docker compose exec web flask db upgrade
```

### 4. Especificidades do seu ambiente (Hostinger VPS + Docker + Traefik)

O `docker-compose.yml` já expõe o serviço `web` para a internet via
**Traefik**, que termina o HTTPS com Let's Encrypt no domínio
`daylog.institutoviva.digital` — é exatamente esse domínio HTTPS que deve
ir na URI de redirecionamento do passo 1 (o Google **recusa** redirect URIs
HTTP em produção; só aceita HTTP para `localhost`). Como o Traefik já
resolve o certificado automaticamente, não é necessário nenhum ajuste
adicional de TLS para o OAuth funcionar — só as credenciais no `.env` e o
redirect URI correto.

---

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python, Flask, SQLAlchemy, Flask-Migrate (Alembic).
- **Frontend**: Jinja2, Tailwind CSS, Phosphor Icons, SweetAlert2.
- **Database**: SQLite (local) / PostgreSQL (homologação/produção via `psycopg2`).
- **Scraper**: BeautifulSoup4, Requests.
- **Segurança**: Flask-Login, Flask-WTF (CSRF), Authlib (login OAuth com Google), sanitização de HTML com Bleach, proteção contra SSRF no scraper.
- **Outros**: Markdown + Pygments (highlight de snippets), ReportLab (exportação de PDF), Flask-Compress (compressão de respostas).

