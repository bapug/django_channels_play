import environ
import os


env = environ.Env()

os.environ.setdefault('WAGTAIL_SEARCH_URLS', 'http://localhost:9290,')

from .common import *

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_SSL_REDIRECT = True
# SECURE_HSTS_SECONDS = 3600
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_HSTS_PRELOAD = True
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DJANGO_DEBUG', default=True)
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

ENABLE_DEBUG_TOOLBAR = DEBUG and env.str('ENABLE_DEBUG_TOOLBAR', default=False)

if ENABLE_DEBUG_TOOLBAR:
    MIDDLEWARE += [
        'djdev_panel.middleware.DebugMiddleware',
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

if DEBUG:
    INSTALLED_APPS += [
        'django_extensions',
        'django_nose',
    ]

if ENABLE_DEBUG_TOOLBAR:
    INSTALLED_APPS += ['debug_toolbar', ]


DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
    'SHOW_TEMPLATE_CONTEXT': True,
}

INTERNAL_IPS = ('127.0.0.1', '10.0.2.2',)

CSRF_TRUSTED_ORIGINS = ['.gardentronic.local', ]

CACHES = {
    'default': {
        **env.cache('REDIS_URL', default='dummycache://')
    }
}

