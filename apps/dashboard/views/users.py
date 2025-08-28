from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db import models
from django import forms
from django.core.exceptions import PermissionDenied

from apps.accounts.models import UserProfile
from apps.locations.models import Location
from apps.stores.models.store import Store

User = get_user_model()


class UserProfileForm(forms.ModelForm):
    """
    Custom form for creating/editing users with profiles
    """
    # User fields
    first_name = forms.CharField(max_length=30, label='Nombre')
    last_name = forms.CharField(max_length=30, label='Apellidos')
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput(), label='Contraseña', required=False)
    
    class Meta:
        model = UserProfile
        fields = ['role', 'location', 'store', 'managed_locations']
        labels = {
            'role': 'Rol',
            'location': 'Plaza asignada',
            'store': 'Tienda asignada',
            'managed_locations': 'Ubicaciones gestionadas'
        }
    
    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        self.is_edit = kwargs.pop('is_edit', False)
        super().__init__(*args, **kwargs)
        
        # Set initial values from user if editing
        if self.instance.pk and hasattr(self.instance, 'user'):
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['password'].required = False
            self.fields['password'].help_text = 'Dejar en blanco para mantener la contraseña actual'
        else:
            self.fields['password'].required = True
        
        # Filter role choices based on current user permissions
        if self.request_user and hasattr(self.request_user, 'profile'):
            profile = self.request_user.profile
            allowed_roles = []
            
            if profile.role == UserProfile.Role.ADMIN:
                allowed_roles = UserProfile.Role.choices
            elif profile.role == UserProfile.Role.ADMIN_PLAZA:
                allowed_roles = [
                    (UserProfile.Role.GERENTE_LOCAL, UserProfile.Role.GERENTE_LOCAL.label),
                    (UserProfile.Role.USUARIO_LOCAL, UserProfile.Role.USUARIO_LOCAL.label)
                ]
            elif profile.role == UserProfile.Role.GERENTE_LOCAL:
                allowed_roles = [(UserProfile.Role.USUARIO_LOCAL, UserProfile.Role.USUARIO_LOCAL.label)]
            
            self.fields['role'].choices = allowed_roles
        
        # Filter location and store choices based on permissions
        self._filter_location_and_store_choices()
    
    def _filter_location_and_store_choices(self):
        """Filter location and store choices based on user permissions"""
        if not self.request_user or not hasattr(self.request_user, 'profile'):
            return
        
        profile = self.request_user.profile
        
        if profile.role == UserProfile.Role.ADMIN:
            # Admin can assign any location or store
            pass
        elif profile.role == UserProfile.Role.ADMIN_PLAZA:
            # Admin plaza can only assign their location and stores in that location
            self.fields['location'].queryset = Location.objects.filter(pk=profile.location.pk)
            if profile.location:
                # Get stores that have occupancies in this location
                self.fields['store'].queryset = Store.objects.filter(
                    occupancies__unit__location=profile.location
                ).distinct()
        elif profile.role == UserProfile.Role.GERENTE_LOCAL:
            # Gerente can only assign their store
            self.fields['store'].queryset = Store.objects.filter(pk=profile.store.pk)
            self.fields['location'].widget = forms.HiddenInput()
        
        # Hide managed_locations for non-admin users
        if profile.role != UserProfile.Role.ADMIN:
            self.fields['managed_locations'].widget = forms.HiddenInput()
    
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        location = cleaned_data.get('location')
        store = cleaned_data.get('store')
        
        # Validation based on role requirements
        if role == UserProfile.Role.ADMIN_PLAZA and not location:
            raise forms.ValidationError('Administrator de Plaza debe tener una plaza asignada.')
        
        if role in [UserProfile.Role.GERENTE_LOCAL, UserProfile.Role.USUARIO_LOCAL] and not store:
            raise forms.ValidationError('Gerente de Local y Usuario Local deben tener una tienda asignada.')
        
        return cleaned_data
    
    @transaction.atomic
    def save(self, commit=True):
        # Create or update the user first
        if hasattr(self.instance, 'user'):
            user = self.instance.user
        else:
            user = User()
        
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
        
        # Now save the profile
        profile = super().save(commit=False)
        profile.user = user
        
        if commit:
            profile.save()
            self.save_m2m()
        
        return profile


class UserListView(LoginRequiredMixin, ListView):
    model = UserProfile
    template_name = 'dashboard/users/list.html'
    context_object_name = 'user_profiles'
    paginate_by = 10
    
    def get_queryset(self):
        """Filter users based on current user's role and permissions"""
        if not hasattr(self.request.user, 'profile'):
            return UserProfile.objects.none()
        
        profile = self.request.user.profile
        
        if profile.role == UserProfile.Role.ADMIN:
            return UserProfile.objects.select_related('user', 'location', 'store').all()
        
        elif profile.role == UserProfile.Role.ADMIN_PLAZA:
            # Can see users in their location
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


class UserCreateView(LoginRequiredMixin, CreateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'dashboard/users/form.html'
    success_url = reverse_lazy('dashboard:users:list')
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user has permission to create users
        if not hasattr(request.user, 'profile'):
            raise PermissionDenied("No tienes permisos para crear usuarios.")
        
        profile = request.user.profile
        if profile.role == UserProfile.Role.USUARIO_LOCAL:
            raise PermissionDenied("No tienes permisos para crear usuarios.")
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request_user'] = self.request.user
        kwargs['is_edit'] = False
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Usuario creado exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Crear Usuario'
        context['form_action'] = 'Crear'
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'dashboard/users/form.html'
    success_url = reverse_lazy('dashboard:users:list')
    
    def dispatch(self, request, *args, **kwargs):
        # Check permissions
        obj = self.get_object()
        if not hasattr(request.user, 'profile'):
            raise PermissionDenied("No tienes permisos para editar usuarios.")
        
        if not request.user.profile.can_manage_user(obj):
            raise PermissionDenied("No tienes permisos para editar este usuario.")
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request_user'] = self.request.user
        kwargs['is_edit'] = True
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Usuario actualizado exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Editar Usuario'
        context['form_action'] = 'Actualizar'
        return context


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = UserProfile
    template_name = 'dashboard/users/delete.html'
    success_url = reverse_lazy('dashboard:users:list')
    
    def dispatch(self, request, *args, **kwargs):
        # Check permissions
        obj = self.get_object()
        if not hasattr(request.user, 'profile'):
            raise PermissionDenied("No tienes permisos para eliminar usuarios.")
        
        if not request.user.profile.can_manage_user(obj):
            raise PermissionDenied("No tienes permisos para eliminar este usuario.")
        
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        # Delete the user as well as the profile
        self.object = self.get_object()
        user = self.object.user
        self.object.delete()
        user.delete()
        messages.success(request, 'Usuario eliminado exitosamente.')
        return redirect(self.success_url)


class UserDetailView(LoginRequiredMixin, DetailView):
    template_name = 'dashboard/users/detail.html'
    context_object_name = 'user_profile'
    model = UserProfile
    
    def dispatch(self, request, *args, **kwargs):
        # Check permissions
        obj = self.get_object()
        if not hasattr(request.user, 'profile'):
            raise PermissionDenied("No tienes permisos para ver este usuario.")
        
        # Admin can see all, others can see users they can manage
        profile = request.user.profile
        if profile.role != UserProfile.Role.ADMIN:
            if not profile.can_manage_user(obj):
                raise PermissionDenied("No tienes permisos para ver este usuario.")
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data here
        return context