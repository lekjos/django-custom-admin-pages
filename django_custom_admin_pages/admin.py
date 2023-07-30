import contextlib
from collections import namedtuple
from collections.abc import Iterable
from typing import TYPE_CHECKING, List, Type, Union

from django.conf import settings
from django.contrib import admin
from django.contrib.admin.apps import AdminConfig
from django.core.exceptions import ImproperlyConfigured
from django.urls import include, path, reverse
from django.views import View

from django_custom_admin_pages.urls import add_view_to_conf

if TYPE_CHECKING:
    from .views.admin_base_view import AdminBaseView


ViewRegister = namedtuple("ViewRegister", ["app_label", "view"])


def get_app_label(view: View) -> str:
    "returns app label or default app for view"
    return getattr(view, "app_label") or settings.CUSTOM_ADMIN_DEFAULT_APP_LABEL


class CustomAdminConfig(AdminConfig):
    default_site = "django_custom_admin_pages.admin.CustomAdminSite"


class CustomAdminSite(admin.AdminSite):
    def __init__(self, *args, **kwargs):
        self._view_registry: List["AdminBaseView"] = []
        super().__init__(*args, **kwargs)

    def get_urls(self):
        """
        Adds urls.py to perch-admin routes if url patterns in it
        """
        urls = super().get_urls()
        with contextlib.suppress(ImportError):
            from .urls import urlpatterns

            if len(urlpatterns) > 0:
                my_urls = [
                    path(
                        "",
                        include("django_custom_admin_pages.urls"),
                    )
                ]
                urls = my_urls + urls

        return urls

    def register_view(self, view_or_iterable: Union[Iterable, "AdminBaseView"]):
        """
        Register the given view(s) with the admin class.

        The view(s) should be class-based views inheriting from AdminBaseView.

        If the view is already registered, raise AlreadyRegistered.
        """
        from .views.admin_base_view import AdminBaseView

        if not isinstance(view_or_iterable, Iterable):
            view_or_iterable = [view_or_iterable]

        for view in view_or_iterable:
            try:
                if not issubclass(view, AdminBaseView):
                    raise ImproperlyConfigured(
                        "Only class-based views inheriting from AdminBaseView can be registered"
                    )
            except TypeError as e:
                raise ImproperlyConfigured(
                    "view_or_iterable must be a class_based view or iterable"
                ) from e

            if (
                not hasattr(view, "view_name")
                or view.view_name is None
                or not isinstance(view.view_name, str)
            ):
                raise ImproperlyConfigured(
                    "View must have name attribute set as string."
                )

            if view in self._view_registry:
                raise admin.sites.AlreadyRegistered(
                    f"View: {str(view.view_name)} is already registered."
                )

            self._view_registry.append(view)

            add_view_to_conf(view)

    def unregister_view(self, view_or_iterable: Union[Iterable, Type]):
        if not isinstance(view_or_iterable, Iterable):
            view_or_iterable = [view_or_iterable]

        original_length = len(self._view_registry)

        for view in view_or_iterable:
            self._view_registry.remove(view)

            if len(self._view_registry) == original_length:
                raise admin.sites.NotRegistered(
                    f"The view {view.__name__} is not registered"
                )

    def _build_modelview(self, view) -> dict:
        """
        Creates dict for custom admin view for use in app_list[models]
        """
        url = reverse(f"{self.name}:{view.route_name}")
        name = view.view_name
        return {
            "name": name,
            "object_name": name,
            "admin_url": url,
            "view_only": True,
        }

    def get_app_list(self, request):
        """
        Adds registered apps to perch-admin app list used for nav.
        """
        app_list = super().get_app_list(request)
        custom_admin_models = []

        for view in self._view_registry:
            found = False
            view_app_label = get_app_label(view).lower()
            if view_app_label == settings.CUSTOM_ADMIN_DEFAULT_APP_LABEL:
                custom_admin_models.append(self._build_modelview(view))
                continue

            for app in app_list:
                if view_app_label == app.get("app_label", "").lower():
                    if view.user_has_permission(request.user):
                        app_models = app["models"]
                        app_models.append(self._build_modelview(view))
                        app_models.sort(key=lambda x: x["name"])
                        found = True
                        break
            if not found:
                raise ImproperlyConfigured(
                    f'The following custom admin view has an app_label that couldn\'t be found: "{view.__name__}". Please check that "{view_app_label}" is a valid app_label.'
                )

        if custom_admin_models:
            app_list += [
                {
                    "name": "Custom Admin Pages",
                    "app_label": settings.CUSTOM_ADMIN_DEFAULT_APP_LABEL,
                    "app_url": f"{reverse('admin:index')}{settings.CUSTOM_ADMIN_DEFAULT_APP_LABEL}/",
                    "models": custom_admin_models,
                }
            ]
            app_list = sorted(app_list, key=lambda x: x["name"])
        return app_list
