from django.contrib import admin
from django.urls import path

from test_proj.another_test_app.views import (
    AnotherExampleAdminView,  # required for view to register
)

urlpatterns = [path("admin/", admin.site.urls)]
