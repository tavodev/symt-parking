from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.stores.models import CommercialUnit
from apps.stores.selectors import commercial_unit_get_all, get_current_store_for_unit
from apps.locations.selectors import locations_get_all


class CommercialUnitListView(LoginRequiredMixin, ListView):
    model = CommercialUnit
    template_name = 'dashboard/commercial_units/list.html'
    context_object_name = 'commercial_units'
    paginate_by = 10

    def get_queryset(self):
        return commercial_unit_get_all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar información del store actual para cada unidad
        units_with_stores = []
        for unit in context['commercial_units']:
            current_store = get_current_store_for_unit(unit)
            units_with_stores.append({
                'unit': unit,
                'current_store': current_store
            })
        context['units_with_stores'] = units_with_stores
        return context


class CommercialUnitCreateView(LoginRequiredMixin, CreateView):
    model = CommercialUnit
    template_name = 'dashboard/commercial_units/form.html'
    fields = ['location', 'code']
    success_url = reverse_lazy('dashboard:commercial_units:list')

    def form_valid(self, form):
        messages.success(self.request, 'Unidad comercial creada exitosamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Crear Unidad Comercial'
        context['form_action'] = 'Crear'
        context['locations'] = locations_get_all()
        return context


class CommercialUnitUpdateView(LoginRequiredMixin, UpdateView):
    model = CommercialUnit
    template_name = 'dashboard/commercial_units/form.html'
    fields = ['location', 'code']
    success_url = reverse_lazy('dashboard:commercial_units:list')

    def form_valid(self, form):
        messages.success(self.request, 'Unidad comercial actualizada exitosamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Editar Unidad Comercial'
        context['form_action'] = 'Actualizar'
        context['locations'] = locations_get_all()
        return context


class CommercialUnitDeleteView(LoginRequiredMixin, DeleteView):
    model = CommercialUnit
    template_name = 'dashboard/commercial_units/delete.html'
    success_url = reverse_lazy('dashboard:commercial_units:list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Unidad comercial eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


class CommercialUnitDetailView(LoginRequiredMixin, DetailView):
    template_name = 'dashboard/commercial_units/detail.html'
    context_object_name = 'commercial_unit'
    model = CommercialUnit

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener store actual
        context['current_store'] = get_current_store_for_unit(self.object)
        # Obtener historial de ocupaciones
        from apps.stores.selectors import unit_occupancy_get_by_unit
        context['occupancy_history'] = unit_occupancy_get_by_unit(self.object)
        return context