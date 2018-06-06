from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from .models import Company


class CompanyAdmin(admin.ModelAdmin):

    list_display = ('id', 'owner', 'name', 'is_active')


admin.site.site_header = _("NiceCode automation")
admin.site.register(Company, CompanyAdmin)
