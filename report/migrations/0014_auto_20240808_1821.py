# Generated by Django 3.0.7 on 2024-08-08 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0013_auto_20240808_1819'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='description',
            field=models.TextField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='receipt',
            name='description',
            field=models.TextField(blank=True, max_length=255, null=True),
        ),
    ]