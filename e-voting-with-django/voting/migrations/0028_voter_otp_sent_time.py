# Generated by Django 4.1.7 on 2023-05-10 13:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0027_alter_shareskeyval_dvalue'),
    ]

    operations = [
        migrations.AddField(
            model_name='voter',
            name='otp_sent_time',
            field=models.TimeField(default=datetime.time(11, 34, 56)),
        ),
    ]
