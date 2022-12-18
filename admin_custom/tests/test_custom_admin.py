import pytest
import sys
from importlib import reload

from django.contrib.auth.models import User
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render
from django.test import Client
from django.urls import path, clear_url_caches, reverse
from django.views.generic import TemplateView
import admin_custom.urls as urls
from admin_custom.views.admin_base_view import AdminBaseView


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
    u = User(
        password="JulianTheWizard",
        is_staff=True,
        is_active=True,
        is_superuser=True,
    )
    u.save()
    return u


@pytest.fixture
def url():
    return reverse("admin:test-route")


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


def test_admin_index_newly_registered_view(user, url):
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

    r = c.get()
    assert r.status_code == 200

    admin_custom_dict: dict = list(
        filter(lambda x: x["app_label"] == "admin_custom", r.context["app_list"])
    )[0]
    test_view: dict = list(
        filter(
            lambda x: x["admin_url"] == "/django-admin/admin-custom/test-route/",
            admin_custom_dict["models"],
        )
    )[0]

    assert admin_custom_dict["app_url"] == "/django-admin/admin-custom/"
    assert admin_custom_dict["name"] == "Custom Admin Pages"
    assert admin_custom_dict["app_label"] == "admin_custom"
    assert test_view["name"] == "Test Name" == test_view["object_name"]
    assert test_view["view_only"]
