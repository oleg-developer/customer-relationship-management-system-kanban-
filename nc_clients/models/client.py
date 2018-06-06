from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices

from nc_core.models.change_tracker_mixin import ChangeTrackerMixin


class ClientExtraTypeFace(models.Model):
    value = models.CharField(max_length=255, verbose_name=_("type"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False)

    class Meta:
        verbose_name = _("Client extra type")
        verbose_name_plural = _("Clients extra types")
        unique_together = (("value", "user"),)

    def __str__(self):
        return self.value


class Client(ChangeTrackerMixin):
    FACE_CHOICES = Choices(
        ("phys", "PHYS", _("Физ. лицо")),
        ("ip", "IP", _("ИП")),
        ("ooo", "OOO", _("ООО")),
        ("pao", "PAO", _("ПАО")),
        ("zao", "ZAO", _("ЗАО")),
        ("other", "OTHER", _("other")),
    )
    FACE_CHOICES_REVERSE = dict(map(reversed, FACE_CHOICES))

    # TODO: Company FK
    # company = models.ForeignKey('nc_core.Company', verbose_name=_("Company"), null=True, blank=True)

    title = models.CharField(max_length=255, blank=False, null=False, verbose_name=_("Название"))
    more_info = models.TextField(blank=True)

    # ALL
    inn = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, verbose_name=_("ИНН"))
    checking_account = models.DecimalField(max_digits=25, decimal_places=0, null=True, blank=True,
                                           verbose_name=_("Расчетный счет"))
    address = models.CharField(max_length=500, blank=True, verbose_name=_("Адрес"))

    # PHYS
    birthday = models.DateField(null=True, blank=True, verbose_name=_("Дата рождения"))
    passport_serial = models.DecimalField(max_digits=4, decimal_places=0, null=True, blank=True,
                                          verbose_name=_("Серия паспорта"))
    passport_number = models.DecimalField(max_digits=6, decimal_places=0, null=True, blank=True,
                                          verbose_name=_("Номер паспорта"))
    passport_date = models.DateField(null=True, blank=True, verbose_name=_("Дата выдачи паспорта"))
    passport_given_by = models.CharField(max_length=500, blank=True, verbose_name=_("Паспорт выдан"))
    mail_code = models.CharField(max_length=20, null=True, blank=True, verbose_name=_("Почтовый индекс"))

    # IP
    ip_name = models.CharField(max_length=255, blank=True, verbose_name=_("Полное название ИП"))
    fact_address = models.CharField(max_length=500, blank=True, verbose_name=_("Фактический адрес"))
    mail_address = models.CharField(max_length=500, blank=True, verbose_name=_("Потовый адрес"))
    ogrn = models.DecimalField(max_digits=13, decimal_places=0, null=True, blank=True, verbose_name=_("ОГРН"))
    okpo = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True, verbose_name=_("ОКПО"))
    correspondent_account = models.DecimalField(max_digits=25, decimal_places=0, null=True, blank=True,
                                                verbose_name=_("Корресподентский счет"))
    bank = models.CharField(max_length=255, blank=True, verbose_name=_("Банк"))
    bik = models.DecimalField(max_digits=9, decimal_places=0, null=True, blank=True, verbose_name=_("БИК"))
    document = models.CharField(max_length=255, blank=True, verbose_name=_("На основании"))

    # OTHER
    general_manager = models.CharField(max_length=255, blank=True, verbose_name=_("Ген. директор"))
    kpp = models.DecimalField(max_digits=9, decimal_places=0, null=True, blank=True, verbose_name=_("КПП"))

    data_items = GenericRelation('nc_core.DataItem')
    group = models.ForeignKey('nc_clients.Group', null=True, blank=True, on_delete=models.SET_NULL)
    tag = models.ForeignKey('nc_clients.Tag', null=True, blank=True, on_delete=models.SET_NULL)
    relations = models.ManyToManyField('self', related_name="related_clients_reverse", blank=True)

    # Типы лиц по умолчанию записываются в _type_face, остальные - как объект ClientExtraTypeFace в _extra_type_face
    _type_face = models.CharField(max_length=10, choices=FACE_CHOICES, default=FACE_CHOICES.OTHER)
    _extra_type_face = models.ForeignKey('nc_clients.ClientExtraTypeFace', null=True, blank=True)

    def get_type_face(self) -> str:
        return self.get__type_face_display() if self._type_face != self.FACE_CHOICES.OTHER else self._extra_type_face.value

    def set_type_face(self, value: str, user: models.Model = None):
        """

        :param value: Системный ИЛИ Читабельный ИЛИ Кастомный тип лица
        :param user: Пользователь для привязки кастомного типа
        :rtype: None
        """
        if value in self.FACE_CHOICES:
            self._type_face = value
            self._extra_type_face = None
        elif value in self.FACE_CHOICES_REVERSE:
            self._type_face = self.FACE_CHOICES_REVERSE[value]
            self._extra_type_face = None
        else:
            self._type_face = self.FACE_CHOICES.OTHER
            self._extra_type_face, created = ClientExtraTypeFace.objects.get_or_create(value=value, user=user)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")
