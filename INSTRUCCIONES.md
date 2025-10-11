# 📋 INSTRUCCIONES PASO A PASO

## 🎯 TU MISIÓN AHORA

Completar el proyecto copiando archivos del monolito y probarlo en local.

---

## PASO 1: Copiar Templates (3 archivos)

### Archivo 1: financiacion_dashboard.html
```
ORIGEN:  C:\Users\aleja\herramienta_deducciones\templates\financiacion_dashboard.html
DESTINO: C:\Users\aleja\fade-financiacion-lite\templates\financiacion_dashboard.html
```

### Archivo 2: financiacion_gestionar.html
```
ORIGEN:  C:\Users\aleja\herramienta_deducciones\templates\financiacion_gestionar.html
DESTINO: C:\Users\aleja\fade-financiacion-lite\templates\financiacion_gestionar.html
```

### Archivo 3: financiacion_adecuacion.html
```
ORIGEN:  C:\Users\aleja\herramienta_deducciones\templates\financiacion_adecuacion.html
DESTINO: C:\Users\aleja\fade-financiacion-lite\templates\financiacion_adecuacion.html
```

---

## PASO 2: Copiar Utils (5 archivos Python)

### Archivo 1: financing_dashboard.py
```
ORIGEN:  C:\Users\aleja\herramienta_deducciones\utils\financing_dashboard.py
DESTINO: C:\Users\aleja\fade-financiacion-lite\utils\financing_dashboard.py
```

### Archivo 2: convocatoria_extractor_updated.py
```
ORIGEN:  C:\Users\aleja\herramienta_deducciones\utils\convocatoria_extractor_updated.py
DESTINO: C:\Users\aleja\fade-financiacion-lite\utils\convocatoria_extractor_updated.py
```
⚠️ **IMPORTANTE**: Este archivo necesita adaptación (ver PASO 6)

### Archivo 3: bdns_scraper.py
```
ORIGEN:  C:\Users\aleja\herramienta_deducciones\utils\bdns_scraper.py
DESTINO: C:\Users\aleja\fade-financiacion-lite\utils\bdns_scraper.py
```
⚠️ **IMPORTANTE**: Este archivo necesita adaptación (ver PASO 6)

### Archivo 4: compatibility_analyzer.py
```
ORIGEN:  C:\Users\aleja\herramienta_deducciones\utils\compatibility_analyzer.py
DESTINO: C:\Users\aleja\fade-financiacion-lite\utils\compatibility_analyzer.py
```

### Archivo 5: pdf_processor.py
```
ORIGEN:  C:\Users\aleja\herramienta_deducciones\utils\pdf_processor.py
DESTINO: C:\Users\aleja\fade-financiacion-lite\utils\pdf_processor.py
```

---

## PASO 3: Copiar Static (carpeta completa)

```
ORIGEN:  C:\Users\aleja\herramienta_deducciones\static\
DESTINO: C:\Users\aleja\fade-financiacion-lite\static\

Esto copiará:
- static/css/main.css
- static/css/dashboard.css  
- static/css/[otros archivos CSS]
- static/js/main.js
- static/js/dashboard.js
- static/js/gestionar.js
- static/js/compatibilidad.js
- static/js/[otros archivos JS]
- static/images/logo-fade.png
- static/images/[otras imágenes]
```

**Opción fácil en Windows**:
1. Abre ambas carpetas en el explorador
2. Selecciona todo el contenido de `C:\Users\aleja\herramienta_deducciones\static\`
3. Copia (Ctrl+C)
4. Pega en `C:\Users\aleja\fade-financiacion-lite\static\` (Ctrl+V)
5. Sobrescribe si pregunta

---

## PASO 4: Copiar Data

```
ORIGEN:  C:\Users\aleja\herramienta_deducciones\data\programas_financiacion.json
DESTINO: C:\Users\aleja\fade-financiacion-lite\data\programas_financiacion.json
```

---

## PASO 5: Crear archivo .env

1. Abre `C:\Users\aleja\fade-financiacion-lite\.env.example`
2. Copia todo el contenido
3. Crea un nuevo archivo llamado `.env` en la misma carpeta
4. Pega el contenido
5. Modifica estos valores:

```env
FLASK_ENV=development

SECRET_KEY=clave-temporal-desarrollo-12345

GEMINI_API_KEY=PEGA_AQUI_TU_API_KEY_REAL

ADMIN_PASSWORD=admin123

DATABASE_PATH=C:\Users\aleja\fade-financiacion-lite\data\programas_financiacion.json

SELENIUM_REMOTE_URL=

LOG_DIR=C:\Users\aleja\fade-financiacion-lite\logs
```

---

## PASO 6: Adaptar Archivos Python (CRÍTICO)

### A) Adaptar bdns_scraper.py

Abre: `C:\Users\aleja\fade-financiacion-lite\utils\bdns_scraper.py`

Busca donde se crea el driver de Chrome (probablemente línea 30-50), algo como:
```python
driver = webdriver.Chrome(options=chrome_options)
```

Reemplázalo por:
```python
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
    # Modo local (desarrollo) - necesita Chrome instalado
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
```

### B) Adaptar convocatoria_extractor_updated.py

Abre: `C:\Users\aleja\fade-financiacion-lite\utils\convocatoria_extractor_updated.py`

Busca donde se carga la API key (probablemente al inicio del archivo o en __init__):
```python
# ANTES - algo como:
with open('config/gemini_config.json') as f:
    config = json.load(f)
    api_key = config['api_key']
```

Reemplázalo por:
```python
# DESPUÉS:
import os

# En la función __init__ o donde se use la API key:
api_key = os.environ.get('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY no está configurada en variables de entorno")
```

### C) Verificar compatibility_analyzer.py

Abre: `C:\Users\aleja\fade-financiacion-lite\utils\compatibility_analyzer.py`

Si también usa la API key de Gemini, hacer el mismo cambio que en el punto B.

---

## PASO 7: Probar en Local (SIN Docker primero)

### 1. Abrir PowerShell en la carpeta del proyecto
```powershell
cd C:\Users\aleja\fade-financiacion-lite
```

### 2. Crear entorno virtual
```powershell
python -m venv venv
```

### 3. Activar entorno virtual
```powershell
venv\Scripts\activate
```
Deberías ver `(venv)` al inicio de la línea.

### 4. Instalar dependencias
```powershell
pip install -r requirements.txt
```
Esto tomará 2-3 minutos.

### 5. Ejecutar aplicación
```powershell
python app.py
```

### 6. Si ves esto, ¡FUNCIONA! 🎉
```
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
```

### 7. Abrir navegador
Abre tu navegador en: **http://localhost:5000**

---

## PASO 8: Verificar Funcionalidad

### ✅ Test 1: Dashboard Público
- URL: http://localhost:5000/
- Deberías ver el dashboard con programas
- Prueba los filtros
- Busca un programa
- **¿Funciona?** ✅ / ❌

### ✅ Test 2: Login Admin
- URL: http://localhost:5000/admin/login
- Introduce contraseña: `admin123`
- Deberías entrar al panel de gestión
- **¿Funciona?** ✅ / ❌

### ✅ Test 3: Extracción con Gemini
- En panel admin, pega texto de una convocatoria
- Click "Extraer información"
- Gemini debería extraer los datos
- **¿Funciona?** ✅ / ❌

### ✅ Test 4: Análisis de Compatibilidad
- URL: http://localhost:5000/financiacion/analizar-compatibilidad
- Completa datos de empresa
- Selecciona una convocatoria
- Click "Analizar"
- **¿Funciona?** ✅ / ❌

### ⚠️ Test 5: Scraping BDNS (Opcional por ahora)
- Este test requiere Chrome instalado
- Si falla, no te preocupes, lo arreglaremos después
- **¿Funciona?** ✅ / ❌ / ⏭️ (saltar)

---

## PASO 9: Si hay errores

### Error común 1: "ModuleNotFoundError: No module named 'X'"
**Solución**: 
```powershell
pip install nombre-del-modulo
```

### Error común 2: "GEMINI_API_KEY no está configurada"
**Solución**: Verifica que el archivo `.env` existe y tiene tu API key correcta.

### Error común 3: "FileNotFoundError: programas_financiacion.json"
**Solución**: Verifica que copiaste el archivo JSON al directorio `data/`

### Error común 4: Templates no se encuentran
**Solución**: Verifica que copiaste los 3 templates HTML al directorio `templates/`

### Error común 5: CSS/JS no cargan
**Solución**: Verifica que copiaste toda la carpeta `static/`

---

## PASO 10: Cuando TODO funcione en local

### ¡EXCELENTE! Ahora puedes:

1. **Hacer commit en Git** (si usas control de versiones)
```powershell
git add .
git commit -m "Versión lite funcional - lista para producción"
git push origin main
```

2. **Preparar para VPS**
   - Seguir documento **MIGRACION.md** para subir al servidor

3. **Documentar cualquier cambio** que hayas hecho

---

## 🆘 SI TE ATASCAS

### Antes de pedir ayuda, verifica:
- [ ] Todos los archivos copiados correctamente
- [ ] Archivo `.env` creado con API key real
- [ ] Entorno virtual activado (`(venv)` visible)
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Sin errores de sintaxis en archivos adaptados

### Información útil para debug:
1. **Logs completos** del error en terminal
2. **Qué estabas haciendo** cuando falló
3. **Qué archivos modificaste** (si alguno)
4. **Captura de pantalla** del error

---

## ✅ CHECKLIST FINAL

Antes de continuar al VPS, verifica que TODO esto funciona:

- [ ] App inicia sin errores (`python app.py`)
- [ ] Dashboard público carga
- [ ] Login admin funciona
- [ ] Lista de programas se muestra
- [ ] Filtros funcionan
- [ ] Extracción Gemini funciona
- [ ] Análisis de compatibilidad funciona
- [ ] No hay errores en la consola/logs
- [ ] CSS y JavaScript cargan correctamente
- [ ] Imágenes se ven bien

---

## 🎯 PRÓXIMO PASO

Cuando TODO lo anterior funcione → **Proceder con migración a VPS**

Documento: **MIGRACION.md** (en la misma carpeta)

---

**RECUERDA**: 
- Ve paso a paso
- No te saltes pasos
- Documenta errores
- Pide ayuda si la necesitas

**¡Tú puedes! 💪**
