from django.urls import path
from apps.dashboard.views import users


urlpatterns = [
    path('', users.UserListView.as_view(), name='list'),
    path('crear/', users.UserCreateView.as_view(), name='create'),
    path('<uuid:pk>/', users.UserDetailView.as_view(), name='detail'),
    path('<uuid:pk>/editar/', users.UserUpdateView.as_view(), name='update'),
    path('<uuid:pk>/eliminar/', users.UserDeleteView.as_view(), name='delete'),
]