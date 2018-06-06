from django.db import models
from django.utils.translation import ugettext_lazy as _


class Group(models.Model):
    name = models.CharField(max_length=255, blank=False)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Group")
        verbose_name_plural = _("Groups")

    def __str__(self):
        return self.name
