import sys
from importlib import reload

import pytest
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render
from django.test import Client
from django.urls import clear_url_caches, path, reverse
from django.urls.exceptions import NoReverseMatch
from django.views.generic import TemplateView

from ..views.admin_base_view import AdminBaseView
from . import urls

User: AbstractUser = get_user_model()

ADMIN_BASE_URL = reverse("admin:index")
ADMIN_CUSTOM_URL = f"/{ADMIN_BASE_URL}/{settings.DEFAULT_CUSTOM_ADMIN_PATH}/"


def reload_urlconf(urlconf=None):
    """
    reloads urlconf, or sepecific urls.py passed in via urlconf arg.
    """
    urlconf = settings.ROOT_URLCONF
    if urlconf in sys.modules:
        clear_url_caches()
        reload(sys.modules[urlconf])


class AnExampleView(AdminBaseView, TemplateView):
    view_name = "Test Name"
    route_name = "test-route"
    template_name = "example_view.html"


class AnotherExampleView(AdminBaseView, TemplateView):
    view_name = "Test Name"
    route_name = "test-route1"
    template_name = "example_view.html"


class NotInheretedView(TemplateView):
    view_name = "Test Name"
    route_name = "test-route"
    template_name = "example_view.html"


def not_a_class_based_view(request):
    return render(request, "example_view.html", context=dict())


class NoViewName(AdminBaseView, TemplateView):
    route_name = "test-route2"
    template_name = "example_view.html"


class NoRouteName(AdminBaseView, TemplateView):
    view_name = "Test Name"
    template_name = "example_view.html"


@pytest.fixture
def user():
    User.objects.create(
        password="JulianTheWizard", is_staff=True, is_active=True, is_superuser=True
    )


def test_register_bad_views():
    """
    Test registering a view
    """

    with pytest.raises(ImproperlyConfigured):
        admin.site.register_view(not_a_class_based_view)

    with pytest.raises(ImproperlyConfigured):
        admin.site.register_view(NoViewName)

    with pytest.raises(ImproperlyConfigured):
        admin.site.register_view(NoRouteName)

    with pytest.raises(ImproperlyConfigured):
        admin.site.register_view(NotInheretedView)


def test_register_twice():
    with pytest.raises(admin.sites.AlreadyRegistered):
        admin.site.register_view([AnExampleView, AnExampleView])
    admin.site.unregister_view(AnExampleView)


def unregister_unregistered_raises_error():
    with pytest.raises(admin.sites.NotRegistered):
        admin.site.unregister_view(AnExampleView)


def test_register_multiple():
    admin.site.register_view([AnExampleView, AnotherExampleView])
    admin.site.unregister_view([AnExampleView, AnotherExampleView])


def test_admin_index_newly_registered_view(user):
    """
    Verify that view is in admin custom views
    """

    # add route in runtime and reload urlconf

    urls.__dict__["urlpatterns"].append(
        path("test-route/", AnExampleView.as_view(), name="test-route")
    )
    reload_urlconf()
    admin.site.register_view(AnExampleView)

    c = Client()
    login_status = c.login(username=user.username, password="JulianTheWizard")
    assert login_status
    assert user.is_staff
    assert user.is_active
    assert user.is_superuser

    r = c.get(f"{ADMIN_CUSTOM_URL}/test-route/")
    assert r.status_code == 200

    admin_custom_dict: dict = list(
        filter(lambda x: x["app_label"] == "admin_custom", r.context["app_list"])
    )[0]
    test_view: dict = list(
        filter(
            lambda x: x["admin_url"] == f"/{ADMIN_CUSTOM_URL}/test-route/",
            admin_custom_dict["models"],
        )
    )[0]

    assert admin_custom_dict["app_url"] == ADMIN_CUSTOM_URL
    assert admin_custom_dict["name"] == "Custom Admin Pages"
    assert admin_custom_dict["app_label"] == settings.CUSTOM_ADMIN_DEFAULT_APP_LABEL
    assert test_view["name"] == "Test Name" == test_view["object_name"]
    assert test_view["view_only"]


def check_admin_custom_route_names():
    admin_site = admin.site
    registered_views = admin_site._view_registry

    for view in registered_views:
        try:
            reverse(view.route_name)
        except NoReverseMatch:
            view_name = getattr(view, "view_name", view.__name__)
            message = f"Custom Admin View: {view_name} is routed incorrectly. Could not find route named: \
{view.route_name}. Check that you registered a url path in admin_custom.urls and that the name matches \
<view_class>.route_name."
            pytest.fail(message)
