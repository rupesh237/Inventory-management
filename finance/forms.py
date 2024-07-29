from django import forms
from .models import Employee, Payroll

from report.models import Receipt, ReceiptTypeChoice, Payment, PaymentTypeChoice


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

class ReceiptForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):                                                     # used to set css classes to the various fields
        super().__init__(*args, **kwargs)
        self.fields['paid_by'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['total'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['paid_amount'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['due_amount'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['type'].widget.attrs.update({'class': 'textinput form-control', 'required': 'true'})
        self.fields['remarks'].widget.attrs.update({'class': 'textinput form-control'})

    class Meta:
        model = Receipt
        fields = ['type', 'paid_by', 'total', 'paid_amount', 'due_amount', 'date', 'remarks']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'required': 'False'  # Optional, to use date picker
        }

    def clean(self):
        cleaned_data = super().clean()
        type = cleaned_data.get('type')
        remarks = cleaned_data.get('remarks')
        
        if type == ReceiptTypeChoice.OTHER and not remarks:
            self.add_error('remarks', 'Remarks must be provided if the receipt type is Other.')
        
        return cleaned_data

class PaymentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):                                                     # used to set css classes to the various fields
        super().__init__(*args, **kwargs)
        self.fields['paid_to'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['total'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['paid_amount'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['due_amount'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['type'].widget.attrs.update({'class': 'textinput form-control', 'required': 'true'})
        self.fields['remarks'].widget.attrs.update({'class': 'textinput form-control'})

    class Meta:
        model = Payment
        fields = ['type', 'paid_to', 'total', 'paid_amount', 'due_amount', 'date', 'remarks']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'required': 'False'  # Optional, to use date picker
        }

    def clean(self):
        cleaned_data = super().clean()
        type = cleaned_data.get('type')
        remarks = cleaned_data.get('remarks')
        
        if type == PaymentTypeChoice.OTHER and not remarks:
            self.add_error('remarks', 'Remarks must be provided if the receipt type is Other.')
        
        return cleaned_data
