# Generated by Django 4.2.7 on 2023-12-01 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_eventdiplomas'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='archived',
            field=models.BooleanField(blank=True, default=False, verbose_name='находится в архиве'),
        ),
    ]
