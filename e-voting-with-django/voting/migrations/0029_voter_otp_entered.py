# Generated by Django 4.1.7 on 2023-05-10 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0028_voter_otp_sent_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='voter',
            name='otp_entered',
            field=models.IntegerField(default=0),
        ),
    ]