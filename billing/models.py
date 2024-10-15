from django.db import models
from django.utils import timezone
from client.models import Client
from tariff.models import Tariff

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices')
    tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Invoice {self.id} - {self.client} - {self.amount}"

    def mark_as_paid(self):
        self.status = 'PAID'
        self.paid_at = timezone.now()
        self.save()

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('MPESA', 'M-Pesa'),
        ('MANUAL', 'Manual'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='payments')
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - {self.client} - {self.amount}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.process_payment()

    def process_payment(self):
        unpaid_invoices = Invoice.objects.filter(client=self.client, status='PENDING').order_by('due_date')
        remaining_amount = self.amount

        for invoice in unpaid_invoices:
            if remaining_amount >= invoice.amount:
                invoice.mark_as_paid()
                remaining_amount -= invoice.amount
                self.invoice = invoice
                self.save()

                service = self.client.pppoe_service
                if service:
                    service.activate()
                
                # Break after paying one invoice
                break
            else:
                # If payment amount is less than invoice amount, don't pay and break the loop
                break

        # If no invoice was paid, update the client's balance with the full payment amount
        if self.invoice is None:
            self.client.update_balance(self.amount)
        # If an invoice was paid and there's remaining amount, update the client's balance
        elif remaining_amount > 0:
            self.client.update_balance(remaining_amount)