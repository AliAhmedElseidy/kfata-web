import os
from .base import *
DEBUG = False
SECRET_KEY = os.environ['SECRET_KEY']
if len(SECRET_KEY) < 50:
    raise ValueError('SECRET_KEY must contain at least 50 random characters.')
if 'DATABASE_URL' not in os.environ:
    raise ValueError('Production requires PostgreSQL DATABASE_URL.')
ALLOWED_HOSTS = [x.strip() for x in os.environ.get('ALLOWED_HOSTS', 'kfata.elsaidy.org').split(',') if x.strip()]
CSRF_TRUSTED_ORIGINS = [PUBLIC_BASE_URL]
# Enable only behind the audited ingress, which must overwrite this header.
if os.environ.get('TRUST_PROXY_HTTPS', 'false').lower() == 'true':
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'true').lower() == 'true'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_CONTENT_TYPE_NOSNIFF = True
STORAGES['staticfiles'] = {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'}

SESSION_COOKIE_AGE = 8 * 60 * 60
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SAMESITE = 'Lax'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Security events contain only a fixed category and counts, without request
# headers, submitted fields, a username or full URL.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {'security': {'format': 'KFATA_SECURITY %(levelname)s %(message)s'}},
    'handlers': {'security': {'class': 'logging.StreamHandler', 'formatter': 'security'}},
    'loggers': {'kfata.security': {'handlers': ['security'], 'level': 'WARNING', 'propagate': False}},
}
