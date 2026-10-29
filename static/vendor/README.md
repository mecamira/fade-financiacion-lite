# Librerías de terceros (servidas desde nuestro propio dominio)

Nada se carga de CDNs externos: la política de contenido (CSP, en `app.py`) solo permite
recursos del propio sitio. Para actualizar una librería, descarga el archivo de la
versión nueva a su carpeta, prueba las pantallas que la usan y actualiza esta tabla.

| Carpeta | Librería | Versión | Origen | Se usa en |
|---|---|---|---|---|
| bootstrap | Bootstrap | 5.1.3 | jsdelivr (`bootstrap@5.1.3/dist`) | todo el sitio |
| jquery | jQuery | 3.7.1 | code.jquery.com | todo el sitio |
| fontawesome | Font Awesome Free | 5.15.4 | cdnjs (`css/all.min.css` + `webfonts/`) | iconos |
| inter | Inter (fuente) | 5.0.18 | jsdelivr (`@fontsource/inter`) | tipografía |
| chartjs | Chart.js | 3.7.1 | jsdelivr | pestaña Estadísticas |
| jspdf | jsPDF + AutoTable | 4.2.1 + 5.0.9 | jsdelivr | exportar a PDF (dashboard y ficha) |
| xlsx | SheetJS (xlsx) | 0.20.3 | cdn.sheetjs.com (no se actualiza en npm/cdnjs) | exportar a Excel |
| tagify | Tagify | 4.39.0 | jsdelivr (`@yaireo/tagify`) | editor de convocatorias (admin) |
| jsoneditor | JSONEditor | 9.9.0 | cdnjs | gestión de convocatorias (admin) |

Los archivos `.js`/`.css` se guardan sin la línea `sourceMappingURL` final.
Nota: el editor JSON de administración no valida la sintaxis en vivo, porque el worker de
Ace necesitaría relajar la CSP (`script-src data:`); el editor funciona igual.
