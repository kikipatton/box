from django import forms
from .models import Router, IPPool
from librouteros import connect
from librouteros.exceptions import LibRouterosError

class RouterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = Router
        fields = ['name', 'ip_address', 'username', 'password', 'api_port', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        if self.instance.pk:
            self.fields['password'].help_text = "Leave empty to keep the current password."

    def clean(self):
        cleaned_data = super().clean()
        ip_address = cleaned_data.get('ip_address')
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        api_port = cleaned_data.get('api_port')

        if not self.instance.pk or (ip_address and username and password and api_port):
            try:
                # If it's a new router or if all connection details are provided, attempt to connect
                connect_password = password if password else self.instance.password
                connect(username=username, password=connect_password, host=ip_address, port=api_port)
            except LibRouterosError as e:
                raise forms.ValidationError(f"Failed to connect to the router: {str(e)}")
            except Exception as e:
                raise forms.ValidationError(f"An unexpected error occurred: {str(e)}")

        return cleaned_data

    def save(self, commit=True):
        router = super().save(commit=False)
        if self.cleaned_data['password']:
            router.password = self.cleaned_data['password']
        if commit:
            router.save()
        return router

class IPPoolForm(forms.ModelForm):
    class Meta:
        model = IPPool
        fields = ['name', 'description']