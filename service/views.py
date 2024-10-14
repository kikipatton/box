from django.views.generic import DetailView
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.db import transaction
from client.models import Client
from network.models import Router, IPPool
from tariff.models import Tariff
from .models import PPPoEService
from .forms import PPPoEServiceForm
from django.core.exceptions import ValidationError

class ClientDetailPPPoEView(DetailView):
    model = Client
    template_name = 'service/servicecreate.html'
    context_object_name = 'client'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pppoe_service'] = PPPoEService.objects.filter(client=self.object).first()
        context['tariffs'] = Tariff.objects.all()
        context['routers'] = Router.objects.all()
        context['ip_pools'] = IPPool.objects.all()
        context['form'] = PPPoEServiceForm(instance=context['pppoe_service'])
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        existing_service = PPPoEService.objects.filter(client=self.object).first()
        form = PPPoEServiceForm(request.POST, instance=existing_service)

        if form.is_valid():
            try:
                pppoe_service = form.save(commit=False)
                pppoe_service.client = self.object
                pppoe_service.save()  # This will trigger the save method in the model

                # Update or create in Mikrotik
                mikrotik_success = pppoe_service.update_or_create_in_mikrotik()
                if not mikrotik_success:
                    raise ValidationError("Failed to update/create PPPoE service in Mikrotik router")

                messages.success(request, 'Service Updated Successfully.' if existing_service else 'Service Created Successfully.')
                return redirect('client_detail_pppoe', pk=self.object.pk)
            except ValidationError as e:
                messages.success(request, str(e))
            except Exception as e:
                messages.success(request, f'Error saving PPPoE service: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.success(request, f'{field}: {error}')

        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('client_detail_pppoe', kwargs={'pk': self.object.pk})
    
    @method_decorator(require_POST)
    def delete_service(self, request, pk, service_pk):
        service = get_object_or_404(PPPoEService, pk=service_pk, client__pk=pk)
        try:
            service.delete()
            messages.success(request, 'PPPoE service deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting PPPoE service: {str(e)}')
        return redirect('client_detail_pppoe', pk=pk)