# Generated by Django 3.0.7 on 2024-07-26 07:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0017_auto_20240724_1420'),
        ('report', '0005_auto_20240725_1839'),
    ]

    operations = [
        migrations.AddField(
            model_name='receipt',
            name='salebill',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='transactions.SaleBillDetails'),
        ),
        migrations.AddField(
            model_name='report',
            name='type',
            field=models.CharField(choices=[('pay', 'PAYMENT'), ('receipt', 'RECEIPT'), ('supplier', 'SUPPLIER')], default='pay', max_length=10),
        ),
        migrations.CreateModel(
            name='SupplierReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transactions.Supplier')),
            ],
        ),
    ]
