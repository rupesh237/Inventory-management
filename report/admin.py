from django.contrib import admin
from .models import Receipt, Payment, ReceiptBill

# Register your models here.
admin.site.register(Receipt)
admin.site.register(Payment)
admin.site.register(ReceiptBill)
