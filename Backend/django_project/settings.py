import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-secret-key-for-edu-platform')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'django_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'django_project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

MYSQL_URL = os.getenv("MYSQL_URL", "").strip()

if MYSQL_URL:
    import urllib.parse
    if MYSQL_URL.startswith("sqlite"):
        db_path = MYSQL_URL.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': db_path or os.path.join(BASE_DIR, 'db.sqlite3'),
            }
        }
    else:
        # mysql+aiomysql://root:%40Sambit01@localhost:3306/edu_platform
        url = urllib.parse.urlparse(MYSQL_URL)
        username = urllib.parse.unquote(url.username or '')
        password = urllib.parse.unquote(url.password or '')
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': url.path.lstrip('/'),
                'USER': username,
                'PASSWORD': password,
                'HOST': url.hostname or 'localhost',
                'PORT': str(url.port or 3306),
                'OPTIONS': {
                    'charset': 'utf8mb4',
                }
            }
        }
else:
    # Default SQLite fallback
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'edu_platform.db'),
        }
    }

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = []

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS Settings
CORS_ALLOW_ALL_ORIGINS = True  # Enable for ease of integration
CORS_ALLOW_CREDENTIALS = True

# JWT Settings
JWT_SECRET_KEY = os.getenv("SECRET_KEY", "9825b4130d23589b27a3c3f87376c66cf01844b7067d0f1a92df55c421713e71")
JWT_REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", "b8dffc24335f2bfc668b3b993b63fd8ce65a5f48f47f6bdfdab973a492df58b1")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# DeepSeek Chatbot Settings
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_MAX_TOKENS = int(os.getenv("DEEPSEEK_MAX_TOKENS", "1000"))
DEEPSEEK_TEMPERATURE = float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7"))

# ML Settings
ML_MODELS_PATH = os.path.abspath(os.path.join(BASE_DIR, '..', 'ML', 'models'))
RETEST_COOLDOWN_DAYS = int(os.getenv("RETEST_COOLDOWN_DAYS", "30"))

# OTP Settings
OTP_EXPIRE_MINUTES = int(os.getenv("OTP_EXPIRE_MINUTES", "10"))
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "False").lower() == "true"
