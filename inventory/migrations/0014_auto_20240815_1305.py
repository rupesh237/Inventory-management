# Generated by Django 3.0.7 on 2024-08-15 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0013_auto_20240814_1938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='placed_at',
            field=models.CharField(max_length=60, null=True),
        ),
    ]
