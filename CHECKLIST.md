# ✅ CHECKLIST DE MIGRACIÓN

## 📦 FASE 1: COPIAR ARCHIVOS DEL MONOLITO

### Templates (3 archivos)
- [ ] financiacion_dashboard.html
- [ ] financiacion_gestionar.html  
- [ ] financiacion_adecuacion.html

### Utils (5 archivos)
- [ ] financing_dashboard.py
- [ ] convocatoria_extractor_updated.py
- [ ] bdns_scraper.py
- [ ] compatibility_analyzer.py
- [ ] pdf_processor.py

### Static (carpeta completa)
- [ ] static/css/
- [ ] static/js/
- [ ] static/images/

### Data
- [ ] programas_financiacion.json

---

## 🔧 FASE 2: CONFIGURACIÓN

- [ ] Crear archivo .env (copia de .env.example)
- [ ] Añadir GEMINI_API_KEY al .env
- [ ] Añadir ADMIN_PASSWORD al .env
- [ ] Verificar DATABASE_PATH en .env

---

## ⚙️ FASE 3: ADAPTACIONES DE CÓDIGO

- [ ] Adaptar bdns_scraper.py (webdriver para Docker)
- [ ] Adaptar convocatoria_extractor_updated.py (API key desde env)
- [ ] (Opcional) Adaptar compatibility_analyzer.py si usa API key

---

## 🧪 FASE 4: PRUEBAS EN LOCAL

### Setup
- [ ] Crear entorno virtual (python -m venv venv)
- [ ] Activar entorno virtual
- [ ] Instalar dependencias (pip install -r requirements.txt)
- [ ] Ejecutar app (python app.py)

### Tests Funcionales
- [ ] Dashboard público carga (http://localhost:5000)
- [ ] Login admin funciona
- [ ] Lista de programas se muestra
- [ ] Filtros funcionan
- [ ] Extracción con Gemini funciona
- [ ] Análisis de compatibilidad funciona
- [ ] No hay errores en consola

---

## 🐳 FASE 5: DOCKER (OPCIONAL - ANTES DEL VPS)

- [ ] Docker Desktop instalado
- [ ] docker-compose build (construir imágenes)
- [ ] docker-compose up -d (iniciar servicios)
- [ ] Verificar en http://localhost:8000
- [ ] Todos los tests funcionales pasan

---

## 🚀 FASE 6: PREPARAR PARA VPS

- [ ] Todo funciona en local
- [ ] Código subido a Git (opcional)
- [ ] Documentar cambios realizados
- [ ] Leer MIGRACION.md

---

## 🌐 FASE 7: DEPLOY EN VPS

- [ ] Contratar VPS (Hetzner CX21)
- [ ] Configurar DNS (programas.fade.es)
- [ ] Ejecutar setup-vps.sh
- [ ] Subir código al VPS
- [ ] Configurar .env en VPS
- [ ] Ejecutar deploy.sh
- [ ] Obtener certificado SSL
- [ ] Verificar funcionalidad en producción

---

## 🔍 FASE 8: VERIFICACIÓN FINAL

- [ ] HTTPS funciona
- [ ] Dashboard público accesible
- [ ] Admin funciona
- [ ] Scraping BDNS funciona
- [ ] Gemini extrae información
- [ ] Análisis de compatibilidad funciona
- [ ] Backups configurados
- [ ] Monitorización activa

---

## 🎉 ¡COMPLETADO!

Si todos los checks están marcados, ¡enhorabuena! 
Has migrado exitosamente la herramienta a producción.

**Fecha de inicio:** __________
**Fecha de finalización:** __________
**Tiempo total:** __________

---

## 📝 NOTAS Y PROBLEMAS ENCONTRADOS

(Usa este espacio para documentar cualquier problema o solución)

```
Problema 1:


Solución 1:


Problema 2:


Solución 2:


```

---

## 🔗 ENLACES ÚTILES

- Proyecto local: file:///C:/Users/aleja/fade-financiacion-lite
- Proyecto monolito: file:///C:/Users/aleja/herramienta_deducciones  
- Documentación: INSTRUCCIONES.md
- GitHub: (cuando lo subas)
- VPS: (cuando lo contrates)
- URL producción: https://programas.fade.es

---

**Última actualización:** $(Get-Date)
