# Generated by Django 4.1.7 on 2023-05-07 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0023_alter_position_end_date_alter_position_end_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='fullname',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
