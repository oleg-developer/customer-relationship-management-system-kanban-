from django.db import models
from django.utils.translation import ugettext_lazy as _


class Tag(models.Model):
    color = models.CharField(max_length=6, blank=True, default="ffffff")
    title = models.CharField(max_length=255, blank=False, null=False)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def __str__(self):
        return self.title
