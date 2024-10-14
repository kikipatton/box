from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.db.models import Sum
from .models import Invoice, Payment, Client
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from service.models import PPPoEService
from .forms import InvoiceForm, PaymentForm
from .forms import InvoiceForm


@csrf_exempt
@require_GET
def process_due_invoices_api(request):
    try:
        processed_count = 0
        for service in PPPoEService.objects.filter(is_active=True, next_billing_date__lte=timezone.now()):
            service.generate_next_invoice()
            processed_count += 1
        
        return JsonResponse({
            'status': 'success',
            'message': f'Processed {processed_count} due invoices',
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e),
        }, status=500)
        
# Invoice Views
class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'billing/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 20
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

@login_required
def create_invoice(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save()
            messages.success(request, f'Invoice for {invoice.client} created successfully.')
            return redirect('invoice_list')
    else:
        form = InvoiceForm()
    return render(request, 'billing/create_invoice.html', {'form': form})

@login_required
def delete_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.method == 'POST':
        invoice.delete()
        messages.success(request, f'Invoice {invoice_id} deleted successfully.')
        return redirect('invoice_list')
    return render(request, 'billing/delete_invoice.html', {'invoice': invoice})

# Payment Views
class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'billing/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 20
    ordering = ['-payment_date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

@login_required
def create_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save()
            messages.success(request, f'Payment of {payment.amount} for {payment.client} recorded successfully.')
            return redirect('payment_list')
    else:
        form = PaymentForm()
    return render(request, 'billing/create_payment.html', {'form': form})

@login_required
def delete_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    if request.method == 'POST':
        client = payment.client
        client.update_balance(-payment.amount)  # Reverse the payment
        payment.delete()
        messages.success(request, f'Payment {payment_id} deleted and client balance updated.')
        return redirect('payment_list')
    return render(request, 'billing/delete_payment.html', {'payment': payment})

# Additional useful views

@login_required
def client_billing_summary(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    invoices = Invoice.objects.filter(client=client).order_by('-created_at')
    payments = Payment.objects.filter(client=client).order_by('-payment_date')
    
    total_invoiced = invoices.aggregate(Sum('amount'))['amount__sum'] or 0
    total_paid = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'client': client,
        'invoices': invoices[:10],  # Show last 10 invoices
        'payments': payments[:10],  # Show last 10 payments
        'total_invoiced': total_invoiced,
        'total_paid': total_paid,
        'balance': client.balance
    }
    return render(request, 'billing/client_billing_summary.html', context)

@login_required
def mark_invoice_as_paid(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.method == 'POST':
        if invoice.client.balance >= invoice.amount:
            invoice.mark_as_paid()
            invoice.client.update_balance(-invoice.amount)
            messages.success(request, f'Invoice {invoice_id} marked as paid.')
        else:
            messages.error(request, f'Insufficient balance to mark invoice {invoice_id} as paid.')
        return redirect('invoice_list')
    return render(request, 'billing/mark_invoice_as_paid.html', {'invoice': invoice})