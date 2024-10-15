from django.urls import path
from . import views

urlpatterns = [
    path('invoices/', views.InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/create/', views.create_invoice, name='create_invoice'),
    path('invoices/<int:invoice_id>/delete/', views.delete_invoice, name='delete_invoice'),
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('payments/create/', views.create_payment, name='create_payment'),
    path('payments/<int:payment_id>/delete/', views.delete_payment, name='delete_payment'),
    path('clients/<int:pk>/billing-summary/', views.client_billing_summary, name='client_billing_summary'),
    path('invoices/<int:invoice_id>/mark-as-paid/', views.mark_invoice_as_paid, name='mark_invoice_as_paid'),
    path('generate-due-invoices/', views.generate_due_invoices, name='generate_due_invoices'),
]