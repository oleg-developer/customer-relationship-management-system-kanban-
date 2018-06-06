from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from positions import PositionField

from nc_core.models.change_tracker_mixin import ChangeTrackerMixin


class Employee(ChangeTrackerMixin):
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    position = PositionField()
    client = models.ForeignKey('nc_clients.Client')
    data_items = GenericRelation('nc_core.DataItem')

    @cached_property
    def full_name(self):
        return " ".join((self.last_name, self.first_name, self.middle_name))

    class Meta:
        verbose_name = _("Employee")
        verbose_name_plural = _("Employees")

    def __str__(self):
        return self.full_name
