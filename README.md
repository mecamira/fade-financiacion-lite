# 🚀 FADE Financiación - Versión Producción Lite

## 📋 PRÓXIMOS PASOS PARA COMPLETAR EL PROYECTO

### ✅ YA CREADO
- ✅ Estructura completa de directorios
- ✅ app.py (Flask app lite)
- ✅ config.py (configuración)
- ✅ requirements.txt
- ✅ Dockerfiles (Flask + Selenium)
- ✅ docker-compose.yml
- ✅ Templates básicos (login, 404, 500)
- ✅ .env.example
- ✅ .gitignore

### 📦 ARCHIVOS A COPIAR DESDE `C:\Users\aleja\herramienta_deducciones`

#### 1. Templates (copiar 3 archivos)
```bash
# Copiar estos archivos:
C:\Users\aleja\herramienta_deducciones\templates\financiacion_dashboard.html
  -> C:\Users\aleja\fade-financiacion-lite\templates\

C:\Users\aleja\herramienta_deducciones\templates\financiacion_gestionar.html
  -> C:\Users\aleja\fade-financiacion-lite\templates\

C:\Users\aleja\herramienta_deducciones\templates\financiacion_adecuacion.html
  -> C:\Users\aleja\fade-financiacion-lite\templates\
```

#### 2. Utils (copiar 5 archivos Python)
```bash
# Copiar estos archivos:
C:\Users\aleja\herramienta_deducciones\utils\financing_dashboard.py
  -> C:\Users\aleja\fade-financiacion-lite\utils\

C:\Users\aleja\herramienta_deducciones\utils\convocatoria_extractor_updated.py
  -> C:\Users\aleja\fade-financiacion-lite\utils\

C:\Users\aleja\herramienta_deducciones\utils\bdns_scraper.py
  -> C:\Users\aleja\fade-financiacion-lite\utils\

C:\Users\aleja\herramienta_deducciones\utils\compatibility_analyzer.py
  -> C:\Users\aleja\fade-financiacion-lite\utils\

C:\Users\aleja\herramienta_deducciones\utils\pdf_processor.py
  -> C:\Users\aleja\fade-financiacion-lite\utils\
```

#### 3. Static (copiar carpeta completa)
```bash
# Copiar toda la carpeta static:
C:\Users\aleja\herramienta_deducciones\static\
  -> C:\Users\aleja\fade-financiacion-lite\static\
  
# Esto incluirá:
# - static/css/*
# - static/js/*
# - static/images/*
```

#### 4. Data (copiar base de datos)
```bash
# Copiar el JSON de programas:
C:\Users\aleja\herramienta_deducciones\data\programas_financiacion.json
  -> C:\Users\aleja\fade-financiacion-lite\data\
```

---

## 🔧 ADAPTACIONES NECESARIAS

### ⚠️ CRÍTICO: Adaptar `utils/bdns_scraper.py`

**Archivo**: `C:\Users\aleja\fade-financiacion-lite\utils\bdns_scraper.py`

Buscar esta línea (aproximadamente línea 30-40):
```python
# ANTES (no funcionará en Docker):
driver = webdriver.Chrome(options=chrome_options)
```

Reemplazar por:
```python
# DESPUÉS (funciona en Docker):
import os
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

selenium_url = os.environ.get('SELENIUM_REMOTE_URL')

if selenium_url:
    # Modo Docker (producción)
    driver = webdriver.Remote(
        command_executor=selenium_url,
        desired_capabilities=DesiredCapabilities.CHROME,
        options=chrome_options
    )
else:
    # Modo local (desarrollo)
    driver = webdriver.Chrome(options=chrome_options)
```

### ⚠️ IMPORTANTE: Adaptar `utils/convocatoria_extractor_updated.py`

**Archivo**: `C:\Users\aleja\fade-financiacion-lite\utils\convocatoria_extractor_updated.py`

Buscar donde se lee la API key (probablemente línea 10-20):
```python
# ANTES:
with open('config/gemini_config.json') as f:
    config = json.load(f)
    api_key = config['api_key']
```

Reemplazar por:
```python
# DESPUÉS:
import os
api_key = os.environ.get('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY no está configurada en variables de entorno")
```

---

## 🔑 CONFIGURAR VARIABLES DE ENTORNO

### 1. Crear archivo `.env` (copia del .env.example)

```bash
# En la carpeta del proyecto, crear .env con tus valores reales:
```

**Archivo**: `C:\Users\aleja\fade-financiacion-lite\.env`

```env
# Flask
FLASK_ENV=development
SECRET_KEY=mi-clave-secreta-temporal-para-desarrollo

# Google Gemini AI (TU API KEY ACTUAL)
GEMINI_API_KEY=TU_API_KEY_AQUI

# Autenticación Admin
ADMIN_PASSWORD=admin123

# Base de datos (en desarrollo, ruta local)
DATABASE_PATH=C:\Users\aleja\fade-financiacion-lite\data\programas_financiacion.json

# Selenium (None para desarrollo local)
SELENIUM_REMOTE_URL=

# Logs (en desarrollo, ruta local)
LOG_DIR=C:\Users\aleja\fade-financiacion-lite\logs
```

---

## 🧪 PROBAR EN LOCAL (Antes de subir al VPS)

### Opción 1: Sin Docker (desarrollo rápido)

```bash
# 1. Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar aplicación
python app.py

# 4. Abrir en navegador:
http://localhost:5000
```

### Opción 2: Con Docker (más realista)

```bash
# 1. Asegúrate de tener Docker Desktop instalado y corriendo

# 2. Construir imágenes
docker-compose build

# 3. Iniciar servicios
docker-compose up -d

# 4. Ver logs
docker-compose logs -f

# 5. Abrir en navegador:
http://localhost:8000

# 6. Detener cuando termines
docker-compose down
```

---

## ✅ CHECKLIST DE VERIFICACIÓN LOCAL

Antes de subir al VPS, verifica que funciona:

- [ ] Dashboard público carga correctamente
- [ ] Login admin funciona
- [ ] Puedes ver la lista de programas
- [ ] Gemini AI extrae información de texto
- [ ] (Opcional) Selenium scraping BDNS funciona
- [ ] Análisis de compatibilidad funciona
- [ ] No hay errores en los logs

---

## 🚀 SUBIR AL VPS (Cuando esté todo probado)

Seguir los pasos de **MIGRACION.md** (documento aparte)

---

## 📁 ESTRUCTURA FINAL DEL PROYECTO

```
C:\Users\aleja\fade-financiacion-lite\
├── app.py                    ✅ Creado
├── config.py                 ✅ Creado
├── requirements.txt          ✅ Creado
├── Dockerfile                ✅ Creado
├── docker-compose.yml        ✅ Creado
├── .env                      🔴 Crear (copia de .env.example)
├── .env.example              ✅ Creado
├── .gitignore                ✅ Creado
│
├── templates/
│   ├── admin_login.html              ✅ Creado
│   ├── 404.html                      ✅ Creado
│   ├── 500.html                      ✅ Creado
│   ├── financiacion_dashboard.html   📋 Copiar
│   ├── financiacion_gestionar.html   📋 Copiar
│   └── financiacion_adecuacion.html  📋 Copiar
│
├── utils/
│   ├── __init__.py                           ✅ Creado
│   ├── financing_dashboard.py                📋 Copiar
│   ├── convocatoria_extractor_updated.py     📋 Copiar y adaptar
│   ├── bdns_scraper.py                       📋 Copiar y adaptar
│   ├── compatibility_analyzer.py             📋 Copiar
│   └── pdf_processor.py                      📋 Copiar
│
├── static/            📋 Copiar carpeta completa
│   ├── css/
│   ├── js/
│   └── images/
│
├── data/
│   └── programas_financiacion.json   📋 Copiar
│
├── docker/
│   └── selenium/
│       └── Dockerfile        ✅ Creado
│
├── nginx/             (para producción)
├── scripts/           (para producción)
├── uploads/           ✅ Creado
└── logs/              ✅ Creado
```

---

## 💡 TIPS

1. **Prueba primero sin Docker** - Es más rápido para desarrollo
2. **Lee los logs** - Si algo falla, los logs te dirán qué
3. **Usa tu API key actual** - No necesitas una nueva de momento
4. **No te preocupes por Selenium inicialmente** - Puedes añadir programas manualmente
5. **Documenta los problemas** - Anota cualquier error que encuentres

---

## 🆘 SI ALGO NO FUNCIONA

1. Verificar que copiaste todos los archivos
2. Verificar que el .env tiene tu API key correcta
3. Ver los logs: `python app.py` mostrará errores
4. Verificar imports en los archivos utils
5. Preguntar - estoy aquí para ayudar

---

**Creado**: $(Get-Date)
**Versión**: 1.0.0
