from django.contrib import admin

from ..models import Subprocess

__all__ = [
    'SubprocessAdmin'
]


@admin.register(Subprocess)
class SubprocessAdmin(admin.ModelAdmin):
    pass
