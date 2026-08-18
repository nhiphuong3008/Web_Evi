"""
EVI Dashboard - Configuration
Quản lý cấu hình ứng dụng từ environment variables.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    APP_NAME = os.getenv('APP_NAME', 'Trung tâm Anh ngữ Vicare')
    SECRET_KEY = os.getenv('APP_SECRET_KEY', 'dev-secret-key')

    # Google Sheets
    GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv(
        'GOOGLE_SHEETS_CREDENTIALS_FILE', 'credentials.json'
    )
    GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv(
        'GOOGLE_SHEETS_SPREADSHEET_ID',
        '1TfI4zZyOXOmm8i3DEbSfh0BsR4KXUVGt2RFRi9nn9M0'
    )
    GOOGLE_SHEETS_BTVN_ID = os.getenv(
        'GOOGLE_SHEETS_BTVN_ID',
        '1wKcmRH9azv9urXvp-Ld4zWwmZ-iuGA2Vo30WzEkBR1I'
    )
    GOOGLE_SHEETS_GRADES_ID = os.getenv(
        'GOOGLE_SHEETS_GRADES_ID',
        '1UzeCvCQ09WDxuXhbYQD3yEOScd4KvYCogcj0WW0BMVM'
    )
    GOOGLE_SHEETS_NEW_GRADES_ID = os.getenv(
        'GOOGLE_SHEETS_NEW_GRADES_ID',
        '1BkNjEfYBXNjY4GyZOhhAVWgOk7t7sNWhxFdpA84vM6o'
    )

    # Flask
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    FLASK_HOST = '0.0.0.0'


# Config mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}


def get_config():
    """Get configuration based on FLASK_ENV."""
    env = os.getenv('FLASK_ENV', 'development')
    return config_map.get(env, DevelopmentConfig)()
