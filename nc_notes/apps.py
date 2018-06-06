from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class NotesAppConfig(AppConfig):
    name = "nc_notes"
    verbose_name = _("Cards notes")
