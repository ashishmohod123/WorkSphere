from django.urls import path
from . import views

app_name = 'leave_management'

urlpatterns = [
    path('', views.leave_list_view, name='list'),
    path('apply/', views.apply_leave_view, name='apply'),
    path('my/', views.my_leaves_view, name='my_leaves'),
    path('<int:pk>/action/', views.leave_action_view, name='action'),
    path('types/', views.leave_type_list_view, name='leave_type_list'),
    path('types/create/', views.leave_type_create_view, name='leave_type_create'),
]
