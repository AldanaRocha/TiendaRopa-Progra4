from pathlib import Path
import environ
from django.contrib.messages import constants as messages
from decouple import config
import os
import dj_database_url

# Inicializar environ y cargar .env
env = environ.Env(
    DEBUG=(bool, True),
    SECRET_KEY=(str, "dev-secret-no-usar-en-prod")
)
environ.Env.read_env() 

BASE_DIR = Path(__file__).resolve().parent.parent

# CONFIGURACIÓN PRINCIPAL ojota 
SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG",default=False)
ALLOWED_HOSTS = ["*"]



MERCADOPAGO_ACCESS_TOKEN = config('MERCADOPAGO_ACCESS_TOKEN')
MERCADOPAGO_PUBLIC_KEY = config('MERCADOPAGO_PUBLIC_KEY')


INSTALLED_APPS = [
    # Django Base
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites", # Necesaria para allauth
    'django.contrib.humanize', # Útil para formatos de números
    
    # Terceros (Identidad y UI)
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.github",
    'widget_tweaks', 
    
    # Terceros (Pagos)
    "mercadopago",

    # Apps Propias del Proyecto
    "core",
    "productos",
    "perfil",
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware',  #render
]

ROOT_URLCONF = "TiendaRopa.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Ruta corregida/simplificada para templates a nivel de proyecto
        "DIRS": [BASE_DIR / "templates"], 
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "TiendaRopa.wsgi.application"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# DATABASES = {
#     'default': dj_database_url.config(
#         default=os.environ.get('DATABASE_URL')
#     )
# }

# --- AUTENTICACIÓN Y ALLAUTH ---
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

ACCOUNT_AUTHENTICATION_METHOD = "email" 
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False 
ACCOUNT_LOGOUT_ON_GET = False 
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_SIGNUP_REDIRECT_URL = "home"
ACCOUNT_LOGOUT_REDIRECT_URL = "home"
ACCOUNT_ADAPTER = 'allauth.account.adapter.DefaultAccountAdapter' 
SOCIALACCOUNT_ADAPTER = 'allauth.socialaccount.adapter.DefaultSocialAccountAdapter'

# --- MENSAJES DE BOOTSTRAP ---
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-secondary',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# --- ARCHIVOS ESTÁTICOS Y MEDIA ---
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"] 
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --- VALIDACIÓN DE PASSWORD ---
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        }
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# --- INTERNACIONALIZACIÓN ---
LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = True

# --- CONFIGURACIÓN DE MODELOS ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Modificación 5: Seguridad en Producción
if not DEBUG:
    # 1. Fuerza el esquema HTTPS (Render)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    
    # 2. Asegura las cookies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # 3. HSTS (Mejoras de seguridad)
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True