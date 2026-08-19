from django.urls import path
from . import views

app_name = 'payroll'

urlpatterns = [
    path('', views.payroll_list_view, name='list'),
    path('generate/', views.generate_monthly_payroll_view, name='generate'),
    path('create/', views.payslip_create_view, name='create'),
    path('<int:pk>/', views.payslip_detail_view, name='detail'),
    path('<int:pk>/status/', views.payslip_status_toggle_view, name='status_toggle'),
    path('my/', views.my_payslips_view, name='my_payslips'),
]
