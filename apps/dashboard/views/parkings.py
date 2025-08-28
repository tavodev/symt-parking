from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.parkings.models import Parking


class ParkingListView(LoginRequiredMixin, ListView):
    model = Parking
    template_name = 'dashboard/parkings/list.html'
    context_object_name = 'parkings'
    paginate_by = 10

    def get_queryset(self):
        return Parking.objects.select_related('location').all()


class ParkingCreateView(LoginRequiredMixin, CreateView):
    model = Parking
    template_name = 'dashboard/parkings/form.html'
    fields = ['location', 'capacity', 'tolerance_minutes']
    success_url = reverse_lazy('dashboard:parkings:list')

    def form_valid(self, form):
        messages.success(self.request, 'Estacionamiento creado exitosamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Crear Estacionamiento'
        context['form_action'] = 'Crear'
        return context


class ParkingUpdateView(LoginRequiredMixin, UpdateView):
    model = Parking
    template_name = 'dashboard/parkings/form.html'
    fields = ['location', 'capacity', 'tolerance_minutes']
    success_url = reverse_lazy('dashboard:parkings:list')

    def form_valid(self, form):
        messages.success(self.request, 'Estacionamiento actualizado exitosamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Editar Estacionamiento'
        context['form_action'] = 'Actualizar'
        return context


class ParkingDeleteView(LoginRequiredMixin, DeleteView):
    model = Parking
    template_name = 'dashboard/parkings/delete.html'
    success_url = reverse_lazy('dashboard:parkings:list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Estacionamiento eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


class ParkingDetailView(LoginRequiredMixin, DetailView):
    template_name = 'dashboard/parkings/detail.html'
    context_object_name = 'parking'
    model = Parking

    def get_object(self):
        return get_object_or_404(Parking.objects.select_related('location'), pk=self.kwargs['pk'])