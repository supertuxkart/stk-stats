# Fill in this file and save as settings_local.py

PROJECT_NAME = 'SuperTuxKart'
PROJECT_URL = 'http://supertuxkart.net/'

# Enable JSON output view, may want to disable for performance reasons.
ENABLE_JSON = False

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

# Add the name/ip of the server that is running the stats server
# For development on localhost use this: ["localhost", "127.0.0.1"]
ALLOWED_HOSTS = ["addons.supertuxkart.net"]

# A tuple that lists people who get code error notifications.
ADMINS = (
    ('Your Name', 'you@example.com'),
)

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'stkstats',
        'USER': 'stkstats_user',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '#################################################'
