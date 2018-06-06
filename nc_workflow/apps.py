from django.utils.translation import ugettext_lazy as _
from django.apps import AppConfig


class ErpWorkflowConfig(AppConfig):
    name = 'nc_workflow'
    verbose_name = _("Workflow")
