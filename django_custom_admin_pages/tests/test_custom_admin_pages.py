import sys
from importlib import reload

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render
from django.test import Client
from django.urls import clear_url_caches, reverse
from django.urls.exceptions import NoReverseMatch
from django.utils.text import get_valid_filename, slugify
from django.views.generic import TemplateView

import pytest

from ..views.admin_base_view import AdminBaseView

User: AbstractUser = get_user_model()

ADMIN_BASE_URL = reverse("admin:index")
django_custom_admin_pages_URL = (
    f"{ADMIN_BASE_URL}{settings.CUSTOM_ADMIN_DEFAULT_APP_LABEL}/"
)


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
    route_name = "test_route"
    template_name = "base_custom_admin.html"


class AnotherExampleView(AdminBaseView, TemplateView):
    view_name = "Test Name"
    route_name = "test_route1"
    template_name = "base_custom_admin.html"


class NotInheretedView(TemplateView):
    view_name = "Test Name"
    route_name = "test_route"
    template_name = "base_custom_admin.html"


def not_a_class_based_view(request):
    return render(request, "base_custom_admin.html", context=dict())


class NoViewName(AdminBaseView, TemplateView):
    route_name = "test_route2"
    template_name = "base_custom_admin.html"


class NoRouteName(AdminBaseView, TemplateView):
    view_name = "Test Name"
    template_name = "base_custom_admin.html"


@pytest.fixture
def user():
    return User.objects.create(
        username="Julian",
        password="JulianTheWizard",
        is_staff=True,
        is_active=True,
        is_superuser=True,
    )


class TestRegisterBadViews:
    """
    Test registering a view
    """

    def it_raises_when_not_class_based(self):
        with pytest.raises(ImproperlyConfigured):
            admin.site.register_view(not_a_class_based_view)

    def it_raises_when_no_view_name(self):
        with pytest.raises(ImproperlyConfigured):
            admin.site.register_view(NoViewName)

    def it_doesnt_raise_when_no_route_name(self):
        admin.site.register_view(NoRouteName)
        assert (
            NoRouteName.route_name == get_valid_filename(NoRouteName.view_name).lower()
        )
        assert NoRouteName.route_path == slugify(NoRouteName.view_name).lower()

    def it_raises_when_not_subclassed(self):
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


@pytest.mark.django_db
def test_admin_index_newly_registered_view(user):
    """
    Verify that view is in admin custom views
    """

    # add route in runtime and reload urlconf

    admin.site.register_view(AnExampleView)
    reload_urlconf()

    c = Client()
    c.force_login(user)
    assert user.is_staff
    assert user.is_active
    assert user.is_superuser

    r = c.get(reverse("admin:test_route"))
    assert r.status_code == 200

    django_custom_admin_pages_dict: dict = list(
        filter(
            lambda x: x["app_label"] == "django_custom_admin_pages",
            r.context["app_list"],
        )
    )[0]
    test_view: dict = list(
        filter(
            lambda x: x["admin_url"] == f"{django_custom_admin_pages_URL}test-name",
            django_custom_admin_pages_dict["models"],
        )
    )[0]

    assert django_custom_admin_pages_dict["app_url"] == django_custom_admin_pages_URL
    assert django_custom_admin_pages_dict["name"] == "Custom Admin Pages"
    assert (
        django_custom_admin_pages_dict["app_label"]
        == settings.CUSTOM_ADMIN_DEFAULT_APP_LABEL
    )
    assert test_view["name"] == "Test Name" == test_view["object_name"]
    assert test_view["view_only"]


def check_django_custom_admin_pages_route_names():
    admin_site = admin.site
    registered_views = admin_site._view_registry

    for view in registered_views:
        try:
            reverse(view.route_name)
        except NoReverseMatch:
            view_name = getattr(view, "view_name", view.__name__)
            message = f"Custom Admin View: {view_name} is routed incorrectly. Could not find route named: \
{view.route_name}. Check that you registered a url path in django_custom_admin_pages.urls and that the name matches \
<view_class>.route_name."
            pytest.fail(message)
