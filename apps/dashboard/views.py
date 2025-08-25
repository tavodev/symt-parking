from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
import json

from apps.tickets.models import Ticket
from apps.stores.models import Store, CommercialUnit
from apps.parkings.models import Parking
from apps.stores.selectors.unit_occupancy import get_current_store_for_unit


class DashboardView(TemplateView):
    template_name = 'dashboard/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Métricas principales
        active_statuses = [
            Ticket.Status.ISSUED, 
            Ticket.Status.VALIDATED, 
            Ticket.Status.PAID
        ]
        context['active_tickets'] = Ticket.objects.filter(
            status__in=active_statuses,
            exit_time__isnull=True
        ).count()
        
        # Usar selector para unidades ocupadas
        context['occupied_units'] = CommercialUnit.objects.filter(
            occupancies__end_date__isnull=True
        ).count()
        
        # Total de espacios en todos los parkings
        context['available_spaces'] = Parking.objects.aggregate(
            total_capacity=Sum('capacity')
        )['total_capacity'] or 0
        
        context['active_stores'] = Store.objects.filter(is_active=True).count()
        
        # Tickets recientes con más información
        context['recent_tickets'] = Ticket.objects.select_related(
            'parking__location', 'validated_by_store'
        ).order_by('-created_at')[:10]
        
        # Datos para gráfico - ocupación semanal simulada basada en datos reales
        context['weekly_occupancy_data'] = json.dumps(
            self._get_weekly_occupancy_data()
        )
        
        return context
    
    def _get_weekly_occupancy_data(self):
        """
        Genera datos de ocupación semanal.
        Por ahora simulado, pero se puede extender para usar datos reales.
        """
        now = timezone.now()
        weekly_data = []
        
        for i in range(7):  # Últimos 7 días
            date = now - timedelta(days=6-i)
            # Simular ocupación basada en día de la semana
            # Fines de semana más ocupados
            if date.weekday() >= 5:  # Sábado y Domingo
                occupancy = 60 + (i * 8)
            else:  # Días de semana
                occupancy = 35 + (i * 7)
            weekly_data.append(occupancy)
        
        return weekly_data
