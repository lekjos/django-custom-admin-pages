_**December 17, 2022**: Heads up, this project is new and a work-in-progress. It's not
currently in a working state, but will be shortly._

# Django Custom Admin Pages

This app is for custom admin views which aren't associated with a specific model. Add
dashboards and other custom admin views here.

_This project was adapted from some code I wrote at ConnectWise working on their SIEM
product and open-sourced with permission. Thank you very much ConnectWise for allowing
me to share this app with the Django community._

## Getting Started

#TODO: Make the app installable and post to pypi :)

- Fork the repo and/or copy the app into your django project root.
- Add `custom_admin_pages` to your installed apps

## Usage

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
## in admin_custom.views.your_radical_view.py
from django.contrib import admin
from django.views.generic import TemplateView
from admin_custom.views.admin_base_view import AdminBaseView

class YourRadicalView(AdminBaseView, TemplateView):
   view_name="My Radical View"
   route_name="your_radical_view" #Must match a path which points to this view in your URLConf
   template_name="my_template.html"
   app_label="marketplace" #if omitted defaults to "admin_custom". Must match app in settings

   # always call super() on get_context_data and use it to start your context dict.
   # the context required to render admin nav-bar is included here.
   def get_context_data(self, *args, **kwargs):
      context:dict = super().get_context_data(*args, **kwargs)
      # add your context ...
      return context

admin.site.register_view(YourRadicalView)
```

```html
<!--In your template-->
{% extends 'admin/base_site.html' %} {% load static %} {% block responsive %}
{{block.super}}
<!-- add any custom scripts and cdns here-->
{% endblock responsive %} {% block title %} Example Admin View {% endblock %} {%
block content %}
<h1>This is an example view</h1>
<p>... for exampling use only.</p>
{% endblock %}
```

### Dev ToDos:

- Get first working version
- Make installable
- Rename app folder
- Rework URLs to automatically register path
- Documentation
- Post to Pypi
- Add github actions for checks
- Add testing for other python and django versions
