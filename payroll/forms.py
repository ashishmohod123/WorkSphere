from django import forms
from .models import Payslip, PaymentStatus, PaymentMethod
from employees.models import Employee

class PayslipCreateForm(forms.ModelForm):
    class Meta:
        model = Payslip
        fields = [
            'employee', 'month', 'year', 'basic_salary',
            'hra', 'medical_allowance', 'special_allowance',
            'tax_deduction', 'provident_fund', 'other_deductions',
            'payment_status', 'payment_date', 'payment_method',
            'transaction_reference', 'notes'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'month': forms.Select(choices=[(i, m) for i, m in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December'], 1)], attrs={'class': 'form-select'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'basic_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'hra': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'medical_allowance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'special_allowance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tax_deduction': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'provident_fund': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'other_deductions': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'transaction_reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UTR / Cheque Ref'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class GenerateMonthlyPayrollForm(forms.Form):
    month = forms.ChoiceField(
        choices=[(i, m) for i, m in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December'], 1)],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    year = forms.IntegerField(
        initial=2026,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
