from django.db import models
from django.conf import settings
from django.utils import timezone
import random

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    head_of_department = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def employee_count(self):
        return self.employees.filter(status='ACTIVE').count()


class Designation(models.Model):
    title = models.CharField(max_length=100)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='designations'
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['title', 'department']
        ordering = ['title']

    def __str__(self):
        return f"{self.title} - {self.department.code}"


class EmployeeStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    INACTIVE = 'INACTIVE', 'Inactive'
    ON_LEAVE = 'ON_LEAVE', 'On Leave'
    PROBATION = 'PROBATION', 'Probation'
    TERMINATED = 'TERMINATED', 'Terminated'


class Gender(models.TextChoices):
    MALE = 'MALE', 'Male'
    FEMALE = 'FEMALE', 'Female'
    OTHER = 'OTHER', 'Other'


class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile'
    )
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )
    designation = models.ForeignKey(
        Designation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )
    joining_date = models.DateField(default=timezone.now)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.MALE)
    blood_group = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Financial details
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Status & Profile
    status = models.CharField(
        max_length=20,
        choices=EmployeeStatus.choices,
        default=EmployeeStatus.ACTIVE
    )
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.employee_id:
            # Auto generate employee ID if not provided, e.g. WS-1045
            rand_num = random.randint(1000, 9999)
            self.employee_id = f"WS-{rand_num}"
            while Employee.objects.filter(employee_id=self.employee_id).exists():
                rand_num = random.randint(1000, 9999)
                self.employee_id = f"WS-{rand_num}"
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def email(self):
        return self.user.email

    @property
    def get_avatar(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        elif self.user.profile_picture and hasattr(self.user.profile_picture, 'url'):
            return self.user.profile_picture.url
        return f"https://ui-avatars.com/api/?name={self.full_name}&background=3b82f6&color=fff"

    @property
    def get_status_badge(self):
        badges = {
            EmployeeStatus.ACTIVE: 'badge-active',
            EmployeeStatus.INACTIVE: 'badge-inactive',
            EmployeeStatus.ON_LEAVE: 'badge-leave',
            EmployeeStatus.PROBATION: 'badge-probation',
            EmployeeStatus.TERMINATED: 'badge-terminated',
        }
        return badges.get(self.status, 'bg-secondary')

    def __str__(self):
        return f"{self.full_name} ({self.employee_id})"

