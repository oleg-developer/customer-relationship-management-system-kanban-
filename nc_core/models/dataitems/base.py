from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils.translation import ugettext_lazy as _
from polymorphic.models import PolymorphicModel

__all__ = [
    'DataItem'
]


class DataItem(PolymorphicModel):
    content_type = models.ForeignKey("contenttypes.ContentType", null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey()

    class Meta:
        verbose_name = _("data item")
        verbose_name_plural = _("data items")

    def __str__(self):
        return str(self.get_real_instance())
