import os
from datetime import timedelta
from sqlalchemy.pool import QueuePool

class Config:
    """Base configuration class with Azure SQL Server using pymssql (no ODBC drivers needed)."""
    
    # Azure SQL Server Configuration - W3 Manifest Database
    DB_USER = "w3admin"
    DB_PASSWORD = "W3Manifest2024!"
    DB_SERVER = "w3manifest-sqlserver-prod.database.windows.net"
    DB_NAME = "w3manifest-db"
    
    # Use pymssql instead of pyodbc - no ODBC drivers needed
    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pymssql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:1433/"
        f"{DB_NAME}?charset=utf8"
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 5,
        "max_overflow": 10,
        "pool_recycle": 1800,
        "pool_timeout": 30,
        "poolclass": QueuePool,
        "echo": False,
        "future": True
    }
    
    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Email Configuration
    EMAIL_SERVER = os.environ.get('EMAIL_SERVER', 'outlook.office365.com')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '993'))
    EMAIL_USE_SSL = True
    EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME', 'ordini.w3@datarockers.cloud')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    EMAIL_CHECK_INTERVAL = int(os.environ.get('EMAIL_CHECK_INTERVAL', '300'))  # seconds
    
    # Azure Configuration
    AZURE_STORAGE_CONNECTION_STRING = os.environ.get('STORAGE_CONNECTION_STRING')
    AZURE_CONTAINER_NAME = 'manifests'
    
    # Celery Configuration (for background tasks)
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,https://w3manifest-frontend-prod.azurewebsites.net').split(',')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Pagination
    ORDERS_PER_PAGE = int(os.environ.get('ORDERS_PER_PAGE', '50'))
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size


# Configurazione unica - SEMPRE Azure
config = {
    'development': Config,
    'testing': Config,
    'production': Config,
    'default': Config
}
