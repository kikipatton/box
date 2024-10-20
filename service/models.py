from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from client.models import Client
from network.models import Router, IPPool
from tariff.models import Tariff
from librouteros import connect
from librouteros.login import token
import traceback
from librouteros.exceptions import TrapError
from billing.models import Invoice


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
    last_billing_date = models.DateTimeField(null=True, blank=True)
    next_billing_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk and PPPoEService.objects.filter(client=self.client).exists():
            raise ValidationError("This client already has a PPPoE service.")
        
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self.create_initial_invoice()

    def create_initial_invoice(self):
        Invoice.objects.create(
            client=self.client,
            tariff=self.tariff,
            amount=self.tariff.price,
            due_date=timezone.now() + timezone.timedelta(days=1)
        )
        self.save()

    def update_next_billing_date(self):
        self.last_billing_date = timezone.now()
        self.next_billing_date = self.last_billing_date + timezone.timedelta(days=30)
        self.save()

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
                    profile=self.tariff.name,
                )
                print(f"Raw response from add operation: {new_secret}")
                
                # Handle the response based on its type
                if isinstance(new_secret, str):
                    new_secret_id = new_secret
                elif isinstance(new_secret, dict):
                    new_secret_id = new_secret.get('ret', '')
                elif isinstance(new_secret, (list, tuple)) and len(new_secret) > 0:
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
                    # Update the related Client model's status to 'Active'
                    if hasattr(self, 'client'):
                        self.client.status = 'Active'
                        self.client.save()
                        print(f"Updated client status to Active for client: {self.client}")
                    else:
                        print("No related client found to update status")
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
        
    def deactivate_in_mikrotik(self):
        print(f"Deactivating in mikrotik for username: {self.username}")
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
                    self.mikrotik_secret_id = self.mikrotik_secret_id  # save the ID after deletion
                except TrapError as trap_error:
                    if "no such item" in str(trap_error).lower():
                        print(f"Secret with ID {self.mikrotik_secret_id} not found. It may have been deleted already.")
                    else:
                        print(f"Error deleting secret with ID {self.mikrotik_secret_id}: {str(trap_error)}")
                except Exception as delete_error:
                    print(f"Unexpected error deleting secret with ID {self.mikrotik_secret_id}: {str(delete_error)}")

            api.close()
            print("Closed connection to RouterOS")
            return True
        except Exception as e:
            print(f"Error updating/creating PPPoE service in Mikrotik: {str(e)}")
            print("Traceback:")
            print(traceback.format_exc())
            return False
        
    @classmethod
    def check_and_update_overdue_services(cls):
        current_time = timezone.now()
        print(f"Starting overdue services check at {current_time}")

        all_clients = Client.objects.select_related('pppoe_service').all()
        
        print(f"Found {all_clients.count()} total clients to check")

        updated_count = 0
        errors = []

        for client in all_clients:
            print(f"Checking client {client.pk}")
            try:
                service = client.pppoe_service
                if service and (service.next_billing_date is None or service.next_billing_date < current_time):
                    print(f"Client {client.pk} has overdue service")
                    with transaction.atomic():
                        # Update client status
                        print(f"Before status change: Client {client.pk} status is {client.status}")
                        client.status = 'Blocked'
                        client.save()
                        print(f"Updated client {client.pk} status to {client.status}")

                        # Delete service from Mikrotik
                        mikrotik_success = service.deactivate_in_mikrotik()
                        
                        if not mikrotik_success:
                            raise Exception(f"Failed to delete service from Mikrotik for client {client.pk}")

                        # Update the next_billing_date if it was null
                        if service.next_billing_date is None:
                            service.next_billing_date = current_time
                            service.save()
                            print(f"Updated null next_billing_date for service {service.id}")

                        updated_count += 1
                        print(f"Successfully blocked client {client.pk} and deleted their service from Mikrotik")
                else:
                    print(f"Client {client.id} service is not overdue or doesn't exist")

            except Exception as e:
                error_message = f"Error processing client {client.pk}: {str(e)}"
                print(error_message)
                errors.append(error_message)

        print(f"Finished processing. Updated {updated_count} clients with {len(errors)} errors")
        return updated_count, errors

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

    def activate(self):
        self.save()
        self.update_or_create_in_mikrotik()
        self.update_next_billing_date()

    def deactivate(self):
        self.save()
        self.update_or_create_in_mikrotik()

    def generate_next_invoice(self):
        if self.next_billing_date and self.next_billing_date <= timezone.now():
            Invoice.objects.create(
                client=self.client,
                tariff=self.tariff,
                amount=self.tariff.price,
                due_date=self.next_billing_date + timezone.timedelta(days=1)
            )
            self.update_next_billing_date()