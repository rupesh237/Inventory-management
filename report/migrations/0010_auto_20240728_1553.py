# Generated by Django 3.0.7 on 2024-07-28 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0009_auto_20240728_1423'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='due_amount',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='payment',
            name='paid_amount',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='receipt',
            name='due_amount',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='receipt',
            name='paid_amount',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='report',
            name='type',
            field=models.CharField(choices=[('payment', 'PAYMENT'), ('receipt', 'RECEIPT'), ('supplier', 'SUPPLIER')], default='pay', max_length=10),
        ),
    ]
