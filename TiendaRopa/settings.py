from pathlib import Path
import environ
from django.contrib.messages import constants as messages
from decouple import config
import os


# Inicializar environ y cargar .env
env = environ.Env(
    DEBUG=(bool, True),
    SECRET_KEY=(str, "dev-secret-no-usar-en-prod")
)
environ.Env.read_env() 

BASE_DIR = Path(__file__).resolve().parent.parent

# CONFIGURACIÓN PRINCIPAL 
SECRET_KEY = env("SECRET_KEY")
#DEBUG = env.bool("DEBUG",default=False)
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = ["*"]
GEMINI_API_KEY = config('GEMINI_API_KEY', default=None)



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
    "django.contrib.sites", 
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
    "chat_ai", 
    "presupuestos",
]

# SITE_ID dinámico según entorno
if DEBUG or os.getenv("DJANGO_DEVELOPMENT", "True") == "True":
    SITE_ID = 2  # localhost:8000 en desarrollo
else:
    SITE_ID = 1  # tiendaropa-progra4.onrender.com en producción

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





# --- AUTENTICACIÓN Y ALLAUTH (ACTUALIZADO) ---
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

# ⚠️ CONFIGURACIÓN ACTUALIZADA - Se reemplazaron las settings deprecated
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = []

# Configuraciones adicionales de allauth
ACCOUNT_EMAIL_VERIFICATION = "none" 
ACCOUNT_LOGOUT_ON_GET = False 
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_SIGNUP_REDIRECT_URL = "home"
ACCOUNT_LOGOUT_REDIRECT_URL = "home"
ACCOUNT_ADAPTER = 'allauth.account.adapter.DefaultAccountAdapter' 
SOCIALACCOUNT_ADAPTER = 'allauth.socialaccount.adapter.DefaultSocialAccountAdapter'

# --- CONFIGURACIÓN PARA EVITAR LA PANTALLA "Confirmación de Conexión" ---
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "none"

# Que Google te loguee automáticamente al volver del OAuth
SOCIALACCOUNT_LOGIN_ON_GET = True

# Opcional pero recomendado para mejorar la compatibilidad
SOCIALACCOUNT_QUERY_EMAIL = True

# Config del proveedor Google (evita confirmaciones extra)
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {
            "prompt": "select_account"
        }, "OAUTH_PKCE_ENABLED": True,
    },
    "github": {
        "SCOPE": ["read:user", "user:email"],
    },
}


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
#STATICFILES_DIRS = [BASE_DIR / "static"] 
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

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
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# 🔧 Desactivar SSL forzado en entorno local
if DEBUG or os.getenv("DJANGO_DEVELOPMENT", "True") == "True":
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False