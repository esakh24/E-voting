# Generated by Django 4.1.7 on 2023-05-08 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0025_alter_voter_voted'),
    ]

    operations = [
        migrations.CreateModel(
            name='SharesKeyVal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dkey', models.EmailField(max_length=254)),
                ('dvalue', models.CharField(db_index=True, default='', max_length=12000)),
            ],
        ),
        migrations.AddField(
            model_name='position',
            name='shares_collected',
            field=models.ManyToManyField(to='voting.shareskeyval'),
        ),
    ]