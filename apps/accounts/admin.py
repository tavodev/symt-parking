from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile
from .forms import CustomUserCreationForm, CustomUserChangeForm


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    # Fields displayed in the user list
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active',
                    'date_joined')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('email',)

    # Fieldset configuration for the edit form
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'phone_number', 'birth_date',
                       'bio', 'profile_picture')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups',
                       'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )

    # Configuration for adding user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1',
                       'password2'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserProfile model
    """
    list_display = ('user', 'get_user_email', 'role', 'location', 'store', 'created_at')
    list_filter = ('role', 'location', 'store', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user',)
    filter_horizontal = ('managed_locations',)
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Role & Assignment', {
            'fields': ('role', 'location', 'store', 'managed_locations'),
            'description': 'Assign user role and related locations/stores based on hierarchy'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_user_email(self, obj):
        """Display user email in list view"""
        return obj.user.email
    get_user_email.short_description = 'Email'
    get_user_email.admin_order_field = 'user__email'
    
    def get_queryset(self, request):
        """Optimize queries with select_related"""
        return super().get_queryset(request).select_related(
            'user', 'location', 'store'
        ).prefetch_related('managed_locations')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Customize foreign key fields based on current user's permissions"""
        if db_field.name == "location":
            # Filter locations based on user permissions if needed
            pass
        elif db_field.name == "store":
            # Filter stores based on user permissions if needed
            pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# Inline admin for displaying UserProfile in CustomUser admin
class UserProfileInline(admin.StackedInline):
    """
    Inline admin for UserProfile to display in CustomUser admin
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile Information'
    fields = ('role', 'location', 'store', 'managed_locations')
    filter_horizontal = ('managed_locations',)


# Update CustomUserAdmin to include UserProfile inline
CustomUserAdmin.inlines = (UserProfileInline,)