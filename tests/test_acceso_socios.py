"""
Tests del acceso de socios con enlace firmado. Se ejecutan con la librería estándar:

    python -m unittest tests.test_acceso_socios -v
"""

import os
import secrets
import tempfile
import time
import unittest

import jwt

from utils import acceso_socios as acceso

CLAVE = 'clave-de-prueba-de-al-menos-32-caracteres!'


def token(clave=CLAVE, **cambios):
    ahora = int(time.time())
    datos = {
        'iss': 'fade.es',
        'aud': 'financiacion.fade.es',
        'sub': '1234',
        'iat': ahora,
        'exp': ahora + 120,
        'jti': secrets.token_hex(16),
    }
    datos.update(cambios)
    datos = {k: v for k, v in datos.items() if v is not None}
    return jwt.encode(datos, clave, algorithm='HS256')


class TestValidarToken(unittest.TestCase):

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def validar(self, t, clave=CLAVE):
        return acceso.validar_token(t, clave, self.dir.name)

    def test_token_valido(self):
        self.assertEqual(self.validar(token()), '1234')

    def test_sub_numerico_se_devuelve_como_texto(self):
        # La especificación pide (string) $socio_id, pero si WordPress lo envía
        # como número se acepta igual
        self.assertEqual(self.validar(token(sub=1234)), '1234')

    def test_reutilizado(self):
        t = token()
        self.validar(t)
        with self.assertRaises(acceso.TokenInvalido):
            self.validar(t)

    def test_caducado(self):
        ahora = int(time.time())
        with self.assertRaises(acceso.TokenInvalido):
            self.validar(token(iat=ahora - 300, exp=ahora - 60))

    def test_desfase_de_reloj_tolerado(self):
        ahora = int(time.time())
        self.assertEqual(self.validar(token(iat=ahora - 130, exp=ahora - 10)), '1234')

    def test_clave_incorrecta(self):
        with self.assertRaises(acceso.TokenInvalido):
            self.validar(token(clave='otra-clave-distinta-de-al-menos-32-caracteres'))

    def test_audiencia_o_emisor_incorrectos(self):
        for cambios in ({'aud': 'otra.web.es'}, {'iss': 'otra.web.es'}):
            with self.subTest(**cambios), self.assertRaises(acceso.TokenInvalido):
                self.validar(token(**cambios))

    def test_campos_obligatorios(self):
        for campo in ('sub', 'jti', 'exp', 'iat', 'aud', 'iss'):
            with self.subTest(campo=campo), self.assertRaises(acceso.TokenInvalido):
                self.validar(token(**{campo: None}))

    def test_vida_demasiado_larga(self):
        ahora = int(time.time())
        with self.assertRaises(acceso.TokenInvalido):
            self.validar(token(iat=ahora, exp=ahora + 3600))

    def test_algoritmo_none_rechazado(self):
        t = jwt.encode({'iss': 'fade.es', 'aud': 'financiacion.fade.es', 'sub': '1',
                        'iat': int(time.time()), 'exp': int(time.time()) + 60,
                        'jti': 'x'}, None, algorithm='none')
        with self.assertRaises(acceso.TokenInvalido):
            self.validar(t)

    def test_sin_clave_configurada(self):
        for clave in ('', 'corta'):
            with self.subTest(clave=clave), self.assertRaises(acceso.TokenInvalido):
                self.validar(token(), clave=clave)

    def test_sin_token(self):
        with self.assertRaises(acceso.TokenInvalido):
            self.validar('')


class TestRutas(unittest.TestCase):
    """Comportamiento de la app con el acceso obligatorio activado y desactivado"""

    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.TemporaryDirectory()
        os.environ['DATABASE_PATH'] = os.path.join(cls.dir.name, 'programas_financiacion.json')
        os.environ['LOG_DIR'] = cls.dir.name
        with open(os.environ['DATABASE_PATH'], 'w') as f:
            f.write('[]')
        from app import app
        cls.app = app

    @classmethod
    def tearDownClass(cls):
        cls.dir.cleanup()

    def setUp(self):
        self.app.config.update(TESTING=True, SOCIOS_JWT_SECRET=CLAVE,
                               SOCIOS_ACCESO_OBLIGATORIO=True,
                               DATABASE_PATH=os.environ['DATABASE_PATH'])
        self.cliente = self.app.test_client()

    def test_sin_sesion_redirige_a_fade(self):
        r = self.cliente.get('/financiacion/dashboard')
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.headers['Location'], 'https://fade.es/login/')

    def test_api_sin_sesion_devuelve_401(self):
        self.assertEqual(self.cliente.get('/api/programas-financiacion').status_code, 401)

    def test_rutas_libres(self):
        self.assertNotEqual(self.cliente.get('/health').status_code, 302)
        self.assertEqual(self.cliente.get('/admin/login').status_code, 200)

    def test_acceso_con_token_abre_sesion(self):
        r = self.cliente.get('/acceso?token=' + token())
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r.headers['Location'].endswith('/financiacion/dashboard'))
        with self.cliente.session_transaction() as s:
            self.assertEqual(s['socio_id'], '1234')
        r = self.cliente.get('/api/programas-financiacion')
        self.assertNotEqual(r.status_code, 401)

    def test_acceso_con_token_invalido_redirige_a_fade(self):
        r = self.cliente.get('/acceso?token=basura')
        self.assertEqual(r.headers['Location'], 'https://fade.es/login/')
        with self.cliente.session_transaction() as s:
            self.assertNotIn('socio_id', s)

    def test_admin_no_necesita_token(self):
        with self.cliente.session_transaction() as s:
            s['admin_logged_in'] = True
        self.assertNotEqual(self.cliente.get('/api/programas-financiacion').status_code, 401)

    def test_desactivado_todo_sigue_abierto(self):
        self.app.config['SOCIOS_ACCESO_OBLIGATORIO'] = False
        self.assertNotEqual(self.cliente.get('/api/programas-financiacion').status_code, 401)
        r = self.cliente.get('/financiacion/dashboard')
        self.assertNotEqual(r.headers.get('Location'), 'https://fade.es/login/')


if __name__ == '__main__':
    unittest.main()
