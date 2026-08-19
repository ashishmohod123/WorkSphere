from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date, datetime
from .models import Attendance, AttendanceStatus
from .forms import AttendanceMarkForm
from employees.models import Employee
from accounts.decorators import hr_required

@login_required
def attendance_list_view(request):
    selected_date_str = request.GET.get('date', '')
    if selected_date_str:
        try:
            target_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            target_date = date.today()
    else:
        target_date = date.today()

    status_filter = request.GET.get('status', '')
    search_q = request.GET.get('q', '')

    attendances = Attendance.objects.filter(date=target_date).select_related('employee__user', 'employee__department')
    
    if status_filter:
        attendances = attendances.filter(status=status_filter)
        
    if search_q:
        attendances = attendances.filter(
            employee__user__first_name__icontains=search_q
        ) | attendances.filter(
            employee__user__last_name__icontains=search_q
        ) | attendances.filter(
            employee__employee_id__icontains=search_q
        )

    # Statistics for the selected day
    total_active_employees = Employee.objects.filter(status='ACTIVE').count()
    present_count = Attendance.objects.filter(date=target_date, status__in=[AttendanceStatus.PRESENT, AttendanceStatus.HALF_DAY]).count()
    absent_count = Attendance.objects.filter(date=target_date, status=AttendanceStatus.ABSENT).count()
    leave_count = Attendance.objects.filter(date=target_date, status=AttendanceStatus.LEAVE).count()

    return render(request, 'attendance/attendance_list.html', {
        'attendances': attendances,
        'target_date': target_date.strftime('%Y-%m-%d'),
        'status_filter': status_filter,
        'search_q': search_q,
        'total_active': total_active_employees,
        'present_count': present_count,
        'absent_count': absent_count,
        'leave_count': leave_count,
        'statuses': AttendanceStatus.choices,
    })

@login_required
def quick_check_in_view(request):
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, "No linked employee profile found for this account.")
        return redirect('dashboard:index')
        
    employee = request.user.employee_profile
    today = date.today()
    now_time = datetime.now().time()

    attendance, created = Attendance.objects.get_or_create(
        employee=employee,
        date=today,
        defaults={'check_in': now_time, 'status': AttendanceStatus.PRESENT}
    )

    if not created and attendance.check_in:
        messages.warning(request, f"You already clocked in today at {attendance.check_in.strftime('%H:%M:%S')}.")
    else:
        attendance.check_in = now_time
        attendance.status = AttendanceStatus.PRESENT
        attendance.save()
        messages.success(request, f"Punch In recorded successfully at {now_time.strftime('%H:%M:%S')}.")
        
    return redirect('dashboard:index')

@login_required
def quick_check_out_view(request):
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, "No linked employee profile found for this account.")
        return redirect('dashboard:index')
        
    employee = request.user.employee_profile
    today = date.today()
    now_time = datetime.now().time()

    try:
        attendance = Attendance.objects.get(employee=employee, date=today)
        if attendance.check_out:
            messages.warning(request, f"You already clocked out today at {attendance.check_out.strftime('%H:%M:%S')}.")
        else:
            attendance.check_out = now_time
            attendance.save() # Automatically calculates working_hours
            messages.success(request, f"Punch Out recorded at {now_time.strftime('%H:%M:%S')}. Total Hours: {attendance.working_hours} hrs.")
    except Attendance.DoesNotExist:
        messages.error(request, "You have not clocked in today yet.")
        
    return redirect('dashboard:index')

@login_required
@hr_required
def mark_attendance_view(request):
    if request.method == 'POST':
        form = AttendanceMarkForm(request.POST)
        if form.is_valid():
            try:
                attendance = form.save()
                messages.success(request, f"Attendance record saved for {attendance.employee.full_name}.")
                return redirect('attendance:list')
            except Exception as e:
                messages.error(request, f"Record already exists or error: {str(e)}")
        else:
            messages.error(request, "Please check the form inputs.")
    else:
        form = AttendanceMarkForm(initial={'date': date.today()})
        
    return render(request, 'attendance/mark_attendance.html', {'form': form})

@login_required
def my_attendance_view(request):
    if not hasattr(request.user, 'employee_profile'):
        messages.info(request, "You are an administrator without a direct employee log.")
        return redirect('attendance:list')
        
    employee = request.user.employee_profile
    attendances = Attendance.objects.filter(employee=employee).order_by('-date')[:30]
    
    total_present = Attendance.objects.filter(employee=employee, status=AttendanceStatus.PRESENT).count()
    total_halfday = Attendance.objects.filter(employee=employee, status=AttendanceStatus.HALF_DAY).count()
    total_absent = Attendance.objects.filter(employee=employee, status=AttendanceStatus.ABSENT).count()
    
    return render(request, 'attendance/my_attendance.html', {
        'employee': employee,
        'attendances': attendances,
        'total_present': total_present,
        'total_halfday': total_halfday,
        'total_absent': total_absent,
    })
