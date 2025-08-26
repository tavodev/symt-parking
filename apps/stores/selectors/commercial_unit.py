from django.db.models import QuerySet
from django.db.models import Q

from ..models import CommercialUnit
from apps.locations.models import Location


def commercial_unit_get_all() -> QuerySet[CommercialUnit]:
    """Obtiene todas las unidades comerciales ordenadas por ubicación y código."""
    return CommercialUnit.objects.select_related('location').order_by('location__name', 'code')


def commercial_unit_get_by_id(unit_id: str) -> CommercialUnit:
    """Obtiene una unidad comercial por su ID."""
    return CommercialUnit.objects.select_related('location').get(pk=unit_id)


def commercial_unit_get_by_location(location: Location) -> QuerySet[CommercialUnit]:
    """Obtiene todas las unidades comerciales de una ubicación específica."""
    return CommercialUnit.objects.filter(location=location).order_by('code')


def commercial_unit_search(query: str) -> QuerySet[CommercialUnit]:
    """Busca unidades comerciales por código o nombre de ubicación."""
    return CommercialUnit.objects.select_related('location').filter(
        Q(code__icontains=query) | Q(location__name__icontains=query)
    ).order_by('location__name', 'code')


def commercial_unit_get_available(location: Location = None) -> QuerySet[CommercialUnit]:
    """Obtiene unidades comerciales que no tienen ocupación activa."""
    queryset = CommercialUnit.objects.select_related('location')
    
    if location:
        queryset = queryset.filter(location=location)
    
    # Filtrar unidades que no tienen ocupaciones activas (end_date es null)
    return queryset.exclude(
        occupancies__end_date__isnull=True
    ).order_by('location__name', 'code')