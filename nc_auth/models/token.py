from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from model_utils.models import TimeStampedModel

from nc_auth import utils
from nc_core.utils import memcached_method

__all__ = [
    'Token'
]


class TokenManager(models.Manager):
    PREFIX = "AuthToken#"

    @memcached_method(
        key=lambda key: TokenManager.PREFIX + key,
        timeout=settings.CACHES_DURATIONS.get("TOKEN", 60)
    )
    def get_by_key(self, key):
        return self.select_related("user").get(key=key)


class Token(TimeStampedModel):
    PLATFORM_CHOICES = Choices(
        ('web', 'WEB', _('Web')),
        ('ios', 'IOS', _('iOS')),
        ('android', 'ANDROID', _('Android')),
    )

    key = models.CharField(
        verbose_name=_('key'),
        max_length=128,
        primary_key=True,
        default=utils.generate_string,
        editable=False
    )

    platform = models.SlugField(
        verbose_name=_('platform'),
        choices=PLATFORM_CHOICES,
        default=PLATFORM_CHOICES.WEB
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('user'),
        related_name='tokens',
        default=None,
        blank=True,
        null=True
    )

    version = models.FloatField(
        verbose_name=_('version'),
        default=1.0
    )

    client = models.CharField(
        verbose_name=_('client'),
        max_length=1024,
        default=''
    )

    objects = TokenManager()

    def __str__(self):
        return "<Token {}:***{}>".format(self.user if self.user else "-", self.key[:4])

    class Meta:
        verbose_name = _('Auth token')
        verbose_name_plural = _('Auth tokens')
