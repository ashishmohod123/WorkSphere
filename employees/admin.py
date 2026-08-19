from django.contrib import admin
from .models import Department, Designation, Employee

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'head_of_department', 'is_active', 'created_at']
    search_fields = ['name', 'code']

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'is_active']
    list_filter = ['department', 'is_active']
    search_fields = ['title']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'full_name', 'department', 'designation', 'basic_salary', 'status', 'joining_date']
    list_filter = ['department', 'designation', 'status']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name', 'user__email']
