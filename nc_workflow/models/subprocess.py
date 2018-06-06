from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from .board import Board


class Subprocess(TimeStampedModel):
    column_from = models.OneToOneField(
        'nc_workflow.Column',
        verbose_name=_("source column"),
        related_name="subprocess_from"
    )

    column_to = models.ForeignKey(
        'nc_workflow.Column',
        verbose_name=_("destination column"),
        related_name="subprocess_to"
    )

    class Meta(object):
        verbose_name = _("Subprocess")
        verbose_name_plural = _("Subprocesses")
        unique_together = (('column_to', 'column_from'),)

    def get_board_field(self, board_type, field):
        if board_type == "to":
            board_id = self.column_to.board_id
        elif board_type == "from":
            board_id = self.column_from.board_id
        else:
            board_id = None
        if field in ("pk", "id") or board_id is None:
            return board_id
        return Board.objects.filter(id=board_id).values_list(field, flat=True)[0]

    def __str__(self):
        return "'{from_board}'.'{from_column}' -> '{to_board}'.'{to_column}'".format(
            from_board=self.column_from.board,
            to_board=self.column_to.board,
            from_column=self.column_from,
            to_column=self.column_to
        )
