from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, DetailView
from .models import Tariff
from .forms import TariffForm

class TariffListView(ListView):
    model = Tariff
    template_name = 'tariff_list.html'
    context_object_name = 'Tariffs'

class TariffDetailView(DetailView):
    model = Tariff
    template_name = 'tariff_detail.html'
    context_object_name = 'Tariff'

class TariffCreateView(CreateView):
    model = Tariff
    form_class = TariffForm
    template_name = 'tariff_create.html'
    success_url = reverse_lazy('Tariff_list')

class TariffUpdateView(UpdateView):
    model = Tariff
    form_class = TariffForm
    template_name = 'tariff_form.html'
    success_url = reverse_lazy('Tariff_list')