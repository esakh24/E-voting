# Generated by Django 4.1.7 on 2023-03-29 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0009_branches_delete_branchaa_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='position',
            name='allowed_branches',
        ),
        migrations.AddField(
            model_name='position',
            name='allowed_branches',
            field=models.IntegerField(choices=[(1, 'arch'), (2, 'cse'), (3, 'biotech')], default=1, verbose_name='branch'),
        ),
    ]
