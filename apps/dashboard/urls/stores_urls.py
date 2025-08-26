from django.urls import path
from apps.dashboard.views import stores


urlpatterns = [
    path('', stores.StoreListView.as_view(), name='list'),
    path('crear/', stores.StoreCreateView.as_view(), name='create'),
    path('<uuid:pk>/', stores.StoreDetailView.as_view(), name='detail'),
    path('<uuid:pk>/editar/', stores.StoreUpdateView.as_view(), name='update'),
    path('<uuid:pk>/eliminar/', stores.StoreDeleteView.as_view(), name='delete'),
]