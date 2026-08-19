from django.db import models
from employees.models import Employee
from django.utils import timezone
from datetime import datetime, date

class AttendanceStatus(models.TextChoices):
    PRESENT = 'PRESENT', 'Present'
    ABSENT = 'ABSENT', 'Absent'
    HALF_DAY = 'HALF_DAY', 'Half Day'
    LEAVE = 'LEAVE', 'On Leave'
    HOLIDAY = 'HOLIDAY', 'Holiday'

class Attendance(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    date = models.DateField(default=date.today)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT
    )
    working_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Calculated total working hours"
    )
    notes = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['employee', 'date']
        ordering = ['-date', 'employee__employee_id']

    def calculate_hours(self):
        if self.check_in and self.check_out:
            today = date.today()
            dt_in = datetime.combine(today, self.check_in)
            dt_out = datetime.combine(today, self.check_out)
            if dt_out >= dt_in:
                diff = dt_out - dt_in
                hours = diff.total_seconds() / 3600.0
                return round(hours, 2)
        return 0.00

    def save(self, *args, **kwargs):
        if self.check_in and self.check_out:
            self.working_hours = self.calculate_hours()
            if self.working_hours < 4.0:
                self.status = AttendanceStatus.HALF_DAY
            else:
                self.status = AttendanceStatus.PRESENT
        super().save(*args, **kwargs)

    @property
    def get_status_badge(self):
        badges = {
            AttendanceStatus.PRESENT: 'badge-present',
            AttendanceStatus.ABSENT: 'badge-absent',
            AttendanceStatus.HALF_DAY: 'badge-halfday',
            AttendanceStatus.LEAVE: 'badge-leave',
            AttendanceStatus.HOLIDAY: 'badge-holiday',
        }
        return badges.get(self.status, 'bg-secondary')

    def __str__(self):
        return f"{self.employee.full_name} - {self.date} ({self.status})"

