# Generated by Django 4.1.7 on 2023-05-14 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_alter_strkeyval_dvalue'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='otp_reset_pass',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
