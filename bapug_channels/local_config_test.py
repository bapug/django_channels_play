# This file is exec'd from settings.py, so it has access to and can
# modify all the variables in settings.py.

# If this file is changed in development, the development server will
# have to be manually restarted because changes will not be noticed
# immediately.

import environ
from os.path import dirname, join

print("Loaded local_config_test from %s." % __file__)


env = environ.Env()
env_file = join(dirname(__file__), '.env.local')

env.read_env(env_file)
from gardenbuzz.settings.test import *

STATIC_ROOT = BASE_DIR("collectedstatic")

###################
# DEPLOY SETTINGS #
###################

INTERNAL_IPS = ('127.0.0.1',
                'localhost',
                'sharpertool.local',
                '0.0.0.0:8001',)

