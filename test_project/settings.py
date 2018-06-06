import os
import platform
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = Path(BASE_DIR)

SECRET_KEY = '*d^*te&dfu^as&f*h#os8ads5ojgn#h2-+f6d=!=o!^l'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'jet',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 'djcelery',
    'django_redis',
    'rest_framework',
    'rest_framework_swagger',
    'django_filters',
    'django_extensions',
    'easy_thumbnails',
    'polymorphic',

    'nc_core',
    'nc_modules',
    'nc_workflow',
    'nc_auth',
    'nc_clients',
    'nc_notes',

    'debug_toolbar'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'test_project.urls'

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

WSGI_APPLICATION = 'wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get("REDIS_CONNECTION"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    } if "REDIS_CONNECTION" in os.environ else {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'rasa-cache',
    }
}

# Cache expired (seconds)
CACHES_DURATIONS = {
    "DEFAULT_PROPERTY": 60,
    "TOKEN": 60,
    "MODULE": 60 * 60,  # 1 hour
    "MODULE_PERMISSIONS": 60 * 2
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# User model

AUTH_USER_MODEL = 'nc_auth.User'

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = str((BASE_PATH / ".." / "static").resolve().absolute())

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_PATH / ".." / "media"
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
MEDIA_ROOT = str(MEDIA_ROOT.resolve().absolute())

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'nc_auth.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'nc_auth.permissions.TokenRequired',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    # 'PAGE_SIZE': 10,
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination'
}

SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': True,
    'SECURITY_DEFINITIONS': {
        'basic': {
            'type': 'basic'
        },
        'api_key': {
            'type': 'apiKey',
            'description': 'Token <token>',
            'name': 'Authorization',
            'in': 'header',
        }
    },
    'DOC_EXPANSION': None,
    'APIS_SORTER': 'alpha',
    'OPERATIONS_SORTER': 'alpha',
    'JSON_EDITOR': False,
}

APPEND_SLASH = True

# Set env HIDE_DEBUG_TOOLBAR=True to hide debug-toolbar
_show_dt = os.environ.get("HIDE_DEBUG_TOOLBAR", "False").capitalize() == "False"
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda *args: _show_dt,
}

# Logging
SQL_LOGGING = DEBUG and bool(int(os.environ.get("SQL_LOGGING", False)))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'debug_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'sql_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'log.sql',
            'formatter': 'sql'
        },
        'redis': {
            'level': 'ERROR',
            'class': 'nc_core.utils.RedisLogHandler'
        }
    },
    'formatters': {
        'sql': {
            '()': 'nc_core.utils.SqlParseFormatter'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['redis'],
            'level': 'ERROR'
        },
        'django.db.backends': {
            'handlers': ['debug_console', 'sql_file'] if platform.system() == "Darwin" else ['sql_file'],
            'level': 'DEBUG',
        } if SQL_LOGGING else {},
    }
}
