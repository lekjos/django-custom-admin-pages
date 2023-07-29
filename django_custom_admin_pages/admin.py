#### DO NOT ADD MODELADMINS HERE ####
# To create an admin page in this app, create a view and url route
# This app is specifically for admin views that custom and not associated with modeladmin object.


import contextlib
from collections import namedtuple
from collections.abc import Iterable
from typing import Dict, List, Type, Union

from django.conf import settings
from django.contrib import admin
from django.contrib.admin.apps import AdminConfig
from django.core.exceptions import ImproperlyConfigured
from django.urls import include, path, reverse
from django.views import View

from .views.admin_base_view import AdminBaseView

ViewRegister = namedtuple("ViewRegister", ["app_label", "view"])


def get_app_label(view: View) -> str:
    "returns app label or default app for view"
    return getattr(view, "app_label") or settings.CUSTOM_ADMIN_DEFAULT_APP_LABEL


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
                        settings.DEFAULT_CUSTOM_ADMIN_PATH,
                        include("django_custom_admin_pages.urls"),
                    )
                ]
                urls = my_urls + urls

        return urls

    def register_view(
        self, view_or_iterable: Union[Iterable, "AdminBaseView"], **options
    ):
        """
        Register the given view(s) with the admin class.

        The view(s) should be class-based views inhereting from AdminBaseView.

        If the view is already registered, raise AlreadyRegistered.
        """

        if not isinstance(view_or_iterable, Iterable):
            view_or_iterable = [view_or_iterable]

        for view in view_or_iterable:
            try:
                if not issubclass(view, AdminBaseView):
                    raise ImproperlyConfigured(
                        "Only class-based views inhereting from AdminBaseView can be registered"
                    )
            except TypeError:
                raise ImproperlyConfigured(
                    "view_or_iterable must be a class_based view or iterable"
                )

            if (
                not hasattr(view, "view_name")
                or view.view_name is None
                or type(view.view_name) is not str
            ):
                raise ImproperlyConfigured(
                    "View must have name attribute set as string."
                )

            if (
                not hasattr(view, "route_name")
                or view.route_name is None
                or type(view.route_name) is not str
            ):
                raise ImproperlyConfigured(
                    "View must have route_name attribute set as string matching url_conf name."
                )

            if view in self._view_registry:
                raise admin.sites.AlreadyRegistered(
                    f"View: {str(view.view_name)} is already registered."
                )

            self._view_registry.append(view)

    def unregister_view(self, view_or_iterable: Union[Iterable, Type]):
        if not isinstance(view_or_iterable, Iterable):
            view_or_iterable = [view_or_iterable]

        original_length = len(self._view_registry)

        for view in view_or_iterable:
            search_func = lambda x: x.view_name != view.view_name and get_app_label(
                x
            ) != get_app_label(view)

            self._view_registry = list(
                filter(
                    search_func,
                    self._view_registry,
                )
            )

            if len(self._view_registry) == original_length:
                raise admin.sites.NotRegistered(
                    f"The view {view.__name__} is not registered"
                )

    def get_custom_admin_model_views(self, request=None) -> List[Dict]:
        """
        Returns list of dicts for each modelview in custom admin app.
        """
        custom_admin_views = [
            view
            for view in self._view_registry
            if get_app_label(view) == settings.DEFAULT_CUSTOM_ADMIN_APP_LABEL
        ]

        return [
            self._build_modelview(view)
            for view in custom_admin_views
            if request is None or view.user_has_permission(request.user)
        ]

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

        for view in self._view_registry:
            for app in app_list:
                if get_app_label(view).lower() == app.get("app_label", "").lower():
                    if view.user_has_permission(request.user):
                        app_models = app["models"]
                        app_models.append(self._build_modelview(view))
                        app_models.sort(key=lambda x: x["name"])
                        break

        if custom_admin_views := self.get_custom_admin_model_views(request):
            app_list += [
                {
                    "name": "Custom Admin Pages",
                    "app_label": settings.DEFAULT_CUSTOM_ADMIN_APP_LABEL,
                    "app_url": f"/{reverse('admin:index')}/{settings.DEFAULT_CUSTOM_ADMIN_PATH}/",
                    "models": custom_admin_views,
                }
            ]
            app_list = sorted(app_list, key=lambda x: x["name"])
        return app_list
