from typing import TYPE_CHECKING
from django.urls import path

# Custom admin site urls go here:
from django.urls import path

if TYPE_CHECKING:
    from .views import AdminBaseView


urlpatterns = []


def add_view_to_conf(view: "AdminBaseView"):
    global urlpatterns
    urlpatterns += [
        path(
            f"{view.app_label}/{view.route_path_slug}",
            view.as_view(),
            name=view.route_name,
        )
    ]
