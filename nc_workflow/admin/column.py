from django.contrib import admin

from ..models import Column

__all__ = [
    'ColumnAdmin'
]


@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'modified')
