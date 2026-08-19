# WorkSphere - Enterprise HR Management System

WorkSphere is a full-stack, enterprise-grade Human Resource Management System (HRMS) built with **Python**, **Django**, **Bootstrap 5**, and modern frontend/backend best practices.

## Key Features
- **Role-Based Authentication**: Admin, HR, and Employee roles with granular permissions.
- **Dynamic Executive Dashboard**: Live stats, cards, recent activity feeds, and charts.
- **Employee Directory**: Profile management, documents, photos, and department mapping.
- **Attendance Engine**: Check-in/check-out tracking, status badges, and daily punch history.
- **Leave Management**: Employee leave requests, multi-level approvals, and balance logs.
- **Payroll System**: Salary calculation engine (Gross, Deductions, Net) and payslip generation.
- **Analytics & Export**: Master CSV/Excel exports for audits and compliance.

## Project Structure
```text
WorkSphere/
├── config/              # Project settings and root routing
├── accounts/            # Custom User model & Role-based authentication
├── employees/           # Employee profiles, departments, and designations
├── attendance/          # Daily punch, tracking, and logs
├── leave_management/    # Leave applications & approval workflows
├── payroll/             # Salary structure, deductions & payslip generator
├── dashboard/           # Metrics, analytics & widgets
├── templates/           # Global templates & base components
├── static/              # CSS, JavaScript & Assets
├── media/               # Dynamic uploads (Avatars, documents)
├── manage.py
├── requirements.txt
└── .env
```
