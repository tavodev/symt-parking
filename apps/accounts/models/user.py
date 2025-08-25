from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from django.db import models
from django.utils import timezone

from apps.accounts.managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that uses email instead of username
    """
    # Basic fields
    email = models.EmailField(unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=30, verbose_name='First name')
    last_name = models.CharField(max_length=30, verbose_name='Last name')

    # Additional custom fields
    phone_number = models.CharField(max_length=15, blank=True,
                                    verbose_name='Phone number')
    birth_date = models.DateField(null=True, blank=True,
                                  verbose_name='Birth date')
    bio = models.TextField(max_length=500, blank=True, verbose_name='Biography')
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        null=True,
        blank=True,
        verbose_name='Profile picture'
    )

    # Control fields
    is_active = models.BooleanField(default=True, verbose_name='Active')
    is_staff = models.BooleanField(default=False, verbose_name='Is staff')
    date_joined = models.DateTimeField(default=timezone.now,
                                       verbose_name='Date joined')

    # Model configuration
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Returns the user's full name"""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Returns the user's short name"""
        return self.first_name