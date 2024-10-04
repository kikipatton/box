from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from .models import Client
from .forms import ClientForm

class ListView(TemplateView):
    # Example of a function-based view
    template_name = "client/clientlist.html"
    
class AddView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'client/clientadd.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_date'] = timezone.now().strftime("%Y-%m-%d")
        return context

    def form_valid(self, form):
        client = form.save(commit=False)
        client.created_by = self.request.user
        client.created_at = timezone.now()
        client.save()
        messages.success(self.request, f'Client added successfully. Account number: {client.account_number}')
        return redirect('clientlist')  # Adjust this to your client list URL name

    def form_invalid(self, form):
        messages.error(self.request, 'Client creation failed. Please check the form.')
        return super().form_invalid(form)