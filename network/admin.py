from django.contrib import admin
from .models import Router, IPPool

# Register your models here.
admin.site.register(Router)
admin.site.register(IPPool)