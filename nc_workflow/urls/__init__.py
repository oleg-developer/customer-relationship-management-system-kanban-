from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from ..viewsets.board import BoardViewSet
from ..viewsets.card import CardViewSet, CardArchiveViewSet, CardBasketViewSet, CardClientAPIView

router = DefaultRouter()
router.register('boards', BoardViewSet, base_name='boards')
router.register('cards', CardViewSet, base_name='cards')

sub_cards_router = DefaultRouter()
sub_cards_router.register('archive', CardArchiveViewSet, base_name='archive')

urlpatterns = [
    url(r'^', include(router.get_urls())),
    url(r'^cards/', include(sub_cards_router.get_urls())),
    url(r'^cards/basket/$', CardBasketViewSet.as_view({
        "get": "list",
        "delete": "destroy_all"
    })),
    url(r'^cards/basket/(?P<pk>[0-9]+)/$', CardBasketViewSet.as_view({
        "get": "retrieve",
        "put": "update",
        "delete": "destroy"
    })),
    url(r'^cards/(?P<card_pk>[0-9]+)/client/(?:(?P<client_pk>[0-9]+)/)?$', CardClientAPIView.as_view())
]
