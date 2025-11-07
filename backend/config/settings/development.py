"""
Development settings
"""
from .base import *
import importlib.util

DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# CORS - allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Disable HTTPS redirect in development
SECURE_SSL_REDIRECT = False

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Dynamically add telegram_bot if available (for volume mounts)
# TEMPORARILY DISABLED - module not in Docker container
# def check_module_exists(module_name):
#     """Check if a module exists without importing it"""
#     try:
#         spec = importlib.util.find_spec(module_name)
#         return spec is not None
#     except (ImportError, ModuleNotFoundError, ValueError):
#         return False

# if check_module_exists('apps.telegram_bot'):
#     if 'apps.telegram_bot' not in INSTALLED_APPS:
#         INSTALLED_APPS = list(INSTALLED_APPS) + ['apps.telegram_bot']

