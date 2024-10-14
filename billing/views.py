from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.db.models import Sum
from .models import Invoice, Payment, Client
from .forms import InvoiceForm, PaymentForm
from .forms import InvoiceForm, ManualPaymentForm, MPesaPaymentForm

# Invoice Views
class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'billing/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 20
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Debug information
        print(f"Number of invoices: {self.get_queryset().count()}")
        for invoice in self.get_queryset()[:5]:  # Print first 5 for debugging
            print(f"Invoice ID: {invoice.id}, Client: {invoice.client}, Amount: {invoice.amount}")
        
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
@login_required
def payment_list(request):
    payments = Payment.objects.all().order_by('-payment_date')
    paginator = Paginator(payments, 20)  # Show 20 payments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'billing/payment_list.html', {'page_obj': page_obj})

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