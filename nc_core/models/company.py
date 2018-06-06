from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

__all__ = [
    'Company'
]


class Company(TimeStampedModel):
    name = models.CharField(
        verbose_name=_('company'),
        max_length=512
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('owner'),
        related_name='companies',
        default=None,
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        verbose_name=_('is active'),
        default=True
    )

    description = models.TextField(
        verbose_name=_('description'),
        blank=True,
        default=''
    )

    default_board = models.OneToOneField(
        'nc_workflow.Board',
        verbose_name=_('default board'),
        related_name='+',
        default=None,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('company')
        verbose_name_plural = _('companies')
