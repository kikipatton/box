from django.db import models
from django.core.exceptions import ValidationError
from client.models import Client
from network.models import Router, IPPool
from tariff.models import Tariff
from librouteros import connect
from librouteros.login import token
import traceback

class PPPoEService(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='pppoe_services')
    tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL, null=True)
    router = models.ForeignKey(Router, on_delete=models.SET_NULL, null=True)
    ip_pool = models.ForeignKey(IPPool, on_delete=models.SET_NULL, null=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def add_to_mikrotik(self):
        print("Adding to Mikrotik...")
        try:
            print(f"Router IP: {self.router.ip_address}")
            print(f"Router Username: {self.router.username}")
            print(f"Router API Port: {self.router.api_port}")
            print(f"Router Password: {self.router.password}")
            
            api = connect(
                host=self.router.ip_address,
                username=self.router.username,
                password=self.router.password,
                port=self.router.api_port,
            )
            print("Successfully connected to RouterOS")
            
            ppp_secret = api.path('ppp', 'secret')
            new_secret = ppp_secret.add(
                name=self.username,
                password=self.password,
                service='pppoe',
                profile=self.tariff.name
            )
            print(f"Successfully added PPPoE secret: {new_secret}")
            api.close()
            return True
        except Exception as e:
            print(f"Error adding PPPoE service to Mikrotik: {str(e)}")
            print("Traceback:")
            print(traceback.format_exc())
            return False

    def save(self, *args, **kwargs):
        print("Saving PPPoEService...")
        print(f"Client: {self.client}")
        print(f"Tariff: {self.tariff}")
        print(f"Router: {self.router}")
        print(f"IP Pool: {self.ip_pool}")
        print(f"Username: {self.username}")
        is_new = self.pk is None
        try:
            super().save(*args, **kwargs)
            print("PPPoEService saved successfully")
            if is_new:
                mikrotik_success = self.add_to_mikrotik()
                if not mikrotik_success:
                    raise ValidationError("Failed to add PPPoE service to Mikrotik router")
        except Exception as e:
            print(f"Error saving PPPoEService: {str(e)}")
            print("Traceback:")
            print(traceback.format_exc())
            raise

    def __str__(self):
        return f"{self.client} - {self.username}"