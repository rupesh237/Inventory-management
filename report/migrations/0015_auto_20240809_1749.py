# Generated by Django 3.0.7 on 2024-08-09 12:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0014_auto_20240808_1821'),
    ]

    operations = [
        migrations.RenameField(
            model_name='receiptbill',
            old_name='tcs',
            new_name='tds',
        ),
    ]