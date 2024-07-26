from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
	    return self.name
    
class Stock(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=30, unique=True)
    quantity = models.IntegerField(default=1)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    is_deleted = models.BooleanField(default=False)

    UNIT_CHOICES = (
         ('kg', 'KILOGRAM'),
         ('l', 'LITRE'),
         ('pc', 'PIECE'),
    )
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='pc')

    def __str__(self):
	    return self.name