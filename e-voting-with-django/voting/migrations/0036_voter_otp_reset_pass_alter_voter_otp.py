# Generated by Django 4.1.7 on 2023-05-14 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0035_results_posid'),
    ]

    operations = [
        migrations.AddField(
            model_name='voter',
            name='otp_reset_pass',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='voter',
            name='otp',
            field=models.CharField(max_length=20, null=True),
        ),
    ]