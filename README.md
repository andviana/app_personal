# DayLog - AppPessoal

Sistema de gerenciamento pessoal para tarefas, listas, pessoas, perfumes e snippets. Desenvolvido com Flask e um design moderno inspirado no Discord.

## 🚀 Funcionalidades

- **Dashboard**: Visão geral do sistema.
- **Tarefas**: Gerenciamento de afazeres com grupos e status.
- **Listas**: Listas de compras ou desejos com importação automática (Scraper).
- **Snippets**: Armazenamento de trechos de código ou texto.
- **Perfumes**: Catálogo pessoal de fragrâncias.
- **Pessoas**: Cadastro de contatos, documentos e arquivos.
- **Segurança**: Autenticação com Flask-Login e proteção CSRF com Flask-WTF.

---

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

3. **Configure as variáveis de ambiente**:
   Crie um arquivo `.env` baseado no arquivo `.env.example`.

4. **Inicie o banco de dados**:
   ```bash
   flask db upgrade
   ```

5. **Execute a aplicação**:
   ```bash
   python run.py
   ```

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
   - `SECRET_KEY`: Uma chave segura e aleatória.
   - `DATABASE_URL`: A URI obtida no Supabase.
   - `FLASK_APP`: `run.py`
   - `FLASK_ENV`: `production`

### 3. Considerações Importantes

- O arquivo `render-build.sh` executa automaticamente as migrações (`flask db upgrade`).
- Se preferir usar SQLite (não recomendado para o plano gratuito do Render), você precisará configurar um **Persistent Disk**.

---

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python, Flask, SQLAlchemy.
- **Frontend**: Jinja2, Tailwind CSS, Phosphor Icons, SweetAlert2.
- **Database**: SQLite (local) / PostgreSQL (produção).
- **Scraper**: BeautifulSoup4, Requests.
- **Segurança**: Flask-Login, Flask-WTF (CSRF).
