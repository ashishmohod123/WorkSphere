from django import forms
from .models import LeaveRequest, LeaveType, LeaveStatus

class LeaveRequestApplyForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Provide justification or reason for leave request...'}),
        }

class LeaveActionForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['status', 'review_remarks']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'review_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'HR / Admin remarks...'}),
        }

class LeaveTypeForm(forms.ModelForm):
    class Meta:
        model = LeaveType
        fields = ['name', 'code', 'days_allowed', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'days_allowed': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
