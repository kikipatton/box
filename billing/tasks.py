from celery import shared_task
from django.utils import timezone
from service.models import PPPoEService

@shared_task
def process_due_invoices():
    for service in PPPoEService.objects.filter(is_active=True, next_billing_date__lte=timezone.now()):
        service.generate_next_invoice()