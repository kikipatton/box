from django.urls import reverse 
from django.views.generic import CreateView, ListView, DetailView
# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from .models import Client
from .forms import ClientForm
from django.db.models import Count, Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


class ListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'client/clientlist.html'
    context_object_name = 'clients'
    paginate_by = 100  # Adjust this value as needed
    

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(account_number__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        
        # Add counts to the context
        context['clients_count'] = queryset.count()
        status_counts = queryset.values('status').annotate(count=Count('status'))
        
        for status in status_counts:
            context[f"{status['status'].lower()}_count"] = status['count']
        
        # Ensure all status counts are in the context, even if zero
        for status in ['active', 'inactive', 'pending']:
            if f"{status}_count" not in context:
                context[f"{status}_count"] = 0

        return context
    
    
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
    

class ClientView(DetailView):
    model = Client
    template_name = 'client/clientaccount.html'
    context_object_name = 'client'
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = ClientForm(request.POST, instance=self.object)
        if form.is_valid():
            form.save()
            return redirect(reverse('clientview', kwargs={'pk': self.object.pk}))
        return self.render_to_response(self.get_context_data(form=form))
    

@login_required
def client_list_json(request):
    clients = Client.objects.filter(created_by=request.user).values(
    'account_number', 'first_name', 'phone_number', 'email', 'status' , 'address'
)
    return JsonResponse(list(clients), safe=False)