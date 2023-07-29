from typing import Optional

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache

User = get_user_model()


@method_decorator(never_cache, name="dispatch")
class AdminBaseView(PermissionRequiredMixin, View):
    """
    Base class for custom admin views
    """

    view_name: Optional[str] = None  # Display name for view in admin menu
    route_name: Optional[str] = None  # Must be set to match route name in url_patterns
    permission_required = ()
    app_label: Optional[str] = None  # Must match app label in settings or be None

    def has_permission(self):
        return self.user_has_permission(self.request.user)

    @classmethod
    def user_has_permission(cls, user: User) -> bool:
        """
        Used to check permission without instance.
        """
        if not user.is_staff and user.is_active:
            return False

        if user.is_superuser:
            return True

        perms = cls.get_permission_required()
        return user.has_perms(perms)

    @classmethod
    def get_permission_required(cls):
        if cls.permission_required is None:
            raise ImproperlyConfigured(
                "{0} is missing the permission_required attribute. Define {0}.permission_required, or override "
                "{0}.get_permission_required().".format(cls.__class__.__name__)
            )
        if isinstance(cls.permission_required, str):
            perms = (cls.permission_required,)
        else:
            perms = cls.permission_required
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
