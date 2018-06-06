from django.contrib import admin

from ..models import Board

__all__ = [
    'BoardAdmin'
]


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'modified')
