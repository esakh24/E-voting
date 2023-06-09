# Generated by Django 4.1.7 on 2023-05-15 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0037_remove_voter_otp_reset_pass'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='allowed_branches',
            field=models.IntegerField(choices=[(1, 'Arch'), (2, 'CSE'), (3, 'Biotech'), (4, 'Electrical'), (5, 'Electronics')], default=1, verbose_name='branch'),
        ),
        migrations.AlterField(
            model_name='results',
            name='allowed_branches',
            field=models.IntegerField(choices=[(1, 'Arch'), (2, 'CSE'), (3, 'Biotech'), (4, 'Electrical'), (5, 'Electronics')], default=1, verbose_name='branch'),
        ),
        migrations.AlterField(
            model_name='voter',
            name='branch',
            field=models.IntegerField(choices=[(1, 'Arch'), (2, 'CSE'), (3, 'Biotech'), (4, 'Electrical'), (5, 'Electronics')], default=1, verbose_name='branch'),
        ),
    ]
