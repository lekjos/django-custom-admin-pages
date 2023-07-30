from django.contrib import admin
from django.views.generic import TemplateView

from django_custom_admin_pages.views.admin_base_view import AdminBaseView


class ExampleAdminView(AdminBaseView, TemplateView):
    """
    Example view to demonstrate custom admin views.

    Dont forget to add a route in custom_admin.urls
    """

    view_name = "Example View"
    route_name = "example_view"
    template_name = "example_view.html"
    app_label = "django_custom_admin_pages"  # if you want your view to be in another app, use the label from settings.

    # always call super() on get_context_data and use it to start your context dict.
    # the context required to render admin nav-bar is included here.
    def get_context_data(self, *args, **kwargs):
        context: dict = super().get_context_data(*args, **kwargs)
        context["title"] = "Example View"
        return context


# register the view after you create it
admin.site.register_view(ExampleAdminView)
