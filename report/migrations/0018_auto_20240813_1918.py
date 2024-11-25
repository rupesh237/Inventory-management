# Generated by Django 3.0.7 on 2024-08-13 13:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0002_auto_20240812_1514'),
        ('report', '0017_remove_receiptbill_discount_percentage'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='branch',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='branchpayment', to='homepage.Branch'),
        ),
        migrations.AddField(
            model_name='receipt',
            name='branch',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='branchreceipt', to='homepage.Branch'),
        ),
    ]
