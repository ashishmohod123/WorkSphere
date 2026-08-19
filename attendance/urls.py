from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_list_view, name='list'),
    path('check-in/', views.quick_check_in_view, name='check_in'),
    path('check-out/', views.quick_check_out_view, name='check_out'),
    path('mark/', views.mark_attendance_view, name='mark'),
    path('my/', views.my_attendance_view, name='my_attendance'),
]
