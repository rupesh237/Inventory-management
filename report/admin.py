from django.contrib import admin
from .models import Receipt, Payment, Report

# Register your models here.
admin.site.register(Receipt)
admin.site.register(Payment)
admin.site.register(Report)
