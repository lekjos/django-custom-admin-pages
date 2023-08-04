import os
from pathlib import Path
import sys

import django
from django.conf import settings

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

settings_module = "django_custom_admin_pages.app_settings"

# Add the path of "top" directory to the sys.path
top_level_dir = Path(__file__).resolve().parent.parent
test_proj_dir = os.path.join(top_level_dir, "test_proj")
sys.path.append(test_proj_dir)


def boot_django():
    settings.configure(
        DEBUG=True,
        SECRET_KEY="deadbeefdeadbeefdeadbeef-deefbed",
        DATABASES=(
            {
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
                }
            }
        ),
        INSTALLED_APPS=(
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django_custom_admin_pages",
            "django_custom_admin_pages.admin.CustomAdminConfig",
            "test_app",
        ),
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
        ],
        TIME_ZONE="UTC",
        ROOT_URLCONF="django_custom_admin_pages.tests.test_urls",
        USE_TZ=True,
        DEFAULT_CUSTOM_ADMIN_PATH="django-custom-admin-pages/",
        CUSTOM_ADMIN_DEFAULT_APP_LABEL="django_custom_admin_pages",
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [os.path.join(os.path.join(BASE_DIR, "tests"), "templates")],
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.debug",
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ],
                },
            },
        ],
    )
    django.setup()


if __name__ == "__main__":
    boot_django()
