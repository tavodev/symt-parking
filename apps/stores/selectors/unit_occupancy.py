from django.db import models
from django.db.models import QuerySet
from django.utils import timezone

from apps.stores.models import CommercialUnit, UnitOccupancy, Store


def get_current_store_for_unit(unit: CommercialUnit, at=None):
    """
    Devuelve la Store vigente para la unidad en el instante 'at' (default: ahora).
    """
    at = at or timezone.now()
    occ = (UnitOccupancy.objects
           .filter(unit=unit, start_date__lte=at)
           .filter(models.Q(end_date__isnull=True) | models.Q(end_date__gte=at))
           .select_related("store")
           .order_by("-start_date")
           .first())
    return occ.store if occ else None


def unit_occupancy_get_all() -> QuerySet[UnitOccupancy]:
    """Obtiene todas las ocupaciones ordenadas por unidad y fecha de inicio."""
    return UnitOccupancy.objects.select_related('unit__location', 'store').order_by('unit', '-start_date')


def unit_occupancy_get_by_id(occupancy_id: int) -> UnitOccupancy:
    """Obtiene una ocupación por su ID."""
    return UnitOccupancy.objects.select_related('unit__location', 'store').get(pk=occupancy_id)


def unit_occupancy_get_active(at=None) -> QuerySet[UnitOccupancy]:
    """Obtiene todas las ocupaciones activas en el momento especificado."""
    at = at or timezone.now()
    return UnitOccupancy.objects.select_related('unit__location', 'store').filter(
        start_date__lte=at
    ).filter(
        models.Q(end_date__isnull=True) | models.Q(end_date__gte=at)
    ).order_by('unit', '-start_date')


def unit_occupancy_get_by_store(store: Store) -> QuerySet[UnitOccupancy]:
    """Obtiene todas las ocupaciones de una tienda específica."""
    return UnitOccupancy.objects.select_related('unit__location', 'store').filter(
        store=store
    ).order_by('-start_date')


def unit_occupancy_get_by_unit(unit: CommercialUnit) -> QuerySet[UnitOccupancy]:
    """Obtiene todas las ocupaciones de una unidad comercial específica."""
    return UnitOccupancy.objects.select_related('unit__location', 'store').filter(
        unit=unit
    ).order_by('-start_date')


def unit_occupancy_get_historical() -> QuerySet[UnitOccupancy]:
    """Obtiene todas las ocupaciones históricas (que ya terminaron)."""
    return UnitOccupancy.objects.select_related('unit__location', 'store').filter(
        end_date__isnull=False,
        end_date__lte=timezone.now()
    ).order_by('-end_date')
