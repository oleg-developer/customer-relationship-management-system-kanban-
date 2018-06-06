from django.db import models
from django.utils.translation import ugettext_lazy as _

from .base import DataItem

__all__ = [
    'Address'
]


class Address(DataItem):
    data = models.CharField(
        max_length=30,
        verbose_name=_("post_address")
    )

    class Meta:
        verbose_name = _("address")
        verbose_name_plural = _("addresses")

    def __str__(self):
        return self.data
