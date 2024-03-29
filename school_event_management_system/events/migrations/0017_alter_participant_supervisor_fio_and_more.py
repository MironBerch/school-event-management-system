# Generated by Django 4.2.7 on 2024-01-19 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0016_participant_supervisor_email_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='supervisor_fio',
            field=models.CharField(blank=True, max_length=255, verbose_name='ФИО руководителя'),
        ),
        migrations.AlterField(
            model_name='team',
            name='supervisor_fio',
            field=models.CharField(blank=True, max_length=255, verbose_name='ФИО руководителя'),
        ),
    ]
