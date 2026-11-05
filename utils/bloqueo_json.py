"""
Bloqueo para las escrituras del JSON de programas.

Dos personas pueden guardar a la vez (o el monitor de concesiones puede escribir
mientras alguien edita): sin bloqueo, la segunda escritura pisa a la primera.
Con este bloqueo cada lectura-modificación-escritura espera su turno.

En Linux (el servidor) usa un flock sobre un archivo junto al JSON. En otros sistemas
no hace nada, que es suficiente para desarrollar en local.
"""

import os
from contextlib import contextmanager

try:
    import fcntl
except ImportError:  # Windows
    fcntl = None


@contextmanager
def bloqueo_json(json_path, espera_max=30):
    """Uso: with bloqueo_json(ruta): leer, modificar y escribir el JSON."""
    if fcntl is None:
        yield
        return
    import time
    with open(os.path.join(os.path.dirname(json_path), '.programas.lock'), 'a') as f:
        inicio = time.time()
        while True:
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.time() - inicio > espera_max:
                    raise TimeoutError('No se pudo obtener el bloqueo del archivo de programas')
                time.sleep(0.1)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
