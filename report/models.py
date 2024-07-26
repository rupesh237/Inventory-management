from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from django.contrib.auth.models import User

from transactions.models import SaleBillDetails, PurchaseBillDetails
from finance.models import Payroll

from transactions.models import Supplier

# Create your models here.
class PaymentTypeChoice(models.TextChoices):
    SALARY = "SALARY", _("Salary")
    PURCHASE = "PURCHASE", _("Purchase")
    EXPENSE = "EXPENSE", _("Expense")
    FOOD = "FOOD", _("Food")
    TRAVEL = "TRAVEL", _("Travel")
    OTHER = "OTHER", _("Other")

class ReceiptTypeChoice(models.TextChoices):
    SALE = "SALE", _("Sale")
    SERVICE_PROVIDED = "SERVICE PROVIDED", _("Service Provided")
    OTHER = "OTHER", _("Other")

class Report(models.Model):
    report_no = models.AutoField(primary_key=True)
    REPORT_TYPE = (
         ('pay', 'PAYMENT'),
         ('receipt', 'RECEIPT'),
         ('supplier', 'SUPPLIER'),
    )
    type = models.CharField(max_length=10, choices=REPORT_TYPE, default='pay')

    def __str__(self):
        return f"{self.report_no}"

class Payment(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, null=True, related_name="paymentreport")
    payment_no = models.AutoField(primary_key=True)
    type = models.CharField(max_length=25, choices=PaymentTypeChoice.choices, default=PaymentTypeChoice.EXPENSE)
    remarks = models.TextField(max_length=255, blank=True, null=True)
    paid_to = models.CharField(max_length=50)
    prepared_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    total = models.FloatField()
    date = models.DateTimeField(blank=True, null=True)

    purchasebill = models.ForeignKey(PurchaseBillDetails, on_delete=models.CASCADE, blank=True, null=True)
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE, null=True, blank=True)

    def clean(self):
        # Custom validation to ensure remarks are provided if type is 'Other'
        if self.type == PaymentTypeChoice.OTHER and not self.remarks:
            raise ValidationError({'remarks': 'Remarks must be provided if the receipt type is Other.'})
        if self.type == PaymentTypeChoice.PURCHASE and not self.purchasebill:
            raise ValidationError({'remarks': 'PurchaseBill must be provided if the receipt type is Purchase.'})

    def save(self, *args, **kwargs):
        self.clean()
        # create report details object
        reportobj = Report()
        reportobj.type = 'PAYMENT'
        reportobj.save()
        self.report = reportobj
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.payment_no}: {self.type}"
    
    class Meta:
        ordering = ['-date'] 

class Receipt(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, null=True, related_name="receiptreport")
    receipt_no = models.AutoField(primary_key=True)
    type = models.CharField(max_length=25, choices=ReceiptTypeChoice.choices, default=ReceiptTypeChoice.SALE)
    remarks = models.TextField(max_length=255, blank=True, null=True)
    paid_by = models.CharField(max_length=50)
    prepared_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    total = models.FloatField()
    date = models.DateTimeField(blank=True, null=True)

    salebill = models.ForeignKey(SaleBillDetails, on_delete=models.CASCADE, blank=True, null=True)

    def clean(self):
        # Custom validation to ensure remarks are provided if type is 'Other'
        if self.type == ReceiptTypeChoice.OTHER and not self.remarks:
            raise ValidationError({'remarks': 'Remarks must be provided if the receipt type is Other.'})
        if self.type == ReceiptTypeChoice.SALE and not self.salebill:
            raise ValidationError({'remarks': 'Salebill must be provided if the receipt type is Sale.'})

    def save(self, *args, **kwargs):
        self.clean()
        # create report details object
        reportobj = Report()
        reportobj.type = 'RECEIPT'
        reportobj.save()
        self.report = reportobj
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.receipt_no}: {self.type}"
    
    class Meta:
        ordering = ['-date'] 

class SupplierReport(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

    
