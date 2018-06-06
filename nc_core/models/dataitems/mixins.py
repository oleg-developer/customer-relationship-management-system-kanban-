from django.contrib.contenttypes.fields import GenericRelation
from django.db import models


class DataItemMixin(models.Model):
    data_items = GenericRelation('nc_clients.DataItem')

    class Meta:
        abstract = True
