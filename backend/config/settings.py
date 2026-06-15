from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
# .env обычно лежит в корне репозитория, но backend можно запускать и отдельно.
# Поэтому безопасно читаем оба варианта, не ломая Docker env_file.
load_dotenv(PROJECT_ROOT / '.env')
load_dotenv(BASE_DIR / '.env', override=False)


def env(name: str, default: str = '') -> str:
    return os.getenv(name, default)


def env_bool(name: str, default: bool = False) -> bool:
    value = env(name, str(default)).lower()
    return value in {'1', 'true', 'yes', 'on'}


def env_list(name: str, default: str = '') -> list[str]:
    raw = env(name, default)
    return [item.strip() for item in raw.split(',') if item.strip()]


SECRET_KEY = env('DJANGO_SECRET_KEY', 'change-me-in-production')
DEBUG = env_bool('DJANGO_DEBUG', True)
ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,backend')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'storages',
    'apps.portal',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES: list[dict[str, Any]] = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB', 'vania_sait'),
        'USER': env('POSTGRES_USER', 'vania_sait'),
        'PASSWORD': env('POSTGRES_PASSWORD', 'vania_sait_password'),
        'HOST': env('POSTGRES_HOST', 'db'),
        'PORT': env('POSTGRES_PORT', '5432'),
        'CONN_MAX_AGE': 60,
    }
}

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = env('TZ', 'Europe/Moscow')
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_PARSER_CLASSES': ['rest_framework.parsers.JSONParser'],
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'vania-sait-runtime-cache',
    }
}

CORS_ALLOWED_ORIGINS = env_list(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost,http://localhost:80,http://localhost:5173,http://127.0.0.1:5173',
)
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS', 'http://localhost,http://127.0.0.1')

SESSION_COOKIE_NAME = 'shiomi_sessionid'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE', not DEBUG)
CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE', not DEBUG)
SESSION_COOKIE_SAMESITE = env('SESSION_COOKIE_SAMESITE', 'Lax')
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', False)
SECURE_HSTS_SECONDS = int(env('SECURE_HSTS_SECONDS', '0'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', False)
SECURE_HSTS_PRELOAD = env_bool('SECURE_HSTS_PRELOAD', False)
X_FRAME_OPTIONS = 'SAMEORIGIN'
SECURE_CONTENT_TYPE_NOSNIFF = True

FRONTEND_URL = env('FRONTEND_URL', 'http://localhost')
BACKEND_URL = env('BACKEND_URL', 'http://localhost')
STEAM_API_KEY = env('STEAM_API_KEY')
STEAM_DEV_LOGIN_ENABLED = env_bool('STEAM_DEV_LOGIN_ENABLED', DEBUG)
STEAM_DEV_STEAM_ID64 = env('STEAM_DEV_STEAM_ID64', '76561198000000000')
STEAM_DEV_USERNAME = env('STEAM_DEV_USERNAME', 'SHIOMI Dev Player')
STEAM_REQUEST_TIMEOUT = float(env('STEAM_REQUEST_TIMEOUT', '8'))
STEAM_OPENID_REALM = env('STEAM_OPENID_REALM', BACKEND_URL.rstrip('/') + '/')
STEAM_RETURN_URL = env('STEAM_RETURN_URL', BACKEND_URL.rstrip('/') + '/api/auth/steam/return/')

GAME_SERVER_HOST = env('GAME_SERVER_HOST', '170.168.115.48')
GAME_SERVER_PORT = int(env('GAME_SERVER_PORT', '27115'))
GAME_SERVER_MAX_PLAYERS = int(env('GAME_SERVER_MAX_PLAYERS', '24'))
GAME_SERVER_TIMEOUT = float(env('GAME_SERVER_TIMEOUT', '0.7'))
GAME_SERVER_CACHE_SECONDS = int(env('GAME_SERVER_CACHE_SECONDS', '30'))

USE_S3_STORAGE = env_bool('USE_S3_STORAGE', False)
if USE_S3_STORAGE:
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_ENDPOINT_URL = env('AWS_S3_ENDPOINT_URL')
    AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', 'auto')
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = False
    STORAGES = {
        'default': {'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage'},
        'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
    }
else:
    STORAGES = {
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
    }

SENTRY_DSN = env('SENTRY_DSN')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=float(env('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
        send_default_pii=False,
        environment=env('SENTRY_ENVIRONMENT', 'production' if not DEBUG else 'development'),
    )

DATA_UPLOAD_MAX_MEMORY_SIZE = int(env('DATA_UPLOAD_MAX_MEMORY_SIZE', str(10 * 1024 * 1024)))
FILE_UPLOAD_MAX_MEMORY_SIZE = int(env('FILE_UPLOAD_MAX_MEMORY_SIZE', str(10 * 1024 * 1024)))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'compact': {
            'format': '[{levelname}] {asctime} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'compact',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': env('DJANGO_LOG_LEVEL', 'INFO'),
    },
}
