from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.ListView.as_view(), name='clientlist'),
    path('client/add/', views.AddView.as_view(), name='clientadd'),
    path('client/json/', views.client_list_json, name='client_list_json'),
    path('client/<int:pk>/', views.ClientView.as_view(), name='clientview'),
    path('mpesa-config/', views.MpesaConfigUpdateView.as_view(), name='mpesa_config_update'),
]