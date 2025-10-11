# Dockerfile para Selenium + Chrome Headless
# Usado para scraping de BDNS

FROM selenium/standalone-chrome:latest

# Metadata
LABEL maintainer="FADE"
LABEL description="Selenium con Chrome headless para scraping BDNS"

# Variables de entorno para optimizar Chrome en servidor
ENV SE_NODE_MAX_SESSIONS=5
ENV SE_NODE_SESSION_TIMEOUT=300
ENV SE_VNC_NO_PASSWORD=1

# Optimizaciones de Chrome para entorno headless
ENV CHROME_FLAGS="--disable-dev-shm-usage --no-sandbox --disable-gpu --disable-software-rasterizer --disable-extensions"

# Directorio de trabajo
WORKDIR /opt/selenium

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:4444/wd/hub/status || exit 1

# Exponer puerto estándar de Selenium
EXPOSE 4444

# Comando por defecto (ya viene del imagen base)
# CMD ["/opt/bin/entry_point.sh"]
