from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    # Employees
    path('', views.employee_list_view, name='list'),
    path('create/', views.employee_create_view, name='create'),
    path('<int:pk>/', views.employee_detail_view, name='detail'),
    path('<int:pk>/edit/', views.employee_update_view, name='update'),
    path('<int:pk>/delete/', views.employee_delete_view, name='delete'),

    # Departments
    path('departments/', views.department_list_view, name='department_list'),
    path('departments/create/', views.department_create_view, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_update_view, name='department_update'),
    path('departments/<int:pk>/delete/', views.department_delete_view, name='department_delete'),

    # Designations
    path('designations/', views.designation_list_view, name='designation_list'),
    path('designations/create/', views.designation_create_view, name='designation_create'),
    path('designations/<int:pk>/edit/', views.designation_update_view, name='designation_update'),
    path('designations/<int:pk>/delete/', views.designation_delete_view, name='designation_delete'),
]
