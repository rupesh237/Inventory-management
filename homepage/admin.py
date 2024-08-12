from django.contrib import admin
from .models import Company, Branch, UserProfile

admin.site.register(Company)
admin.site.register(Branch)
admin.site.register(UserProfile)