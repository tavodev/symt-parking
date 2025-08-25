# apps/parking/models.py
from django.db import models
from apps.locations.models import Location


class Parking(models.Model):
    location = models.OneToOneField(
        Location,
        on_delete=models.CASCADE,
        related_name="parking"
    )
    capacity = models.PositiveIntegerField(default=0)
    tolerance_minutes = models.PositiveIntegerField(default=15)

    def __str__(self):
        return f"Parking @ {self.location.name}"
