from django.conf import settings
from django.db import models


class ChangeTrackerMixin(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    user_created = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+")
    user_modified = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="+")
    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False, blank=True)

    class Meta:
        abstract = True
