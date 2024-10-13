from django.urls import path
from .views import ClientDetailPPPoEView

urlpatterns = [
    path('client/<int:pk>/pppoe/', ClientDetailPPPoEView.as_view(), name='client_detail_pppoe'),
    path('client/<int:pk>/pppoe/<int:service_pk>/delete/', ClientDetailPPPoEView.as_view(http_method_names=['post']), name='delete_pppoe_service'),
]