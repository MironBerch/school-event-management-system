# Generated by Django 4.2.7 on 2023-12-13 22:35

import ckeditor.fields

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0011_event_need_presentation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='description',
        ),
        migrations.AddField(
            model_name='task',
            name='task',
            field=ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='задание мероприятия'),
        ),
    ]
