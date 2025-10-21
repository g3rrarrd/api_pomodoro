FROM python:3.13-slim

# Evita prompts interactivos al instalar
ENV DEBIAN_FRONTEND=noninteractive

# Crea directorio de trabajo
WORKDIR /app

# Copia requirements e instala dependencias del sistema necesarias para pyodbc
COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y curl gnupg apt-transport-https unixodbc-dev && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia el código de tu aplicación
COPY . .

# Expone el puerto donde correrá FastAPI
EXPOSE 8000

# Comando para iniciar el servidor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
