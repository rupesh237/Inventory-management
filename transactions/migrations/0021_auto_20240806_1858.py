# Generated by Django 3.0.7 on 2024-08-06 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0020_auto_20240806_1750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchasebilldetails',
            name='cgst',
            field=models.FloatField(default=0.0, null=True),
        ),
        migrations.AlterField(
            model_name='purchasebilldetails',
            name='igst',
            field=models.FloatField(default=0.0, null=True),
        ),
        migrations.AlterField(
            model_name='purchasebilldetails',
            name='sgst',
            field=models.FloatField(default=0.0, null=True),
        ),
        migrations.AlterField(
            model_name='purchasebilldetails',
            name='tcs',
            field=models.FloatField(default=0.0, null=True),
        ),
        migrations.AlterField(
            model_name='salebilldetails',
            name='cgst',
            field=models.FloatField(default=0.0, null=True),
        ),
        migrations.AlterField(
            model_name='salebilldetails',
            name='igst',
            field=models.FloatField(default=0.0, null=True),
        ),
        migrations.AlterField(
            model_name='salebilldetails',
            name='sgst',
            field=models.FloatField(default=0.0, null=True),
        ),
        migrations.AlterField(
            model_name='salebilldetails',
            name='tcs',
            field=models.FloatField(default=0.0, null=True),
        ),
    ]
