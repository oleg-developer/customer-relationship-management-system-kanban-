from django.db import models
from django.utils.translation import ugettext_lazy as _

from .base import DataItem

__all__ = [
    'Email'
]


class Email(DataItem):
    data = models.EmailField(
        verbose_name=_("mail"),
        max_length=30
    )

    class Meta:
        verbose_name = _("mail")
        verbose_name_plural = _("mails")

    def __str__(self):
        return self.data
