# Use uma imagem base com Python
FROM python:3.11-slim

# Instalar dependências do sistema necessárias
RUN apt-get update && \
    apt-get install -y \
    tesseract-ocr \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Setar o diretório de trabalho
WORKDIR /app

# Copiar o arquivo de requisitos e instalar as dependências do Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código para o container
COPY . /app/

# Definir o comando padrão para rodar a aplicação
CMD ["gunicorn", "main:app"]
