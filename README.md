# Django Custom Admin Pages
A django app that lets you add standard class-based views to the django admin index and navigation. Create a view, register it like you would a ModelAdmin, and it appears in the Django Admin Nav.


## Installation

1. Install the app from pypi `pip install django_custom_admin_pages`
2. Remove `django.contrib.admin` from your installed apps
3. In your django settings file add the following lines to your `INSTALLED_APPS``:

```python
INSTALLED_APPS = [
   # "django.contrib.admin", #REMOVE THIS LINE
   # ...
   "django_custom_admin_pages",
   "django_custom_admin_pages.admin.CustomAdminConfig"
   # ...
]
```
4. If you've defined a custom django admin site, you can also subclass `django_custom_admin_pages.admin.CustomAdminConfig`:

```python
from django_custom_admin_pages.admin import CustomAdminConfig
class MyCustomAdminSite(CustomAdminConfig):
   pass
```

_This app is currently in beta and only tested in django 3.2 / python 3.10_


## Usage

This app is for custom admin views which aren't associated with a specific model. Add dashboards and other custom admin views here.

To create a new custom admin view:

1. Create a class-based view in `django_custom_admin_pages.views` which inherits from `custom_admin.views.admin_base_view.AdminBaseView`.
2. Set the view class attribute `view_name` to whatever name you want displayed in the admin index.
3. Register the view similar to how you would register a ModelAdmin using a custom admin function: `admin.site.register_view(YourView)`.
4. Use the template `django_custom_admin_pages.templates.base_custom_admin.html` as a sample for how to extend the admin templates so that your view has the admin nav.

5. _Optional_: Set the view class attribute `app_label` to the app you'd like the admin view to display in. This must match a label in `settings.INSTALLED_APPS`. This will default to a new app called `django_custom_admin_pages` if left unset.
6. _Optional_: Set the view class attribute `route_name` to manually override the automatically generated route_name in `urlpatterns`.


See `example_view.py` for more details. (It only routes in local dev)

_Example:_

```python
## in django_custom_admin_pages.views.your_special_view.py
from django.contrib import admin
from django.views.generic import TemplateView
from django_custom_admin_pages.views.admin_base_view import AdminBaseView

class YourCustomView(AdminBaseView, TemplateView):
   view_name="My Super Special View"
   template_name="my_template.html"
   route_name="some-custom-route-name" # if omitted defaults to snake_case of view_name
   app_label="my_app" # if omitted defaults to "django_custom_admin_pages". Must match app in settings

   # always call super() on get_context_data and use it to start your context dict.
   # the context required to render admin nav-bar is included here.
   def get_context_data(self, *args, **kwargs):
      context:dict = super().get_context_data(*args, **kwargs)
      # add your context ...
      return context

admin.site.register_view(YourCustomView)
```

Your template should extend `admin/base.html` so you don't lose the nav and admin styling:
```html
<!--In your template-->
{% extends 'admin/base_site.html' %}
{% load static %} 
{% block responsive %}
{{block.super}}
<!-- add any custom scripts and cdns here-->
{% endblock responsive %} 
{% block title %} Example Admin View {% endblock %}
{% block content %}
<h1>Hello World</h1>
{% endblock %}
```
OR you can extend the `base_custom_admin.html` template:
```html
<!-- your_template.html -->
{% extends 'base_custom_admin.html' with title="your page title" %} 
{% block content %}
<h1>Hello World</h1>
{% endblock %}
```

_Example With Generic ListView:_

```python
## in django_custom_admin_pages.views.your_special_view.py
from django.contrib import admin
from django.views.generic import ListView
from django_custom_admin_pages.views.admin_base_view import AdminBaseView

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


admin.site.register_view(YourSpecialViewWithModels)
```

```html
<!-- template_with_models.html -->
{% extends 'admin/base_site.html' %}
{% block title %} Example Admin View With Models {% endblock %}

{% block content %}
<h1>Look at all these models:</h1>

{% for object in object_list %}
<h3>{{ object.name }} | {{ object.pk }}</h3>
{% endfor %} 
{% endblock %}
```

## Configurable Settings

- `CUSTOM_ADMIN_DEFAULT_APP_LABEL`: set to override the default app_label (default: `django_custom_admin_pages`)

## Contributing

Reach out to the author if you'd like to contribute! Also free to file bug reports or feature requests via [github issues](https://github.com/lekjos/django-custom-admin-pages/issues).

### Local Development

To start the test_project:
- `cd <repo_root>`
- `poetry install --with dev`
- `python test_proj/manage.py migrate`
- `python test_proj/manage.py createsuperuser` (follow prompts)
- `python test_proj/manage.py runserver`
- Navigate too `localhost:8000/admin`, log in, and there should be one custom admin view.

To run the test suite:
- `poetry run pytest`

Prior to committing:
1. Run pylint:
   - `cd <repo_root>`
   - `poetry run pylint django_custom_admin_pages/`

2. Run black:
   - `poetry run black .`

2. Run isort:
   - `poetry run isort django_custom_admin_pages/`