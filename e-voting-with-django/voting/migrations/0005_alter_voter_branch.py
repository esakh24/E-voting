# Generated by Django 4.1.7 on 2023-03-28 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0004_alter_voter_branch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='voter',
            name='branch',
            field=models.IntegerField(choices=[(1, 'Architectural'), (2, 'biomedical'), (3, 'civil'), (4, 'mechanical'), (5, 'electrical'), (6, 'aerospace'), (7, 'CS'), (8, 'chemical')], default=1, max_length=20),
        ),
    ]