from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Client(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    
    account_number = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    organization = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Inactive')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Account: {self.account_number})"

    class Meta:
        ordering = ['-created_at']
        
class ClientService(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    router = models.ForeignKey('network.Router', on_delete=models.CASCADE)
    pppoe_username = models.CharField(max_length=50, unique=True)
    pppoe_password = models.CharField(max_length=50)
    pool = models.ForeignKey('network.IPPool', on_delete=models.SET_NULL, null=True)
    tariff = models.ForeignKey('tariff.Tariff', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client} - {self.pppoe_username}"