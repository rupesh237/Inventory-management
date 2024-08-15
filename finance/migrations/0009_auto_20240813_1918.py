# Generated by Django 3.0.7 on 2024-08-13 13:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0002_auto_20240812_1514'),
        ('finance', '0008_auto_20240728_1423'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='branch',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employeebranch', to='homepage.Branch'),
        ),
        migrations.AddField(
            model_name='payroll',
            name='branch',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payrollbranch', to='homepage.Branch'),
        ),
    ]
