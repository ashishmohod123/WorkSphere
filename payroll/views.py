from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from datetime import date
from decimal import Decimal
from .models import Payslip, PaymentStatus, PaymentMethod
from .forms import PayslipCreateForm, GenerateMonthlyPayrollForm
from employees.models import Employee
from accounts.decorators import hr_required

@login_required
def payroll_list_view(request):
    current_year = date.today().year
    current_month = date.today().month

    year_filter = request.GET.get('year', str(current_year))
    month_filter = request.GET.get('month', str(current_month))
    status_filter = request.GET.get('status', '')

    payslips = Payslip.objects.select_related('employee__user', 'employee__department', 'employee__designation').all()

    if year_filter:
        payslips = payslips.filter(year=year_filter)
    if month_filter:
        payslips = payslips.filter(month=month_filter)
    if status_filter:
        payslips = payslips.filter(payment_status=status_filter)

    totals = payslips.aggregate(
        total_gross=Sum('gross_salary'),
        total_deductions=Sum('tax_deduction') + Sum('provident_fund') + Sum('other_deductions'),
        total_net=Sum('net_salary')
    )

    months = [(i, m) for i, m in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December'], 1)]
    years = [2024, 2025, 2026, 2027]

    return render(request, 'payroll/payroll_list.html', {
        'payslips': payslips,
        'year_filter': int(year_filter) if year_filter else current_year,
        'month_filter': int(month_filter) if month_filter else current_month,
        'status_filter': status_filter,
        'months': months,
        'years': years,
        'statuses': PaymentStatus.choices,
        'total_gross': totals['total_gross'] or Decimal('0.00'),
        'total_net': totals['total_net'] or Decimal('0.00'),
        'total_deductions': totals['total_deductions'] or Decimal('0.00'),
        'gen_form': GenerateMonthlyPayrollForm(initial={'month': current_month, 'year': current_year})
    })

@login_required
@hr_required
def generate_monthly_payroll_view(request):
    if request.method == 'POST':
        form = GenerateMonthlyPayrollForm(request.POST)
        if form.is_valid():
            month = int(form.cleaned_data['month'])
            year = int(form.cleaned_data['year'])
            
            active_employees = Employee.objects.filter(status='ACTIVE')
            generated_count = 0
            
            for emp in active_employees:
                if not Payslip.objects.filter(employee=emp, month=month, year=year).exists():
                    # Indian Salary Structure Breakdown
                    basic = emp.basic_salary
                    hra = basic * Decimal('0.40')               # 40% HRA
                    medical = Decimal('2500.00')                 # Fixed Medical / Conveyance
                    special = basic * Decimal('0.15')            # 15% Special Allowance
                    tax = basic * Decimal('0.10')                # 10% TDS
                    pf = basic * Decimal('0.12')                 # 12% Employee Provident Fund
                    pt = Decimal('200.00')                       # ₹200 Professional Tax

                    Payslip.objects.create(
                        employee=emp,
                        month=month,
                        year=year,
                        basic_salary=basic,
                        hra=hra,
                        medical_allowance=medical,
                        special_allowance=special,
                        tax_deduction=tax,
                        provident_fund=pf,
                        other_deductions=pt,
                        payment_status=PaymentStatus.UNPAID
                    )
                    generated_count += 1
                    
            if generated_count > 0:
                messages.success(request, f"Generated {generated_count} Indian INR payslips for {month}/{year}.")
            else:
                messages.info(request, "Payslips for this month have already been generated for all active staff.")
                
            return redirect('payroll:list')
    return redirect('payroll:list')

@login_required
@hr_required
def payslip_create_view(request):
    if request.method == 'POST':
        form = PayslipCreateForm(request.POST)
        if form.is_valid():
            payslip = form.save()
            messages.success(request, f"Payslip created for {payslip.employee.full_name}.")
            return redirect('payroll:detail', pk=payslip.pk)
    else:
        form = PayslipCreateForm()
    return render(request, 'payroll/payslip_form.html', {'form': form, 'title': 'Create Custom Payslip (INR ₹)'})

@login_required
def payslip_detail_view(request, pk):
    payslip = get_object_or_404(Payslip.objects.select_related('employee__user', 'employee__department', 'employee__designation'), pk=pk)
    
    if request.user.role == 'EMPLOYEE' and payslip.employee.user != request.user:
        messages.error(request, "Access restricted to your own payslips.")
        return redirect('dashboard:index')
        
    return render(request, 'payroll/payslip_detail.html', {'payslip': payslip})

@login_required
@hr_required
def payslip_status_toggle_view(request, pk):
    payslip = get_object_or_404(Payslip, pk=pk)
    new_status = request.POST.get('status', PaymentStatus.PAID)
    payslip.payment_status = new_status
    if new_status == PaymentStatus.PAID:
        payslip.payment_date = date.today()
    payslip.save()
    messages.success(request, f"Payslip for {payslip.employee.full_name} updated to {new_status}.")
    return redirect('payroll:list')

@login_required
def my_payslips_view(request):
    if not hasattr(request.user, 'employee_profile'):
        messages.info(request, "Administrator account.")
        return redirect('payroll:list')
        
    employee = request.user.employee_profile
    payslips = Payslip.objects.filter(employee=employee).order_by('-year', '-month')
    
    return render(request, 'payroll/my_payslips.html', {
        'employee': employee,
        'payslips': payslips,
    })
