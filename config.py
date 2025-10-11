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
    
    # Base de datos (JSON file)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or os.path.join(BASE_DIR, 'data', 'programas_financiacion.json')
    
    # Google Gemini AI
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # Autenticación admin
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'changeme'
    
    # Selenium (para scraping BDNS)
    SELENIUM_REMOTE_URL = os.environ.get('SELENIUM_REMOTE_URL') or 'http://selenium:4444/wd/hub'
    CHROME_HEADLESS = True
    
    # Uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size
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
        assert os.environ.get('ADMIN_PASSWORD'), 'ADMIN_PASSWORD no está configurada'


# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
