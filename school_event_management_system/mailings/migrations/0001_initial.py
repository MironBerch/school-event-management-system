# Generated by Django 4.2.7 on 2024-01-08 16:15

import ckeditor_uploader.fields

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Mailing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('header', models.CharField(verbose_name='заголовок письма')),
                ('content', ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name='содержание письма')),
                ('is_sent', models.BooleanField(default=False, verbose_name='отправлено')),
                ('dispatch_time', models.DateTimeField(blank=True, null=True, verbose_name='время отправки')),
                ('recipients', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'рассылка',
                'verbose_name_plural': 'рассылки',
            },
        ),
    ]
