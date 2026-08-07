from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv
load_dotenv(os.path.join(Path(__file__).resolve().parent.parent, '.env'))

# =========================
# BASE
# =========================
# =========================

OPTIONS = {
    "ssl": {"ssl-mode": "REQUIRED"}
}

BASE_DIR = Path(__file__).resolve().parent.parent

SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = False

# DEBUG - default False for production
DEBUG = os.environ.get("DEBUG", "False") == "True"

# Configurar cookies de sessão e CSRF
# Por padrão não usar 'Secure' para facilitar desenvolvimento local (HTTP).
# Em produção, defina FORCE_SECURE_COOKIES=True para forçar Secure.
FORCE_SECURE_COOKIES = os.environ.get("FORCE_SECURE_COOKIES", "False") == "True"

SESSION_COOKIE_SECURE = FORCE_SECURE_COOKIES
CSRF_COOKIE_SECURE = FORCE_SECURE_COOKIES
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# =========================
# SEGURANÇA
# =========================

from django.core.management.utils import get_random_secret_key

# Em produção, a SECRET_KEY DEVE estar em variáveis de ambiente
# Se não estiver, use uma chave fixa para evitar invalidar cookies a cada deploy
if os.getenv("SECRET_KEY"):
    SECRET_KEY = os.getenv("SECRET_KEY")
else:
    if DEBUG:
        # Local development - usar aleatória está OK
        SECRET_KEY = get_random_secret_key()
    else:
        # Produção sem SECRET_KEY definida - usar fallback fixo
        # IMPORTANTE: Adicione SECRET_KEY às variáveis de ambiente do Railway!
        SECRET_KEY = "odontopro-fallback-key-change-in-production-12345-abcde-fghij-klmno"
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            "SECRET_KEY não definida em variáveis de ambiente! "
            "Usando fallback. Cookies podem estar sendo invalidados a cada deploy. "
            "Para produção, ACRESCENTE SECRET_KEY nas variáveis do Railway!"
        )



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

    'cloudinary',
    'cloudinary_storage',

    'odontoPro',
]

CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME', '')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY', '')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET', '')

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': CLOUDINARY_CLOUD_NAME,
    'API_KEY': CLOUDINARY_API_KEY,
    'API_SECRET': CLOUDINARY_API_SECRET,
}

# Compatibility for older settings style used in Django 4.x docs.
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Cloudinary SDK receives the same environment values for runtime URL generation.
if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
    import cloudinary
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
    )


# =========================
# MIDDLEWARE
# =========================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # Servir static no Railway
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Restaurar sessão automaticamente via uid_signed
    'odontoPro.middleware.RestoreSessionMiddleware',
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
# DATABASE (Local / Aiven / Railway)
# =========================

DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
        )
    }

    engine = DATABASES['default'].get('ENGINE', '')
    if 'postgresql' in engine and not DEBUG:
        DATABASES['default']['OPTIONS'] = {
            'sslmode': 'require',
        }

elif DEBUG:
    # Desenvolvimento local sem DATABASE_URL - usar SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    raise Exception("DATABASE_URL não está definida. Configure o .env para produção.")

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

USE_TZ = False


# =========================
# STATIC FILES
# =========================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

if DEBUG:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
    STATICFILES_STORAGE_BACKEND = "django.contrib.staticfiles.storage.StaticFilesStorage"
else:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
    STATICFILES_STORAGE_BACKEND = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# onde estão seus arquivos css/js/img
STATICFILES_DIRS = [
    BASE_DIR / "odontoPro/static"
]

# Django 5: storage backend selection must be the same for the runtime storage
# API and staticfiles resolution. Default to a non-manifest static backend while
# in development, so `static` template tags don't explode on missing hashes.
if DEBUG:
    STORAGES = {
        'default': {
            'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage',
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    }
else:
    STORAGES = {
        'default': {
            'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }

# =========================
# MEDIA FILES
# =========================

# Cloudinary becomes the storage backend for ImageField/FileField uploads.
# Keeping MEDIA_URL for legacy references while Cloudinary's CDN URL resolves
# through the file storage API and django-cloudinary-storage.
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 🔧 Configurar WhiteNoise para servir também arquivos de mídia
# Isso é necessário no Railway pois ele não tem nginx/apache para servir mídia
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True


# =========================
# DEFAULT ID
# =========================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'