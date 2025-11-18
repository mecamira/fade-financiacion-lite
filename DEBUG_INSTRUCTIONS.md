# Instrucciones de Debugging

## Problema 1: Error al editar convocatorias existentes

### Verificar en el navegador (F12)

1. Abre la página de edición de convocatorias
2. Presiona **F12** para abrir las herramientas de desarrollador
3. Ve a la pestaña **Console**
4. Intenta editar una convocatoria
5. Busca mensajes que comiencen con:
   - `[DEBUG]` - Información de depuración
   - `[ERROR]` - Errores capturados
6. Copia todo el output de la consola y compártelo

### Logs esperados

Si todo funciona correctamente, deberías ver:
```
[DEBUG] Intentando cargar programa con ID: xxx
[DEBUG] Response status: 200
[DEBUG] Datos recibidos: {success: true, programa: {...}}
[DEBUG] Programa cargado exitosamente: {...}
[DEBUG] Iniciando carga de datos en formulario: {...}
[DEBUG] Datos cargados exitosamente en el formulario
```

Si hay un error, verás mensajes de `[ERROR]` con detalles específicos.

## Problema 2: El scraping de BDNS no extrae los nuevos campos

### Verificar que el código está actualizado en el servidor

En el servidor, ejecuta:

```bash
cd /root/fade-financiacion-lite
docker exec fade-financiacion-app python3 verify_scraper_version.py
```

Deberías ver:
```
✓ _extraer_nombre_oficial EXISTE
✓ _extraer_extracto_info EXISTE
✓ _extraer_bases_reguladoras EXISTE
✓ Extrae 'nombre_oficial'
✓ Extrae 'extracto_info'
✓ Extrae 'fecha_publicacion'
```

Si ves ✗, significa que el código no está actualizado.

### Si el código está desactualizado

1. Asegúrate de hacer pull de la última versión:
```bash
cd /root/fade-financiacion-lite
git pull origin main
```

2. Forzar reconstrucción completa (sin caché):
```bash
docker compose down
docker compose build --no-cache flask-app
docker compose up -d
```

3. Verificar nuevamente:
```bash
docker exec fade-financiacion-app python3 verify_scraper_version.py
```

### Ver logs del scraping en tiempo real

Para ver qué está extrayendo el scraper cuando procesas una convocatoria:

```bash
docker logs -f fade-financiacion-app
```

Luego, en la web, intenta añadir una convocatoria desde BDNS.

Deberías ver en los logs:
```
🔍 Buscando título oficial de la convocatoria...
   ✓ Título oficial encontrado: ...
🔍 Buscando extractos de la convocatoria...
   ✓ Tabla de extractos encontrada!
   ✓ Fecha de publicación: 2025-XX-XX
   ✓ URL extracto: https://...
```

### Verificar que la convocatoria guardada tiene los campos nuevos

```bash
docker exec fade-financiacion-app python3 -c "
import json
with open('/app/data/programas_financiacion.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    # Mostrar la última convocatoria agregada
    if data['programas']:
        ultimo = data['programas'][-1]
        print('Nombre oficial:', ultimo.get('nombre_oficial', 'NO EXISTE'))
        print('Extracto:', ultimo.get('enlaces', {}).get('extracto', 'NO EXISTE'))
        print('Fondos europeos:', ultimo.get('fondos_europeos', 'NO EXISTE'))
        print('Tipo ayuda (array):', ultimo.get('tipo_ayuda', 'NO EXISTE'))
"
```

## Problema 3: Limpiar caché de Python

Si los cambios no se aplican, puede ser por archivos .pyc en caché:

```bash
docker exec fade-financiacion-app find /app -name "*.pyc" -delete
docker exec fade-financiacion-app find /app -name "__pycache__" -type d -exec rm -rf {} +
docker compose restart flask-app
```

## Contacto

Si después de seguir estos pasos el problema persiste, comparte:
1. El output completo de `verify_scraper_version.py`
2. Los logs de la consola del navegador (F12)
3. Los logs del contenedor cuando intentas añadir una convocatoria
