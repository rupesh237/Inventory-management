from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Permission

from .models import Company, Branch, UserProfile

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

class UserCreationWithProfileForm(UserCreationForm):
    branch = forms.ModelChoiceField(queryset=Branch.objects.all(), required=True)

    def __init__(self, *args, **kwargs):  
        branch = kwargs.pop('branch', None)
        super().__init__(*args, **kwargs)
        if branch:
            self.fields['branch'].queryset = Branch.objects.filter(id=branch.id)

        is_staff = forms.BooleanField(required=False, label="Staff Status")
        is_superuser = forms.BooleanField(required=False, label="Superuser Status")
        is_active = forms.BooleanField(required=False, initial=True, label="Active Status")

        self.fields['branch'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['branch'].initial = branch
        self.fields['branch'].disabled = True 
        self.fields['first_name'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['username'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['email'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['is_active'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['is_staff'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['is_superuser'].widget.attrs.update({'class': 'form-check-input'})


    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'branch','is_staff', 'is_superuser', 'is_active']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = self.cleaned_data['is_staff']
        user.is_superuser = self.cleaned_data['is_superuser']
        user.is_active = self.cleaned_data['is_active']
        if commit:
            user.save()
            # Update or create the profile with the selected branch
            UserProfile.objects.update_or_create(
                user=user,
                defaults={'branch': self.cleaned_data['branch']}
            )
        return user