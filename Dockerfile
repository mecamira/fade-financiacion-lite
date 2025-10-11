# Dockerfile para aplicación Flask
FROM python:3.11-slim

# Metadata
LABEL maintainer="FADE"
LABEL description="FADE Herramienta de Financiación - Versión Producción"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN useradd -m -u 1000 fade && \
    mkdir -p /app /var/log/fade-financiacion && \
    chown -R fade:fade /app /var/log/fade-financiacion

# Directorio de trabajo
WORKDIR /app

# Copiar requirements e instalar dependencias
COPY --chown=fade:fade requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY --chown=fade:fade . .

# Crear directorios necesarios
RUN mkdir -p data uploads logs && \
    chown -R fade:fade data uploads logs

# Cambiar a usuario no-root
USER fade

# Exponer puerto
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Comando por defecto (se puede sobrescribir en docker-compose)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "app:app"]
