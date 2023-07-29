from django.conf import settings
from django.urls import path

from admin_custom import views

# Custom admin site urls go here:
urlpatterns = [
    path(
        "notification/send-system-notification",
        views.SystemNotificationSendView.as_view(),
        name="system-notification-send",
    ),
    path(
        "siem-events/runs",
        views.SiemEventJobView.as_view(),
        name="siem-event-jobs",
    ),
    path(
        "siem-events/events",
        views.SiemEventEventsView.as_view(),
        name="siem-event-events",
    ),
]

# in local development include the example view
if settings.ENV == "development":
    urlpatterns.append(
        path(r"example/", views.ExampleAdminView.as_view(), name="example_view")
    )
#
