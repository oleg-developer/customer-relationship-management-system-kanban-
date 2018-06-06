from django.contrib import admin

from ..models import Transition

__all__ = [
    'TransitionAdmin'
]


@admin.register(Transition)
class TransitionAdmin(admin.ModelAdmin):
    pass
