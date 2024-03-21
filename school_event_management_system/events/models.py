from ckeditor_uploader.fields import RichTextUploadingField
from phonenumber_field.modelfields import PhoneNumberField

from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
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
    INDIVIDUAL_AND_COLLECTIVE = 'Индивидуальное, коллективное', 'Индивидуальное, коллективное'
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
    description = RichTextUploadingField(
        verbose_name=_('описание мероприятия'),
        blank=True,
        null=True,
    )

    need_presentation = models.BooleanField(
        verbose_name=_('нужна презентация'),
        blank=True,
        default=False,
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
        default=1,
    )
    minimum_number_of_team_members = models.IntegerField(
        verbose_name=_('минимальное количество участников в команде'),
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        blank=True,
        null=True,
        default=1,
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
        verbose_name=_('уровень мероприятия'),
        blank=True,
        max_length=50,
        choices=EventStageChoices.choices,
        default=EventStageChoices.SCHOOL,
    )

    date_of_starting_registration = models.DateField(
        verbose_name=_('дата начала регистрации'),
        blank=True,
        null=True,
    )
    date_of_ending_registration = models.DateField(
        verbose_name=_('дата окончания регистрации'),
        blank=True,
        null=True,
    )
    date_of_starting_event = models.DateField(
        verbose_name=_('дата начала мероприятия'),
        blank=True,
        null=True,
    )

    need_account = models.BooleanField(
        verbose_name=_('нужен аккаунт у участников'),
        blank=True,
        default=True,
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
        null=True,
        blank=True,
    )
    supervisor_fio = models.CharField(
        verbose_name=_('ФИО руководителя'),
        max_length=255,
        blank=True,
    )
    supervisor_phone_number = PhoneNumberField(
        verbose_name=_('номер телефона руководителя'),
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?[0-9]{7,15}$',
                message='Номер телефона необходимо ввести в формате: +XXXXXXXXXXXXX.',
            ),
        ],
    )
    supervisor_email = models.EmailField(
        verbose_name=_('почта руководителя'),
        max_length=60,
        blank=True,
    )
    name = models.CharField(
        verbose_name=_('название команды'),
        max_length=100,
    )
    school_class = models.CharField(
        verbose_name=_('класс который представляет команда'),
        max_length=5,
        blank=True,
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
        null=True,
        blank=True,
        related_name='participant',
    )
    fio = models.CharField(
        verbose_name=_('ФИО ученика'),
        max_length=255,
        blank=True,
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
    supervisor_fio = models.CharField(
        verbose_name=_('ФИО руководителя'),
        max_length=255,
        blank=True,
    )
    supervisor_phone_number = PhoneNumberField(
        verbose_name=_('номер телефона руководителя'),
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?[0-9]{7,15}$',
                message='Номер телефона необходимо ввести в формате: +XXXXXXXXXXXXX.',
            ),
        ],
    )
    supervisor_email = models.EmailField(
        verbose_name=_('почта руководителя'),
        max_length=60,
        blank=True,
    )

    class Meta:
        verbose_name = _('участник')
        verbose_name_plural = _('участники')

    def __str__(self):
        if self.user:
            return f'{self.user} {self.event}'
        else:
            return f'{self.fio} {self.event}'


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


class Solution(models.Model):
    event = models.ForeignKey(
        Event,
        verbose_name=_('мероприятие'),
        on_delete=models.CASCADE,
    )
    participant = models.ForeignKey(
        Participant,
        verbose_name=_('участник'),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    team = models.ForeignKey(
        Team,
        verbose_name=_('команда'),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    subject = models.CharField(
        verbose_name=_('предмет'),
        max_length=255,
    )
    theses = models.CharField(
        verbose_name=_('краткие тезисы'),
        max_length=5120,
        blank=True,
    )
    topic = models.CharField(
        verbose_name=_('тема проекта'),
        max_length=255,
    )
    url = models.URLField(
        verbose_name=_('ссылка на файлы'),
        blank=True,
    )

    class Meta:
        verbose_name = _('Работа')
        verbose_name_plural = _('Работы')

    def __str__(self):
        return f'{self.event} - {self.topic} - {self.url}'


class Task(models.Model):
    event = models.ForeignKey(
        Event,
        verbose_name=_('мероприятие'),
        on_delete=models.CASCADE,
    )
    task = RichTextUploadingField(
        verbose_name=_('задание мероприятия'),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _('Задание мероприятия')
        verbose_name_plural = _('Задания мероприятий')

    def __str__(self):
        return f'{self.event}'
