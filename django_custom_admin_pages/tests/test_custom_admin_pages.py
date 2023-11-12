import sys
from importlib import reload

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render
from django.test import RequestFactory
from django.urls import clear_url_caches, reverse
from django.utils.text import get_valid_filename, slugify
from django.views.generic import TemplateView

import pytest

from ..exceptions import CustomAdminImportException
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


class AnExampleAppView(AdminBaseView, TemplateView):
    view_name = "Test App View"
    app_label = "test_app"
    route_name = "test_app_route"
    template_name = "base_custom_admin.html"
    permission_required = "test_app.test_perm"


class BadAppNameView(AnExampleView):
    app_label = "fake_app"


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
def superuser():
    return User.objects.create(
        username="Julian",
        password="JulianTheWizard",
        is_staff=True,
        is_active=True,
        is_superuser=True,
    )


class TestRegistration:
    """
    Test registering a view
    """

    def test_it_raises_when_not_class_based(self):
        with pytest.raises(ImproperlyConfigured):
            admin.site.register_view(not_a_class_based_view)

    def test_it_raises_when_no_view_name(self):
        with pytest.raises(ImproperlyConfigured):
            admin.site.register_view(NoViewName)

    def test_it_doesnt_raise_when_no_route_name(self):
        admin.site.register_view(NoRouteName)
        assert (
            NoRouteName.route_name == get_valid_filename(NoRouteName.view_name).lower()
        )
        assert NoRouteName.route_path == slugify(NoRouteName.view_name).lower()

    def test_it_raises_when_not_subclassed(self):
        with pytest.raises(ImproperlyConfigured):
            admin.site.register_view(NotInheretedView)

    def test_register_twice(self):
        with pytest.raises(admin.sites.AlreadyRegistered):
            admin.site.register_view([AnExampleView, AnExampleView])
        admin.site.unregister_view(AnExampleView)

    def test_unregister_unregistered_raises_error(self):
        with pytest.raises(admin.sites.NotRegistered):
            admin.site.unregister_view(AnExampleView)

    def test_register_multiple(self):
        admin.site.register_view([AnExampleView, AnotherExampleView])
        admin.site.unregister_view([AnExampleView, AnotherExampleView])

    @pytest.mark.django_db
    def test_register_late_raises(self, superuser):
        admin.site.register_view(AnExampleView)

        request_factory = RequestFactory()

        with pytest.raises(
            CustomAdminImportException,
            match="Cannot find CustomAdminView: Test Name. This is most likely because the root url conf was loaded before the view was registered. Try importing the view at the top of your root url conf or placing the registration above url_patterns.",
        ):
            request = request_factory.get(reverse("admin:index"))
            request.user = superuser
            admin.site.get_app_list(request)

        admin.site.unregister_view(AnExampleView)

    def test_register_bad_app_name(self):
        with pytest.raises(
            ImproperlyConfigured,
            match="Your view Test Name has an invalid app_label: fake_app. App label must be in settings.INSTALLED_APPS",
        ):
            admin.site.register_view(BadAppNameView)


@pytest.fixture
def view():
    admin.site.register_view(AnExampleView)
    reload_urlconf()
    yield
    admin.site.unregister_view(AnExampleView)


@pytest.fixture
def view_to_register():
    return AnExampleAppView


@pytest.fixture
def app_view(view_to_register):
    admin.site.register_view(view_to_register)
    reload_urlconf()
    yield
    admin.site.unregister_view(view_to_register)


class TestPageRendering:
    @pytest.fixture
    def super_client(self, client, superuser):
        client.force_login(superuser)
        assert superuser.is_staff
        assert superuser.is_active
        assert superuser.is_superuser
        return client

    @pytest.mark.django_db
    def test_admin_index_newly_registered_view(self, view, super_client):
        """
        Verify that view is in admin custom views
        """

        # add route in runtime and reload urlconf

        r = super_client.get(reverse("admin:test_route"))
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

        assert (
            django_custom_admin_pages_dict["app_url"] == django_custom_admin_pages_URL
        )
        assert django_custom_admin_pages_dict["name"] == "Custom Admin Pages"
        assert (
            django_custom_admin_pages_dict["app_label"]
            == settings.CUSTOM_ADMIN_DEFAULT_APP_LABEL
        )
        assert test_view["name"] == "Test Name" == test_view["object_name"]
        assert test_view["view_only"]

    @pytest.mark.django_db
    def test_admin_index_newly_registered_app_view(self, app_view, super_client):
        """
        Verify that view is in admin custom views
        """

        # add route in runtime and reload urlconf

        r = super_client.get(reverse("admin:test_app_route"))
        assert r.status_code == 200

        app_dict: dict = [
            x for x in r.context["app_list"] if x["app_label"] == "test_app"
        ][0]

        test_view: dict = [
            x
            for x in app_dict["models"]
            if x["admin_url"] == "/admin/test_app/test-app-view"
        ][0]

        assert app_dict["app_url"] == "/admin/test_app/"
        assert app_dict["name"] == "Test_App"
        assert app_dict["app_label"] == "test_app"
        assert test_view["name"] == "Test App View" == test_view["object_name"]
        assert test_view["view_only"]


class TestGetAppList:
    class TestCaseStandardRegistration:
        """test an app registered in INSTALLED_APPS with just app name"""

        @pytest.mark.django_db
        def test_get_app_list(self, superuser, app_view):
            request_factory = RequestFactory()
            request = request_factory.get(reverse("admin:index"))
            request.user = superuser

            app_list = admin.site.get_app_list(request)
            test_app = [x for x in app_list if x["name"] == "Test_App"][0]
            assert (
                len([x for x in test_app["models"] if x["name"] == "Test App View"])
                == 1
            )

    class TestCaseFullRegistration:
        """test an app registered in INSTALLED_APPS with app_name.apps.appconfig"""

        @pytest.mark.django_db
        def test_get_app_list(self, superuser):
            request_factory = RequestFactory()
            request = request_factory.get(reverse("admin:index"))
            request.user = superuser

            app_list = admin.site.get_app_list(request)
            test_app = [x for x in app_list if x["name"] == "Another_Test_App"][0]
            assert (
                len(
                    [
                        x
                        for x in test_app["models"]
                        if x["name"] == "Another Example View"
                    ]
                )
                == 1
            )


class TestPermissions:
    @pytest.fixture
    def test_app_ct(self):
        return ContentType.objects.get(app_label="test_app", model="somemodel")

    @pytest.fixture
    def permission(self, test_app_ct):
        return Permission.objects.create(
            name="Test Perm", codename="test_perm", content_type=test_app_ct
        )

    @pytest.fixture
    def active(self):
        return True

    @pytest.fixture
    def staff(self):
        return True

    @pytest.fixture
    def user(self, permission, active, staff):
        u = User.objects.create(
            username="Bill",
            password="Billspw",
            is_staff=staff,
            is_active=active,
        )
        if permission:
            u.user_permissions.add(permission)
        return u

    class TestCaseRequiredPermission:
        @pytest.mark.django_db
        def test_it_shows_if_user_has_permission(self, user, app_view):
            request_factory = RequestFactory()
            request = request_factory.get(reverse("admin:index"))
            request.user = user

            app_list = admin.site.get_app_list(request)
            test_app = [x for x in app_list if x["name"] == "Test_App"][0]
            assert (
                len([x for x in test_app["models"] if x["name"] == "Test App View"])
                == 1
            )

    class TestCaseNotRequiredPermission:
        @pytest.fixture
        def view_to_register(self):
            return AnExampleView

        @pytest.fixture
        def permission(self):
            return None

        @pytest.mark.django_db
        def test_it_shows_to_staff_with_no_permission(self, user, app_view):
            user.user_permissions.clear()
            request_factory = RequestFactory()
            request = request_factory.get(reverse("admin:index"))
            request.user = user

            app_list = admin.site.get_app_list(request)
            test_app = [x for x in app_list if x["name"] == "Custom Admin Pages"][0]
            assert len([x for x in test_app["models"] if x["name"] == "Test Name"]) == 1

    class TestCaseMissingRequiredPermission:
        @pytest.fixture
        def permission(self):
            return None

        @pytest.mark.django_db
        def test_it_doesnt_show_if_user_has_no_permission(self, user, app_view):
            user.user_permissions.clear()
            request_factory = RequestFactory()
            request = request_factory.get(reverse("admin:index"))
            request.user = user

            app_list = admin.site.get_app_list(request)
            assert len([x for x in app_list if x["name"] == "Test_App"]) == 0

    class TestCaseInactiveUser:
        @pytest.fixture
        def active(self):
            return False

        @pytest.mark.django_db
        def test_it_denies_inactive_user(self, user, app_view):
            request_factory = RequestFactory()
            request = request_factory.get(reverse("admin:index"))
            request.user = user

            app_list = admin.site.get_app_list(request)
            assert len([x for x in app_list if x["name"] == "Test_App"]) == 0

    class TestCaseNotStaff:
        @pytest.fixture
        def staff(self):
            return False

        @pytest.mark.django_db
        def test_it_denies_inactive_user(self, user, app_view):
            request_factory = RequestFactory()
            request = request_factory.get(reverse("admin:index"))
            request.user = user

            app_list = admin.site.get_app_list(request)
            assert len([x for x in app_list if x["name"] == "Test_App"]) == 0
