from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

__all__ = [
    'Transition'
]


class Transition(TimeStampedModel):
    from_column = models.ForeignKey(
        'nc_workflow.Column',
        verbose_name=_("source column"),
        related_name="transitions_from"
    )

    to_column = models.ForeignKey(
        'nc_workflow.Column',
        verbose_name=_("destination column"),
        related_name="transitions_to"
    )

    active = models.BooleanField(
        _("Active"),
        default=True
    )

    class Meta(object):
        unique_together = ('from_column', 'to_column')
        verbose_name = _("transition")
        verbose_name_plural = _("transitions")

    def __str__(self):
        return "{from_} -> {to_}".format(
            from_=self.from_column.title,
            to_=self.to_column.title
        )

    def save(self, *args, **kwargs):
        from . import Column
        assert self.from_column.board == self.to_column.board
        assert self.from_column.type != Column.TYPE_CHOICES.LAST
        super(Transition, self).save(*args, **kwargs)

    @classmethod
    def has_transition(cls, column_1, column_2):
        return Transition.objects.filter(
            active=True,
            from_column=column_1,
            to_column=column_2
        ).exists()
