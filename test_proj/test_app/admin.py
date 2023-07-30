from django.contrib import admin
from .models import SomeModel

# Register your models here.


@admin.register(SomeModel)
class SomeModelAdmin(admin.ModelAdmin):
    pass
