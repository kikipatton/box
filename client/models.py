from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Client(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Blocked', 'Blocked')
    ]
    
    account_number = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    organization = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def update_balance(self, amount):
        self.balance += amount
        self.save()

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Account: {self.account_number})"

    class Meta:
        ordering = ['-created_at']
        
class MpesaConfig(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    environment = models.CharField(max_length=20, choices=[('sandbox', 'Sandbox'), ('production', 'Production')])
    consumer_key = models.CharField(max_length=255)
    consumer_secret = models.CharField(max_length=255)
    shortcode = models.CharField(max_length=20)
    passkey = models.CharField(max_length=255)

    def __str__(self):
        return self.name