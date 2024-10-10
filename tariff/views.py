from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Tariff
from .forms import TariffForm

class TariffListView(ListView):
    model = Tariff
    template_name = 'tariff/tariff_list.html'
    context_object_name = 'tariffs'

class TariffDetailView(DetailView):
    model = Tariff
    template_name = 'tarrif/tariff_detail.html'
    context_object_name = 'tariff'

class TariffCreateView(CreateView):
    model = Tariff
    form_class = TariffForm
    template_name = 'tariff/tariff_form.html'
    success_url = reverse_lazy('tariff_list')

class TariffUpdateView(UpdateView):
    model = Tariff
    form_class = TariffForm
    template_name = 'tariff_form.html'
    success_url = reverse_lazy('tariff_list')