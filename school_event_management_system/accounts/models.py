from os import environ

from model_utils import FieldTracker
from phonenumber_field.modelfields import PhoneNumberField

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.managers import ActivatedAccountsManager, UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Пользовательская модель `User`."""

    profile: 'Profile'
    username = None
    email = models.EmailField(
        verbose_name=_('почта'),
        max_length=60,
        unique=True,
    )
    name = models.CharField(
        verbose_name=_('имя'),
        max_length=30,
    )
    surname = models.CharField(
        verbose_name=_('фамилия'),
        max_length=30,
    )
    patronymic = models.CharField(
        verbose_name=_('отчество'),
        max_length=30,
        blank=True,
    )

    date_joined = models.DateTimeField(
        verbose_name=_('дата присоединения'),
        auto_now_add=True,
    )
    last_login = models.DateTimeField(
        verbose_name=_('последний вход в систему'),
        auto_now=True,
    )

    class RoleChoices(models.TextChoices):
        STUDENT = 'ученик', 'ученик'
        TEACHER = 'учитель', 'учитель'
        ANOTHER = 'другая', 'другая'

    role = models.CharField(
        max_length=10,
        choices=RoleChoices.choices,
        verbose_name=_('роль'),
        default=RoleChoices.STUDENT,
    )

    is_email_confirmed = models.BooleanField(
        verbose_name=_('электронная почта подтверждена'),
        default=False,
    )

    is_active = models.BooleanField(
        verbose_name=_('активный'),
        default=True,
    )
    is_staff = models.BooleanField(
        verbose_name=_('персонал'),
        default=False,
    )
    is_superuser = models.BooleanField(
        verbose_name=_('суперпользователь'),
        default=False,
    )

    objects = UserManager()
    activated = ActivatedAccountsManager()

    # login parameter
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    # email field tracker
    email_tracker = FieldTracker(fields=['email'])

    class Meta:
        verbose_name = _('пользователь')
        verbose_name_plural = _('пользователи')

    def __str__(self):
        return f'{self.surname} {self.name}'

    @property
    def full_name(self):
        return f'{self.surname} {self.name} {self.patronymic}'


class Profile(models.Model):
    """Профиль для `User`."""

    date_of_birth = models.DateField(
        verbose_name=_('дата рождения'),
        blank=True,
        null=True,
    )
    from_current_school = models.BooleanField(
        verbose_name=_(f"из {environ.get('SCHOOL_NAME')}"),
        blank=True,
        default=True,
    )
    school = models.CharField(
        verbose_name=_('школа'),
        blank=True,
        max_length=255,
        default=environ.get('SCHOOL_NAME'),
    )
    YEAR_CHOICES = [
        (None, 'Не обучаюсь в школе'),
        (1, '1-й класс'),
        (2, '2-й класс'),
        (3, '3-й класс'),
        (4, '4-й класс'),
        (5, '5-й класс'),
        (6, '6-й класс'),
        (7, '7-й класс'),
        (8, '8-й класс'),
        (9, '9-й класс'),
        (10, '10-й класс'),
        (11, '11-й класс'),
    ]
    year_of_study = models.SmallIntegerField(
        verbose_name=_('год обучения'),
        blank=True,
        null=True,
        choices=YEAR_CHOICES,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(11),
        ],
    )
    phone_number = PhoneNumberField(
        verbose_name=_('номер телефона'),
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?[0-9]{7,15}$',
                message='Номер телефона необходимо ввести в формате: +XXXXXXXXXXXXX.',
            ),
        ],
    )

    user: User = models.OneToOneField(
        User,
        verbose_name=_('пользователь'),
        related_name='profile',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _('профиль')
        verbose_name_plural = _('профили')

    def __str__(self):
        return f'Профиль {self.user}'
