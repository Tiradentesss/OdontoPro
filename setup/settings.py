from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv
load_dotenv()

# =========================
# BASE
# =========================

OPTIONS = {
    "ssl": {"ssl-mode": "REQUIRED"}
}

BASE_DIR = Path(__file__).resolve().parent.parent

SESSION_ENGINE = "django.contrib.sessions.backends.db"

# Permissões de cookie de sessão/coleta de CSRF
DEBUG = os.environ.get("DEBUG", "False") == "True"

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14  # 14 dias
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# =========================
# SEGURANÇA
# =========================

from django.core.management.utils import get_random_secret_key
from django.core.exceptions import ImproperlyConfigured

raw_secret_key = os.getenv("SECRET_KEY")
if raw_secret_key:
    SECRET_KEY = raw_secret_key
elif DEBUG:
    SECRET_KEY = get_random_secret_key()
    print("[WARN] SECRET_KEY ausente; gerando chave temporária em DEBUG")
else:
    raise ImproperlyConfigured("SECRET_KEY must be set in the environment in non-DEBUG mode")


IS_RAILWAY = 'RAILWAY_ENVIRONMENT' in os.environ

# Adicione isso (para Railway domains)
ALLOWED_HOSTS = ['.railway.app', '.up.railway.app', 'localhost', '127.0.0.1']

# Se usar HTTPS (Railway força)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_TRUSTED_ORIGINS = ['https://*.railway.app', 'https://*.up.railway.app']


# =========================
# APPS
# =========================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'odontoPro',
]


# =========================
# MIDDLEWARE
# =========================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # servir static no Railway
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# =========================
# URLS
# =========================

ROOT_URLCONF = 'setup.urls'

WSGI_APPLICATION = 'setup.wsgi.application'


# =========================
# TEMPLATES
# =========================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        # pasta templates global
        'DIRS': [BASE_DIR / "templates"],

        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# =========================
# DATABASE (Aiven / Railway)
# =========================

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
    )
}

DATABASES['default']['OPTIONS'] = {
    'ssl': {},
    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
}

import logging
logger = logging.getLogger(__name__)

logger.info(f"Usando DATABASE_URL: {os.getenv('DATABASE_URL')}")
logger.info(f"Parsed DB config: {DATABASES['default']}")

# =========================
# PASSWORD
# =========================

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


# =========================
# INTERNACIONALIZAÇÃO
# =========================

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Belem'

USE_I18N = True

USE_TZ = True


# =========================
# STATIC FILES
# =========================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# onde estão seus arquivos css/js/img
STATICFILES_DIRS = [
    BASE_DIR / "odontoPro/static"
]

# =========================
# MEDIA FILES
# =========================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Garantir pasta de upload existe (geralmente apenas local; em container pode ser volume
# persistente ou storage remoto, não recomendado em disco efêmero de produção).
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

# =========================
# DEFAULT ID
# =========================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'