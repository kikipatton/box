from django import forms
from .models import Tariff

class TariffForm(forms.ModelForm):
    class Meta:
        model = Tariff
        fields = ['name', 'price', 'description']