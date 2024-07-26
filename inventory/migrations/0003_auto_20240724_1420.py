# Generated by Django 3.0.7 on 2024-07-24 08:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_stock_created_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='stock',
            name='unit',
            field=models.CharField(choices=[('kg', 'KILOGRAM'), ('l', 'LITRE'), ('pie', 'PIECE')], default='pie', max_length=10),
        ),
        migrations.AddField(
            model_name='stock',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.Category'),
        ),
    ]
