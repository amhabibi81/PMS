"""Local development settings -- SQLite, no Docker/Postgres required.

Usage:
  set DJANGO_SETTINGS_MODULE=config.settings_local
  python manage.py migrate
  python manage.py seed_demo
  python manage.py runserver

This file is for local viewing only. Docker uses config.settings (Postgres).
"""
import os

from .settings import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),  # noqa: F405
    }
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
