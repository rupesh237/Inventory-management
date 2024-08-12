from django import forms
from .models import Stock, Barcode

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
        if Stock.objects.filter(name=name).exists():
            raise ValidationError(f"A stock item with the name '{name}' already exists.")
        return name

    def clean_placed_at(self):
        placed_at = self.cleaned_data.get('placed_at')
        if placed_at and Stock.objects.filter(placed_at=placed_at).exists():
            raise ValidationError(f"A stock item is already placed at '{placed_at}'.")
        return placed_at
       
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.request and self.request.user:
            instance.created_by = self.request.user
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