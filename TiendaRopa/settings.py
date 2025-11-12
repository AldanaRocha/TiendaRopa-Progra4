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

# --- CONFIGURACIÓN PRINCIPAL ---
SECRET_KEY = env("SECRET_KEY")
DEBUG = os.environ.get('DEBUG', 'True') == 'True' # Mantenemos la lectura de DEBUG por OS
ALLOWED_HOSTS = ["*"]

# Lógica de Render ya estaba correcta
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
 ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
 
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

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
    "chat_ai",
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware", # Whitenoise ya estaba correcto
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
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

# --- MODIFICACIÓN CLAVE: DATABASES con Fallback para desarrollo ---
if os.environ.get('DATABASE_URL'):
    # Usar configuración de Render (PostgreSQL) si DATABASE_URL existe
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600 # Recomendado para producción
        )
    }
else:
    # Usar configuración local (SQLite) si DATABASE_URL no existe
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
# --- FIN DE LA MODIFICACIÓN ---


# --- AUTENTICACIÓN Y ALLAUTH ---
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"
# [EL RESTO DE AUTENTICACIÓN Y MENSAJES ESTÁ CORRECTO]

# --- ARCHIVOS ESTÁTICOS Y MEDIA ---
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"] 
STATIC_ROOT = BASE_DIR / "staticfiles" # STATIC_ROOT ya estaba correcto

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# [EL RESTO DE VALIDACIÓN E INTERNACIONALIZACIÓN ESTÁ CORRECTO]
# ...

# Modificación 5: Seguridad en Producción (al final, ya estaba correcto)
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