from django.db import models
from employees.models import Employee
from decimal import Decimal

class PaymentStatus(models.TextChoices):
    UNPAID = 'UNPAID', 'Unpaid'
    PAID = 'PAID', 'Paid'
    PROCESSING = 'PROCESSING', 'Processing'

class PaymentMethod(models.TextChoices):
    BANK_TRANSFER = 'BANK_TRANSFER', 'Direct Bank NEFT / IMPS'
    CHEQUE = 'CHEQUE', 'Cheque'
    CASH = 'CASH', 'Cash'
    UPI = 'UPI', 'UPI Corporate'

class Payslip(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='payslips'
    )
    month = models.PositiveSmallIntegerField(help_text="Month (1-12)")
    year = models.PositiveIntegerField(help_text="Year (e.g. 2026)")
    
    # Earnings (in INR ₹)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, help_text="Basic Salary (INR)")
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="House Rent Allowance (HRA)")
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Medical & Conveyance")
    special_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Special Allowance")
    
    # Deductions (in INR ₹)
    tax_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Income Tax (TDS)")
    provident_fund = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Employee Provident Fund (EPF)")
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('200.00'), verbose_name="Professional Tax & Others")
    
    # Totals
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    
    # Disbursement Details
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID
    )
    payment_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.BANK_TRANSFER
    )
    transaction_reference = models.CharField(max_length=100, blank=True, help_text="UTR / NEFT / IMPS Reference Number")
    notes = models.TextField(blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['employee', 'month', 'year']
        ordering = ['-year', '-month', 'employee__employee_id']

    @property
    def total_allowances(self):
        return self.hra + self.medical_allowance + self.special_allowance

    @property
    def total_deductions(self):
        return self.tax_deduction + self.provident_fund + self.other_deductions

    def save(self, *args, **kwargs):
        self.gross_salary = self.basic_salary + self.total_allowances
        self.net_salary = max(Decimal('0.00'), self.gross_salary - self.total_deductions)
        super().save(*args, **kwargs)

    @property
    def get_month_name(self):
        months = [
            '', 'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        return months[self.month] if 1 <= self.month <= 12 else str(self.month)

    @property
    def get_status_badge(self):
        badges = {
            PaymentStatus.PAID: 'badge-paid',
            PaymentStatus.UNPAID: 'badge-unpaid',
            PaymentStatus.PROCESSING: 'badge-processing',
        }
        return badges.get(self.payment_status, 'bg-secondary')

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_month_name} {self.year} (Net: ₹{self.net_salary})"
