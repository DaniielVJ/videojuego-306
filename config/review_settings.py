"""Demostración local aislada; nunca apunta a db.sqlite3 ni lee .env."""
from .test_settings import *  # noqa: F403

DEBUG = True
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / '.review' / 'db.sqlite3'}}
MEDIA_ROOT = BASE_DIR / '.review' / 'media'
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}
