# Guía de usuario (presentación HTML)

Genera `Guia_Usuario_Programas_Financiacion.html`, autocontenido (~4 MB), a partir de capturas reales de producción.

```
pip install playwright pillow requests
python capturar.py     # fotografía la web y calcula las regiones (capturas/, regiones.json)
python construir.py    # construye el HTML
python qa.py           # recorrido de comprobación (opcional)
```

Los textos y pasos están en `guion.py`; el diseño y el motor, en `plantilla.html`.
Atajos: ← → pasos · N guion · A ver todos · G índice · F pantalla completa.
