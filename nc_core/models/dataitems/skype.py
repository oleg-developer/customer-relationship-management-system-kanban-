from django.db import models
from django.utils.translation import ugettext_lazy as _

from .base import DataItem

__all__ = [
    'Skype'
]


class Skype(DataItem):
    data = models.CharField(
        verbose_name=_("login"),
        max_length=30
    )

    class Meta:
        verbose_name = _("skype")
        verbose_name_plural = _("skype")

    def __str__(self):
        return self.data
