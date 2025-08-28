from django.urls import path, include
from apps.dashboard.views import DashboardView
from . import locations_urls, stores_urls, commercial_units_urls, unit_occupancies_urls, parkings_urls, tickets_urls, users_urls

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardView.as_view(), name='index'),
    path(
        'locations/',
        include((locations_urls.urlpatterns, 'locations')),
    ),
    path(
        'tiendas/',
        include((stores_urls.urlpatterns, 'stores')),
    ),
    path(
        'unidades-comerciales/',
        include((commercial_units_urls.urlpatterns, 'commercial_units')),
    ),
    path(
        'ocupaciones/',
        include((unit_occupancies_urls.urlpatterns, 'unit_occupancies')),
    ),
    path(
        'estacionamientos/',
        include((parkings_urls.urlpatterns, 'parkings')),
    ),
    path(
        'tickets/',
        include((tickets_urls.urlpatterns, 'tickets')),
    ),
    path(
        'usuarios/',
        include((users_urls.urlpatterns, 'users')),
    ),
]