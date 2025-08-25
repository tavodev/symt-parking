from django.db import models

from apps.common.models import BaseModel
from apps.locations.models import Location


class CommercialUnit(BaseModel):
    """
    Espacio físico (no cambia). E.g., Local 201, Kiosko 15.
    """
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="units"
    )
    code = models.CharField(max_length=32)

    class Meta:
        unique_together = [("location", "code")]
        indexes = [models.Index(fields=["location", "code"])]

    def __str__(self):
        return f"{self.location.name} - {self.code}"
