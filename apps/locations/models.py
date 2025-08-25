from django.db import models

from apps.common.models import BaseModel


class Location(BaseModel):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    capacity = models.PositiveIntegerField(default=0)
    tolerance_minutes = models.PositiveIntegerField(default=15)

    def __str__(self):
        return self.name
