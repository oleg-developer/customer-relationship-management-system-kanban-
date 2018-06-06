from django.db import models
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from .base import DataItem

__all__ = [
    'PhoneNumber'
]


class PhoneNumber(DataItem):
    number = PhoneNumberField(
        verbose_name=_("phone"),
        max_length=25,
        blank=False, null=False
    )

    data = models.CharField(max_length=50, blank=True)

    is_primary = models.BooleanField(
        verbose_name=_("is primary"),
        default=False,
        blank=True
    )

    class Meta:
        verbose_name = _("phone")
        verbose_name_plural = _("phones")

    def __str__(self):
        return self.data
