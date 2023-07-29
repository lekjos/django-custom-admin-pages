import os

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "django_custom_admin_pages")
)

DEBUG = True
DATABASES = (
    {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    },
)
INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django_custom_admin_pages",
)
TIME_ZONE = ("UTC",)
USE_TZ = (True,)


DEFAULT_CUSTOM_ADMIN_PATH = "django-custom-admin-pages/"

CUSTOM_ADMIN_DEFAULT_APP_LABEL = "django_custom_admin_pages"
