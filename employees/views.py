from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.db import transaction
from .models import Department, Designation, Employee, EmployeeStatus
from .forms import DepartmentForm, DesignationForm, EmployeeCreateForm, EmployeeUpdateForm
from accounts.models import User, UserRole
from accounts.decorators import hr_required, admin_required

# --- EMPLOYEE VIEWS ---

@login_required
def employee_list_view(request):
    employees = Employee.objects.select_related('user', 'department', 'designation').all()
    
    # Search Filter
    search_query = request.GET.get('q', '')
    if search_query:
        employees = employees.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(employee_id__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
        
    # Department Filter
    dept_id = request.GET.get('department')
    if dept_id:
        employees = employees.filter(department_id=dept_id)
        
    # Status Filter
    status = request.GET.get('status')
    if status:
        employees = employees.filter(status=status)
        
    departments = Department.objects.filter(is_active=True)
    statuses = EmployeeStatus.choices
    
    return render(request, 'employees/employee_list.html', {
        'employees': employees,
        'departments': departments,
        'statuses': statuses,
        'search_query': search_query,
        'selected_dept': dept_id,
        'selected_status': status,
        'total_count': employees.count(),
    })

@login_required
def employee_detail_view(request, pk):
    employee = get_object_or_404(
        Employee.objects.select_related('user', 'department', 'designation'),
        pk=pk
    )
    
    # Restrict employees to only view their own profile unless HR/Admin
    if request.user.role == UserRole.EMPLOYEE and employee.user != request.user:
        messages.error(request, "You can only view your own profile.")
        return redirect('dashboard:index')
        
    recent_attendance = employee.attendances.all()[:10]
    recent_leaves = employee.leave_requests.all()[:10]
    recent_payslips = employee.payslips.all()[:6]
    
    return render(request, 'employees/employee_detail.html', {
        'employee': employee,
        'recent_attendance': recent_attendance,
        'recent_leaves': recent_leaves,
        'recent_payslips': recent_payslips,
    })

@login_required
@hr_required
def employee_create_view(request):
    if request.method == 'POST':
        form = EmployeeCreateForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # 1. Create User
                    username = form.cleaned_data['username']
                    email = form.cleaned_data['email']
                    password = form.cleaned_data['password']
                    first_name = form.cleaned_data['first_name']
                    last_name = form.cleaned_data['last_name']
                    role = form.cleaned_data['role']
                    
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        role=role
                    )
                    
                    # 2. Create Employee profile
                    employee = form.save(commit=False)
                    employee.user = user
                    employee.save()
                    
                    messages.success(request, f"Employee {employee.full_name} ({employee.employee_id}) created successfully!")
                    return redirect('employees:detail', pk=employee.pk)
            except Exception as e:
                messages.error(request, f"Error creating employee: {str(e)}")
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = EmployeeCreateForm()
        
    return render(request, 'employees/employee_form.html', {
        'form': form,
        'title': 'Add New Employee'
    })

@login_required
@hr_required
def employee_update_view(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    user = employee.user
    
    if request.method == 'POST':
        form = EmployeeUpdateForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            
            form.save()
            messages.success(request, f"Employee details for {employee.full_name} updated successfully.")
            return redirect('employees:detail', pk=employee.pk)
        else:
            messages.error(request, "Please review form errors.")
    else:
        initial_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        form = EmployeeUpdateForm(instance=employee, initial=initial_data)
        
    return render(request, 'employees/employee_form.html', {
        'form': form,
        'title': f'Edit Employee: {employee.full_name}',
        'employee': employee
    })

@login_required
@admin_required
def employee_delete_view(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        name = employee.full_name
        employee.user.delete() # Deletes user and cascades to employee profile
        messages.success(request, f"Employee {name} removed successfully.")
        return redirect('employees:list')
    return render(request, 'employees/employee_confirm_delete.html', {'employee': employee})


# --- DEPARTMENT VIEWS ---

@login_required
@hr_required
def department_list_view(request):
    departments = Department.objects.annotate(
        total_staff=Count('employees', filter=Q(employees__status='ACTIVE'))
    ).all()
    return render(request, 'employees/department_list.html', {'departments': departments})

@login_required
@hr_required
def department_create_view(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Department created successfully.")
            return redirect('employees:department_list')
    else:
        form = DepartmentForm()
    return render(request, 'employees/department_form.html', {'form': form, 'title': 'Create Department'})

@login_required
@hr_required
def department_update_view(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=dept)
        if form.is_valid():
            form.save()
            messages.success(request, "Department updated successfully.")
            return redirect('employees:department_list')
    else:
        form = DepartmentForm(instance=dept)
    return render(request, 'employees/department_form.html', {'form': form, 'title': f'Edit Department: {dept.name}'})

@login_required
@admin_required
def department_delete_view(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        name = dept.name
        dept.delete()
        messages.success(request, f"Department '{name}' deleted.")
        return redirect('employees:department_list')
    return render(request, 'employees/confirm_delete.html', {'object': dept, 'type': 'Department'})


# --- DESIGNATION VIEWS ---

@login_required
@hr_required
def designation_list_view(request):
    designations = Designation.objects.select_related('department').all()
    return render(request, 'employees/designation_list.html', {'designations': designations})

@login_required
@hr_required
def designation_create_view(request):
    if request.method == 'POST':
        form = DesignationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Designation created successfully.")
            return redirect('employees:designation_list')
    else:
        form = DesignationForm()
    return render(request, 'employees/designation_form.html', {'form': form, 'title': 'Create Designation'})

@login_required
@hr_required
def designation_update_view(request, pk):
    desig = get_object_or_404(Designation, pk=pk)
    if request.method == 'POST':
        form = DesignationForm(request.POST, instance=desig)
        if form.is_valid():
            form.save()
            messages.success(request, "Designation updated successfully.")
            return redirect('employees:designation_list')
    else:
        form = DesignationForm(instance=desig)
    return render(request, 'employees/designation_form.html', {'form': form, 'title': f'Edit Designation: {desig.title}'})

@login_required
@admin_required
def designation_delete_view(request, pk):
    desig = get_object_or_404(Designation, pk=pk)
    if request.method == 'POST':
        title = desig.title
        desig.delete()
        messages.success(request, f"Designation '{title}' deleted.")
        return redirect('employees:designation_list')
    return render(request, 'employees/confirm_delete.html', {'object': desig, 'type': 'Designation'})
