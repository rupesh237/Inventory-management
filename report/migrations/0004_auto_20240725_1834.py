# Generated by Django 3.0.7 on 2024-07-25 12:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('report', '0003_auto_20240725_1620'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='payment',
            options={'ordering': ['-date']},
        ),
        migrations.RemoveField(
            model_name='payment',
            name='id',
        ),
        migrations.AddField(
            model_name='payment',
            name='date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='paid_to',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_no',
            field=models.AutoField(default=11, primary_key=True, serialize=False),
        ),
        migrations.AddField(
            model_name='payment',
            name='prepared_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='payment',
            name='remarks',
            field=models.TextField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='report',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='paymentreport', to='report.Report'),
        ),
        migrations.AddField(
            model_name='payment',
            name='total',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='type',
            field=models.CharField(choices=[('SAL', 'Salary'), ('PUR', 'Purchase'), ('EX', 'Expense'), ('FD', 'Food'), ('TR', 'Travel'), ('OT', 'Other')], default='EX', max_length=25),
        ),
        migrations.AlterField(
            model_name='receipt',
            name='date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
