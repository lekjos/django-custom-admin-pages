import pytest

from django.test.client import Client
from django.urls import reverse

from admin_custom.views.system_notification_send_view import SystemNotificationSendView
from notification.utils import get_notification_admin_group
from tests.utilities import static_fixture, lambda_fixture


class DescribeSystemNotificationSendView:
    client = static_fixture(Client())
    url = static_fixture(reverse(f"admin:{SystemNotificationSendView.route_name}"))

    class AbstractPermsTst:
        user = lambda_fixture("non_superuser_staff")
        expected_response = static_fixture(403)

        @pytest.fixture
        def authed_client(self, client: Client, user) -> Client:
            client.force_login(user)
            return client

        def test_permission(self, authed_client, user, expected_response, url):
            res = authed_client.get(url)
            assert res.status_code == expected_response

    class ContextNoPermission(AbstractPermsTst):

        expected_response = static_fixture(403)

    class ContextWithPermission(AbstractPermsTst):
        expected_response = static_fixture(200)

        @pytest.fixture
        def group(self):
            return get_notification_admin_group()

        user = lambda_fixture(
            lambda staff_factory, group: staff_factory(
                is_staff=True,
                groups=group,
            )
        )
