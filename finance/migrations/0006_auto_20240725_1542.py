# Generated by Django 3.0.7 on 2024-07-25 09:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0005_auto_20240725_1313'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='payroll',
            options={'ordering': ['-paid_date']},
        ),
    ]
