from django.db import models
from django.utils.translation import ugettext_lazy as _

from .base import DataItem

__all__ = [
    'WebSite'
]


class WebSite(DataItem):
    data = models.CharField(
        verbose_name=_("url"),
        max_length=30
    )

    class Meta:
        verbose_name = _("website")
        verbose_name_plural = _("websites")

    def __str__(self):
        return self.data
