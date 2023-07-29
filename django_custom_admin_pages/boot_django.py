import os
import django
from django.conf import settings

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

settings_module = "django_custom_admin_pages.app_settings"


def boot_django():
    settings.configure(
        DEBUG=True,
        SECRET_KEY="deadbeefdeadbeefdeadbeef-deefbed",
        ENV="development",
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
        ),
        TIME_ZONE=("UTC",),
        USE_TZ=(True,),
        DEFAULT_CUSTOM_ADMIN_PATH="django-custom-admin-pages/",
        CUSTOM_ADMIN_DEFAULT_APP_LABEL="django_custom_admin_pages",
    )
    django.setup()


if __name__ == "__main__":
    boot_django()
