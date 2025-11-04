"""
Local development settings without Docker dependencies
Uses SQLite instead of PostgreSQL and disables Celery
"""
from .development import *

# Use SQLite for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Disable Celery for local development
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Disable Channels - use regular HTTP instead of WebSocket
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

print("Running in LOCAL mode (SQLite, no Redis/PostgreSQL required)")

