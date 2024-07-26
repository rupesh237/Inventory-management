from django import forms
from .models import Receipt, ReceiptTypeChoice, Payment, PaymentTypeChoice


class ReceiptForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):                                                     # used to set css classes to the various fields
        super().__init__(*args, **kwargs)
        self.fields['paid_by'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['total'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['type'].widget.attrs.update({'class': 'textinput form-control', 'required': 'true'})
        self.fields['remarks'].widget.attrs.update({'class': 'textinput form-control'})

    class Meta:
        model = Receipt
        fields = ['type', 'paid_by', 'total', 'date', 'remarks']
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
        self.fields['type'].widget.attrs.update({'class': 'textinput form-control', 'required': 'true'})
        self.fields['remarks'].widget.attrs.update({'class': 'textinput form-control'})

    class Meta:
        model = Payment
        fields = ['type', 'paid_to', 'total', 'date', 'remarks']
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
