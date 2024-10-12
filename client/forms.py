from django import forms
from .models import Client, ClientService

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email', 'organization', 'phone_number', 'address', 'city', 'status']
        widgets = {
            'first_name': forms.TextInput(attrs={'required': True}),
            'last_name': forms.TextInput(attrs={'required': True}),
            'phone_number': forms.TextInput(attrs={'required': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['phone_number'].required = True
        
class ClientServiceForm(forms.ModelForm):
    class Meta:
        model = ClientService
        fields = ['client', 'router', 'pppoe_username', 'pppoe_password', 'pool', 'tariff']
        widgets = {
            'pppoe_password': forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})