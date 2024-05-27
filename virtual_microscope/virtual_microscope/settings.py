"""
Django settings for virtual_microscope project.

Generated by 'django-admin startproject' using Django 2.2.11.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'q8+a9-q&i&06rel!!wygym!8-j(@3@@*#g6m#c#wlw@v&-bf7v'


MAX_UPLOAD_SIZE = 134359738368 # 32 GB en bytes

FILE_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_SIZE  # El archivo se almacenará en memoria antes de guardarlo en el sistema de archivos

DATA_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_SIZE  # Tamaño máximo de datos en memoria antes de procesar la solicitud

# Configuración de Dropzone
DROPZONE_MAX_FILE_SIZE = MAX_UPLOAD_SIZE  # 32 GB en bytes


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*'] 
# USE_X_FORWARDED_HOST = True
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_TRUSTED_ORIGINS = ["http://localhost:80"]


# Application definition
CELERY_BROKER_URL =  'redis://redis_vm:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis_vm:6379/0'

 # Cambia esto según la ubicación de tu servidor RabbitMQ
# CELERY_RESULT_BACKEND = 'django-db+postgresql://postgres:microVirtual@localhost:5432/microscopio' # Cambia esto según tu preferencia

CELERY_CACHE_BACKEND = 'django-cache'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True


CELERY_TASK_TRACK_STARTED = True
# CELERY_TASK_TIME_LIMIT = 30 * 60

# FILETRANSFERS_UPLOAD_FUNCTION = 'filetransfers.api.simple.upload'
# FILETRANSFERS_DOWNLOAD_FUNCTION = 'filetransfers.api.simple.download'

# TRANSFER_SERVER = 'nginx' 

# TRANSFER_MAPPINGS = {
#     '/mnt/shared/downloads': '/downloads',
# }

INSTALLED_APPS = [
    'microscope',
    'website_management',    
    'projects',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'channels',
    'daphne',
    'django.contrib.staticfiles',
    'django_celery_results',
]

ASGI_APPLICATION = 'virtual_microscope.asgi.application'
# python3 manage.py migrate django_celery_results

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django_transfer.middleware.TransferMiddleware',
    # 'channels.middleware.WebSocketMiddleware', 
]

# if DEBUG:
#     # ... Otras configuraciones de DEBUG

#     INSTALLED_APPS += [
#         'debug_toolbar',
#     ]

#     MIDDLEWARE += [
#         'debug_toolbar.middleware.DebugToolbarMiddleware',
#     ]

#     INTERNAL_IPS = [
#         # Agrega aquí tu dirección IP o rango de IPs
#         '127.0.0.1',
#     ]

#     DEBUG_TOOLBAR_CONFIG = {
#         'SHOW_TOOLBAR_CALLBACK': lambda request: True,
#     }

ROOT_URLCONF = 'virtual_microscope.urls'

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

MIME_TYPES = {
    'js': 'application/javascript',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'channels': {
        'handlers': ['console'],
        'level': 'DEBUG',  # O ajusta al nivel que desees
    },
}
WSGI_APPLICATION = 'virtual_microscope.wsgi.application'
# urls.static import static
# from django.core.asgi import get_asgi_application
# from channels.asgi import ProtocolTypeRouter
# from channels.routing import URLRouter
# from Projects import routing

# application = ProtocolTypeRouter({
#     'http': get_asgi_application(),
#     'websocket': URLRouter(
#         # path('ws/projects/', consumers.ChatConsumer.as_asgi()),
#         routing.websocket_urlpatterns,
#     ),
# })


# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels.layers.InMemoryChannelLayer',  # Cambia esto por tu backend preferido
#     },
# }

# FTP_HOST = 'localhost'
# FTP_USER = 'usuario_ftp'
# FTP_PASSWORD = 'contraseña_ftp'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis_vm', 6379)],
        },
    },
}


CHANNELS_LAYER = 'Project.routing.application'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'microscopio',
        'USER': 'postgres',
        'PASSWORD': 'microVirtual',
        'HOST': 'db_vm',
        'PORT': '5432',
        'OPTIONS': {
            'options': '-c timezone=UTC',
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'es-eu'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

#USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_URL = '/static/'

# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR, "static"),
#     # '/static/',
# )


STATIC_ROOT = '/app/static/'
# remove STATIC_ROOT
MEDIA_URL = '/media/'
MEDIA_ROOT = '/app/media/'