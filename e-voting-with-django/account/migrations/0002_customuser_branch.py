# Generated by Django 4.1.7 on 2023-03-28 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='branch',
            field=models.CharField(choices=[(1, 'Architectural'), (2, 'biomedical'), (3, 'civil'), (4, 'mechanical'), (5, 'electrical'), (6, 'aerospace'), (7, 'computer science'), (8, 'chemical')], default='NONE', max_length=1),
        ),
    ]
