from .base import *
DEBUG = True
SECRET_KEY = 'development-only-never-use-in-production'
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

