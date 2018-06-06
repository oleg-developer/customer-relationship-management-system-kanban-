from django.utils.translation import ugettext_lazy as _
from django.apps import AppConfig


class AuthConfig(AppConfig):
    name = 'nc_auth'
    verbose_name = _("Authentication")