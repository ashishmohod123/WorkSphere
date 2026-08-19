from django.db import models
from django.contrib.auth.models import AbstractUser

class UserRole(models.TextChoices):
    ADMIN = 'ADMIN', 'Administrator'
    HR = 'HR', 'HR Manager'
    EMPLOYEE = 'EMPLOYEE', 'Employee'

class User(AbstractUser):
    """
    Custom User model extending Django AbstractUser with enterprise RBAC roles.
    """
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.EMPLOYEE,
        help_text="Role determining access permissions within WorkSphere."
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN or self.is_superuser

    @property
    def is_hr(self):
        return self.role in [UserRole.HR, UserRole.ADMIN] or self.is_superuser

    @property
    def is_employee(self):
        return self.role == UserRole.EMPLOYEE

    @property
    def get_role_badge(self):
        badges = {
            UserRole.ADMIN: 'bg-danger',
            UserRole.HR: 'bg-primary',
            UserRole.EMPLOYEE: 'bg-info text-dark',
        }
        return badges.get(self.role, 'bg-secondary')

    @property
    def get_avatar_url(self):
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return f"https://ui-avatars.com/api/?name={self.get_full_name() or self.username}&background=2563eb&color=fff"

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

