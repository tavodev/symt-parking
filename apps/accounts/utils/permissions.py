from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from apps.accounts.models import UserProfile


def role_required(*roles):
    """
    Decorator that requires the user to have one of the specified roles.
    Usage: @role_required(UserProfile.Role.ADMIN, UserProfile.Role.ADMIN_PLAZA)
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not hasattr(request.user, 'profile'):
                raise PermissionDenied("Usuario no tiene perfil asignado.")
            
            if request.user.profile.role not in roles:
                raise PermissionDenied("No tienes permisos para acceder a esta función.")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def can_manage_user_required(view_func):
    """
    Decorator that requires the user to be able to manage the target user.
    Expects a 'pk' parameter in the URL that refers to a UserProfile.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            raise PermissionDenied("Usuario no tiene perfil asignado.")
        
        # Get the target user profile
        target_profile_pk = kwargs.get('pk')
        if not target_profile_pk:
            raise PermissionDenied("ID de usuario no especificado.")
        
        target_profile = get_object_or_404(UserProfile, pk=target_profile_pk)
        
        if not request.user.profile.can_manage_user(target_profile):
            raise PermissionDenied("No tienes permisos para gestionar este usuario.")
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


class RoleRequiredMixin(LoginRequiredMixin):
    """
    Mixin that requires the user to have one of the specified roles.
    Usage: class MyView(RoleRequiredMixin, View): required_roles = [UserProfile.Role.ADMIN]
    """
    required_roles = []
    
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            raise PermissionDenied("Usuario no tiene perfil asignado.")
        
        if self.required_roles and request.user.profile.role not in self.required_roles:
            raise PermissionDenied("No tienes permisos para acceder a esta función.")
        
        return super().dispatch(request, *args, **kwargs)


class CanManageUserMixin(LoginRequiredMixin):
    """
    Mixin that requires the user to be able to manage the target user.
    Expects a 'pk' parameter in the URL that refers to a UserProfile.
    """
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            raise PermissionDenied("Usuario no tiene perfil asignado.")
        
        # Get the target user profile
        target_profile_pk = kwargs.get('pk')
        if target_profile_pk:
            target_profile = get_object_or_404(UserProfile, pk=target_profile_pk)
            
            if not request.user.profile.can_manage_user(target_profile):
                raise PermissionDenied("No tienes permisos para gestionar este usuario.")
        
        return super().dispatch(request, *args, **kwargs)


class UserManagementMixin(LoginRequiredMixin):
    """
    Mixin that provides common functionality for user management views.
    Filters querysets based on the current user's role and permissions.
    """
    
    def get_user_queryset(self):
        """
        Get a filtered queryset of users based on current user's permissions
        """
        if not hasattr(self.request.user, 'profile'):
            return UserProfile.objects.none()
        
        profile = self.request.user.profile
        
        if profile.role == UserProfile.Role.ADMIN:
            return UserProfile.objects.select_related('user', 'location', 'store').all()
        
        elif profile.role == UserProfile.Role.ADMIN_PLAZA:
            # Can see users in their location
            from django.db import models
            return UserProfile.objects.select_related('user', 'location', 'store').filter(
                models.Q(location=profile.location) | 
                models.Q(store__occupancies__unit__location=profile.location)
            ).distinct()
        
        elif profile.role == UserProfile.Role.GERENTE_LOCAL:
            # Can only see users in their store
            return UserProfile.objects.select_related('user', 'location', 'store').filter(
                store=profile.store
            )
        
        return UserProfile.objects.none()
    
    def get_allowed_roles_for_creation(self):
        """
        Get the roles that the current user can create
        """
        if not hasattr(self.request.user, 'profile'):
            return []
        
        profile = self.request.user.profile
        
        if profile.role == UserProfile.Role.ADMIN:
            return list(UserProfile.Role.choices)
        elif profile.role == UserProfile.Role.ADMIN_PLAZA:
            return [
                (UserProfile.Role.GERENTE_LOCAL, UserProfile.Role.GERENTE_LOCAL.label),
                (UserProfile.Role.USUARIO_LOCAL, UserProfile.Role.USUARIO_LOCAL.label)
            ]
        elif profile.role == UserProfile.Role.GERENTE_LOCAL:
            return [(UserProfile.Role.USUARIO_LOCAL, UserProfile.Role.USUARIO_LOCAL.label)]
        
        return []
    
    def can_create_users(self):
        """
        Check if the current user can create users
        """
        if not hasattr(self.request.user, 'profile'):
            return False
        
        profile = self.request.user.profile
        return profile.role != UserProfile.Role.USUARIO_LOCAL


class AdminOnlyMixin(RoleRequiredMixin):
    """Shortcut mixin for admin-only views"""
    required_roles = [UserProfile.Role.ADMIN]


class AdminOrPlazaAdminMixin(RoleRequiredMixin):
    """Shortcut mixin for admin or plaza admin views"""
    required_roles = [UserProfile.Role.ADMIN, UserProfile.Role.ADMIN_PLAZA]


class ManagerOrAboveMixin(RoleRequiredMixin):
    """Shortcut mixin for manager-level and above access"""
    required_roles = [
        UserProfile.Role.ADMIN, 
        UserProfile.Role.ADMIN_PLAZA, 
        UserProfile.Role.GERENTE_LOCAL
    ]