# Usar o Python oficial
FROM python:3.10-slim

# Instalar o FFmpeg (Essencial para qualidade máxima e MP3) no sistema do servidor
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Configurar a pasta de trabalho
WORKDIR /app

# Copiar os requerimentos e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código (o app.py)
COPY . .

# Comando para ligar o servidor usando o Gunicorn (ideal para a web)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
