from django.contrib import admin
from .models import Stock, Category, Barcode, StockTransfer

admin.site.register(Stock)
admin.site.register(Category)
admin.site.register(Barcode)
admin.site.register(StockTransfer)