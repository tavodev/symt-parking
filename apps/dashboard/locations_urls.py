from django.urls import path
from apps.dashboard.views import locations

app_name = 'locations'

urlpatterns = [
    path('', locations.LocationListView.as_view(), name='list'),
    path('crear/', locations.LocationCreateView.as_view(), name='create'),
    path('<str:pk>/', locations.LocationDetailView.as_view(), name='detail'),
    path('<str:pk>/editar/', locations.LocationUpdateView.as_view(), name='update'),
    path('<str:pk>/eliminar/', locations.LocationDeleteView.as_view(), name='delete'),
]