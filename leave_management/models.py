from django.db import models
from employees.models import Employee
from django.conf import settings
from django.utils import timezone

class LeaveType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10, unique=True)
    days_allowed = models.PositiveIntegerField(default=12, help_text="Total days permitted per year")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.days_allowed} days)"


class LeaveStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending Approval'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'
    CANCELLED = 'CANCELLED', 'Cancelled'


class LeaveRequest(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        related_name='requests'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.PositiveIntegerField(default=1)
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=LeaveStatus.choices,
        default=LeaveStatus.PENDING
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_leave_requests'
    )
    review_remarks = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-applied_at']

    def save(self, *args, **kwargs):
        if self.start_date and self.end_date:
            delta = (self.end_date - self.start_date).days + 1
            self.total_days = max(1, delta)
        super().save(*args, **kwargs)

    @property
    def get_status_badge(self):
        badges = {
            LeaveStatus.PENDING: 'badge-pending',
            LeaveStatus.APPROVED: 'badge-approved',
            LeaveStatus.REJECTED: 'badge-rejected',
            LeaveStatus.CANCELLED: 'badge-cancelled',
        }
        return badges.get(self.status, 'bg-secondary')

    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} ({self.status})"

