from django.urls import path, include
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='index'),
    path('locations/', include('apps.dashboard.locations_urls', namespace='locations')),
]