from django.apps import AppConfig
import re


class DjangoCustomAdminPagesConfig(AppConfig):
    name = "django_custom_admin_pages"

    def ready(self):
        # Load default settings when the app is ready
        from . import default_settings
        from django.conf import settings

        for setting in dir(default_settings):
            if not hasattr(settings, setting):
                value = getattr(default_settings, setting)
                setattr(settings, setting, value)
