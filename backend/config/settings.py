"""
VirtualFit Pro — Enterprise Configuration
==========================================
Centralized, environment-aware config.
All secrets come from environment variables ONLY.
"""

import os
import secrets
from datetime import timedelta


def _require(key: str) -> str:
    """Raise immediately if a required env var is missing."""
    val = os.environ.get(key, '').strip()
    if not val or val.startswith('CHANGE_THIS') or val.startswith('your_'):
        # In development, warn. In production, crash.
        if os.environ.get('FLASK_ENV') == 'production':
            raise EnvironmentError(
                f"❌ Required environment variable '{key}' is not set. "
                "Set it before running in production."
            )
    return val or ''


class BaseConfig:
    # ── Flask Core ────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    DEBUG = False
    TESTING = False
    JSON_SORT_KEYS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB upload limit

    # ── JWT ───────────────────────────────────────────────
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or secrets.token_hex(32)
    # Ensure minimum 32 bytes for HS256
    if len(JWT_SECRET_KEY) < 32:
        JWT_SECRET_KEY = JWT_SECRET_KEY + secrets.token_hex(16)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 900))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 604800))
    )
    JWT_ALGORITHM = 'HS256'

    # ── Database — MySQL ──────────────────────────────────
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASS = os.environ.get('DB_PASS', '')
    DB_NAME = os.environ.get('DB_NAME', 'virtualfit_db')
    DB_POOL_SIZE = int(os.environ.get('DB_POOL_SIZE', 10))
    DB_MAX_OVERFLOW = int(os.environ.get('DB_MAX_OVERFLOW', 20))

    # ── Supabase ──────────────────────────────────────────
    SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

    # ── AI APIs ───────────────────────────────────────────
    FAL_API_KEY = os.environ.get('FAL_API_KEY', '')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    LIGHTX_API_KEY = os.environ.get('LIGHTX_API_KEY', '')

    # ── Payment ───────────────────────────────────────────
    PAYHERE_MERCHANT_ID = os.environ.get('PAYHERE_MERCHANT_ID', '')
    PAYHERE_SECRET = os.environ.get('PAYHERE_SECRET', '')
    PAYHERE_SANDBOX = os.environ.get('PAYHERE_SANDBOX', 'true').lower() == 'true'

    # ── CORS ──────────────────────────────────────────────
    ALLOWED_ORIGINS = [
        o.strip()
        for o in os.environ.get(
            'ALLOWED_ORIGINS', 'http://localhost:5000'
        ).split(',')
    ]

    # ── WhatsApp ──────────────────────────────────────────
    ADMIN_WHATSAPP = os.environ.get('ADMIN_WHATSAPP', '')

    # ── Security ──────────────────────────────────────────
    BCRYPT_ROUNDS = 12
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION = 900  # 15 minutes in seconds
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # ── Rate Limiting ─────────────────────────────────────
    RATELIMIT_DEFAULT = os.environ.get('RATE_LIMIT_DEFAULT', '100 per hour')
    RATELIMIT_AUTH = os.environ.get('RATE_LIMIT_AUTH', '5 per minute')
    RATELIMIT_AI = os.environ.get('RATE_LIMIT_AI', '20 per minute')
    RATELIMIT_STORAGE_URL = 'memory://'

    # ── Logging ───────────────────────────────────────────
    LOG_LEVEL = 'INFO'
    LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')

    # ── Image Validation ──────────────────────────────────
    MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
    ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/webp'}

    # ── Privacy ───────────────────────────────────────────
    STORE_CUSTOMER_PHOTOS = False
    PHOTO_RETENTION_HOURS = 0  # Never stored


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # HTTP OK in dev
    LOG_LEVEL = 'DEBUG'
    BCRYPT_ROUNDS = 10  # Faster in dev


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    BCRYPT_ROUNDS = 14  # Stronger in prod
    LOG_LEVEL = 'WARNING'
    RATELIMIT_AUTH = '3 per minute'

    def __init__(self):
        # Validate critical secrets exist in production
        _require('SECRET_KEY')
        _require('JWT_SECRET_KEY')
        _require('SUPABASE_URL')
        _require('SUPABASE_KEY')


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    BCRYPT_ROUNDS = 4
    DB_NAME = 'virtualfit_test'
    SESSION_COOKIE_SECURE = False


_config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}


def get_config():
    env = os.environ.get('FLASK_ENV', 'development').lower()
    cfg_class = _config_map.get(env, DevelopmentConfig)
    return cfg_class()
