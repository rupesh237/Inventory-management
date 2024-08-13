from django.db import models

from django.contrib.auth.models import User

class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    address = models.TextField()
    postal_code = models.CharField(max_length=20)
    registration_number = models.CharField(max_length=30)
    established_date = models.DateField(blank=True, null=True)
    pan_no = models.CharField(max_length=9)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)

    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        verbose_name_plural = "Companies"


class Branch(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    city = models.CharField(max_length=100)
    address = models.TextField()
    postal_code = models.CharField(max_length=20)
    established_date = models.DateField(blank=True, null=True)
    # manager_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.company.name}"
    
    class Meta:
        verbose_name_plural = "Branches"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='users')

    def __str__(self):
        return f"{self.user.username} - {self.branch.name}"