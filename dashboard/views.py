import csv
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from datetime import date, datetime
from django.db.models import Count, Sum, Q

from accounts.models import User, UserRole
from employees.models import Employee, Department, Designation
from attendance.models import Attendance, AttendanceStatus
from leave_management.models import LeaveRequest, LeaveStatus, LeaveType
from payroll.models import Payslip, PaymentStatus
from accounts.decorators import hr_required

@login_required
def dashboard_view(request):
    user = request.user
    today = date.today()
    current_month = today.month
    current_year = today.year

    if user.role in [UserRole.ADMIN, UserRole.HR] or user.is_superuser:
        # --- EXECUTIVE / HR METRICS ---
        total_employees = Employee.objects.filter(status='ACTIVE').count()
        total_departments = Department.objects.filter(is_active=True).count()
        
        # Today attendance
        present_today = Attendance.objects.filter(date=today, status__in=[AttendanceStatus.PRESENT, AttendanceStatus.HALF_DAY]).count()
        absent_today = Attendance.objects.filter(date=today, status=AttendanceStatus.ABSENT).count()
        leave_today = Attendance.objects.filter(date=today, status=AttendanceStatus.LEAVE).count()
        
        pending_leaves_count = LeaveRequest.objects.filter(status=LeaveStatus.PENDING).count()
        
        # Monthly Payroll
        payroll_stats = Payslip.objects.filter(month=current_month, year=current_year).aggregate(
            total_net=Sum('net_salary'),
            total_gross=Sum('gross_salary')
        )
        monthly_payroll_total = payroll_stats['total_net'] or 0.00
        
        # Department Breakdown for Chart.js
        dept_data = Department.objects.annotate(
            emp_count=Count('employees', filter=Q(employees__status='ACTIVE'))
        ).values('name', 'emp_count')
        
        dept_labels = [d['name'] for d in dept_data]
        dept_counts = [d['emp_count'] for d in dept_data]

        # Recent activities
        recent_employees = Employee.objects.select_related('user', 'department', 'designation').order_by('-created_at')[:5]
        recent_leaves = LeaveRequest.objects.select_related('employee__user', 'leave_type').order_by('-applied_at')[:5]
        recent_punches = Attendance.objects.filter(date=today).select_related('employee__user').order_by('-updated_at')[:5]

        context = {
            'is_hr_admin': True,
            'total_employees': total_employees,
            'total_departments': total_departments,
            'present_today': present_today,
            'absent_today': absent_today,
            'leave_today': leave_today,
            'pending_leaves_count': pending_leaves_count,
            'monthly_payroll_total': monthly_payroll_total,
            'dept_labels': dept_labels,
            'dept_counts': dept_counts,
            'recent_employees': recent_employees,
            'recent_leaves': recent_leaves,
            'recent_punches': recent_punches,
            'today': today,
        }
    else:
        # --- EMPLOYEE DASHBOARD ---
        employee = getattr(user, 'employee_profile', None)
        today_attendance = None
        my_leaves = []
        latest_payslip = None
        
        if employee:
            today_attendance = Attendance.objects.filter(employee=employee, date=today).first()
            my_leaves = LeaveRequest.objects.filter(employee=employee).order_by('-applied_at')[:5]
            latest_payslip = Payslip.objects.filter(employee=employee).order_by('-year', '-month').first()

        context = {
            'is_hr_admin': False,
            'employee': employee,
            'today_attendance': today_attendance,
            'my_leaves': my_leaves,
            'latest_payslip': latest_payslip,
            'today': today,
        }

    return render(request, 'dashboard/index.html', context)


@login_required
@hr_required
def reports_view(request):
    return render(request, 'dashboard/reports.html')


# --- CSV EXPORT HANDLERS ---

@login_required
@hr_required
def export_employees_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="WorkSphere_Employees_{date.today()}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Employee ID', 'Full Name', 'Email', 'Phone', 'Department', 'Designation', 'Joining Date', 'Salary', 'Status'])
    
    employees = Employee.objects.select_related('user', 'department', 'designation').all()
    for emp in employees:
        writer.writerow([
            emp.employee_id,
            emp.full_name,
            emp.email,
            emp.phone,
            emp.department.name if emp.department else 'N/A',
            emp.designation.title if emp.designation else 'N/A',
            emp.joining_date,
            emp.basic_salary,
            emp.get_status_display()
        ])
    return response

@login_required
@hr_required
def export_attendance_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="WorkSphere_Attendance_{date.today()}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Employee ID', 'Full Name', 'Department', 'Check In', 'Check Out', 'Working Hours', 'Status'])
    
    records = Attendance.objects.select_related('employee__user', 'employee__department').all().order_by('-date')
    for att in records:
        writer.writerow([
            att.date,
            att.employee.employee_id,
            att.employee.full_name,
            att.employee.department.name if att.employee.department else 'N/A',
            att.check_in.strftime('%H:%M:%S') if att.check_in else 'N/A',
            att.check_out.strftime('%H:%M:%S') if att.check_out else 'N/A',
            att.working_hours,
            att.get_status_display()
        ])
    return response

@login_required
@hr_required
def export_leaves_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="WorkSphere_Leaves_{date.today()}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Employee ID', 'Full Name', 'Leave Type', 'Start Date', 'End Date', 'Days', 'Status', 'Applied At'])
    
    leaves = LeaveRequest.objects.select_related('employee__user', 'leave_type').all()
    for l in leaves:
        writer.writerow([
            l.employee.employee_id,
            l.employee.full_name,
            l.leave_type.name,
            l.start_date,
            l.end_date,
            l.total_days,
            l.get_status_display(),
            l.applied_at.strftime('%Y-%m-%d %H:%M')
        ])
    return response

@login_required
@hr_required
def export_payroll_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="WorkSphere_Payroll_{date.today()}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Month', 'Year', 'Employee ID', 'Full Name', 'Basic', 'Allowances', 'Gross', 'Deductions', 'Net Salary', 'Payment Status'])
    
    payslips = Payslip.objects.select_related('employee__user').all()
    for p in payslips:
        writer.writerow([
            p.get_month_name,
            p.year,
            p.employee.employee_id,
            p.employee.full_name,
            p.basic_salary,
            p.total_allowances,
            p.gross_salary,
            p.total_deductions,
            p.net_salary,
            p.get_payment_status_display()
        ])
    return response


def portfolio_view(request):
    """
    Public Developer Portfolio & Project Showcase for Ashish Mohod.
    Displays all full-stack projects, tech stacks, GitHub links, and live demo links.
    """
    projects = [
        {
            'title': 'WorkSphere HRMS',
            'subtitle': 'Enterprise Human Resource & Statutory Indian Payroll System',
            'icon': 'fa-solid fa-people-roof',
            'category': 'Enterprise Full-Stack / SaaS',
            'status': 'Live on Vercel',
            'status_class': 'badge-present',
            'description': 'A robust, multi-tenant capable HR Management System with 3-tier Role-Based Access Control (Admin, HR, Employee), daily biometric attendance tracking, working hours engine, multi-tier leave approval workflow, and an Indian statutory payroll engine (INR) calculating EPF, TDS, and printable payslip invoices.',
            'highlights': [
                'Statutory Indian Payroll (Basic, 40% HRA, Medical, 10% TDS, 12% EPF, PT)',
                '1-Click Punch In / Punch Out with auto-calculated daily hours',
                'Interactive Executive & Employee Dashboards with Chart.js analytics',
                'Atomic transactions & N+1 query optimization using select_related',
                'Master CSV Data Export Hub for Employees, Attendance, Leaves & Payroll'
            ],
            'technologies': ['Python 3', 'Django 5', 'Bootstrap 5', 'Chart.js', 'WhiteNoise', 'Vercel Serverless', 'PostgreSQL / SQLite'],
            'github_url': 'https://github.com/ashishmohod123/WorkSphere',
            'live_url': 'https://worksphere-hrms-lac.vercel.app/accounts/login/',
            'featured': True,
        },
        {
            'title': 'MediCure HMS Pro',
            'subtitle': 'Comprehensive Hospital & Electronic Health Records (EHR) Platform',
            'icon': 'fa-solid fa-hospital-user',
            'category': 'Healthcare & Medical Systems',
            'status': 'GitHub Active',
            'status_class': 'badge-active',
            'description': 'An enterprise clinical health management platform managing outpatient/inpatient admissions (OPD/IPD), real-time doctor appointment scheduling, patient electronic medical history, digital prescription generation, laboratory diagnostics, and integrated pharmacy billing.',
            'highlights': [
                'Doctor Scheduling & Patient Appointment Queue Management',
                'Electronic Medical Records (EMR) with prescription generator',
                'Hospital Bed & Ward Inpatient Admission Tracking',
                'Automated Hospital Billing, Pharmacy & Diagnostic Invoicing'
            ],
            'technologies': ['Python', 'Django', 'PostgreSQL', 'JavaScript', 'Bootstrap 5', 'HTML5/CSS3'],
            'github_url': 'https://github.com/ashishmohod123/MediCure-HMS-Pro',
            'live_url': 'https://github.com/ashishmohod123/MediCure-HMS-Pro',
            'featured': True,
        },
        {
            'title': 'CloudMart E-Commerce',
            'subtitle': 'Full-Stack Online Retail & Payment Processing Engine',
            'icon': 'fa-solid fa-cart-shopping',
            'category': 'FinTech & E-Commerce',
            'status': 'Open Source',
            'status_class': 'badge-probation',
            'description': 'Modern online store architecture with dynamic product categorization, facet search & filtering, real-time shopping cart session management, order tracking, and multi-gateway payments (Razorpay & Stripe) with automated transactional emails.',
            'highlights': [
                'Integrated Razorpay & Stripe Payment Gateways with Webhooks',
                'Dynamic Catalog Search with pricing & rating filters',
                'Order Lifecycle Management & Automated Invoice Generation',
                'User Ratings, Verified Reviews, and Wishlist Engine'
            ],
            'technologies': ['Python', 'Django', 'Django REST Framework', 'Stripe / Razorpay API', 'PostgreSQL', 'Redis'],
            'github_url': 'https://github.com/ashishmohod123',
            'live_url': 'https://github.com/ashishmohod123',
            'featured': False,
        },
        {
            'title': 'TaskFlow Agile Kanban',
            'subtitle': 'Real-Time Sprint & Team Collaboration Platform',
            'icon': 'fa-solid fa-list-check',
            'category': 'Productivity & Collaboration',
            'status': 'Open Source',
            'status_class': 'badge-leave',
            'description': 'Agile project tracking tool for software engineering teams featuring drag-and-drop Kanban task boards, milestone roadmaps, sprint burndown velocity charts, team permissions, and real-time activity feeds.',
            'highlights': [
                'Drag-and-Drop Kanban Task Board with status transitions',
                'Sprint Planning & Velocity Burndown Metrics',
                'Role-Based Project Workspace Permissions',
                'Task comments, attachments, and activity timelines'
            ],
            'technologies': ['Python', 'Django', 'JavaScript ES6+', 'Chart.js', 'TailwindCSS', 'WebSockets'],
            'github_url': 'https://github.com/ashishmohod123',
            'live_url': 'https://github.com/ashishmohod123',
            'featured': False,
        }
    ]
    return render(request, 'dashboard/portfolio.html', {
        'projects': projects,
        'developer_name': 'Ashish Mohod',
        'title': 'Ashish Mohod - Full Stack Python & Django Developer Portfolio',
    })

