from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='index'),
    path('portfolio/', views.portfolio_view, name='portfolio'),
    path('resume/', views.resume_view, name='resume'),
    path('reports/', views.reports_view, name='reports'),
    path('export/employees/', views.export_employees_csv, name='export_employees'),
    path('export/attendance/', views.export_attendance_csv, name='export_attendance'),
    path('export/leaves/', views.export_leaves_csv, name='export_leaves'),
    path('export/payroll/', views.export_payroll_csv, name='export_payroll'),
]
