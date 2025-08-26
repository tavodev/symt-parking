from django import forms
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from apps.stores.models import UnitOccupancy
from apps.stores.selectors import (
    unit_occupancy_get_all, 
    store_get_active, 
    commercial_unit_get_all
)


class UnitOccupancyForm(forms.ModelForm):
    class Meta:
        model = UnitOccupancy
        fields = ['unit', 'store', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'end_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'store': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit'].queryset = commercial_unit_get_all()
        self.fields['store'].queryset = store_get_active()
        self.fields['end_date'].required = False
        
        # Configurar valores iniciales para datetime-local
        if self.instance.pk:
            if self.instance.start_date:
                self.initial['start_date'] = self.instance.start_date.strftime('%Y-%m-%dT%H:%M')
            if self.instance.end_date:
                self.initial['end_date'] = self.instance.end_date.strftime('%Y-%m-%dT%H:%M')


class UnitOccupancyListView(LoginRequiredMixin, ListView):
    model = UnitOccupancy
    template_name = 'dashboard/unit_occupancies/list.html'
    context_object_name = 'occupancies'
    paginate_by = 10

    def get_queryset(self):
        return unit_occupancy_get_all()


class UnitOccupancyCreateView(LoginRequiredMixin, CreateView):
    model = UnitOccupancy
    form_class = UnitOccupancyForm
    template_name = 'dashboard/unit_occupancies/form.html'
    success_url = reverse_lazy('dashboard:unit_occupancies:list')

    def form_valid(self, form):
        try:
            # Llamar clean() para validar overlaps
            form.instance.clean()
            messages.success(self.request, 'Ocupación creada exitosamente.')
            return super().form_valid(form)
        except forms.ValidationError as e:
            for field, errors in e.error_dict.items():
                for error in errors:
                    form.add_error(field, error)
            return self.form_invalid(form)
        except Exception as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Crear Ocupación'
        context['form_action'] = 'Crear'
        return context


class UnitOccupancyUpdateView(LoginRequiredMixin, UpdateView):
    model = UnitOccupancy
    form_class = UnitOccupancyForm
    template_name = 'dashboard/unit_occupancies/form.html'
    success_url = reverse_lazy('dashboard:unit_occupancies:list')

    def form_valid(self, form):
        try:
            # Llamar clean() para validar overlaps
            form.instance.clean()
            messages.success(self.request, 'Ocupación actualizada exitosamente.')
            return super().form_valid(form)
        except forms.ValidationError as e:
            for field, errors in e.error_dict.items():
                for error in errors:
                    form.add_error(field, error)
            return self.form_invalid(form)
        except Exception as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Editar Ocupación'
        context['form_action'] = 'Actualizar'
        return context


class UnitOccupancyDeleteView(LoginRequiredMixin, DeleteView):
    model = UnitOccupancy
    template_name = 'dashboard/unit_occupancies/delete.html'
    success_url = reverse_lazy('dashboard:unit_occupancies:list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Ocupación eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


class UnitOccupancyDetailView(LoginRequiredMixin, DetailView):
    template_name = 'dashboard/unit_occupancies/detail.html'
    context_object_name = 'occupancy'
    model = UnitOccupancy

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Verificar si está activa
        context['is_active'] = self.object.is_active_at()
        return context