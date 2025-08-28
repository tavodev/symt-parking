from django.urls import path
from apps.dashboard.views import tickets


urlpatterns = [
    path('', tickets.TicketListView.as_view(), name='list'),
    path('crear/', tickets.TicketCreateView.as_view(), name='create'),
    path('<uuid:pk>/', tickets.TicketDetailView.as_view(), name='detail'),
    path('<uuid:pk>/editar/', tickets.TicketUpdateView.as_view(), name='update'),
    path('<uuid:pk>/eliminar/', tickets.TicketDeleteView.as_view(), name='delete'),
]