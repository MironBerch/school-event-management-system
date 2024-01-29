# Generated by Django 4.2.7 on 2024-01-29 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0021_solution_theses'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='solution',
            options={'verbose_name': 'Работа', 'verbose_name_plural': 'Работы'},
        ),
        migrations.AddField(
            model_name='participant',
            name='fio',
            field=models.CharField(blank=True, max_length=255, verbose_name='ФИО ученика'),
        ),
        migrations.AlterField(
            model_name='solution',
            name='subject',
            field=models.CharField(max_length=255, verbose_name='предмет'),
        ),
        migrations.AlterField(
            model_name='solution',
            name='theses',
            field=models.CharField(blank=True, max_length=5120, verbose_name='краткие тезисы'),
        ),
    ]
