from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, \
    DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.locations.models import Location
from apps.locations.selectors import locations_get_all


class LocationListView(LoginRequiredMixin, ListView):
    model = Location
    template_name = 'dashboard/locations/list.html'
    context_object_name = 'locations'
    paginate_by = 10

    def get_queryset(self):
        return locations_get_all()


class LocationCreateView(LoginRequiredMixin, CreateView):
    model = Location
    template_name = 'dashboard/locations/form.html'
    fields = ['name', 'address', 'capacity', 'tolerance_minutes']
    success_url = reverse_lazy('dashboard:locations:list')

    def form_valid(self, form):
        messages.success(self.request, 'Ubicación creada exitosamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Crear Ubicación'
        context['form_action'] = 'Crear'
        return context


class LocationUpdateView(LoginRequiredMixin, UpdateView):
    model = Location
    template_name = 'dashboard/locations/form.html'
    fields = ['name', 'address', 'capacity', 'tolerance_minutes']
    success_url = reverse_lazy('dashboard:locations:list')

    def form_valid(self, form):
        messages.success(self.request, 'Ubicación actualizada exitosamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Editar Ubicación'
        context['form_action'] = 'Actualizar'
        return context


class LocationDeleteView(LoginRequiredMixin, DeleteView):
    model = Location
    template_name = 'dashboard/locations/delete.html'
    success_url = reverse_lazy('dashboard:locations:list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Ubicación eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


class LocationDetailView(LoginRequiredMixin, DetailView):
    template_name = 'dashboard/locations/detail.html'
    context_object_name = 'location'
    model = Location