from django import forms
from .models import Employee, Payroll


class EmployeeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):                                                     # used to set css classes to the various fields
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class': 'textinput form-control', 'required': 'true'})
        self.fields['last_name'].widget.attrs.update({'class': 'textinput form-control', 'required': 'true'})
        self.fields['email'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['phone_number'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '10', 'pattern' : '[0-9]{10}', 'title' : 'Numbers only', 'required': 'true'})
        self.fields['address'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['date_of_birth'].widget.attrs.update({'class': 'dateinput form-control'})
        self.fields['date_of_joining'].widget.attrs.update({'class': 'dateinput form-control'})
        self.fields['position'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['salary'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '10', 'pattern' : '[0-9]{10}'})

    class Meta:
        model = Employee
        fields = "__all__"
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'date_of_joining': forms.DateInput(attrs={'type': 'date'}),
        }

class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = ['employee', 'period_start', 'period_end', 'basic_salary', 'allowances', 'bonuses', 'deductions', 'paid_date']
        widgets = {
            'period_start': forms.DateInput(attrs={'type': 'date'}),
            'period_end': forms.DateInput(attrs={'type': 'date'}),
            'paid_date': forms.DateInput(attrs={'type': 'date'}),
        }