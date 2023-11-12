import contextlib
from collections import namedtuple
from collections.abc import Iterable
from typing import TYPE_CHECKING, List, Type, Union

import django
from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.apps import AdminConfig
from django.core.exceptions import ImproperlyConfigured
from django.urls import NoReverseMatch, include, path, reverse
from django.views import View

from django_custom_admin_pages.exceptions import CustomAdminImportException
from django_custom_admin_pages.urls import add_view_to_conf

if TYPE_CHECKING:
    from .views.admin_base_view import AdminBaseView


ViewRegister = namedtuple("ViewRegister", ["app_label", "view"])


def get_installed_apps():
    installed_apps = [app_config.name for app_config in apps.get_app_configs()]
    return installed_apps


def get_app_label(view: View) -> str:
    "returns app label or default app for view"
    return getattr(view, "app_label") or settings.CUSTOM_ADMIN_DEFAULT_APP_LABEL


class CustomAdminConfig(AdminConfig):
    """
    AdminConfig for CustomAdminSite. Use if you are not subclassing CustomAdminSite.
    """

    default_site = "django_custom_admin_pages.admin.CustomAdminSite"


class CustomAdminSite(admin.AdminSite):
    """
    An Admin site which can register standard django views as well as ModelAdmins.
    User admin.sites.register_view(AdminBaseView) to add a new custom admin view.
    """

    def __init__(self, *args, **kwargs):
        self._view_registry: List["AdminBaseView"] = []
        super().__init__(*args, **kwargs)

    def get_urls(self):
        """
        Adds registered view urls after adding to ModelAdmin urls.

        :return: url list
        :rtype: list[path]
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
        Register view(s) with the CustomAdminSite. The view(s) should be class-based views inheriting from AdminBaseView.

        :param view_or_iterable: iterable of views or view
        :type view_or_iterable: iterable[View] or View
        :raise admin.sites.AlreadyRegistered: If view is already registered.
        :return: None
        :rtype: None
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

            if app_label := getattr(view, "app_label", None):
                if not app_label in get_installed_apps():
                    raise ImproperlyConfigured(
                        f"Your view {view.view_name} has an invalid app_label: {app_label}. App label must be in settings.INSTALLED_APPS"
                    )

            if view in self._view_registry:
                raise admin.sites.AlreadyRegistered(
                    f"View: {str(view.view_name)} is already registered."
                )

            self._view_registry.append(view)

            add_view_to_conf(view)

    def unregister_view(self, view_or_iterable: Union[Iterable, Type]):
        """
        Unregisters view from CustomAdminSite.

        :param view_or_iterable: iterable of views or view
        :type view_or_iterable: iterable[View] or View
        :raise admin.sites.NotRegistered: If view is already not registered.
        :return: None
        :rtype: None
        """

        def _raise_not_registered(view, e=None):
            msg = f"The view {view.__name__} is not registered"
            if e:
                raise admin.sites.NotRegistered(msg) from e
            raise admin.sites.NotRegistered(msg)

        if not isinstance(view_or_iterable, Iterable):
            view_or_iterable = [view_or_iterable]

        original_length = len(self._view_registry)

        for view in view_or_iterable:
            try:
                self._view_registry.remove(view)
            except ValueError as e:
                _raise_not_registered(view, e)

            if len(self._view_registry) == original_length:
                _raise_not_registered(view)

    def _build_modelview(self, view) -> dict:
        """
        Creates dict for custom admin view for use in app_list[models]
        """
        try:
            url = reverse(f"{self.name}:{view.route_name}")
        except NoReverseMatch as e:
            message = (
                f"Cannot find CustomAdminView: {view.view_name}. This is most likely because the "
                + "root url conf was loaded before the view was registered. Try importing the view at "
                + "the top of your root url conf or placing the registration above url_patterns."
            )
            raise CustomAdminImportException(message) from e
        name = view.view_name
        return {
            "name": name,
            "object_name": name,
            "admin_url": url,
            "view_only": True,
        }

    def get_app_list(self, request, app_label=None):
        """
        Adds registered views to the app_list after generating ModelAdmin app_list.

        :param request: request
        :type request: HttpRequest
        :raise django.core.exceptions.ImproperlyConfigured: if invalid app_label on view class attribute
        :return: app_list
        :rtype: List[Dict]
        """
        super_kwargs = {"app_label": app_label} if django.VERSION >= (4, 1) else {}

        app_list = super().get_app_list(request, **super_kwargs)
        custom_admin_models = []

        for view in self._view_registry:
            found = False
            if not view().user_has_permission(request.user):
                # skip if no permission
                continue

            view_app_label = get_app_label(view).lower()

            if view_app_label == settings.CUSTOM_ADMIN_DEFAULT_APP_LABEL:
                custom_admin_models.append(self._build_modelview(view))
                # add to custom admin
                continue

            for app in app_list:
                if view_app_label == app.get("app_label", "").lower():
                    found = True
                    app_models = app["models"]
                    app_models.append(self._build_modelview(view))
                    app_models.sort(key=lambda x: x["name"])
                    # if app exists add view to models
                    break

            if not found:
                remaining_apps = set(set(get_installed_apps())).difference(
                    [x["app_label"] for x in app_list]
                )
                for app in remaining_apps:
                    if view_app_label == app:
                        found = True
                        app_config = apps.get_app_config(view_app_label)
                        app_name = app_config.verbose_name
                        # if app doesn't exist, create it and add model.
                        app_list.append(
                            {
                                "name": app_name,
                                "app_label": view_app_label,
                                "app_url": f"{reverse(f'{self.name}:{view.route_name}')}{view_app_label}/",
                                "models": [self._build_modelview(view)],
                            }
                        )

            if not found:
                raise ImproperlyConfigured(
                    f'The following custom admin view has an app_label that couldn\'t be found: "{view.__name__}". Please check that "{view_app_label}" is a valid app_label.'
                )

        if custom_admin_models:
            # add the default custom admin app if any models
            app_list += [self._build_custom_admin_app(custom_admin_models)]

        app_list = sorted(app_list, key=lambda x: x["name"])
        return app_list

    def _build_custom_admin_app(self, custom_admin_models):
        return {
            "name": "Custom Admin Pages",
            "app_label": settings.CUSTOM_ADMIN_DEFAULT_APP_LABEL,
            "app_url": f"{reverse(f'{self.name}:index')}{settings.CUSTOM_ADMIN_DEFAULT_APP_LABEL}/",
            "models": custom_admin_models,
        }
