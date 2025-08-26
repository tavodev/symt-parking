from django.urls import path
from apps.dashboard.views import commercial_units


urlpatterns = [
    path('', commercial_units.CommercialUnitListView.as_view(), name='list'),
    path('crear/', commercial_units.CommercialUnitCreateView.as_view(), name='create'),
    path('<uuid:pk>/', commercial_units.CommercialUnitDetailView.as_view(), name='detail'),
    path('<uuid:pk>/editar/', commercial_units.CommercialUnitUpdateView.as_view(), name='update'),
    path('<uuid:pk>/eliminar/', commercial_units.CommercialUnitDeleteView.as_view(), name='delete'),
]