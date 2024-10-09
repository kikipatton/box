from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Router, IPPool
from .forms import RouterForm, IPPoolForm

def home(request):
    return render(request, 'network/home.html')

class RouterListView(LoginRequiredMixin, ListView):
    model = Router
    template_name = 'network/networklist.html'
    context_object_name = 'routers'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ip_pools'] = IPPool.objects.all()
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Router '{form.instance.name}' was successfully added.")
        return response

    def form_invalid(self, form):
        for error in form.non_field_errors():
            messages.error(self.request, error)
        return super().form_invalid(form)

class RouterDetailView(LoginRequiredMixin, DetailView):
    model = Router
    template_name = 'network/router_detail.html'

class RouterCreateView(LoginRequiredMixin, CreateView):
    model = Router
    form_class = RouterForm
    template_name = 'network/router_create.html'
    success_url = reverse_lazy('networklist')

class RouterDeleteView(LoginRequiredMixin, DeleteView):
    model = Router
    template_name = 'network/router_confirm_delete.html'
    success_url = reverse_lazy('networklist')


class IPPoolDetailView(LoginRequiredMixin, DetailView):
    model = IPPool
    template_name = 'network/ip_pool_detail.html'

class IPPoolCreateView(LoginRequiredMixin, CreateView):
    model = IPPool
    form_class = IPPoolForm
    template_name = 'network/pool_create.html'
    success_url = reverse_lazy('networklist')

class IPPoolUpdateView(LoginRequiredMixin, UpdateView):
    model = IPPool
    form_class = IPPoolForm
    template_name = 'network/ip_pool_form.html'

class IPPoolDeleteView(LoginRequiredMixin, DeleteView):
    model = IPPool
    template_name = 'network/ip_pool_confirm_delete.html'
    success_url = reverse_lazy('networklist')