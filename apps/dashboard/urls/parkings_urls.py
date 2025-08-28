from django.urls import path
from apps.dashboard.views import parkings


urlpatterns = [
    path('', parkings.ParkingListView.as_view(), name='list'),
    path('crear/', parkings.ParkingCreateView.as_view(), name='create'),
    path('<uuid:pk>/', parkings.ParkingDetailView.as_view(), name='detail'),
    path('<uuid:pk>/editar/', parkings.ParkingUpdateView.as_view(), name='update'),
    path('<uuid:pk>/eliminar/', parkings.ParkingDeleteView.as_view(), name='delete'),
]