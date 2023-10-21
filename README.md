[![PyPI](https://img.shields.io/pypi/v/django-custom-admin-pages)](https://pypi.org/project/django-custom-admin-pages/)
![Python Supported](https://img.shields.io/badge/Python-_3.8,_3.9,_3.10,_3.11,_3.12-blue)
![Django Supported](https://img.shields.io/badge/Django-3.2,_4.0,_4.1,_4.2-blue)
[![Tests](https://github.com/lekjos/django-custom-admin-pages/actions/workflows/build_and_test.yml/badge.svg)](https://github.com/lekjos/django-custom-admin-pages/actions/workflows/build_and_test.yml)
[![Docs](https://readthedocs.org/projects/django-custom-admin-pages/badge/?version=latest)](https://django-custom-admin-pages.readthedocs.io/en/latest/?badge=latest)
[![CodeCov](https://codecov.io/gh/lekjos/django-custom-admin-pages/branch/master/graph/badge.svg?token=AJG2WICKXA)](https://codecov.io/gh/lekjos/django-custom-admin-pages)
![PyPI - Downloads](https://img.shields.io/pypi/dm/django-custom-admin-pages)


# Django Custom Admin Pages
A django app that lets you add standard class-based views to the django admin index and navigation. Create a view, register it like you would a ModelAdmin, and it appears in the Django Admin Nav.

![Example View](docs/source/static/example_view.png)

Check out the [full documentation](https://django-custom-admin-pages.readthedocs.io) for more in-depth information.


## Quick Start

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

## Usage

To create a new custom admin view:

1. Create a class-based view in `django_custom_admin_pages.views` which inherits from `custom_admin.views.admin_base_view.AdminBaseView`.
2. Set the view class attribute `view_name` to whatever name you want displayed in the admin index.
3. Register the view similar to how you would register a ModelAdmin using a custom admin function: `admin.site.register_view(YourView)`.
4. Use the template `django_custom_admin_pages.templates.base_custom_admin.html` as a sample for how to extend the admin templates so that your view has the admin nav.


Also see `test_proj.test_app.views.example_view.py`

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

Your template should extend `admin/base.html` or `base_custom_admin.html` template:
```html
<!-- my_template.html -->
{% extends 'base_custom_admin.html' with title="your page title" %} 
{% block content %}
<h1>Hello World</h1>
{% endblock %}
```

### Important: Custom Views Must Be Registered Before Admin URLs are Loaded

Be sure to import the files where your views are stored prior to loading your root url conf. For example:

```python
# project/urls.py
from django.contrib import admin

# importing view before url_patterns ensures it's registered!
from some_app.views import YourCustomView 

url_patterns = [
   path("admin/", admin.site.urls),
   ...
]
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
