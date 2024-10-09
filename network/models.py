from django.db import models
from django.urls import reverse

class Router(models.Model):
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    api_port = models.IntegerField(default=8728)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('router_detail', args=[str(self.id)])

class IPPool(models.Model):
    name = models.CharField(max_length=100, unique=True)
    router = models.ForeignKey(Router, on_delete=models.CASCADE)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} on {self.router.name}"

    def get_absolute_url(self):
        return reverse('ip_pool_detail', args=[str(self.id)])
