from django.db import models
from django.conf import settings

from apps.common.models import BaseModel
from apps.locations.models import Location
from apps.stores.models.store import Store


class UserProfile(BaseModel):
    """
    Profile extension for CustomUser with role and relationship information
    """
    
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        ADMIN_PLAZA = 'admin_plaza', 'Administrator de Plaza'
        GERENTE_LOCAL = 'gerente_local', 'Gerente de Local'
        USUARIO_LOCAL = 'usuario_local', 'Usuario Local'
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USUARIO_LOCAL,
        verbose_name='Rol'
    )
    
    # For Admin Plaza - one location per user
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='plaza_admins',
        verbose_name='Plaza asignada'
    )
    
    # For Gerente Local and Usuario Local - one store per user
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='Tienda asignada'
    )
    
    # For Admin - can have multiple locations (many-to-many through a separate relationship)
    managed_locations = models.ManyToManyField(
        Location,
        blank=True,
        related_name='admins',
        verbose_name='Ubicaciones gestionadas'
    )
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['location']),
            models.Index(fields=['store']),
        ]
        constraints = [
            # Admin Plaza must have a location
            models.CheckConstraint(
                condition=~(models.Q(role='admin_plaza') & models.Q(location__isnull=True)),
                name='admin_plaza_must_have_location'
            ),
            # Gerente Local must have a store
            models.CheckConstraint(
                condition=~(models.Q(role='gerente_local') & models.Q(store__isnull=True)),
                name='gerente_local_must_have_store'
            ),
            # Usuario Local must have a store
            models.CheckConstraint(
                condition=~(models.Q(role='usuario_local') & models.Q(store__isnull=True)),
                name='usuario_local_must_have_store'
            ),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"
    
    def can_manage_user(self, target_profile):
        """
        Check if this user can manage another user based on role hierarchy
        """
        if self.role == UserProfile.Role.ADMIN:
            return True
        
        if self.role == UserProfile.Role.ADMIN_PLAZA:
            # Can manage gerente_local and usuario_local in their location
            if target_profile.role in [UserProfile.Role.GERENTE_LOCAL, UserProfile.Role.USUARIO_LOCAL]:
                if target_profile.store and target_profile.store.location == self.location:
                    return True
        
        if self.role == UserProfile.Role.GERENTE_LOCAL:
            # Can only manage usuario_local in their store
            if target_profile.role == UserProfile.Role.USUARIO_LOCAL:
                return target_profile.store == self.store
        
        return False
    
    def can_create_role(self, target_role):
        """
        Check if this user can create users with the target role
        """
        if self.role == UserProfile.Role.ADMIN:
            return True
        
        if self.role == UserProfile.Role.ADMIN_PLAZA:
            return target_role in [UserProfile.Role.GERENTE_LOCAL, UserProfile.Role.USUARIO_LOCAL]
        
        if self.role == UserProfile.Role.GERENTE_LOCAL:
            return target_role == UserProfile.Role.USUARIO_LOCAL
        
        return False
    
    def get_managed_locations(self):
        """
        Get all locations this user can manage
        """
        if self.role == UserProfile.Role.ADMIN:
            return self.managed_locations.all()
        
        if self.role == UserProfile.Role.ADMIN_PLAZA:
            return [self.location] if self.location else []
        
        return []
    
    def get_managed_stores(self):
        """
        Get all stores this user can manage
        """
        if self.role == UserProfile.Role.ADMIN:
            return Store.objects.all()
        
        if self.role == UserProfile.Role.ADMIN_PLAZA and self.location:
            return Store.objects.filter(occupancies__unit__location=self.location).distinct()
        
        if self.role == UserProfile.Role.GERENTE_LOCAL and self.store:
            return [self.store]
        
        return Store.objects.none()