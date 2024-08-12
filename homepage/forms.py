from django import forms

from .models import Company, Branch

class CompanyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):                                                     
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'textinput form-control', 'required': 'true'})
        self.fields['phone_number'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '10', 'pattern' : '[0-9]{13}', 'title' : 'Numbers only', 'required': 'true'})
        self.fields['email'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['country'].widget.attrs.update({'class': 'textinput form-control', 'required': 'true'})
        self.fields['city'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['address'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['postal_code'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '10', 'pattern' : '[0-9]{6}'})
        self.fields['registration_number'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['established_date'].widget.attrs.update({'class': 'dateinput form-control'})
        self.fields['pan_no'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '10', 'pattern' : '[0-9]{9}', 'title' : 'Numbers only', 'required': 'true'})
        self.fields['logo'].widget = forms.ClearableFileInput(attrs={'class': 'fileinput form-control', 'accept': 'image/*'})


    class Meta:
        model = Company
        fields = "__all__"
        widgets = {
            'established_date': forms.DateInput(attrs={'type': 'date'}),
        }


class BranchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):  
        self.request = kwargs.pop('request', None)                                                     
        super().__init__(*args, **kwargs)

        self.fields['name'].widget.attrs.update({'class': 'textinput form-control', 'required': 'true'})
        self.fields['phone_number'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '15', 'pattern' : '[0-9]{10}', 'title' : 'Numbers only', 'required': 'true'})
        self.fields['email'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['city'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['address'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['postal_code'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '10', 'pattern' : '[0-9]{5}'})
        self.fields['established_date'].widget.attrs.update({'class': 'dateinput form-control'})

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.company_id:
            user_branch = self.request.user.profile.branch
            print(user_branch)
            instance.company = user_branch.company
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Branch
        fields = ['name', 'phone_number', 'email', 'city', 'address', 'postal_code', 'established_date']
        widgets = {
            'established_date': forms.DateInput(attrs={'type': 'date'}),
        }