from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import User


def get_event_image_upload_path(instance: 'Event', filename: str) -> str:
    return f'upload/{instance.name}/{filename}'


def get_event_regulations_upload_path(instance: 'Event', filename: str) -> str:
    return f'upload/{instance.name}/{filename}'


def get_event_results_upload_path(instance: 'Event', filename: str) -> str:
    return f'upload/{instance.name}/{filename}'


class EventStatusChoices(models.TextChoices):
    REGISTRATION_PENDING = 'Ожидание регистрации', 'Ожидание регистрации'
    REGISTRATION_OPEN = 'Регистрация открыта', 'Регистрация открыта'
    ONGOING = 'В процессе', 'В процессе'
    COMPLETED = 'Завершено', 'Завершено'
    CANCELLED = 'Отменено', 'Отменено'
    POSTPONED = 'Отложено', 'Отложено'


class EventTypeChoices(models.TextChoices):
    INDIVIDUAL = 'Индивидуальное', 'Индивидуальное'
    TEAM = 'Командное', 'Командное'
    CLASS_TEAMS = 'Командное от классов', 'Командное от классов'


class EventStageChoices(models.TextChoices):
    SCHOOL = 'Школьный', 'Школьный'
    DISTRICT = 'Районный', 'Районный'
    CITY = 'Городской', 'Городской'
    REGIONAL = 'Региональный', 'Региональный'
    NATIONAL = 'Всероссийский', 'Всероссийский'
    INTERNATIONAL = 'Международный', 'Международный'


class Event(models.Model):
    image = models.ImageField(
        verbose_name=_('изображение предварительного просмотра мероприятия'),
        blank=True,
        null=True,
        upload_to=get_event_image_upload_path,
    )
    name = models.CharField(
        verbose_name=_('название мероприятия'),
        max_length=100,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name=_('url мероприятия'),
        max_length=100,
        unique=True,
    )
    description = models.TextField(
        verbose_name=_('описание мероприятия'),
        blank=True,
    )

    regulations = models.FileField(
        verbose_name=_('регламент мероприятия'),
        blank=True,
        null=True,
        upload_to=get_event_regulations_upload_path,
    )
    results = models.FileField(
        verbose_name=_('итоги мероприятия'),
        blank=True,
        null=True,
        upload_to=get_event_results_upload_path,
    )

    maximum_number_of_team_members = models.IntegerField(
        verbose_name=_('максимальное количество участников в команде'),
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        blank=True,
        null=True,
    )
    minimum_number_of_team_members = models.IntegerField(
        verbose_name=_('минимальное количество участников в команде'),
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        blank=True,
        null=True,
    )

    status = models.CharField(
        verbose_name=_('статус мероприятия'),
        blank=True,
        max_length=50,
        choices=EventStatusChoices.choices,
    )
    type = models.CharField(
        verbose_name=_('тип мероприятия'),
        blank=True,
        max_length=50,
        choices=EventTypeChoices.choices,
    )
    stage = models.CharField(
        verbose_name=_('этап мероприятия'),
        blank=True,
        max_length=50,
        choices=EventStageChoices.choices,
        default=EventStageChoices.SCHOOL,
    )

    date_of_starting_registration = models.DateField(
        verbose_name=_('дата начала регистрации'),
    )
    date_of_ending_registration = models.DateField(
        verbose_name=_('дата окончания регистрации'),
    )
    date_of_starting_event = models.DateField(
        verbose_name=_('дата начала мероприятия'),
    )

    published = models.BooleanField(
        verbose_name=_('является ли опубликованным'),
        blank=True,
        default=False,
    )
    archived = models.BooleanField(
        verbose_name=_('находится в архиве'),
        blank=True,
        default=False,
    )

    class Meta:
        verbose_name = _('мероприятие')
        verbose_name_plural = _('мероприятия')

    def __str__(self):
        return self.name


class Team(models.Model):
    event = models.ForeignKey(
        Event,
        verbose_name=_('мероприятие'),
        on_delete=models.CASCADE,
        related_name='teams',
    )
    supervisor = models.ForeignKey(
        User,
        verbose_name=_('руководитель'),
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        verbose_name=_('название команды'),
        max_length=100,
    )

    class Meta:
        verbose_name = _('команда')
        verbose_name_plural = _('команды')

    def __str__(self):
        return f'{self.name}'


class Participant(models.Model):
    event = models.ForeignKey(
        Event,
        verbose_name=_('мероприятие'),
        on_delete=models.CASCADE,
        related_name='participants',
    )
    user = models.ForeignKey(
        User,
        verbose_name=_('пользователь'),
        on_delete=models.CASCADE,
        related_name='participant',
    )
    team = models.ForeignKey(
        Team,
        verbose_name=_('команда'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='participants',
    )
    supervisor = models.ForeignKey(
        User,
        verbose_name=_('руководитель'),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='supervised_participants',
    )

    class Meta:
        verbose_name = _('участник')
        verbose_name_plural = _('участники')

    def __str__(self):
        return f'{self.user} {self.event}'


class EventDiplomas(models.Model):
    event = models.ForeignKey(
        Event,
        verbose_name=_('мероприятие'),
        on_delete=models.CASCADE,
    )
    url = models.URLField(
        verbose_name=_('ссылка на дипломы'),
    )

    class Meta:
        verbose_name = _('Дипломы мероприятия')
        verbose_name_plural = _('Дипломы мероприятий')

    def __str__(self):
        return f'{self.event}'
