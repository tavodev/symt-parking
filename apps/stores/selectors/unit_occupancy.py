from django.db import models
from django.utils import timezone

from apps.stores.models import CommercialUnit, UnitOccupancy


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
