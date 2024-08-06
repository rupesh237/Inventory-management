from django.contrib import admin
from .models import Stock, Category, Barcode

admin.site.register(Stock)
admin.site.register(Category)
admin.site.register(Barcode)