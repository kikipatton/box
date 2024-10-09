from django import forms
from .models import Router, IPPool

class RouterForm(forms.ModelForm):
    class Meta:
        model = Router
        fields = ['name', 'ip_address', 'username', 'password', 'api_port', 'is_active']
        widgets = {
            'password': forms.PasswordInput(),
        }

class IPPoolForm(forms.ModelForm):
    class Meta:
        model = IPPool
        fields = ['name', 'router', 'description']