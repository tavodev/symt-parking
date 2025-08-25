# apps/stores/models.py
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.stores.models import CommercialUnit, Store


class UnitOccupancy(models.Model):
    """
    Relación con vigencia entre una unidad y una tienda.
    Maneja histórico. Evita traslapes por validación en clean().
    """
    unit = models.ForeignKey(
        CommercialUnit, on_delete=models.CASCADE,
        related_name="occupancies"
    )
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE,
        related_name="unit_occupancies"
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(
        blank=True,
        null=True)  # null = ocupación vigente/actual

    class Meta:
        ordering = ["unit", "-start_date"]
        indexes = [
            models.Index(fields=["unit", "start_date"]),
            models.Index(fields=["unit", "end_date"]),
        ]

    def __str__(self):
        fin = self.end_date.isoformat() if self.end_date else "present"
        return f"{self.unit} -> {self.store} ({self.start_date.isoformat()} - {fin})"

    def clean(self):
        """
        Evita traslapes de ocupaciones en la misma unit.
        Reglas:
          - end_date puede ser None (ocupación actual).
          - Intervalos se consideran [start_date, end_date] (si end_date) o abierto.
        """
        if self.end_date and self.end_date <= self.start_date:
            raise ValidationError(
                {"end_date": "end_date debe ser posterior a start_date."})

        # Query de solapamiento:
        # Overlap si: (A.start <= B.end or B.end is null) AND (A.end is null or A.end >= B.start)
        qs = UnitOccupancy.objects.filter(unit=self.unit).exclude(pk=self.pk)

        if self.end_date:
            overlapping = qs.filter(
                models.Q(end_date__isnull=True) | models.Q(
                    start_date__lte=self.end_date),
                # y además que su fin sea después/incluya mi inicio
                models.Q(end_date__isnull=True) | models.Q(
                    end_date__gte=self.start_date),
            )
        else:
            # Ocupación abierta: choca con cualquier otra que no termine antes de mi inicio
            overlapping = qs.filter(
                models.Q(end_date__isnull=True) | models.Q(
                    end_date__gte=self.start_date)
            )

        if overlapping.exists():
            raise ValidationError(
                "Ya existe una ocupación que se solapa en esta unidad.")

    # Helper para saber si está vigente al momento 'at'
    def is_active_at(self, at=None):
        at = at or timezone.now()
        if self.end_date is None:
            return self.start_date <= at
        return self.start_date <= at <= self.end_date
