# This file is exec'd from settings.py, so it has access to and can
# modify all the variables in settings.py.

# If this file is changed in development, the development server will
# have to be manually restarted because changes will not be noticed
# immediately.

import environ
from os.path import dirname, join
import sys

print("Loaded local_config from %s." % __file__)

env_file = join(dirname(__file__), '.env.local')

env = environ.Env()

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    print("Running test mode..")
    env.read_env(env_file)
    from bapug_channels.settings.test import *
else:
    print("Bootstrap from local.config")
    if env.bool('DJANGO_DOCKER', False):
        env.read_env('.env.local.docker')
    else:
        env.read_env(env_file)

    from bapug_channels.settings.dev import *

STATIC_ROOT = BASE_DIR("collectedstatic")

###################
# DEPLOY SETTINGS #
###################

INTERNAL_IPS = ('127.0.0.1',
                'localhost',
                'channels.local',
                '0.0.0.0:8003',)

STATICFILES_DIRS += [
#    BASE_DIR('src/django-comments-xtd/django_comments_xtd/static'),
]

