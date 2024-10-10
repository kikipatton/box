from django.urls import path
from .views import TariffListView, TariffDetailView, TariffCreateView, TariffUpdateView

urlpatterns = [
    path('', TariffListView.as_view(), name='tariff_list'),
    path('<int:pk>/', TariffDetailView.as_view(), name='tariff_detail'),
    path('create/', TariffCreateView.as_view(), name='tariff_create'),
    path('<int:pk>/update/', TariffUpdateView.as_view(), name='tariff_update'),
]