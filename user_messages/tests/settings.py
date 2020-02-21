import os

ROOT_URLCONF = "user_messages.urls"

SECRET_KEY = " "

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend', 'guardian.backends.ObjectPermissionBackend')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'tests/templates')],
        'APP_DIRS': False,
        'OPTIONS': {
            'context_processors': [
                "user_messages.context_processors.user_messages"
            ]
        }
    },
]

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    "user_messages",
    'guardian',
    'geonode.groups',
    "taggit",
]


MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

USE_TZ = True
