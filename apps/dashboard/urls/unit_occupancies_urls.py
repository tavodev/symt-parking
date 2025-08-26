from django.urls import path
from apps.dashboard.views import unit_occupancies


urlpatterns = [
    path('', unit_occupancies.UnitOccupancyListView.as_view(), name='list'),
    path('crear/', unit_occupancies.UnitOccupancyCreateView.as_view(), name='create'),
    path('<int:pk>/', unit_occupancies.UnitOccupancyDetailView.as_view(), name='detail'),
    path('<int:pk>/editar/', unit_occupancies.UnitOccupancyUpdateView.as_view(), name='update'),
    path('<int:pk>/eliminar/', unit_occupancies.UnitOccupancyDeleteView.as_view(), name='delete'),
]