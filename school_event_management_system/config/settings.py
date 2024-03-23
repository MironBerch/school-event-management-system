from os import environ
from pathlib import Path
from socket import gethostbyname_ex, gethostname

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = environ.get('SECRET_KEY')

DEBUG = int(environ.get('DEBUG'))

ALLOWED_HOSTS = ['*']

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # django 3rd party
    'debug_toolbar',
    'phonenumber_field',
    'django_bootstrap5',
    'bootstrap_datepicker_plus',
    'ckeditor',
    'ckeditor_uploader',

    # local
    'accounts.apps.AccountsConfig',
    'mailings.apps.MailingsConfig',
    'common.apps.CommonConfig',
    'events.apps.EventsConfig',
    'main.apps.MainConfig',
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'accounts/templates',
            BASE_DIR / 'events/templates',
            BASE_DIR / 'main/templates',
            BASE_DIR / 'mailings/templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'common.context_processors.school_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': environ.get('DB_NAME'),
        'USER': environ.get('DB_USER'),
        'PASSWORD': environ.get('DB_PASSWORD'),
        'HOST': 'db',
        'PORT': 5432,
    },
}


# Password validation

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


# Authentication

AUTH_USER_MODEL = 'accounts.User'


# Internationalization

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

PHONENUMBER_DEFAULT_REGION = 'RU'


# Static files (CSS, JavaScript, Images)

STATIC_URL = 'static/'

if DEBUG:
    STATICFILES_DIRS = [
        BASE_DIR / 'static',
    ]
else:
    STATIC_ROOT = BASE_DIR / 'static'

# Media files

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Login redirect urls

LOGIN_URL = 'signin'
LOGIN_REDIRECT_URL = 'events_list'

# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# SMTP

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = environ.get('DEFAULT_FROM_EMAIL')
EMAIL_HOST_USER = environ.get('EMAIL_HOST_USER')
EMAIL_HOST = environ.get('EMAIL_HOST')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_PASSWORD = environ.get('EMAIL_HOST_PASSWORD')

# Celery

CELERY_BROKER_URL = environ.get('CELERY_BROKER_URL')

# INTERNAL IPS configuration

hostname, _, ips = gethostbyname_ex(gethostname())
INTERNAL_IPS = [ip[: ip.rfind('.')] + '.1' for ip in ips] + ['127.0.0.1', '10.0.2.2']

# Ckeditor configuration

CKEDITOR_UPLOAD_PATH = 'content/ckeditor/'
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_CONFIGS = {
    'default': {
        'allowedContent': True,
        'skin': 'moono',
        'width': 'auto',
        'height': 'auto',
        'toolbar': 'Custom',
        'toolbar_Basic': [
            ['Source', '-', 'Bold', 'Italic'],
        ],
        'toolbar_Custom': [
            {
                'name': 'document',
                'items': [
                    'Source', '-', 'Save', 'NewPage', 'Preview', 'Print', '-', 'Templates',
                ],
            },
            {
                'name': 'clipboard',
                'items': [
                    'Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo',
                ],
            },
            {
                'name': 'editing',
                'items': ['Find', 'Replace', '-', 'SelectAll'],
            },
            '/',
            {
                'name': 'basicstyles',
                'items': [
                    'Bold',
                    'Italic',
                    'Underline',
                    'Strike',
                    'Subscript',
                    'Superscript',
                    '-',
                    'RemoveFormat',
                ],
            },
            {
                'name': 'paragraph',
                'items': [
                    'NumberedList',
                    'BulletedList',
                    '-',
                    'Outdent',
                    'Indent',
                    '-',
                    'Blockquote',
                    'CreateDiv',
                    '-',
                    'JustifyLeft',
                    'JustifyCenter',
                    'JustifyRight',
                    'JustifyBlock',
                    '-',
                    'BidiLtr',
                    'BidiRtl',
                ],
            },
            {
                'name': 'links', 'items': ['Link', 'Unlink', 'Anchor', 'Youtube'],
            },
            {
                'name': 'insert',
                'items': [
                    'Image',
                    'Flash',
                    'Table',
                    'HorizontalRule',
                    'Smiley',
                    'SpecialChar',
                    'PageBreak',
                    'Iframe',
                ],
            },
            '/',
            {
                'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize'],
            },
            {
                'name': 'colors', 'items': ['TextColor', 'BGColor'],
            },
            {
                'name': 'tools', 'items': ['Maximize', 'ShowBlocks', 'Preview'],
            },
        ],
        'tabSpaces': 4,
        'extraPlugins': ','.join(
            [
                'uploadimage',
                'div',
                'autolink',
                'autoembed',
                'embedsemantic',
                'autogrow',
                'widget',
                'lineutils',
                'clipboard',
                'dialog',
                'dialogui',
                'elementspath',
            ],
        ),
    },
}
