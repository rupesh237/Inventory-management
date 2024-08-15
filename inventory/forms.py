from django import forms
from .models import Stock, Barcode, StockTransfer

from homepage.models import Branch

from django.core.exceptions import ValidationError

class StockForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)                                                        # used to set css classes to the various fields
        super().__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['name'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['placed_at'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['price'].widget.attrs.update({'class': 'textinput form-control', 'min': '1.0'})
        self.fields['quantity'].widget.attrs.update({'class': 'textinput form-control', 'min': '1'})
        self.fields['unit'].widget.attrs.update({'class': 'textinput form-control'})

    def clean_name(self):
        name = self.cleaned_data.get('name')
        # Check if the name already exists in a different instance
        if Stock.objects.exclude(id=self.instance.id).filter(name=name).exists():
            raise ValidationError(f"A stock item with the name '{name}' already exists.")
        return name


    def clean_placed_at(self):
        placed_at = self.cleaned_data.get('placed_at')
        # Check if the placement already exists in a different instance
        if placed_at and Stock.objects.exclude(id=self.instance.id).filter(placed_at=placed_at).exists():
            raise ValidationError(f"A stock item is already placed at '{placed_at}'.")
        return placed_at

       
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.request and self.request.user:
            instance.created_by = self.request.user
        if not instance.branch_id:
            user_branch = self.request.user.profile.branch
            instance.branch = user_branch
        if commit:
            instance.save()
        if not Barcode.objects.filter(product=instance).exists():
            barcode = Barcode(product=instance)
            barcode.generate_barcode()
            barcode.save()
            print("Barcode created.")
        return instance

    class Meta:
        model = Stock
        fields = ['category', 'name', 'placed_at', 'price', 'quantity', 'unit']

class StockTransferForm(forms.ModelForm):
    class Meta:
        model = StockTransfer
        fields = ['stock', 'from_branch', 'to_branch', 'quantity']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        
        self.fields['stock'].queryset = Stock.objects.filter(branch=user.profile.branch)
        self.fields['stock'].widget.attrs.update({'class': 'textinput form-control'})
        
        self.fields['from_branch'].initial = user.profile.branch
        self.fields['from_branch'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['from_branch'].disabled = True 

        self.fields['to_branch'].queryset = Branch.objects.exclude(id=user.profile.branch.id)
        self.fields['to_branch'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['quantity'].widget.attrs.update({'class': 'textinput form-control'})