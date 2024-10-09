from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Router, IPPool
from .forms import RouterForm, IPPoolForm

def home(request):
    return render(request, 'network/home.html')

class RouterListView(LoginRequiredMixin, ListView):
    model = Router, IPPool
    template_name = 'network/networklist.html'
    context_object_name = 'routers'

class RouterDetailView(LoginRequiredMixin, DetailView):
    model = Router
    template_name = 'network/router_detail.html'

class RouterCreateView(LoginRequiredMixin, CreateView):
    model = Router
    form_class = RouterForm
    template_name = 'network/router_create.html'

class RouterDeleteView(LoginRequiredMixin, DeleteView):
    model = Router
    template_name = 'network/router_confirm_delete.html'
    success_url = reverse_lazy('router_list')


class IPPoolDetailView(LoginRequiredMixin, DetailView):
    model = IPPool
    template_name = 'network/ip_pool_detail.html'

class IPPoolCreateView(LoginRequiredMixin, CreateView):
    model = IPPool
    form_class = IPPoolForm
    template_name = 'network/pool_create.html'

class IPPoolUpdateView(LoginRequiredMixin, UpdateView):
    model = IPPool
    form_class = IPPoolForm
    template_name = 'network/ip_pool_form.html'

class IPPoolDeleteView(LoginRequiredMixin, DeleteView):
    model = IPPool
    template_name = 'network/ip_pool_confirm_delete.html'
    success_url = reverse_lazy('ip_pool_list')