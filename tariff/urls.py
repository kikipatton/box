from django.urls import path
from .views import (
    TariffListView,
    TariffDetailView,
    TariffCreateView,
    TariffUpdateView,
)

urlpatterns = [
    path('tariff/', TariffListView.as_view(), name='tariff_list'),
    path('tariff/<int:pk>/', TariffDetailView.as_view(), name='tariff_detail'),
    path('tariff/create/', TariffCreateView.as_view(), name='tariff_create'),
    path('tariff/<int:pk>/update/', TariffUpdateView.as_view(), name='tariff_update'),
]