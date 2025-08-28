from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.tickets.models import Ticket


class TicketListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'dashboard/tickets/list.html'
    context_object_name = 'tickets'
    paginate_by = 15

    def get_queryset(self):
        return Ticket.objects.select_related('parking', 'validated_by_store').all()


class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    template_name = 'dashboard/tickets/form.html'
    fields = ['parking', 'code', 'plate_number', 'notes', 'status']
    success_url = reverse_lazy('dashboard:tickets:list')

    def form_valid(self, form):
        messages.success(self.request, 'Ticket creado exitosamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Crear Ticket'
        context['form_action'] = 'Crear'
        return context


class TicketUpdateView(LoginRequiredMixin, UpdateView):
    model = Ticket
    template_name = 'dashboard/tickets/form.html'
    fields = ['parking', 'code', 'validated_by_store', 'amount', 'discount_applied', 'exit_time', 'plate_number', 'notes', 'status']
    success_url = reverse_lazy('dashboard:tickets:list')

    def form_valid(self, form):
        messages.success(self.request, 'Ticket actualizado exitosamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Editar Ticket'
        context['form_action'] = 'Actualizar'
        return context


class TicketDeleteView(LoginRequiredMixin, DeleteView):
    model = Ticket
    template_name = 'dashboard/tickets/delete.html'
    success_url = reverse_lazy('dashboard:tickets:list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Ticket eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


class TicketDetailView(LoginRequiredMixin, DetailView):
    template_name = 'dashboard/tickets/detail.html'
    context_object_name = 'ticket'
    model = Ticket

    def get_object(self):
        return get_object_or_404(
            Ticket.objects.select_related('parking', 'validated_by_store'),
            pk=self.kwargs['pk']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket = self.object
        
        duration = ticket.duration
        total_seconds = duration.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        
        duration_text = ""
        if duration.days > 0:
            duration_text += f"{duration.days} día{'s' if duration.days > 1 else ''}, "
        if hours > 0:
            duration_text += f"{hours} hora{'s' if hours > 1 else ''}, "
        duration_text += f"{minutes} minuto{'s' if minutes != 1 else ''}"
        
        context['duration_display'] = duration_text
        context['total_amount_display'] = ticket.total_amount
        context['can_exit_display'] = ticket.can_exit()
        context['is_expired_display'] = ticket.is_expired()
        
        return context