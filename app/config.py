import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-never-use-in-prod"

    WTF_CSRF_SECRET_KEY = os.environ.get("WTF_CSRF_SECRET_KEY") or SECRET_KEY
    WTF_CSRF_TIME_LIMIT = 3600  # 1小时过期

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///visco.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security configuration
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "prod"  # Force HTTPS in production environment
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes session timeout

    # Encryption key
    ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY") or Fernet.generate_key().decode()


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False


# Configuration mapping
config_by_name = {
    "dev": DevelopmentConfig,
    "prod": ProductionConfig
}