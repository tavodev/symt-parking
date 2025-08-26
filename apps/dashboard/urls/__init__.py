from django.urls import path, include
from apps.dashboard.views import DashboardView
from . import locations_urls

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardView.as_view(), name='index'),
    path(
        'locations/',
        include((locations_urls.urlpatterns,'locations')),
    ),
]