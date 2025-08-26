from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.stores.models import Store
from apps.stores.selectors import store_get_all


class StoreListView(LoginRequiredMixin, ListView):
    model = Store
    template_name = 'dashboard/stores/list.html'
    context_object_name = 'stores'
    paginate_by = 10

    def get_queryset(self):
        return store_get_all()


class StoreCreateView(LoginRequiredMixin, CreateView):
    model = Store
    template_name = 'dashboard/stores/form.html'
    fields = ['name', 'is_active']
    success_url = reverse_lazy('dashboard:stores:list')

    def form_valid(self, form):
        messages.success(self.request, 'Tienda creada exitosamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Crear Tienda'
        context['form_action'] = 'Crear'
        return context


class StoreUpdateView(LoginRequiredMixin, UpdateView):
    model = Store
    template_name = 'dashboard/stores/form.html'
    fields = ['name', 'is_active']
    success_url = reverse_lazy('dashboard:stores:list')

    def form_valid(self, form):
        messages.success(self.request, 'Tienda actualizada exitosamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Editar Tienda'
        context['form_action'] = 'Actualizar'
        return context


class StoreDeleteView(LoginRequiredMixin, DeleteView):
    model = Store
    template_name = 'dashboard/stores/delete.html'
    success_url = reverse_lazy('dashboard:stores:list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Tienda eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


class StoreDetailView(LoginRequiredMixin, DetailView):
    template_name = 'dashboard/stores/detail.html'
    context_object_name = 'store'
    model = Store

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener ocupaciones actuales de la tienda
        from apps.stores.selectors import unit_occupancy_get_by_store
        context['current_occupancies'] = unit_occupancy_get_by_store(self.object).filter(
            end_date__isnull=True
        )
        # Obtener historial de ocupaciones
        context['occupancy_history'] = unit_occupancy_get_by_store(self.object).filter(
            end_date__isnull=False
        )[:5]  # Últimas 5
        return context