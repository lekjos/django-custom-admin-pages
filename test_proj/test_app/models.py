from django.db import models


# Create your models here.
class SomeModel(models.Model):
    some_field = models.BooleanField(default=False)
