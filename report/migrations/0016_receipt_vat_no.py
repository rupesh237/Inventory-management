# Generated by Django 3.0.7 on 2024-08-09 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0015_auto_20240809_1749'),
    ]

    operations = [
        migrations.AddField(
            model_name='receipt',
            name='vat_no',
            field=models.CharField(max_length=9, null=True),
        ),
    ]
