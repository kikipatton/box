from django import forms
from .models import Router, IPPool
from librouteros import connect
from librouteros.exceptions import LibRouterosError

class RouterForm(forms.ModelForm):
    class Meta:
        model = Router
        fields = ['name', 'ip_address', 'username', 'password', 'api_port', 'is_active']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        ip_address = cleaned_data.get('ip_address')
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        api_port = cleaned_data.get('api_port')

        if ip_address and username and password and api_port:
            try:
                # Attempt to connect to the router
                connect(username=username, password=password, host=ip_address, port=api_port)
            except LibRouterosError as e:
                raise forms.ValidationError(f"Failed to connect to the router: {str(e)}")
            except Exception as e:
                raise forms.ValidationError(f"An unexpected error occurred: {str(e)}")

        return cleaned_data

class IPPoolForm(forms.ModelForm):
    class Meta:
        model = IPPool
        fields = ['name', 'description']