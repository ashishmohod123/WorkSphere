from django.contrib import admin
from .models import Payslip

@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ['employee', 'month', 'year', 'basic_salary', 'gross_salary', 'net_salary', 'payment_status']
    list_filter = ['payment_status', 'year', 'month']
    search_fields = ['employee__employee_id', 'employee__user__first_name', 'employee__user__last_name']
