# Generated by Django 4.1.7 on 2023-03-29 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0008_branchaa_remove_position_allowed_branches_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Branches',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bid', models.IntegerField(default=1)),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.DeleteModel(
            name='Branchaa',
        ),
        migrations.AlterField(
            model_name='position',
            name='allowed_branches',
            field=models.ManyToManyField(to='voting.branches'),
        ),
    ]
