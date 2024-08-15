from django.db import models
from django.db.models import UniqueConstraint
from django.contrib.auth.models import User

import random
from io import BytesIO
from django.core.files.base import ContentFile
from barcode import EAN13
from barcode.writer import ImageWriter

from homepage.models import Branch


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
	    return self.name
    
class Stock(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=30)
    placed_at = models.CharField(max_length=60, null=True)
    price = models.FloatField(default=0.0)
    quantity = models.IntegerField(default=1)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    is_deleted = models.BooleanField(default=False)

    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True)

    UNIT_CHOICES = (
         ('kg', 'KILOGRAM'),
         ('ltr', 'LITRE'),
         ('pc', 'PIECE'),
    )
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='pc')

    constraints = [
        UniqueConstraint(fields=['name', 'branch'], name='unique_name_per_branch'),
        UniqueConstraint(fields=['placed_at', 'branch'], name='unique_placed_at_per_branch')
        ]


    def __str__(self):
	    return self.name
    

class Barcode(models.Model):
    product_code = models.CharField(max_length=12, unique=True)
    product = models.ForeignKey(Stock, on_delete=models.DO_NOTHING)
    barcode = models.ImageField(upload_to='barcodes/', null=True)

    def generate_barcode(self):
        code = str(random.randint(100000000000, 999999999999))
        self.product_code = code
        ean = EAN13(code, writer=ImageWriter())

        # Save barcode image to a BytesIO object
        buffer = BytesIO()
        ean.write(buffer, options={'format': 'PNG'})

        # Save image to the barcode field
        filename = f'barcode_{self.product.name}.png'
        self.barcode.save(filename, ContentFile(buffer.getvalue()), save=False)
        print(f"Barcode saved as {filename}.")

    def save(self, *args, **kwargs):
        if not self.barcode:
            self.generate_barcode()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product_code

# Script to create barcodes for all stocks
def create_barcodes_for_all_stocks():
    from .models import Stock, Barcode

    stocks = Stock.objects.all()
    for stock in stocks:
        if not Barcode.objects.filter(product=stock).exists():
            barcode = Barcode(product=stock)
            barcode.save()
        else:
             print("Barcode for all stocks already generated.")

    def  __str__(self):
        return self.product_code
    

class StockTransfer(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('canceled', 'Canceled'),
    )

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    from_branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='transfers_out')
    to_branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='transfers_in')
    quantity = models.IntegerField()
    transferred_by = models.ForeignKey(User, on_delete=models.CASCADE)
    transfer_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')


    def __str__(self):
        return f"Transfer {self.quantity} of {self.stock.name} from {self.from_branch.name} to {self.to_branch.name}"
    

