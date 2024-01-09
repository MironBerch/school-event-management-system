from ckeditor_uploader.fields import RichTextUploadingField

from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import User


class Mailing(models.Model):
    header = models.CharField(
        verbose_name=_('заголовок письма'),
    )
    content = RichTextUploadingField(
        verbose_name=_('содержание письма'),
        blank=True,
        null=True,
    )
    recipients = models.ManyToManyField(
        User,
    )
    is_sent = models.BooleanField(
        default=False,
        verbose_name=_('отправлено'),
    )
    dispatch_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('время отправки'),
    )

    def __str__(self):
        return self.pk

    class Meta:
        verbose_name = _('рассылка')
        verbose_name_plural = _('рассылки')
