import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Base de datos
    DATABASE_URL: str = os.getenv('SQL_SERVER_CONNECTION_STRING')
    
    # Servidor
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', 8000))
    WORKERS: int = int(os.getenv('WORKERS', 1))
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'info')
    
    # Desarrollo
    DEBUG: bool = os.getenv('DEBUG', 'true').lower() == 'true'
    RELOAD: bool = os.getenv('RELOAD', 'true').lower() == 'true'
    
    # CORS
    ALLOWED_ORIGINS: list = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
    
    # Seguridad
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'clave_secreta_por_defecto')
    TOKEN_EXPIRE_MINUTES: int = int(os.getenv('TOKEN_EXPIRE_MINUTES', 30))

# Instancia global de configuración
settings = Settings()
