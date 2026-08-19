from django.contrib import admin
from .models import LeaveType, LeaveRequest

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'days_allowed', 'is_active']

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'total_days', 'status', 'applied_at']
    list_filter = ['status', 'leave_type']
    search_fields = ['employee__employee_id', 'employee__user__first_name', 'employee__user__last_name']
