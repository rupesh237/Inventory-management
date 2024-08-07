# Generated by Django 3.0.7 on 2024-07-28 08:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0018_auto_20240726_1638'),
        ('finance', '0008_auto_20240728_1423'),
        ('report', '0008_auto_20240726_1638'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payroll',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='finance.Payroll'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='purchasebill',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='transactions.PurchaseBillDetails'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='report',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='paymentreport', to='report.Report'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='type',
            field=models.CharField(choices=[('SALARY', 'Salary'), ('PURCHASE', 'Purchase'), ('EXPENSE', 'Expense'), ('FOOD', 'Food'), ('TRAVEL', 'Travel'), ('DUE', 'Due'), ('OTHER', 'Other')], default='EXPENSE', max_length=25),
        ),
        migrations.AlterField(
            model_name='receipt',
            name='report',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='receiptreport', to='report.Report'),
        ),
        migrations.AlterField(
            model_name='receipt',
            name='salebill',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='transactions.SaleBillDetails'),
        ),
        migrations.AlterField(
            model_name='supplierreport',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='transactions.Supplier'),
        ),
    ]
