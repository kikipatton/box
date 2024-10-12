from django.views.generic import DetailView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.db import transaction
from client.models import Client
from network.models import Router, IPPool
from tariff.models import Tariff
from .models import PPPoEService
from .forms import PPPoEServiceForm

class ClientDetailPPPoEView(DetailView):
    model = Client
    template_name = 'service/servicecreate.html'
    context_object_name = 'client'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pppoe_services'] = PPPoEService.objects.filter(client=self.object)
        context['tariffs'] = Tariff.objects.all()
        context['routers'] = Router.objects.all()
        context['ip_pools'] = IPPool.objects.all()
        context['form'] = PPPoEServiceForm()
        
    
    # Get the first PPPoE service for this client (if any)
        pppoe_service = PPPoEService.objects.filter(client=self.object).first()
        context['pppoe_service'] = pppoe_service

        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        print("POST request received")
        self.object = self.get_object()
        form = PPPoEServiceForm(request.POST)
        print(f"Form data: {request.POST}")
        if form.is_valid():
            print("Form is valid")
            try:
                pppoe_service = form.save(commit=False)
                pppoe_service.client = self.object
                print(f"PPPoEService object created: {pppoe_service.__dict__}")
                pppoe_service.save()
                print("PPPoEService saved successfully")
                messages.success(request, 'PPPoE service created successfully.')
                return redirect('client_detail_pppoe', pk=self.object.pk)
            except Exception as e:
                print(f"Error saving PPPoEService: {str(e)}")
                messages.error(request, f'Error creating PPPoE service: {str(e)}')
        else:
            print(f"Form is invalid. Errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('client_detail_pppoe', kwargs={'pk': self.object.pk})