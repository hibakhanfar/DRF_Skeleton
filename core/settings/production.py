from .base import *

DEBUG = False
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
