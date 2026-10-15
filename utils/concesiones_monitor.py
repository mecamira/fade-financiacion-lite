"""
Monitor de concesiones BDNS.

Detecta automáticamente cuándo una convocatoria en seguimiento ha sido
resuelta, consultando el endpoint público de concesiones:

    https://www.infosubvenciones.es/bdnstrans/api/concesiones/busqueda

Ejecución diaria desde el cron del host (comprueba todas las convocatorias
sin resolver, una vez al día):

    docker compose exec -T flask-app python -m utils.concesiones_monitor --forzar

Desde el Panel del Servidor se puede lanzar a mano. Esa ruta respeta un
límite de INTERVALO_MIN_HORAS por convocatoria (para que pulsar el botón
varias veces no martillee la API) salvo que se marque "forzar".

Ritmo de consultas deliberadamente suave para respetar la API pública:
  - pausa de 2 segundos entre llamadas
  - tope de concesiones guardadas por convocatoria (MAX_CONCESIONES)
"""

import argparse
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
# Un poco por debajo de 24h a propósito: el cron arranca cada día con unos
# segundos de diferencia y con un límite de 24h exactas se saltaba pasadas
# enteras cuando arrancaba un instante antes que el día anterior.
INTERVALO_MIN_HORAS = 20
MAX_CONCESIONES = 500          # tope de concesiones guardadas por convocatoria
PAGE_SIZE = 100
LOCK_MAX_SEGUNDOS = 20 * 60    # un lock más antiguo se considera huérfano

# Campos del programa que gestiona el monitor (el resto no se toca nunca)
CAMPOS_MONITOR = ('ultima_comprobacion_concesiones', 'resuelta',
                  'fecha_resolucion_detectada', 'concesiones', 'total_concesiones')


def _json_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.environ.get('DATABASE_PATH',
                          os.path.join(base_dir, 'data', 'programas_financiacion.json'))


def _lock_path():
    return os.path.join(os.path.dirname(_json_path()), '.monitor_concesiones.lock')


def _normalizar_bdns(codigo):
    """Convierte el código BDNS a cadena de dígitos ('860141.0' → '860141')."""
    if codigo is None:
        return None
    s = str(codigo).strip()
    if s.endswith('.0'):
        s = s[:-2]
    return s if s.isdigit() else None


def _parse_fecha(valor):
    if not valor:
        return None
    try:
        return datetime.fromisoformat(valor)
    except ValueError:
        return None


# ============================================================================
# LOCK (evita dos pasadas simultáneas: botón manual + cron, o doble clic)
# ============================================================================

def lock_activo():
    path = _lock_path()
    try:
        return os.path.exists(path) and (time.time() - os.path.getmtime(path)) <= LOCK_MAX_SEGUNDOS
    except OSError:
        return False


def _adquirir_lock():
    path = _lock_path()
    try:
        if os.path.exists(path) and not lock_activo():
            os.remove(path)  # lock huérfano de una pasada que murió
    except OSError:
        pass
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        return True
    except FileExistsError:
        return False
    except OSError as e:
        # Si no se puede crear el lock (permisos...), mejor ejecutar que no hacer nada
        logger.warning(f"No se pudo crear el lock del monitor ({e}); se continúa sin él")
        return True


def _liberar_lock():
    try:
        os.remove(_lock_path())
    except OSError:
        pass


# ============================================================================
# CONSULTA A LA API
# ============================================================================

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


# ============================================================================
# NOTIFICACIONES TELEGRAM
# ============================================================================

def _enviar_telegram(texto):
    """Envía un mensaje por Telegram. False si no está configurado o falla."""
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        logger.info("Telegram no configurado (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID); se omite notificación")
        return False
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={'chat_id': chat_id, 'text': texto, 'parse_mode': 'Markdown'},
            timeout=15,
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Error enviando notificación Telegram: {e}")
        return False


def notificar_telegram(resueltas):
    """Notificación agrupada de convocatorias resueltas."""
    lineas = ["🔔 *Convocatorias resueltas detectadas*", ""]
    for r in resueltas:
        importe_total = sum(c.get('importe') or 0 for c in r['concesiones'])
        lineas.append(f"✅ *{r['nombre']}*")
        lineas.append(f"   BDNS {r['codigo_bdns']} · {r['total_concesiones']} concesiones"
                      + (f" · {importe_total:,.0f} €".replace(',', '.') if importe_total else ""))
        lineas.append("")
    lineas.append("Ver detalle en el Dashboard de Programas.")

    ok = _enviar_telegram('\n'.join(lineas))
    if ok:
        logger.info(f"Notificación Telegram enviada ({len(resueltas)} convocatorias)")
    return ok


def notificar_fallo(comprobadas, errores):
    """Aviso de que el monitor no está pudiendo consultar la BDNS."""
    ok = _enviar_telegram(
        "⚠️ *Monitor de concesiones con problemas*\n\n"
        f"No se pudo consultar la BDNS en {errores} de {comprobadas} convocatorias. "
        "Puede ser una caída temporal de la API o que haya limitado el acceso. "
        "Revisa el Panel del Servidor."
    )
    if ok:
        logger.info("Aviso de fallo enviado por Telegram")
    return ok


# ============================================================================
# LECTURA / ESCRITURA DEL JSON
# ============================================================================

def _cargar(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"No se pudo leer {path}: {e}")
        return None, None
    programas = data.get('programas', data) if isinstance(data, dict) else data
    return data, programas


def _volcar(path, actualizados):
    """
    Aplica los campos del monitor sobre una copia RECIÉN LEÍDA del JSON.

    La pasada dura varios minutos; si se escribiera la copia leída al
    empezar, se perderían los cambios que haya hecho alguien mientras tanto
    (por ejemplo, guardar una convocatoria nueva). Volviendo a leer justo
    antes de escribir, solo se tocan los campos del monitor en los programas
    comprobados.
    """
    if not actualizados:
        return True
    data, programas = _cargar(path)
    if programas is None:
        return False
    for p in programas:
        upd = actualizados.get(p.get('id'))
        if upd:
            p.update({k: v for k, v in upd.items() if k in CAMPOS_MONITOR})
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logger.error(f"No se pudo guardar {path}: {e}")
        return False


def _clasificar(programas, forzar, ahora):
    """Separa los programas a comprobar de los que se omiten, con el motivo."""
    limite = ahora - timedelta(hours=INTERVALO_MIN_HORAS)
    pendientes = []
    stats = {'omitidas': 0, 'resueltas_previas': 0, 'sin_bdns': 0, 'ultima_comprobacion': None}
    for p in programas:
        if not _normalizar_bdns(p.get('codigo_bdns')):
            stats['sin_bdns'] += 1
            continue
        if p.get('resuelta'):
            stats['resueltas_previas'] += 1
            continue
        ultima = _parse_fecha(p.get('ultima_comprobacion_concesiones'))
        if ultima and (stats['ultima_comprobacion'] is None or ultima > stats['ultima_comprobacion']):
            stats['ultima_comprobacion'] = ultima
        if not forzar and ultima and ultima > limite:
            stats['omitidas'] += 1
            continue
        pendientes.append(p)
    return pendientes, stats


def planificar(forzar=False):
    """
    Dice qué haría una pasada ahora mismo, sin consultar la API.
    Lo usa el botón del Panel del Servidor para informar al usuario.
    """
    data, programas = _cargar(_json_path())
    if programas is None:
        return {'error': 'No se pudo leer la base de datos de programas'}
    pendientes, stats = _clasificar(programas, forzar, datetime.now())
    stats['a_comprobar'] = len(pendientes)
    stats['ocupado'] = lock_activo()
    return stats


# ============================================================================
# PASADA DEL MONITOR
# ============================================================================

def ejecutar_monitor(forzar=False):
    """
    Pasada completa del monitor. Devuelve un resumen:
    comprobadas, errores, omitidas, resueltas_previas, sin_bdns, resueltas (lista).
    """
    resumen = {'comprobadas': 0, 'errores': 0, 'omitidas': 0, 'resueltas_previas': 0,
               'sin_bdns': 0, 'resueltas': [], 'ocupado': False}

    if not _adquirir_lock():
        logger.info("Monitor de concesiones: ya hay otra pasada en curso, se omite esta")
        resumen['ocupado'] = True
        return resumen
    try:
        _ejecutar(forzar, resumen)
    finally:
        _liberar_lock()
    return resumen


def _ejecutar(forzar, resumen):
    path = _json_path()
    data, programas = _cargar(path)
    if programas is None:
        return

    pendientes, stats = _clasificar(programas, forzar, datetime.now())
    resumen.update({k: stats[k] for k in ('omitidas', 'resueltas_previas', 'sin_bdns')})

    actualizados = {}
    for i, p in enumerate(pendientes):
        if i > 0:
            time.sleep(PAUSA_ENTRE_LLAMADAS)

        codigo = _normalizar_bdns(p.get('codigo_bdns'))
        nombre = p.get('nombre_coloquial') or p.get('nombre') or codigo
        total, concesiones = consultar_concesiones(codigo, p.get('vpd') or 'GE')
        resumen['comprobadas'] += 1

        if total is None:
            # Error de red: no se sella la comprobación, se reintenta en la próxima pasada
            resumen['errores'] += 1
            continue

        ahora = datetime.now().isoformat()
        upd = {'ultima_comprobacion_concesiones': ahora}
        if total > 0:
            upd.update({'resuelta': True, 'fecha_resolucion_detectada': ahora,
                        'concesiones': concesiones, 'total_concesiones': total})
            resumen['resueltas'].append({'nombre': nombre, 'codigo_bdns': codigo,
                                         'total_concesiones': total, 'concesiones': concesiones})
            logger.info(f"RESUELTA: {nombre} (BDNS {codigo}) — {total} concesiones")
        else:
            logger.info(f"Sin concesiones aún: {nombre} (BDNS {codigo})")
        actualizados[p.get('id')] = upd

    guardado = _volcar(path, actualizados)

    # Solo se avisa si el resultado quedó guardado: si no, la próxima pasada
    # lo volverá a detectar y se evita avisar dos veces de lo mismo.
    if resumen['resueltas'] and guardado:
        notificar_telegram(resumen['resueltas'])
    if resumen['comprobadas'] and resumen['errores'] * 2 >= resumen['comprobadas']:
        notificar_fallo(resumen['comprobadas'], resumen['errores'])

    logger.info(
        f"Monitor concesiones: {resumen['comprobadas']} comprobadas "
        f"({resumen['errores']} con error), {len(resumen['resueltas'])} resueltas nuevas; "
        f"omitidas: {resumen['omitidas']} por comprobarse hace menos de {INTERVALO_MIN_HORAS} h, "
        f"{resumen['resueltas_previas']} ya resueltas, {resumen['sin_bdns']} sin código BDNS"
    )


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - concesiones_monitor - %(levelname)s - %(message)s',
    )
    parser = argparse.ArgumentParser(description='Monitor de concesiones BDNS')
    parser.add_argument('--forzar', action='store_true',
                        help=f'ignora el límite de {INTERVALO_MIN_HORAS} h y comprueba todas las convocatorias sin resolver')
    args = parser.parse_args()
    ejecutar_monitor(forzar=args.forzar)
    sys.exit(0)
