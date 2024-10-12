from django.urls import path
from .views import ClientDetailPPPoEView

urlpatterns = [
    path('client/<int:pk>/pppoe/', ClientDetailPPPoEView.as_view(), name='client_detail_pppoe'),
]