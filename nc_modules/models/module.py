from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices

from nc_core.utils import memcached_method


class ModuleManager(models.Manager):
    PREFIX = "Module#"

    @memcached_method(
        key=PREFIX,
        timeout=settings.CACHES_DURATIONS.get("MODULE", 60)
    )
    def get_all(self):
        return self.all()

    @memcached_method(
        key=lambda name: ModuleManager.PREFIX + name,
        timeout=settings.CACHES_DURATIONS.get("MODULE", 60)
    )
    def get_by_name(self, name):
        return self.get(name=name)

    @memcached_method(
        key=lambda user: ModuleManager.PREFIX + str(user.id),
        timeout=settings.CACHES_DURATIONS.get("MODULE_PERMISSIONS", 60)
    )
    def get_for_user(self, user):
        """@manually_invalidated"""
        return user.module_permissions.all()


class Module(models.Model):
    TYPE_CHOICES = Choices(
        ('global', 'GLOBAL', _("Global module")),
        ('card', 'CARD', _("Card module")),
    )

    name = models.CharField(_("name"), max_length=255, blank=False, unique=True, db_index=True)
    verbose_name = models.CharField(_("verbose name"), max_length=255, blank=True)
    type = models.CharField(_("type"), max_length=20, choices=TYPE_CHOICES)

    objects = ModuleManager()

    class Meta:
        verbose_name = _("Module")
        verbose_name_plural = _("Modules")

    def __repr__(self):
        return "<Module {}>".format(self.name)

    def __str__(self):
        return self.verbose_name
