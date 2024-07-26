# Generated by Django 3.0.7 on 2024-07-17 12:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('transactions', '0011_auto_20240717_1803'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchaseitem',
            name='prepared_by',
        ),
        migrations.RemoveField(
            model_name='saleitem',
            name='prepared_by',
        ),
        migrations.AddField(
            model_name='purchasebill',
            name='prepared_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='salebill',
            name='prepared_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
