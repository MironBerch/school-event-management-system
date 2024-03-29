# Generated by Django 4.2.7 on 2024-01-16 16:16

import phonenumber_field.modelfields

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0015_alter_event_maximum_number_of_team_members_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='supervisor_email',
            field=models.EmailField(blank=True, max_length=60, verbose_name='почта руководителя'),
        ),
        migrations.AddField(
            model_name='participant',
            name='supervisor_fio',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='participant',
            name='supervisor_phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None, validators=[django.core.validators.RegexValidator(message='Номер телефона необходимо ввести в формате: +XXXXXXXXXXXXX.', regex='^\\+?[0-9]{7,15}$')], verbose_name='номер телефона руководителя'),
        ),
        migrations.AddField(
            model_name='team',
            name='supervisor_email',
            field=models.EmailField(blank=True, max_length=60, verbose_name='почта руководителя'),
        ),
        migrations.AddField(
            model_name='team',
            name='supervisor_fio',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='team',
            name='supervisor_phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None, validators=[django.core.validators.RegexValidator(message='Номер телефона необходимо ввести в формате: +XXXXXXXXXXXXX.', regex='^\\+?[0-9]{7,15}$')], verbose_name='номер телефона руководителя'),
        ),
        migrations.AlterField(
            model_name='team',
            name='supervisor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='руководитель'),
        ),
    ]
