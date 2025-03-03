"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 4.2.11.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta
import os
from celery.schedules import crontab
# Build paths inside the project like this: BASE_DIR / 'subdir'.
# SECURITY WARNING: keep the secret key used in production secret!
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))
SECRET_KEY = os.getenv('SECRET_KEY')
# SECRET_KEY = 'hjbfhbdfhbsayfbdhussfb'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG') == 'True'

allowed_hosts_str = os.getenv('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = allowed_hosts_str.split(',')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api',
    'corsheaders',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'rest_framework',
    'django_filters',
    'channels',
]
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
AUTHENTICATION_BACKENDS = [
    'api.login.email_backend.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

CORS_ALLOWED_ORIGINS = [
   'http://localhost:3000', 
   'http://127.0.0.1:3000', 
   'http://localhost:3007', 
   'http://localhost:3008', 
   'http://localhost:3018',
   'http://localhost:3019', 
   'http://localhost:3029', 
   'http://localhost:3009', 
   'http://127.0.0.1:3008', 
   'http://127.0.0.1:3009',  
   'http://18.142.230.37', 
   'http://localhost:3010', 
   'http://localhost:8081',
   'http://localhost:5500',
   'http://127.0.0.1:5500',
   'https://devhunt-beta.vercel.app'
]
ROOT_URLCONF = 'backend.urls'
CORS_ALLOW_HEADERS = [
    'content-type',
    'accept',
    'authorization',
    'x-csrftoken',
]

CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=300),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=15),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
}

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

ASGI_APPLICATION = 'backend.asgi.application'

WSGI_APPLICATION = 'backend.wsgi.application'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_HOSTNAME = os.getenv('REDIS_HOSTNAME')
REDIS_PORT = os.getenv('REDIS_PORT')  # Default to 6379 if not set

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [f"redis://:{REDIS_PASSWORD}@{REDIS_HOSTNAME}:{REDIS_PORT}/0"],
        },
    },
}

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),  # địa chỉ máy chủ cơ sở dữ liệu
        'PORT': os.environ.get('DB_PORT'),  # cổng cơ sở dữ liệu
    }
}
# print("#######,",os.environ.get('PGADMIN_DEFAULT_EMAIL'))
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        
    ),
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Ho_Chi_Minh'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = '/static/'  # Đường dẫn truy cập tệp tĩnh
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') 
# Default primary key field type

# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-fieldSTATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# https://docs.djangoproject.com/en/4.2/ref/
# Default primary key field typesettings/#default-auto-fi
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
EMAIL_BACKEND =  os.getenv('EMAIL_BACKEND')
EMAIL_HOST =  os.getenv('EMAIL_HOST')
EMAIL_PORT =  os.getenv('EMAIL_PORT')
EMAIL_USE_TLS =  os.getenv('EMAIL_USE_TLS')
EMAIL_HOST_USER =  os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD =  os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_TITLE = os.getenv('EMAIL_TITLE')

CELERY_BEAT_SCHEDULE = {
    'check-jobs-expiry-every-day': {
        'task': 'api.job.signals.notify_expiring_jobs',
        'schedule': crontab(hour=0, minute=0),  # Chạy vào nửa đêm mỗi ngày
        # 'schedule': 120,
    },
}
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Ho_Chi_Minh'

GOOGLE_API_TOKEN = os.getenv('GOOGLE_API_TOKEN')
