from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, time, timedelta
from decimal import Decimal
import random

from accounts.models import User, UserRole
from employees.models import Department, Designation, Employee, EmployeeStatus, Gender
from attendance.models import Attendance, AttendanceStatus
from leave_management.models import LeaveType, LeaveRequest, LeaveStatus
from payroll.models import Payslip, PaymentStatus, PaymentMethod

class Command(BaseCommand):
    help = "Seed WorkSphere database with 100% Indian company, employees and INR salary data"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Flushing and re-seeding WorkSphere database with Indian records..."))

        # Clean existing records to avoid duplicates
        Payslip.objects.all().delete()
        LeaveRequest.objects.all().delete()
        LeaveType.objects.all().delete()
        Attendance.objects.all().delete()
        Employee.objects.all().delete()
        Designation.objects.all().delete()
        Department.objects.all().delete()
        User.objects.all().delete()

        # 1. Create Superuser / Admin (ashish.mohod)
        admin_user = User.objects.create(
            username='admin',
            email='ashish.mohod@worksphere.in',
            first_name='Aarav',
            last_name='Sharma',
            role=UserRole.ADMIN,
            phone='+91 98201 12345',
            is_staff=True,
            is_superuser=True,
        )
        admin_user.set_password('admin123')
        admin_user.save()
        self.stdout.write(self.style.SUCCESS("Created Admin: admin (ashish.mohod) / admin123"))

        # 2. Create HR Manager (Pooja Verma)
        hr_user = User.objects.create(
            username='hr_pooja',
            email='pooja.verma@worksphere.in',
            first_name='Pooja',
            last_name='Verma',
            role=UserRole.HR,
            phone='+91 98450 67890',
            is_staff=True,
        )
        hr_user.set_password('hr12345')
        hr_user.save()
        self.stdout.write(self.style.SUCCESS("Created HR Manager: hr_pooja (Pooja Verma) / hr12345"))

        # 3. Create Departments (Indian corporate structure)
        depts_data = [
            ('Information Technology & Engineering', 'ENG', 'Software Engineering, Full Stack, Cloud & Data Platforms'),
            ('Human Resources & Talent', 'HR', 'Talent Acquisition, Employee Relations, Engagement & Culture'),
            ('Marketing & Business Growth', 'MKT', 'Digital Marketing, Enterprise Sales & Client Partnerships'),
            ('Finance & Corporate Accounts', 'FIN', 'Corporate Tax, Financial Compliance, Audits & Payroll Management'),
            ('Product Strategy & UI/UX Design', 'PRD', 'Product Strategy, UX Research, Interaction Design & Prototyping'),
        ]
        departments = {}
        for name, code, desc in depts_data:
            dept = Department.objects.create(
                name=name,
                code=code,
                description=desc,
                head_of_department=admin_user
            )
            departments[code] = dept

        # 4. Create Designations
        desigs_data = [
            ('Lead Python & Django Architect', 'ENG', 'Enterprise backend architecture and scalability'),
            ('Senior Full Stack Developer', 'ENG', 'Python, Django, React and PostgreSQL development'),
            ('DevOps & Cloud Engineer', 'ENG', 'AWS, Docker, CI/CD pipelines & monitoring'),
            ('Associate QA Automation Engineer', 'ENG', 'Automated testing and quality assurance'),
            ('HR Business Partner', 'HR', 'Strategic HR planning and employee growth'),
            ('Talent Acquisition Specialist', 'HR', 'Campus and lateral hiring for engineering talent'),
            ('AVP Business Development', 'MKT', 'Pan-India enterprise client relationships'),
            ('Growth Marketing Manager', 'MKT', 'SEO, SEM, social growth and branding'),
            ('Financial Controller & Tax Lead', 'FIN', 'Direct/Indirect taxation, GST & TDS management'),
            ('Senior Payroll Accountant', 'FIN', 'EPF, ESI, gratuity & monthly salary disbursement'),
            ('Principal Product Designer', 'PRD', 'Design system, Figma UI/UX wireframes and user testing'),
        ]
        designations = {}
        for title, dept_code, desc in desigs_data:
            desig = Designation.objects.create(
                title=title,
                department=departments[dept_code],
                description=desc
            )
            designations[title] = desig

        # 5. Create Indian Employees with INR Monthly Salaries
        staff_data = [
            ('rohit_v', 'emp12345', 'Rohit', 'Verma', 'rohit.verma@worksphere.in', 'ENG', 'Lead Python & Django Architect', 125000.00, '+91 98200 11223', 'Bengaluru, Karnataka', 'WS-1001', 'O+', Gender.MALE),
            ('ananya_d', 'emp12345', 'Ananya', 'Deshmukh', 'ananya.deshmukh@worksphere.in', 'PRD', 'Principal Product Designer', 95000.00, '+91 98455 22334', 'Pune, Maharashtra', 'WS-1002', 'B+', Gender.FEMALE),
            ('karthik_i', 'emp12345', 'Karthik', 'Iyer', 'karthik.iyer@worksphere.in', 'ENG', 'DevOps & Cloud Engineer', 110000.00, '+91 98111 33445', 'Chennai, Tamil Nadu', 'WS-1003', 'A+', Gender.MALE),
            ('priya_n', 'emp12345', 'Priya', 'Nair', 'priya.nair@worksphere.in', 'FIN', 'Financial Controller & Tax Lead', 115000.00, '+91 98333 44556', 'Mumbai, Maharashtra', 'WS-1004', 'AB+', Gender.FEMALE),
            ('vikram_p', 'emp12345', 'Vikramaditya', 'Patil', 'vikram.patil@worksphere.in', 'MKT', 'Growth Marketing Manager', 85000.00, '+91 98666 55667', 'Hyderabad, Telangana', 'WS-1005', 'O-', Gender.MALE),
            ('sneha_k', 'emp12345', 'Sneha', 'Kulkarni', 'sneha.kulkarni@worksphere.in', 'HR', 'Talent Acquisition Specialist', 70000.00, '+91 98777 66778', 'Noida, Uttar Pradesh', 'WS-1006', 'B+', Gender.FEMALE),
        ]

        employee_objects = []
        for uname, pwd, fname, lname, email, dept_code, desig_title, salary, phone, city, emp_id, blood, gender in staff_data:
            u = User.objects.create(
                username=uname,
                email=email,
                first_name=fname,
                last_name=lname,
                role=UserRole.EMPLOYEE,
                phone=phone
            )
            u.set_password(pwd)
            u.save()

            emp = Employee.objects.create(
                user=u,
                employee_id=emp_id,
                department=departments[dept_code],
                designation=designations[desig_title],
                joining_date=date(2024, 2, 1),
                date_of_birth=date(1996, 6, 15),
                gender=gender,
                blood_group=blood,
                phone=phone,
                emergency_contact='+91 98000 00000',
                address=f"Flat 402, Green Meadows Residency, {city}",
                city=city,
                basic_salary=Decimal(str(salary)),
                status=EmployeeStatus.ACTIVE
            )
            employee_objects.append(emp)

        # 6. Create Indian Leave Types
        leave_types_data = [
            ('Casual Leave (CL)', 'CL', 12, 'Annual casual paid leave for personal affairs'),
            ('Sick / Medical Leave (SL)', 'SL', 10, 'Health recovery and medical checkups'),
            ('Privilege / Annual Leave (PL)', 'PL', 18, 'Annual earned vacation and festival travel'),
            ('Festival & Optional Holiday', 'FH', 4, 'Regional festivals (Diwali, Eid, Pongal, Ganesh Chaturthi)'),
            ('Emergency Leave', 'EL', 5, 'Immediate family emergencies'),
        ]
        l_types = {}
        for name, code, days, desc in leave_types_data:
            lt = LeaveType.objects.create(
                name=name,
                code=code,
                days_allowed=days,
                description=desc
            )
            l_types[code] = lt

        # 7. Create Today & Recent Attendance Records
        today = date.today()
        for emp in employee_objects:
            # Today attendance
            Attendance.objects.create(
                employee=emp,
                date=today,
                check_in=time(9, 30, 0),
                check_out=time(18, 15, 0),
                status=AttendanceStatus.PRESENT,
                working_hours=Decimal('8.75'),
                notes='Office punch-in (Bengaluru HQ)'
            )
            # Past 5 days logs
            for d in range(1, 6):
                past_date = today - timedelta(days=d)
                if past_date.weekday() < 5:
                    Attendance.objects.create(
                        employee=emp,
                        date=past_date,
                        check_in=time(9, 20, 0),
                        check_out=time(18, 0, 0),
                        status=AttendanceStatus.PRESENT,
                        working_hours=Decimal('8.65'),
                        notes='Biometric biometric scan'
                    )

        # 8. Create Realistic Indian Leave Requests
        LeaveRequest.objects.create(
            employee=employee_objects[0], # Rohit Verma
            leave_type=l_types['PL'],
            start_date=today + timedelta(days=6),
            end_date=today + timedelta(days=10),
            total_days=5,
            reason='Family trip to Rishikesh and Golden Temple with parents.',
            status=LeaveStatus.PENDING
        )
        LeaveRequest.objects.create(
            employee=employee_objects[1], # Ananya Deshmukh
            leave_type=l_types['FH'],
            start_date=today - timedelta(days=8),
            end_date=today - timedelta(days=7),
            total_days=2,
            reason='Attending traditional family festival ceremonies in Pune.',
            status=LeaveStatus.APPROVED,
            reviewed_by=hr_user,
            review_remarks='Approved. Enjoy the festival celebrations!',
            reviewed_at=timezone.now()
        )
        LeaveRequest.objects.create(
            employee=employee_objects[2], # Karthik Iyer
            leave_type=l_types['SL'],
            start_date=today + timedelta(days=2),
            end_date=today + timedelta(days=3),
            total_days=2,
            reason='Dental surgery and root canal appointment.',
            status=LeaveStatus.PENDING
        )

        # 9. Create Indian Monthly Payroll Slips (INR (Rs.))
        curr_month = today.month
        curr_year = today.year
        prev_month = 12 if curr_month == 1 else curr_month - 1
        prev_year = curr_year - 1 if curr_month == 1 else curr_year

        for emp in employee_objects:
            basic = emp.basic_salary
            hra = basic * Decimal('0.40')                # 40% HRA
            medical = Decimal('2500.00')                 # Medical / Conveyance
            special = basic * Decimal('0.15')            # 15% Special Allowance
            tax = basic * Decimal('0.10')                # 10% TDS
            pf = basic * Decimal('0.12')                 # 12% EPF
            pt = Decimal('200.00')                       # Professional Tax

            # Previous Month - Paid via NEFT / IMPS
            Payslip.objects.create(
                employee=emp,
                month=prev_month,
                year=prev_year,
                basic_salary=basic,
                hra=hra,
                medical_allowance=medical,
                special_allowance=special,
                tax_deduction=tax,
                provident_fund=pf,
                other_deductions=pt,
                payment_status=PaymentStatus.PAID,
                payment_date=date(prev_year, prev_month, 28),
                payment_method=PaymentMethod.BANK_TRANSFER,
                transaction_reference=f'NEFT-HDFC-WS-{random.randint(10000000, 99999999)}',
                notes='Salary disbursed via HDFC Corporate Banking'
            )

            # Current Month - Unpaid / In Review
            Payslip.objects.create(
                employee=emp,
                month=curr_month,
                year=curr_year,
                basic_salary=basic,
                hra=hra,
                medical_allowance=medical,
                special_allowance=special,
                tax_deduction=tax,
                provident_fund=pf,
                other_deductions=pt,
                payment_status=PaymentStatus.UNPAID,
                notes='Current month payroll computation'
            )

        self.stdout.write(self.style.SUCCESS("All records successfully updated to 100% Indian employees, INR (Rs.) salaries, EPF/TDS and Indian departments!"))
