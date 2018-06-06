import logging

from django.conf import settings
from django.db import models, IntegrityError
from django.db.models.aggregates import Min, Max
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from positions import PositionField

from nc_core.models.change_tracker_mixin import ChangeTrackerMixin

logger = logging.getLogger(__name__)


class Card(ChangeTrackerMixin):
    DEFAULT_COLOR = 'ffffff'
    STATUS_CHOICES = Choices(
        ('active', 'ACTIVE', _('active')),
        ('archive', 'ARCHIVE', _('archive')),
        ('basket', 'BASKET', _('basket')),
    )

    status = models.CharField(
        verbose_name=_('status'),
        max_length=32,
        choices=STATUS_CHOICES,
        default=STATUS_CHOICES.ACTIVE
    )

    company = models.ForeignKey('nc_core.Company', verbose_name=_("Company"), null=True, blank=True)
    column = models.ForeignKey('nc_workflow.Column', verbose_name=_("column"), related_name='cards',
                               blank=True, null=True, on_delete=models.SET_NULL)
    client = models.ForeignKey('nc_clients.Client', verbose_name=_("Client"), null=True, blank=True)

    position = PositionField(collection='column', verbose_name=_("position"), default=0)
    title = models.CharField(_("title"), max_length=512, default="", blank=True)
    color = models.CharField(_("color"), max_length=16, default=DEFAULT_COLOR, blank=True)

    slug_id = models.PositiveIntegerField(_("slug id"), default=0)

    blocked = models.BooleanField(_("is blocked"), default=False)
    blocked_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("blocked by"), related_name="blocked_cards",
                                   default=None, null=True, blank=True)

    archive_date = models.DateTimeField(_("archive at"), blank=True, null=True)
    basket_date = models.DateTimeField(_("to basket at"), blank=True, null=True)

    @property
    def is_first(self):
        Card = self.__class__
        return self.position == Card.objects.filter(column_id=self.column_id) \
            .aggregate(position=Min("position"))["position"]

    @property
    def is_last(self):
        Card = self.__class__
        return self.position == Card.objects.filter(column_id=self.column_id) \
            .aggregate(position=Max("position"))["position"]

    class Meta(object):
        verbose_name = _("card")
        verbose_name_plural = _("cards")
        ordering = ('position',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._old_column = self.column
        self._old_status = self.status

    def __str__(self):
        return self.title

    def validate_transition(self):
        from .transition import Transition
        if self._old_column != self.column and self._old_column is not None and self.column is not None:
            if not Transition.objects.filter(from_column=self._old_column, to_column=self.column).exists():
                # Не допустимый переход
                raise IntegrityError(_("Illegal transition"))

    def save(self, *args, **kwargs):
        # Fix position==None when using partial update
        position_cache_name = self._meta.get_field("position").get_cache_name()
        position_cache = getattr(self, position_cache_name)
        if position_cache[1] is None:
            setattr(self, position_cache_name, (position_cache[0], position_cache[0]))

        set_after_status = None
        # Перевод из архива/корзины
        if self.status != self.STATUS_CHOICES.ACTIVE and self.column and self.column != self._old_column:
            if self.column.has_subprocess_from:
                raise IntegrityError(_("Transition from archive to column with subprocess is forbidden"))
            if self.column.is_end_workflow:
                raise IntegrityError(_("Transition from archive to 'is_end_workflow' column is forbidden"))
            set_after_status = self.STATUS_CHOICES.ACTIVE
            self.archive_date = None
            self.basket_date = None

        # Активные карточки перемещаются в рамках Transitions
        if self.status == self.STATUS_CHOICES.ACTIVE:
            self.validate_transition()

        # Перевод в архив
        if self.status == self.STATUS_CHOICES.ACTIVE and self.column.is_end_workflow:
            set_after_status = self.STATUS_CHOICES.ARCHIVE
            self.column = None
            self.archive_date = timezone.now()
        # Перевод в корзину
        elif self._old_status == self.STATUS_CHOICES.ACTIVE and self.status == self.STATUS_CHOICES.BASKET:
            self.column = None
            self.basket_date = timezone.now()

        # Обработка subprocess
        if self.column and self.column.has_subprocess_from:
            self.column = self.column.subprocess_from.column_to

        if set_after_status:
            self.status = set_after_status

        super(Card, self).save(*args, **kwargs)
