from django.contrib import admin
from .models import Client

# Register your models here.
default_auto_field = 'django.db.models.BigAutoField'
admin.site.register(Client)