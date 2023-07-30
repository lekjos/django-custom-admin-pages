from django.apps import AppConfig


class DjangoCustomAdminPagesConfig(AppConfig):
    name = "django_custom_admin_pages"

    def ready(self):
        # Load default settings when the app is ready
        from django.conf import settings

        from . import default_settings

        for setting in dir(default_settings):
            if not hasattr(settings, setting):
                value = getattr(default_settings, setting)
                setattr(settings, setting, value)
