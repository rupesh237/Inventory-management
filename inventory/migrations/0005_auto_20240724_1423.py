# Generated by Django 3.0.7 on 2024-07-24 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_auto_20240724_1423'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='unit',
            field=models.CharField(choices=[('kg', 'KILOGRAM'), ('l', 'LITRE'), ('pc', 'PIECE')], default='pc', max_length=10),
        ),
    ]
