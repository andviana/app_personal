# Stage 1: Compilação otimizada do CSS (Tailwind CSS) via Node.js
FROM node:20-slim AS css-builder
WORKDIR /app
COPY package*.json ./
COPY tailwind.config.js postcss.config.js ./
COPY app/static ./app/static
COPY app/templates ./app/templates
RUN npm ci && npm run build:css

# Stage 2: Ambiente de Produção Python leve e seguro
FROM python:3.11-slim

# Evita arquivos .pyc e força saída direta para stdout/stderr
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=production

WORKDIR /app

# Instalação das dependências do SO necessárias para compilar bibliotecas C (ex: libpq-dev para Postgres)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalação das dependências da aplicação em Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Cópia de todo o código-fonte da aplicação
COPY . .

# Copia o CSS compilado e minificado gerado no estágio 1
COPY --from=css-builder /app/app/static/css/output.css ./app/static/css/output.css

# Exposição da porta da aplicação
EXPOSE 5000

# Servidor de Produção WSGI (Gunicorn)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "run:app"]
