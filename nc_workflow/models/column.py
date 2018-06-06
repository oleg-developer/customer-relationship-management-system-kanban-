from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from model_utils.models import TimeStampedModel
from positions import PositionField

from nc_core.utils import memcached_property

__all__ = [
    'Column'
]


class Column(TimeStampedModel):
    CACHE_PREFIX = "Column#"
    TYPE_CHOICES = Choices(
        ('regular', 'REGULAR', _('regular')),
        ('first', 'FIRST', _('start workflow')),
        ('last', 'LAST', _('end workflow')),
    )

    title = models.CharField(
        verbose_name=_('title'),
        max_length=512,
        blank=True,
        default=''
    )

    board = models.ForeignKey(
        'nc_workflow.Board',
        verbose_name=_('board'),
        related_name='columns',
        on_delete=models.CASCADE
    )

    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Users")
    )

    type = models.CharField(
        verbose_name=_('type'),
        max_length=32,
        choices=TYPE_CHOICES,
        default=TYPE_CHOICES.REGULAR
    )

    position = PositionField(
        verbose_name=_('position'),
        collection='board'
    )

    class Meta(object):
        verbose_name = _('column')
        verbose_name_plural = _('columns')
        ordering = ('position',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Переопределяем save() для того что бы начальная и конечная колонки были уникальными
        """
        columns = self.board.columns.exclude(id=self.id)
        if self.type in (Column.TYPE_CHOICES.FIRST, Column.TYPE_CHOICES.LAST):
            columns.filter(type=self.type).update(type=self.TYPE_CHOICES.REGULAR)
            # raise IntegrityError(_("Board already contains first/last column"))
        super(Column, self).save(*args, **kwargs)

    @cached_property
    def has_subprocess_from(self):
        "There is a cross-boards transition from this column"
        from .subprocess import Subprocess
        try:
            return bool(self.subprocess_from)
        except Subprocess.DoesNotExist:
            return False

    @cached_property
    def has_subprocess_to(self):
        "There're cross-boards transitions to this column"
        return self.subprocess_to.exists()

    @memcached_property(
        key=lambda self: self.CACHE_PREFIX + str(self.id),
        timeout=30  # seconds
    )
    def is_subprocess(self):
        """
        @manually_invalidated
        Alias to has_subprocess_from
        """
        return self.has_subprocess_from

    @cached_property
    def is_start_workflow(self):
        return self.type == self.TYPE_CHOICES.FIRST

    @cached_property
    def is_end_workflow(self):
        return self.type == self.TYPE_CHOICES.LAST

    def delete(self, using=None, keep_parents=False):
        from . import Card
        self.cards.update(status=Card.STATUS_CHOICES.BASKET, basket_date=timezone.now())
        return super(Column, self).delete(using=using, keep_parents=keep_parents)
