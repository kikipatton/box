from django.db import models
from django.urls import reverse

class Router(models.Model):
    name = models.CharField(max_length=100, unique=True)
    ip_address = models.GenericIPAddressField()
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    api_port = models.IntegerField(default=8728)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('router_detail', kwargs={'pk': self.pk})

class IPPool(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('networklist', args=[str(self.id)])
