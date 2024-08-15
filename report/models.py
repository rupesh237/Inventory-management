from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from django.contrib.auth.models import User

from transactions.models import SaleBillDetails, PurchaseBillDetails
from finance.models import Payroll
from homepage.models import Branch

from django.apps import apps

# Create your models here.
class PaymentTypeChoice(models.TextChoices):
    SALARY = "SALARY", _("Salary")
    PURCHASE = "PURCHASE", _("Purchase")
    EXPENSE = "EXPENSE", _("Expense")
    FOOD = "FOOD", _("Food")
    TRAVEL = "TRAVEL", _("Travel")
    DUE = "DUE", _("Due")
    OTHER = "OTHER", _("Other")

class ReceiptTypeChoice(models.TextChoices):
    SALE = "SALE", _("Sale")
    SERVICE_PROVIDED = "SERVICE PROVIDED", _("Service Provided")
    DUE = "DUE", _("Due")
    OTHER = "OTHER", _("Other")


class Payment(models.Model):
    payment_no = models.AutoField(primary_key=True)
    type = models.CharField(max_length=25, choices=PaymentTypeChoice.choices, default=PaymentTypeChoice.EXPENSE)
    remarks = models.TextField(max_length=255, blank=True, null=True)
    description = models.TextField(max_length=255, blank=True, null=True)
    paid_to = models.CharField(max_length=50)
    prepared_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    total = models.FloatField()
    paid_amount = models.FloatField(default=0.0)
    due_amount = models.FloatField(default=0.0)
    date = models.DateTimeField(blank=True, null=True)

    purchasebill = models.ForeignKey(PurchaseBillDetails, on_delete=models.CASCADE, blank=True, null=True)
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='branchpayment', null=True)

    def clean(self):
        # Custom validation to ensure remarks are provided if type is 'Other'
        if self.type == PaymentTypeChoice.OTHER and not self.remarks:
            raise ValidationError({'remarks': 'Remarks must be provided if the receipt type is Other.'})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.payment_no}: {self.type}"
    
    class Meta:
        ordering = ['-date'] 

class Receipt(models.Model):
    receipt_no = models.AutoField(primary_key=True)
    type = models.CharField(max_length=25, choices=ReceiptTypeChoice.choices, default=ReceiptTypeChoice.SALE)
    remarks = models.TextField(max_length=255, blank=True, null=True)
    description = models.TextField(max_length=255, blank=True, null=True)
    paid_by = models.CharField(max_length=50)
    vat_no = models.CharField(max_length=9, null=True)
    prepared_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    total = models.FloatField()
    paid_amount = models.FloatField(default=0.0)
    due_amount = models.FloatField(default=0.0)
    date = models.DateTimeField(blank=True, null=True)

    salebill = models.ForeignKey(SaleBillDetails, on_delete=models.CASCADE, blank=True, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='branchreceipt', null=True)

    def clean(self):
        # Custom validation to ensure remarks are provided if type is 'Other'
        if self.type == ReceiptTypeChoice.OTHER and not self.remarks:
            raise ValidationError({'remarks': 'Remarks must be provided if the receipt type is Other.'})
        
    def make_receipt_bill(self):
        ReceiptBill = apps.get_model('report', 'ReceiptBill')
        receiptbill, created = ReceiptBill.objects.get_or_create(
            receipt=self,
            defaults={
                'total': self.total,
                'paid_amount': self.paid_amount,
                'due_amount': self.due_amount,
            }
        )
        # If the ReceiptBill was created for the first time
        if created:
            # If VAT number is provided, calculate the taxes
            receiptbill.paid_amount = self.paid_amount
            if self.vat_no:
                receiptbill.get_total_amount_with_taxes()
            else:
                receiptbill.total = self.total
                receiptbill.due_amount = self.due_amount

            receiptbill.save()
        else:
            # If the ReceiptBill already exists, update the necessary fields
            receiptbill.paid_amount = self.paid_amount
            if self.vat_no:
                receiptbill.get_total_amount_with_taxes()
            else:
                receiptbill.total = self.total
                receiptbill.due_amount = self.due_amount
            receiptbill.save()

    def save(self, *args, **kwargs):
        # Ensure the related SaleBill is saved first
        if not self:
            raise ValueError("Cannot create Bill without a saved Receipt instance.")
        super().save(*args, **kwargs)
        if not self.salebill:
            self.make_receipt_bill()

        
    def __str__(self):
        return f"{self.receipt_no}: {self.type}"
    
    class Meta:
        ordering = ['-date'] 

#contains the other details in the purchases bill
class ReceiptBill(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete = models.CASCADE, related_name='receipt')
    
    eway = models.CharField(max_length=50, blank=True, null=True)    
    veh = models.CharField(max_length=50, blank=True, null=True)
    destination = models.CharField(max_length=50, blank=True, null=True)
    po = models.CharField(max_length=50, blank=True, null=True)
    
    cgst = models.FloatField(default=0.0, null=True)
    sgst = models.FloatField(default=0.0, null=True)
    igst = models.FloatField(default=0.0, null=True)
    cess = models.FloatField(default=0.0, null=True)
    tds = models.FloatField(default=0.0, null=True)
    
    discount_amount = models.FloatField(default=0.0, null=True)
    total = models.FloatField(default=0.0)
    paid_amount = models.FloatField(default=0.0)
    due_amount = models.FloatField(default=0.0)

    def get_total_amount_with_taxes(self):
        total = float(self.receipt.total)
        self.cgst = 0.13 * total
        self.tds = 0.015 * total

        self.total = total + self.cgst - self.tds
        self.due_amount = self.total - self.paid_amount

    def __str__(self):
	    return "Receipt no: " + str(self.receipt.receipt_no)

    
