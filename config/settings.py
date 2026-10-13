import sys
from datetime import timedelta
from pathlib import Path

import dj_database_url
import environ

from . import constants as c


BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY', default='dev-insecure-key-change-me')
DEBUG = env('DEBUG', default=True)
ALLOWED_HOSTS = env.list(
    'ALLOWED_HOSTS',
    default=['localhost', '127.0.0.1'],
)

# Render автоматически даёт переменную RENDER_EXTERNAL_HOSTNAME
RENDER_EXTERNAL_HOSTNAME = env('RENDER_EXTERNAL_HOSTNAME', default='')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = env.list(
    'CSRF_TRUSTED_ORIGINS',
    default=[],
)
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary_storage',  # ← для медиа
    'cloudinary',  # ← для медиа
    'whitenoise.runserver_nostatic',  # ← для статики
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_spectacular',
    'django_filters',
    'apps.accounts',
    'apps.players',
    'apps.matches',
    'apps.news',
    'apps.staff',
    'apps.training',
    'apps.gallery',
    'apps.league',
    'apps.vk',
    'apps.api',
    'apps.web',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
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
                'config.context_processors.site_meta',  # ← новое
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASE_URL = env('DATABASE_URL', default='')

# === ВРЕМЕННАЯ ОТЛАДКА — удалим после деплоя ===


print(f'[DB DEBUG] DATABASE_URL present: {bool(DATABASE_URL)}', flush=True)
print(f'[DB DEBUG] DATABASE_URL length: {len(DATABASE_URL)}', flush=True)
print(f'[DB DEBUG] DATABASE_URL prefix: {DATABASE_URL[:40]}', flush=True)
print(f'[DB DEBUG] DATABASE_URL suffix: {DATABASE_URL[-40:]}', flush=True)
print(f'[DB DEBUG] python executable: {sys.executable}', flush=True)
# === /ОТЛАДКА ===

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True,
        ),
    }
    print('[DB DEBUG] Using dj_database_url', flush=True)
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('POSTGRES_DB', default='futsal'),
            'USER': env('POSTGRES_USER', default='futsal'),
            'PASSWORD': env('POSTGRES_PASSWORD', default='futsal'),
            'HOST': env('POSTGRES_HOST', default='db'),
            'PORT': env('POSTGRES_PORT', default='5432'),
        }
    }
    print('[DB DEBUG] Using FALLBACK POSTGRES_HOST=db', flush=True)

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

USE_CLOUDINARY = env.bool('USE_CLOUDINARY', default=False)

if USE_CLOUDINARY:
    # Продакшн: медиа в Cloudinary
    STORAGES = {
        'default': {
            'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage',
        },
        'staticfiles': {
            'BACKEND': (
                'whitenoise.storage.' 'CompressedManifestStaticFilesStorage'
            ),
        },
    }
else:
    # Локально: медиа в media/
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': (
                'whitenoise.storage.' 'CompressedManifestStaticFilesStorage'
            ),
        },
    }

# Cloudinary (медиа)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY': env('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': env('CLOUDINARY_API_SECRET', default=''),
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


AUTH_USER_MODEL = 'accounts.User'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': c.API_PAGE_SIZE,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=c.JWT_ACCESS_MINUTES),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=c.JWT_REFRESH_DAYS),
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Futsal Team API',
    'DESCRIPTION': 'API сайта мини-футбольной команды',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# --- Auth (frontend) ---
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# --- SEO / Sitemap ---
SITE_URL = env('SITE_URL', default='http://localhost:8000')
SITE_NAME = c.SITE_NAME
SITE_DESCRIPTION = c.SITE_DESCRIPTION
SITE_KEYWORDS = c.SITE_KEYWORDS

# =============================================================================
# О клубе
# =============================================================================

SITE_SLOGAN = c.SITE_SLOGAN
SITE_SHORT_DESCRIPTION = c.SITE_SHORT_DESCRIPTION
SITE_HISTORY = c.SITE_HISTORY
SITE_CONTACT_PHONE = c.SITE_CONTACT_PHONE
SITE_CONTACT_EMAIL = c.SITE_CONTACT_EMAIL
SITE_CONTACT_VK = c.SITE_CONTACT_VK
SITE_CONTACT_TELEGRAM = c.SITE_CONTACT_TELEGRAM
SITE_CITY = c.SITE_CITY


# =============================================================================
# Production settings
# =============================================================================

if not DEBUG:
    # Безопасность
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SESSION_COOKIE_SECURE = env.bool(
        'SESSION_COOKIE_SECURE',
        default=False,
    )
    CSRF_COOKIE_SECURE = env.bool(
        'CSRF_COOKIE_SECURE',
        default=False,
    )

    # За прокси (nginx) — чтобы Django знал схему (http/https)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # Логирование
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': (
                    '{levelname} {asctime} {module} '
                    '{process:d} {thread:d} {message}'
                ),
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    }

# --- ВКонтакте ---
VK_ACCESS_TOKEN = env('VK_ACCESS_TOKEN', default='')
