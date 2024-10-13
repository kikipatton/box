from django.db import models
from django.core.exceptions import ValidationError
from client.models import Client
from network.models import Router, IPPool
from tariff.models import Tariff
from librouteros import connect
from librouteros.login import token
import traceback
from librouteros.exceptions import TrapError

class PPPoEService(models.Model):
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='pppoe_service')
    tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL, null=True)
    router = models.ForeignKey(Router, on_delete=models.SET_NULL, null=True)
    ip_pool = models.ForeignKey(IPPool, on_delete=models.SET_NULL, null=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    mikrotik_secret_id = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk and PPPoEService.objects.filter(client=self.client).exists():
            raise ValidationError("This client already has a PPPoE service.")
        super().save(*args, **kwargs)

    def update_or_create_in_mikrotik(self):
        print(f"Updating or creating in Mikrotik for username: {self.username}")
        try:
            api = connect(
                host=self.router.ip_address,
                username=self.router.username,
                password=self.router.password,
                port=self.router.api_port,
            )
            print("Successfully connected to RouterOS")
            
            ppp_secret = api.path('ppp', 'secret')
            
            # Delete existing secret if we have an ID
            if self.mikrotik_secret_id:
                print(f"Attempting to delete existing secret with ID: {self.mikrotik_secret_id}")
                try:
                    ppp_secret.remove(self.mikrotik_secret_id)
                    print(f"Deleted existing secret with ID: {self.mikrotik_secret_id}")
                    self.mikrotik_secret_id = None  # Clear the ID after deletion
                except TrapError as trap_error:
                    if "no such item" in str(trap_error).lower():
                        print(f"Secret with ID {self.mikrotik_secret_id} not found. It may have been deleted already.")
                    else:
                        print(f"Error deleting secret with ID {self.mikrotik_secret_id}: {str(trap_error)}")
                except Exception as delete_error:
                    print(f"Unexpected error deleting secret with ID {self.mikrotik_secret_id}: {str(delete_error)}")

            # Create new secret
            print(f"Creating new secret for username: {self.username}")
            try:
                new_secret = ppp_secret.add(
                    name=self.username,
                    password=self.password,
                    service='pppoe',
                    profile=self.tariff.name
                )
                print(f"Raw response from add operation: {new_secret}")
                
                # Handle the response based on its type
                if isinstance(new_secret, str):
                    # If it's a string, it might be the ID directly
                    new_secret_id = new_secret
                elif isinstance(new_secret, dict):
                    # If it's a dictionary, try to get the 'ret' key
                    new_secret_id = new_secret.get('ret', '')
                elif isinstance(new_secret, (list, tuple)) and len(new_secret) > 0:
                    # If it's a list or tuple, take the first item
                    new_secret_id = new_secret[0]
                else:
                    raise ValueError(f"Unexpected response format: {type(new_secret)}")
                
                if new_secret_id:
                    print(f"Successfully created new PPPoE secret with ID: {new_secret_id}")
                    self.mikrotik_secret_id = new_secret_id
                    self.save()
                else:
                    raise ValueError("Failed to extract new secret ID from the response")
                
            except TrapError as trap_error:
                print(f"Error creating new secret: {str(trap_error)}")
                raise
            except ValueError as value_error:
                print(f"Error processing new secret response: {str(value_error)}")
                raise

            # Verify that the secret was actually created using the returned ID
            try:
                verified_secret = ppp_secret.select('name', '.id').where('.id', self.mikrotik_secret_id)
                if list(verified_secret):
                    print(f"Verified: PPPoE secret exists with ID: {self.mikrotik_secret_id}")
                else:
                    print(f"Verification failed: PPPoE secret not found with ID: {self.mikrotik_secret_id}")
                    return False
            except Exception as verify_error:
                print(f"Error verifying new secret: {str(verify_error)}")
                return False

            api.close()
            print("Closed connection to RouterOS")
            return True
        except Exception as e:
            print(f"Error updating/creating PPPoE service in Mikrotik: {str(e)}")
            print("Traceback:")
            print(traceback.format_exc())
            return False

    def delete_from_mikrotik(self):
        print("Deleting from Mikrotik...")
        try:
            api = connect(
                host=self.router.ip_address,
                username=self.router.username,
                password=self.router.password,
                port=self.router.api_port,
            )
            print("Successfully connected to RouterOS")
            
            ppp_secret = api.path('ppp', 'secret')
            
            # Find the secret with matching username
            for secret in ppp_secret:
                if secret['name'] == self.username:
                    # Remove the secret
                    ppp_secret.remove(secret['.id'])
                    print(f"Successfully removed PPPoE secret for username: {self.username}")
                    break
            else:
                print(f"No PPPoE secret found for username: {self.username}")

            api.close()
            return True
        except Exception as e:
            print(f"Error deleting PPPoE service from Mikrotik: {str(e)}")
            print("Traceback:")
            print(traceback.format_exc())
            return False

    def delete(self, *args, **kwargs):
        try:
            mikrotik_success = self.delete_from_mikrotik()
            if not mikrotik_success:
                raise ValidationError("Failed to delete PPPoE service from Mikrotik router")
            super().delete(*args, **kwargs)
        except Exception as e:
            print(f"Error deleting PPPoEService: {str(e)}")
            print("Traceback:")
            print(traceback.format_exc())
            raise

    def __str__(self):
        return f"{self.client} - {self.username}"