# Generated by Django 4.2.7 on 2023-11-26 10:54

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import events.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to=events.models.get_event_image_upload_path, verbose_name='изображение предварительного просмотра мероприятия')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='название мероприятия')),
                ('slug', models.SlugField(max_length=100, unique=True, verbose_name='url мероприятия')),
                ('description', models.TextField(blank=True, verbose_name='описание мероприятия')),
                ('maximum_number_of_team_members', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='максимальное количество участников в команде')),
                ('minimum_number_of_team_members', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='минимальное количество участников в команде')),
                ('status', models.CharField(blank=True, choices=[('Ожидание регистрации', 'Ожидание регистрации'), ('Регистрация открыта', 'Регистрация открыта'), ('В процессе', 'В процессе'), ('Завершено', 'Завершено'), ('Отменено', 'Отменено'), ('Отложено', 'Отложено')], max_length=50, verbose_name='статус мероприятия')),
                ('type', models.CharField(blank=True, choices=[('Индивидуальное', 'Индивидуальное'), ('Командное', 'Командное'), ('Командное от классов', 'Командное от классов')], max_length=50, verbose_name='тип мероприятия')),
                ('stage', models.CharField(blank=True, choices=[('Школьный', 'Школьный'), ('Районный', 'Районный'), ('Городской', 'Городской'), ('Региональный', 'Региональный'), ('Всероссийский', 'Всероссийский'), ('Международный', 'Международный')], default='Школьный', max_length=50, verbose_name='этап мероприятия')),
                ('date_of_starting_registration', models.DateField(verbose_name='дата начала регистрации')),
                ('date_of_ending_registration', models.DateField(verbose_name='дата окончания регистрации')),
                ('date_of_starting_event', models.DateField(verbose_name='дата начала мероприятия')),
                ('published', models.BooleanField(blank=True, default=False, verbose_name='является ли опубликованным')),
            ],
            options={
                'verbose_name': 'мероприятие',
                'verbose_name_plural': 'мероприятия',
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='название команды')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teams', to='events.event', verbose_name='мероприятие')),
                ('supervisor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='руководитель')),
            ],
            options={
                'verbose_name': 'команда',
                'verbose_name_plural': 'команды',
            },
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='events.event', verbose_name='мероприятие')),
                ('supervisor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='supervised_participants', to=settings.AUTH_USER_MODEL, verbose_name='руководитель')),
                ('team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='participants', to='events.team', verbose_name='команда')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participant', to=settings.AUTH_USER_MODEL, verbose_name='пользователь')),
            ],
            options={
                'verbose_name': 'участник',
                'verbose_name_plural': 'участники',
            },
        ),
    ]
