# apps/stores/models.py
from django.db import models

from apps.common.models import BaseModel


class Store(BaseModel):
    """
    Negocio/operador (puede moverse de unidad o cerrar/abrir en el tiempo).
    """
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [models.Index(fields=["name"])]

    def __str__(self):
        return self.name

