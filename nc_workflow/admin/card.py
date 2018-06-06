from django.contrib import admin

from ..models import Card

__all__ = [
    'CardAdmin'
]


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    pass
