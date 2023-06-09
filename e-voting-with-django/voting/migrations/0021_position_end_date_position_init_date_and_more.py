# Generated by Django 4.1.7 on 2023-04-06 10:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0020_position_end_time_position_init_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='position',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 4, 6, 10, 0, 9, 317176, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AddField(
            model_name='position',
            name='init_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 4, 6, 10, 0, 9, 317176, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='position',
            name='end_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 4, 6, 10, 0, 9, 317176, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='position',
            name='init_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 4, 6, 10, 0, 9, 317176, tzinfo=datetime.timezone.utc)),
        ),
    ]
