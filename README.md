# Admin-Custom App
This app is in the process from being ported from an existing project into an installable app.

# Usage

This app is for custom admin views which aren't associated with a specific model. Add dashboards and other custom admin views here.

To create a new custom admin view:

1. Create a class-based view in `admin_custom.views` which inherets from `custom_admin.views.admin_base_view.AdminBaseView`.
2. Create a route in `admin_custom.urls`, be sure to name it.
3. Set the view class attribute `view_name` to whatever name you want displayed in the admin index.
4. Set the view class attribute `route_name` equal to the route name in step 2.
5. Set the view class attribute `app_label` to the app you'd like the admin view to display in. This must match the label in settings. Alternatively remove the attribute to make the view appear in `admin_custom` app.
6. Register the view like you would register a model using a custom admin funciton: `admin.site.register_view(YourView)`.
7. Use the template `admin_custom.templates.example_view.html` as a sample for how to extend the admin templates so that your view has the admin nav.

See `example_view.py` for more details. (It only routes in local dev)

_Example:_

```python
## in admin_custom.views.your_special_view.py
from django.contrib import admin
from django.views.generic import TemplateView
from admin_custom.views.admin_base_view import AdminBaseView

class YourSpecialView(AdminBaseView, TemplateView):
   view_name="My Super Special View"
   route_name="your_special_view"
   template_name="my_template.html"
   app_label="marketplace" #if omitted defaults to "admin_custom". Must match app in settings

   # always call super() on get_context_data and use it to start your context dict.
   # the context required to render admin nav-bar is included here.
   def get_context_data(self, *args, **kwargs):
      context:dict = super().get_context_data(*args, **kwargs)
      # add your context ...
      return context

admin.site.register_view(YourViewClass)
```

```html
<!--In your template-->
{% extends 'admin/base_site.html' %} {% load static %} {% block responsive %}
{{block.super}}
<!-- add any custom scripts and cdns here-->
{% endblock responsive %} {% block title %} Example Admin View {% endblock %}
{% block content %}
<h1>This is an example view</h1>
<p>... for exampling use only.</p>
{% endblock %}
```

_Example Incorporating Models:_

```python
## in admin_custom.views.your_special_view.py
from django.contrib import admin
from django.views.generic import ListView
from admin_custom.views.admin_base_view import AdminBaseView

class YourSpecialViewWithModels(AdminBaseView, ListView):
   # Using the Team Model as an example
   model: Team = Team
   ordering = ['pk']
   paginate_by = 5
   context_object_name = "team"
   view_name="My Super Special View With Models"
   route_name="your_special_view_with_models"
   template_name="my_template_with_models.html"
   app_label="an_existing_app_in_your_project"

   # always call super() on get_context_data and use it to start your context dict.
   # the context required to render admin nav-bar is included here.
   def get_context_data(self, *args, **kwargs):
      context:dict = super().get_context_data(*args, **kwargs)
      # add your context ...
      return context

admin.site.register_view(YourViewClass)
```

```html
<!--In your template-->
{% extends 'admin/base_site.html' %} {% load static %} {% block responsive %}
{{block.super}}
<!-- add additional scripts here -->
{% endblock responsive %} {% block title %} Example Admin View With Models {%
endblock %} {% block content %}
<h1>This is an custom view with models</h1>
<p>... for exampling use only.</p>
{% for object in object_list %}
<h3>{{ object.name }} | {{ object.pk }}</h3>
{% endfor %} {% endblock %}
```
