# Generated by Django 4.1.7 on 2023-04-01 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0014_position_candidate_filled'),
    ]

    operations = [
        migrations.AddField(
            model_name='votes',
            name='enc_vote',
            field=models.CharField(default='', max_length=10000000),
        ),
    ]