from django.db import models
from django.contrib.auth.models import User
from inventory.models import Stock

from django.apps import apps

#contains suppliers
class Supplier(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=12, unique=True)
    address = models.CharField(max_length=200)
    email = models.EmailField(max_length=254, unique=True)
    gstin = models.CharField(max_length=9, unique=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
	    return self.name


#contains the purchase bills made
class PurchaseBill(models.Model):
    billno = models.AutoField(primary_key=True)
    time = models.DateTimeField()
    supplier = models.ForeignKey(Supplier, on_delete = models.CASCADE, related_name='purchasesupplier')
    prepared_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def get_items_list(self):
        return PurchaseItem.objects.filter(billno=self)

    def get_total_price(self):
        purchaseitems = PurchaseItem.objects.filter(billno=self)
        total = 0
        for item in purchaseitems:
            total += item.totalprice
        return total
    
    def __str__(self):
	    return "Bill no: " + str(self.billno)

#contains the purchase stocks made
class PurchaseItem(models.Model):
    billno = models.ForeignKey(PurchaseBill, on_delete = models.CASCADE, related_name='purchasebillno')
    stock = models.ForeignKey(Stock, on_delete = models.CASCADE, related_name='purchaseitem')
    quantity = models.IntegerField(default=1)
    perprice = models.IntegerField(default=1)
    totalprice = models.IntegerField(default=1)

    def __str__(self):
	    return "Bill no: " + str(self.billno.billno) + ", Item = " + self.stock.name

#contains the other details in the purchases bill
class PurchaseBillDetails(models.Model):
    billno = models.ForeignKey(PurchaseBill, on_delete = models.CASCADE, related_name='purchasedetailsbillno')
    
    eway = models.CharField(max_length=50, blank=True, null=True)    
    veh = models.CharField(max_length=50, blank=True, null=True)
    destination = models.CharField(max_length=50, blank=True, null=True)
    po = models.CharField(max_length=50, blank=True, null=True)
    
    cgst = models.FloatField(default=0.0, null=True)
    sgst = models.FloatField(default=0.0, null=True)
    igst = models.FloatField(default=0.0, null=True)
    cess = models.FloatField(default=0.0, null=True)
    tcs = models.FloatField(default=0.0, null=True)
    
    discount_percentage = models.SmallIntegerField(null=True, default=0)
    discount_amount = models.FloatField(default=0.0, null=True)
    total = models.FloatField(default=0.0)
    paid_amount = models.FloatField(default=0.0)
    due_amount = models.FloatField(default=0.0)

    def get_total_amount_with_taxes(self):
        total = float(self.billno.get_total_price())
        if not self.discount_amount:
            self.discount_amount = (float(self.discount_percentage) * total)/100
        self.total = total + self.cgst - self.discount_amount

    def make_payment_report(self):
        Payment = apps.get_model('report', 'Payment')
        payment, created = Payment.objects.get_or_create(
            purchasebill=self,
            defaults={
                'type': "PURCHASE",
                'paid_to': self.billno.supplier.name,
                'prepared_by': self.billno.prepared_by,
                'total': self.total,
                'paid_amount': self.paid_amount,
                'due_amount': self.due_amount,
                'date': self.billno.time,
            }
        )
        if not created:
            # If a Payment report already exists, update the necessary fields
            payment.type = "PURCHASE"
            payment.paid_to = self.billno.supplier.name
            payment.prepared_by = self.billno.prepared_by
            payment.total = self.total
            payment.paid_amount = self.paid_amount
            payment.due_amount = self.due_amount
            payment.date = self.billno.time
            payment.save()
        
    def save(self, *args, **kwargs):
        # Ensure the related SaleBill is saved first
        if not self.billno_id:
            raise ValueError("Cannot save PurcahseBillDetails without a saved PurchaseBill instance.")
        
        super().save(*args, **kwargs)
        self.make_payment_report()


    def __str__(self):
	    return "Bill no: " + str(self.billno.billno)


#contains the sale bills made
class SaleBill(models.Model):
    billno = models.AutoField(primary_key=True)
    time = models.DateTimeField(auto_now=True)
    prepared_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=12)
    address = models.CharField(max_length=200)
    email = models.EmailField(max_length=254)
    gstin = models.CharField(max_length=9, null=True)
    
    def get_items_list(self):
        return SaleItem.objects.filter(billno=self)
        
    def get_total_price(self):
        saleitems = SaleItem.objects.filter(billno=self)
        total = 0
        for item in saleitems:
            total += item.totalprice
        return total
    
    def __str__(self):
	    return "Bill no: " + str(self.billno)

#contains the sale stocks made
class SaleItem(models.Model):
    billno = models.ForeignKey(SaleBill, on_delete = models.CASCADE, related_name='salebillno')
    stock = models.ForeignKey(Stock, on_delete = models.CASCADE, related_name='saleitem')
    quantity = models.IntegerField(default=1)
    perprice = models.IntegerField(default=1)
    totalprice = models.IntegerField(default=1)

    def __str__(self):
	    return "Bill no: " + str(self.billno.billno) + ", Item = " + self.stock.name

#contains the other details in the sales bill
class SaleBillDetails(models.Model):
    billno = models.ForeignKey(SaleBill, on_delete = models.CASCADE, related_name='saledetailsbillno')
    
    eway = models.CharField(max_length=50, blank=True, null=True)    
    veh = models.CharField(max_length=50, blank=True, null=True)
    destination = models.CharField(max_length=50, blank=True, null=True)
    po = models.CharField(max_length=50, blank=True, null=True)
    
    cgst = models.FloatField(default=0.0, null=True)
    sgst = models.FloatField(default=0.0, null=True)
    igst = models.FloatField(default=0.0, null=True)
    cess = models.FloatField(default=0.0, null=True)
    tcs = models.FloatField(default=0.0, null=True)

    discount_percentage = models.SmallIntegerField(null=True, default=0)
    discount_amount = models.FloatField(default=0.0, null=True)
    total = models.FloatField(default=0.0)
    paid_amount = models.FloatField(default=0.0)
    due_amount = models.FloatField(default=0.0)

    def get_total_amount_with_taxes(self):
        total = float(self.billno.get_total_price())
        if not self.discount_amount:
            self.discount_amount = (float(self.discount_percentage) * total)/100
        self.total = total + self.cgst - self.discount_amount

    def make_receipt_report(self):
        Receipt = apps.get_model('report', 'Receipt')
        receipt, created = Receipt.objects.get_or_create(
            salebill=self,
            defaults={
                'type': "SALE",
                'paid_by': self.billno.name,
                'prepared_by': self.billno.prepared_by,
                'total': self.total,
                'paid_amount': self.paid_amount,
                'due_amount': self.due_amount,
                'date': self.billno.time,
            }
        )
        if not created:
            # If a Payment report already exists, update the necessary fields
            receipt.type = "SALE"
            receipt.paid_by = self.billno.name
            receipt.prepared_by = self.billno.prepared_by
            receipt.total = self.total
            receipt.paid_amount = self.paid_amount
            receipt.due_amount = self.due_amount
            receipt.date = self.billno.time
            receipt.save()

    def save(self, *args, **kwargs):
        # Ensure the related SaleBill is saved first
        if not self.billno_id:
            raise ValueError("Cannot save SaleBillDetails without a saved SaleBill instance.")
        
        super().save(*args, **kwargs)
        self.make_receipt_report()

    def __str__(self):
	    return "Bill no: " + str(self.billno.billno)
