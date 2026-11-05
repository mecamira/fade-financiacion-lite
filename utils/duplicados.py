"""
Detección de convocatorias duplicadas (mismo código BDNS).

Se evitan al guardar (ver financing_dashboard.ProgramaDuplicado), pero esta
comprobación diaria atrapa las que se hayan colado de todos modos: dos personas
guardando a la vez, importaciones antiguas, ediciones del JSON a mano...

Ejecución diaria desde el cron del host:

    docker compose exec -T flask-app python -m utils.duplicados

Si hay duplicados, lo deja en el log y avisa por Telegram (el mismo bot del
monitor de concesiones). Si no hay ninguno, no envía nada.
"""

import json
import logging
import sys

from utils.concesiones_monitor import _enviar_telegram, _json_path, _md, _normalizar_bdns

logger = logging.getLogger(__name__)


def buscar_duplicados(programas):
    """Agrupa los programas con el mismo código BDNS. Devuelve solo los grupos repetidos y no confirmados."""
    por_codigo = {}
    for p in programas:
        codigo = _normalizar_bdns(p.get('codigo_bdns'))
        if codigo:
            por_codigo.setdefault(codigo, []).append({
                'id': p.get('id'),
                'nombre': p.get('nombre_coloquial') or p.get('nombre') or p.get('id'),
                'organismo': p.get('organismo') or '',
                'confirmado': bool(p.get('duplicado_confirmado')),
            })
    # Un grupo está "confirmado" si alguien aceptó guardar la BDNS repetida a propósito
    # (varios programas distintos bajo una misma convocatoria): todos menos uno llevan la marca
    return [{'bdns': c, 'programas': ps} for c, ps in sorted(por_codigo.items())
            if len(ps) > 1 and sum(1 for p in ps if not p['confirmado']) > 1]


def cargar_duplicados():
    """Lee el JSON de programas y devuelve los grupos duplicados (lista vacía si no hay o si falla la lectura)."""
    try:
        with open(_json_path(), 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"No se pudo leer el archivo de programas: {e}")
        return []
    programas = data.get('programas', data) if isinstance(data, dict) else data
    return buscar_duplicados(programas)


def comprobar(notificar=True):
    grupos = cargar_duplicados()
    if not grupos:
        logger.info("Duplicados: ninguno")
        return grupos
    lineas = [f"⚠️ *Convocatorias duplicadas* ({len(grupos)})", ""]
    for g in grupos:
        lineas.append(f"BDNS {g['bdns']}:")
        for p in g['programas']:
            lineas.append(f"   • {_md(p['nombre'])} (id: {_md(p['id'])})")
        lineas.append("")
    lineas.append("Elimina las sobrantes en Administración → Editar convocatorias.")
    texto = '\n'.join(lineas)
    logger.warning("Duplicados encontrados:\n" + texto)
    if notificar:
        _enviar_telegram(texto)
    return grupos


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - duplicados - %(levelname)s - %(message)s')
    comprobar()
    sys.exit(0)
