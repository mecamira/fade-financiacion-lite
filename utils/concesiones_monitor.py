"""
Monitor de concesiones BDNS.

Detecta automáticamente cuándo una convocatoria en seguimiento ha sido
resuelta, consultando el endpoint público de concesiones:

    https://www.infosubvenciones.es/bdnstrans/api/concesiones/busqueda

Diseñado para ejecutarse UNA VEZ AL DÍA vía cron del host:

    docker compose exec -T flask-app python -m utils.concesiones_monitor

Ritmo de consultas deliberadamente suave para respetar la API pública:
  - máximo una comprobación cada 24h por convocatoria
  - pausa de 2 segundos entre llamadas
  - tope de concesiones guardadas por convocatoria (MAX_CONCESIONES)
"""

import json
import os
import sys
import time
import logging
from datetime import datetime, timedelta

import requests

logger = logging.getLogger(__name__)

BDNS_CONCESIONES_URL = 'https://www.infosubvenciones.es/bdnstrans/api/concesiones/busqueda'
HEADERS = {'User-Agent': 'Mozilla/5.0'}

PAUSA_ENTRE_LLAMADAS = 2       # segundos entre peticiones a BDNS
INTERVALO_MIN_HORAS = 24       # no re-comprobar una convocatoria antes de esto
MAX_CONCESIONES = 500          # tope de concesiones guardadas por convocatoria
PAGE_SIZE = 100


def _json_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.environ.get('DATABASE_PATH',
                          os.path.join(base_dir, 'data', 'programas_financiacion.json'))


def _normalizar_bdns(codigo):
    """Convierte el código BDNS a cadena de dígitos ('860141.0' → '860141')."""
    if codigo is None:
        return None
    s = str(codigo).strip()
    if s.endswith('.0'):
        s = s[:-2]
    return s if s.isdigit() else None


def consultar_concesiones(codigo_bdns, vpd='GE'):
    """
    Consulta las concesiones de una convocatoria.
    Devuelve (total_elements, lista_concesiones) o (None, []) si hay error.
    """
    concesiones = []
    page = 0
    total = None
    while True:
        try:
            r = requests.get(BDNS_CONCESIONES_URL, params={
                'vpd': vpd,
                'numeroConvocatoria': codigo_bdns,
                'pageSize': PAGE_SIZE,
                'page': page,
            }, timeout=30, headers=HEADERS)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            logger.warning(f"Error consultando concesiones de {codigo_bdns}: {e}")
            return None, []

        if total is None:
            total = data.get('totalElements', 0)
        if total == 0:
            return 0, []

        for item in data.get('content', []):
            concesiones.append({
                'beneficiario':     item.get('beneficiario'),
                'importe':          item.get('importe'),
                'ayuda_equivalente': item.get('ayudaEquivalente'),
                'fecha_concesion':  item.get('fechaConcesion'),
                'instrumento':      (item.get('instrumento') or '').strip() or None,
                'url_br':           item.get('urlBR'),
            })

        if len(concesiones) >= min(total, MAX_CONCESIONES) or data.get('last', True):
            break
        page += 1
        time.sleep(PAUSA_ENTRE_LLAMADAS)

    return total, concesiones[:MAX_CONCESIONES]


def notificar_telegram(resueltas):
    """
    Envía una notificación agrupada por Telegram.
    Requiere TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID en el entorno.
    Devuelve True si se envió, False si no está configurado o falla.
    """
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        logger.info("Telegram no configurado (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID); se omite notificación")
        return False

    lineas = ["🔔 *Convocatorias resueltas detectadas*", ""]
    for r in resueltas:
        importe_total = sum(c.get('importe') or 0 for c in r['concesiones'])
        lineas.append(f"✅ *{r['nombre']}*")
        lineas.append(f"   BDNS {r['codigo_bdns']} · {r['total_concesiones']} concesiones"
                      + (f" · {importe_total:,.0f} €".replace(',', '.') if importe_total else ""))
        lineas.append("")
    lineas.append("Ver detalle en el Dashboard de Programas.")

    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={'chat_id': chat_id, 'text': '\n'.join(lineas), 'parse_mode': 'Markdown'},
            timeout=15,
        )
        resp.raise_for_status()
        logger.info(f"Notificación Telegram enviada ({len(resueltas)} convocatorias)")
        return True
    except Exception as e:
        logger.error(f"Error enviando notificación Telegram: {e}")
        return False


def ejecutar_monitor():
    """
    Pasada completa del monitor. Devuelve la lista de convocatorias
    marcadas como resueltas en esta ejecución.
    """
    path = _json_path()
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"No se pudo leer {path}: {e}")
        return []

    programas = data.get('programas', data) if isinstance(data, dict) else data
    ahora = datetime.now()
    limite = ahora - timedelta(hours=INTERVALO_MIN_HORAS)
    resueltas_ahora = []
    comprobadas = 0

    for p in programas:
        codigo = _normalizar_bdns(p.get('codigo_bdns'))
        if not codigo:
            continue
        if p.get('resuelta'):
            continue

        # Rate limit: máximo una comprobación cada INTERVALO_MIN_HORAS
        ultima = p.get('ultima_comprobacion_concesiones')
        if ultima:
            try:
                if datetime.fromisoformat(ultima) > limite:
                    continue
            except ValueError:
                pass

        if comprobadas > 0:
            time.sleep(PAUSA_ENTRE_LLAMADAS)
        comprobadas += 1

        vpd = p.get('vpd') or 'GE'
        total, concesiones = consultar_concesiones(codigo, vpd)
        p['ultima_comprobacion_concesiones'] = ahora.isoformat()

        if total is None:
            continue  # error de red: reintentará en la próxima pasada

        nombre = p.get('nombre_coloquial') or p.get('nombre') or codigo
        if total > 0:
            p['resuelta'] = True
            p['fecha_resolucion_detectada'] = ahora.isoformat()
            p['concesiones'] = concesiones
            p['total_concesiones'] = total
            resueltas_ahora.append({
                'nombre': nombre,
                'codigo_bdns': codigo,
                'total_concesiones': total,
                'concesiones': concesiones,
            })
            logger.info(f"RESUELTA: {nombre} (BDNS {codigo}) — {total} concesiones")
        else:
            logger.info(f"Sin concesiones aún: {nombre} (BDNS {codigo})")

    # Guardar cambios (aunque solo sea la fecha de comprobación)
    if comprobadas > 0:
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"No se pudo guardar {path}: {e}")

    if resueltas_ahora:
        notificar_telegram(resueltas_ahora)

    logger.info(f"Monitor concesiones: {comprobadas} comprobadas, "
                f"{len(resueltas_ahora)} resueltas nuevas")
    return resueltas_ahora


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - concesiones_monitor - %(levelname)s - %(message)s',
    )
    resueltas = ejecutar_monitor()
    sys.exit(0)
