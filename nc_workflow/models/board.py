from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel
from positions import PositionField

from nc_workflow.models.column import Column


class Board(TimeStampedModel):
    company = models.ForeignKey(
        'nc_core.Company',
        verbose_name=_('company'),
        related_name='boards',
        blank=True, null=True
    )

    title = models.CharField(
        _("title"),
        max_length=512,
        blank=True
    )

    position = PositionField(
        _("position"),
        unique_for_fields=('company',),
        default=0
    )

    @property
    def column_workflow_start(self):
        """
        Получение первой колонки на доске
        """
        columns = self.columns.filter(type=Column.TYPE_CHOICES.FIRST)
        if columns.exists():
            return columns.first()
        else:
            return self.columns.filter(type=Column.TYPE_CHOICES.REGULAR).order_by('position').first()

    @property
    def column_workflow_end(self):
        """
        Получение последней колонки на доске
        """
        columns = self.columns.filter(type=Column.TYPE_CHOICES.LAST)
        if columns.exists():
            return columns.last()
        else:
            return self.columns.filter(type=Column.TYPE_CHOICES.REGULAR).order_by('-position').first()

    class Meta(object):
        verbose_name = _('board')
        verbose_name_plural = _('boards')
        ordering = ('position',)

    def __str__(self):
        return self.title

    def delete(self, using=None, keep_parents=False):
        from . import Card
        # Карточки удаляемой доски уходят в корзину
        Card.objects.filter(column__board=self).update(status=Card.STATUS_CHOICES.BASKET, basket_date=timezone.now())
        return super().delete(using=using, keep_parents=keep_parents)
