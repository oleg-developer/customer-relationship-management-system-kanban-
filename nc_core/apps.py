from django.utils.translation import ugettext_lazy as _
from django.apps import AppConfig


class ErpCoreConfig(AppConfig):
    name = 'nc_core'
    verbose_name = _("Core")
