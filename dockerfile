# Imagem base slim (leve e segura)
FROM python:3.12-slim

# Evita arquivos .pyc e melhora logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Diretório de trabalho
WORKDIR /app

# Instala dependências do sistema (para MySQL/MariaDB e build)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb-dev-compat build-essential pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements.txt e instala pacotes Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Remove pacotes de build para reduzir tamanho da imagem
RUN apt-get purge -y --auto-remove build-essential pkg-config

# Copia o projeto inteiro
COPY . .

# Copia o start.sh (arquivo separado para evitar erros de sintaxe)
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expõe porta (Railway usa $PORT, mas 8000 como fallback)
EXPOSE 8000

# Comando final
CMD ["/app/start.sh"]