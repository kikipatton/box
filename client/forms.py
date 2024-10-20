from django import forms
from .models import Client, MpesaConfig

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email', 'organization', 'phone_number', 'address', 'city']
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

class MpesaConfigForm(forms.ModelForm):
    class Meta:
        model = MpesaConfig
        fields = ['name', 'environment', 'consumer_key', 'consumer_secret', 'shortcode', 'passkey']
        widgets = {
            'consumer_secret': forms.PasswordInput(),
            'passkey': forms.PasswordInput(),
        }