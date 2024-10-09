from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='networking_home'),
    
    path('routers/', views.RouterListView.as_view(), name='networklist'),
    path('routers/create/', views.RouterCreateView.as_view(), name='router_create'),
    path('routers/<int:pk>/', views.RouterDetailView.as_view(), name='router_detail'),
    path('routers/<int:pk>/delete/', views.RouterDeleteView.as_view(), name='router_delete'),
    
    path('ip-pools/create/', views.IPPoolCreateView.as_view(), name='pool_create'),
    path('ip-pools/<int:pk>/', views.IPPoolDetailView.as_view(), name='ip_pool_detail'),
    path('ip-pools/<int:pk>/update/', views.IPPoolUpdateView.as_view(), name='ip_pool_update'),
    path('ip-pools/<int:pk>/delete/', views.IPPoolDeleteView.as_view(), name='ip_pool_delete'),
]