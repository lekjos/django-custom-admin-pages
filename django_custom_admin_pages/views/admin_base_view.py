from typing import TYPE_CHECKING, Optional

from django.contrib import admin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser


@method_decorator(never_cache, name="dispatch")
class AdminBaseView(PermissionRequiredMixin, View):
    """
    Base class for custom admin views
    """

    view_name: str = None  # Display name for view in admin menu
    route_name: Optional[
        str
    ] = None  # The name of the path to be created, defaults to no name
    route_path: Optional[
        str
    ] = None  # The slug for the path to be created, defaults to view name
    permission_required = ()
    app_label: Optional[str] = None  # Must match app label in settings or be None

    def has_permission(self):
        return self.user_has_permission(self.request.user)

    def user_has_permission(self, user: "AbstractBaseUser") -> bool:
        """
        Used to check permission without instance.
        """
        if not user.is_active:
            return False

        if user.is_superuser:
            return True

        if user.is_staff:
            if perms := self.get_permission_required():
                return user.has_perms(perms)
            return True

        return False

    def get_permission_required(self):
        if self.permission_required is None:
            cls_name = self.__class__.__name__
            message = f"{cls_name} is missing the permission_required attribute. Define {cls_name}.permission_required, or override {cls_name}.get_permission_required()."
            raise ImproperlyConfigured(message)
        if isinstance(self.permission_required, str):
            perms = (self.permission_required,)
        else:
            perms = self.permission_required
        return perms

    def get_context_data(self, *args, **kwargs):
        """
        adds admin site context
        """
        admin_site = admin.site
        self.request.name = admin_site.name
        context: dict = admin_site.each_context(self.request)
        if hasattr(super(), "get_context_data"):
            context.update(super().get_context_data(*args, **kwargs))
        return context
