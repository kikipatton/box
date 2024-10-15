from django import forms
from .models import PPPoEService
from tariff.models import Tariff
from network.models import Router, IPPool

class PPPoEServiceForm(forms.ModelForm):
    tariff = forms.ModelChoiceField(queryset=Tariff.objects.all(), required=True)
    router = forms.ModelChoiceField(queryset=Router.objects.all(), required=True)
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(max_length=100, required=True)

    class Meta:
        model = PPPoEService
        fields = ['tariff', 'router', 'username', 'password']

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance