from django.db import models
from django.apps import apps

from django.contrib.auth.models import User


# Create your models here.
class Employee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    date_of_birth = models.DateField()
    date_of_joining = models.DateField()
    # department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Payroll(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING)
    period_start = models.DateField()
    period_end = models.DateField()
    paid_date = models.DateField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    prepared_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payroll for {self.employee.first_name} {self.employee.last_name} - {self.period_start} to {self.period_end}"

    def calculate_net_salary(self):
        self.net_salary = self.basic_salary + self.allowances + self.bonuses - self.deductions
        return self.net_salary
    
    def make_payment_report(self):
        Payment = apps.get_model('report', 'Payment')
        payment, created = Payment.objects.get_or_create(
            payroll=self,
            defaults={
                'type': "SALARY",
                'paid_to': f"{self.employee.first_name} {self.employee.last_name}",
                'prepared_by': self.prepared_by,
                'total': self.net_salary,
                'date': self.created_at,
            }
        )
        if not created:
            # If a Payment report already exists, update the necessary fields
            payment.type = "SALARY"
            payment.paid_to = f"{self.employee.first_name} {self.employee.last_name}"
            payment.prepared_by = self.prepared_by
            payment.total = self.net_salary
            payment.date = self.paid_date
            payment.save()

    def save(self, *args, **kwargs):
        self.calculate_net_salary()
        if not self.calculate_net_salary:
            raise ValueError("Cannot save without a saved net salary.")

        super().save(*args, **kwargs)
        self.make_payment_report()

    class Meta:
        ordering = ['-paid_date'] 
