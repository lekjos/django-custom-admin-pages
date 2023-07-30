from typing import TYPE_CHECKING

from django.conf import settings
from django.urls import path
from django.utils.text import get_valid_filename, slugify

if TYPE_CHECKING:
    from .views import AdminBaseView


urlpatterns = []


def add_view_to_conf(view: "AdminBaseView"):
    global urlpatterns  # pylint: disable=global-statement

    if not view.app_label:
        view.app_label = settings.CUSTOM_ADMIN_DEFAULT_APP_LABEL
    if not view.route_path:
        view.route_path = slugify(view.view_name).lower()

    if not view.route_name:
        view.route_name = get_valid_filename(view.view_name).lower()

    urlpatterns += [
        path(
            f"{view.app_label}/{view.route_path}",
            view.as_view(),
            name=view.route_name,
        )
    ]
