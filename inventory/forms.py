from django import forms
from .models import Stock, Barcode

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
       
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.request and self.request.user:
            instance.created_by = self.request.user
            print(instance.created_by)
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