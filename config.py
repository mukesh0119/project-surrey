import os

class Config:
    """Base configuration with default settings."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key')
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'docx', 'txt', 'pdf'}
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Configuration for development environment."""
    DEBUG = True


class TestingConfig(Config):
    """Configuration for testing environment."""
    TESTING = True
    DEBUG = True


class ProductionConfig(Config):
    """Configuration for production environment."""
    DEBUG = False


# Environment-specific configuration mapping
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
