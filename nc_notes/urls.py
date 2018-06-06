# coding=utf-8
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from .api import NotesOfCardView, NotesViewSet

note_router = DefaultRouter()
note_router.register("notes", NotesViewSet, base_name="notes")

urlpatterns = [
    url(r'^cards/(?P<card_id>\d+)/notes/$', NotesOfCardView.as_view({
        "get": "list"
    })),
    url(r'^', include(note_router.get_urls()))
]
