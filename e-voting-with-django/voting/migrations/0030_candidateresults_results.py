# Generated by Django 4.1.7 on 2023-05-10 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0029_voter_otp_entered'),
    ]

    operations = [
        migrations.CreateModel(
            name='CandidateResults',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname', models.CharField(max_length=50)),
                ('photo', models.ImageField(upload_to='candidates')),
                ('position', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Results',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position_name', models.CharField(max_length=255)),
                ('candidate_result', models.ManyToManyField(to='voting.candidateresults')),
            ],
        ),
    ]