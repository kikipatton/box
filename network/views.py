from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Router, IPPool
from .forms import RouterForm, IPPoolForm
from librouteros import connect
from librouteros.exceptions import LibRouterosError

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

class RouterDetailView(DetailView):
    model = Router
    template_name = 'network/router_detail.html'
    context_object_name = 'router'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = RouterForm(instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = RouterForm(request.POST, instance=self.object)
        if form.is_valid():
            form.save()
            messages.success(request, f"Router '{self.object.name}' has been updated successfully.")
            return redirect('router_detail', pk=self.object.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
            return self.render_to_response(self.get_context_data(form=form))

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
    
    
def check_router_connection(request, pk):
    router = get_object_or_404(Router, pk=pk)
    try:
        # Attempt to connect to the router
        connect(username=router.username, password=router.password, host=router.ip_address, port=router.api_port)
        messages.success(request, f"Successfully connected to '{router.name}'.")
    except LibRouterosError as e:
        messages.error(request, f"Failed to connect to router '{router.name}': {str(e)}")
    except Exception as e:
        messages.error(request, f"An unexpected error occurred while connecting to '{router.name}': {str(e)}")
    
    return redirect(reverse('router_detail', kwargs={'pk': pk}))