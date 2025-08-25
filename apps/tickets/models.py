from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.common.models import BaseModel
from apps.parkings.models import Parking
from apps.stores.models import Store


class Ticket(BaseModel):
    class Status(models.TextChoices):
        ISSUED = "issued", "Issued"
        VALIDATED = "validated", "Validated"
        PAID = "paid", "Paid"
        EXITED = "exited", "Exited"
        EXPIRED = "expired", "Expired"
        LOST = "lost", "Lost"
        CANCELED = "canceled", "Canceled"

    parking = models.ForeignKey(
        Parking,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    code = models.CharField(max_length=64, unique=True)  # código/QR/barcode
    paid_at = models.DateTimeField(blank=True, null=True)
    validated_by_store = models.ForeignKey(
        Store,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="validated_tickets"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_applied = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Descuento aplicado por validación de tienda"
    )
    exit_time = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Momento de salida del estacionamiento"
    )
    plate_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text="Placa del vehículo"
    )
    notes = models.TextField(
        blank=True,
        help_text="Observaciones adicionales"
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.ISSUED
    )

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["parking", "created_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["exit_time"]),
            models.Index(fields=["plate_number"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gte=0),
                name="ticket_amount_non_negative"
            ),
            models.CheckConstraint(
                check=models.Q(discount_applied__gte=0),
                name="ticket_discount_non_negative"
            ),
        ]

    def __str__(self):
        return f"Ticket {self.code} ({self.status})"
    
    @property
    def entry_time(self):
        """Alias para created_at - momento de entrada al estacionamiento"""
        return self.created_at
    
    @property
    def duration(self):
        """Duración de la estadía en el estacionamiento"""
        end_time = self.exit_time or timezone.now()
        return end_time - self.created_at
    
    @property
    def total_amount(self):
        """Monto total después de aplicar descuentos"""
        return max(0, self.amount - self.discount_applied)
    
    def is_expired(self):
        """Verifica si el ticket ha excedido el tiempo de tolerancia"""
        if not hasattr(self.parking, 'tolerance_minutes'):
            return False
        return self.duration > timedelta(minutes=self.parking.tolerance_minutes)
    
    def calculate_fee(self, hourly_rate=None):
        """Calcula la tarifa basada en la duración (implementación básica)"""
        if not hourly_rate:
            hourly_rate = 20  # Tarifa por defecto
        hours = max(1.0, self.duration.total_seconds() / 3600)  # Mínimo 1 hora
        return round(hours * hourly_rate, 2)
    
    def can_exit(self):
        """Verifica si el ticket puede ser usado para salir"""
        return self.status in [self.Status.PAID, self.Status.VALIDATED]
    
    def clean(self):
        """Validaciones personalizadas del modelo"""
        super().clean()
        
        # Validar que exit_time no sea anterior a created_at
        if self.exit_time and self.exit_time < self.created_at:
            raise ValidationError({
                'exit_time': 'La hora de salida no puede ser anterior a la hora de entrada.'
            })
        
        # Validar que paid_at no sea anterior a created_at
        if self.paid_at and self.paid_at < self.created_at:
            raise ValidationError({
                'paid_at': 'La hora de pago no puede ser anterior a la hora de entrada.'
            })
        
        # Validar coherencia de estados
        if self.status == self.Status.EXITED and not self.exit_time:
            raise ValidationError({
                'exit_time': 'Un ticket con estado EXITED debe tener hora de salida.'
            })
            
        if self.status == self.Status.PAID and not self.paid_at:
            raise ValidationError({
                'paid_at': 'Un ticket con estado PAID debe tener hora de pago.'
            })
    
    def save(self, *args, **kwargs):
        """Override save para ejecutar validaciones"""
        self.clean()
        super().save(*args, **kwargs)
