"""
Development settings
"""
from .base import *

DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# CORS - allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Disable HTTPS redirect in development
SECURE_SSL_REDIRECT = False

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

