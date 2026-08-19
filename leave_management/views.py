from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import LeaveRequest, LeaveType, LeaveStatus
from .forms import LeaveRequestApplyForm, LeaveActionForm, LeaveTypeForm
from employees.models import Employee
from accounts.decorators import hr_required

@login_required
def leave_list_view(request):
    status_filter = request.GET.get('status', '')
    leaves = LeaveRequest.objects.select_related('employee__user', 'employee__department', 'leave_type').all()
    
    if status_filter:
        leaves = leaves.filter(status=status_filter)
        
    pending_count = LeaveRequest.objects.filter(status=LeaveStatus.PENDING).count()
    approved_count = LeaveRequest.objects.filter(status=LeaveStatus.APPROVED).count()
    rejected_count = LeaveRequest.objects.filter(status=LeaveStatus.REJECTED).count()
    
    return render(request, 'leave_management/leave_list.html', {
        'leaves': leaves,
        'status_filter': status_filter,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'statuses': LeaveStatus.choices,
    })

@login_required
def apply_leave_view(request):
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, "Only registered employees can submit leave applications.")
        return redirect('dashboard:index')
        
    employee = request.user.employee_profile
    if request.method == 'POST':
        form = LeaveRequestApplyForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = employee
            leave.status = LeaveStatus.PENDING
            leave.save()
            messages.success(request, "Your leave application has been submitted to HR for review.")
            return redirect('leave_management:my_leaves')
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = LeaveRequestApplyForm()
        
    return render(request, 'leave_management/apply_leave.html', {'form': form})

@login_required
def my_leaves_view(request):
    if not hasattr(request.user, 'employee_profile'):
        messages.info(request, "Administrator account.")
        return redirect('leave_management:list')
        
    employee = request.user.employee_profile
    leaves = LeaveRequest.objects.filter(employee=employee).select_related('leave_type')
    
    return render(request, 'leave_management/my_leaves.html', {
        'employee': employee,
        'leaves': leaves,
    })

@login_required
@hr_required
def leave_action_view(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        remarks = request.POST.get('remarks', '')
        
        if action == 'APPROVE':
            leave.status = LeaveStatus.APPROVED
            leave.review_remarks = remarks
            leave.reviewed_by = request.user
            leave.reviewed_at = timezone.now()
            leave.save()
            messages.success(request, f"Leave application for {leave.employee.full_name} has been APPROVED.")
        elif action == 'REJECT':
            leave.status = LeaveStatus.REJECTED
            leave.review_remarks = remarks
            leave.reviewed_by = request.user
            leave.reviewed_at = timezone.now()
            leave.save()
            messages.warning(request, f"Leave application for {leave.employee.full_name} has been REJECTED.")
            
        return redirect('leave_management:list')
        
    return render(request, 'leave_management/leave_review.html', {'leave': leave})

@login_required
@hr_required
def leave_type_list_view(request):
    leave_types = LeaveType.objects.all()
    return render(request, 'leave_management/leave_type_list.html', {'leave_types': leave_types})

@login_required
@hr_required
def leave_type_create_view(request):
    if request.method == 'POST':
        form = LeaveTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New Leave Category added.")
            return redirect('leave_management:leave_type_list')
    else:
        form = LeaveTypeForm()
    return render(request, 'leave_management/leave_type_form.html', {'form': form})
