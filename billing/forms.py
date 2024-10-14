from django import forms
from django.core.exceptions import ValidationError
from .models import Invoice, Payment, Client, Tariff

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['client', 'tariff', 'amount', 'due_date']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.all().order_by('account_number')
        self.fields['tariff'].queryset = Tariff.objects.all().order_by('name')

    def clean(self):
        cleaned_data = super().clean()
        client = cleaned_data.get('client')
        tariff = cleaned_data.get('tariff')
        amount = cleaned_data.get('amount')

        if tariff and amount and amount < tariff.price:
            raise ValidationError("Invoice amount cannot be less than the tariff price.")

        if client and client.pppoe_service:
            if tariff and client.pppoe_service.tariff != tariff:
                raise ValidationError("The selected tariff doesn't match the client's current service tariff.")
        
        return cleaned_data

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['client', 'amount', 'payment_method', 'transaction_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.all().order_by('account_number')

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise ValidationError("Payment amount must be greater than zero.")
        return amount

    def clean_transaction_id(self):
        transaction_id = self.cleaned_data.get('transaction_id')
        if Payment.objects.filter(transaction_id=transaction_id).exists():
            raise ValidationError("This transaction ID already exists. Please enter a unique transaction ID.")
        return transaction_id

class ManualPaymentForm(PaymentForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].initial = 'MANUAL'
        self.fields['payment_method'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['payment_method'] = 'MANUAL'
        return cleaned_data

class MPesaPaymentForm(PaymentForm):
    phone_number = forms.CharField(max_length=15, help_text="Enter the M-Pesa phone number used for payment")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].initial = 'MPESA'
        self.fields['payment_method'].widget = forms.HiddenInput()
        self.fields['transaction_id'].label = "M-Pesa Transaction ID"

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['payment_method'] = 'MPESA'
        return cleaned_data

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        # Add any specific validation for M-Pesa phone numbers here
        # For example, ensuring it starts with the correct country code
        if not phone.startswith('+254'):
            raise ValidationError("Please enter a valid Kenyan phone number starting with +254")
        return phone