"""
Configuración centralizada para FADE Financiación
"""

import os
from datetime import timedelta


class Config:
    """Configuración base de la aplicación"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)

    # Cookie de sesión solo por HTTPS. Activar (SESSION_COOKIE_SECURE=1 en .env)
    # únicamente cuando el sitio ya se sirva por HTTPS: si no, el navegador no
    # envía la cookie y nadie puede iniciar sesión.
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', '0') == '1'

    # Acceso de socios desde la zona privada de fade.es (ver utils/acceso_socios.py).
    # SOCIOS_JWT_SECRET: clave compartida con la web de fade.es.
    # SOCIOS_ACCESO_OBLIGATORIO=1 exige sesión de socio (o de admin) en todas las
    # páginas; mientras sea 0 la herramienta sigue abierta como hasta ahora.
    SOCIOS_JWT_SECRET = os.environ.get('SOCIOS_JWT_SECRET', '')
    SOCIOS_ACCESO_OBLIGATORIO = os.environ.get('SOCIOS_ACCESO_OBLIGATORIO', '0') == '1'
    SOCIOS_LOGIN_URL = os.environ.get('SOCIOS_LOGIN_URL') or 'https://fade.es/login/'
    
    # Base de datos (JSON file)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or os.path.join(BASE_DIR, 'data', 'programas_financiacion.json')
    
    # Google Gemini AI
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # Autenticación admin: usuarios individuales con contraseña hasheada,
    # gestionados con scripts/crear_admin_user.py (ver utils/admin_auth.py).
    # ADMIN_PASSWORD ya no se usa para autenticar; se mantiene solo por
    # compatibilidad con despliegues antiguos que aún la definan en .env.
    
    # Selenium (para scraping BDNS)
    SELENIUM_REMOTE_URL = os.environ.get('SELENIUM_REMOTE_URL') or 'http://selenium:4444/wd/hub'
    CHROME_HEADLESS = True
    
    # Uploads
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB max file size
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'txt'}
    
    # Logging
    LOG_DIR = os.environ.get('LOG_DIR') or os.path.join(BASE_DIR, 'logs')
    
    # URLs
    BDNS_BASE_URL = 'https://www.infosubvenciones.es/bdnstrans/'


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False
    SELENIUM_REMOTE_URL = None  # Usar Chrome local


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    
    # En producción, forzar que existan las variables críticas
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Validar variables críticas
        assert os.environ.get('SECRET_KEY'), 'SECRET_KEY no está configurada'
        assert os.environ.get('GEMINI_API_KEY'), 'GEMINI_API_KEY no está configurada'


# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
