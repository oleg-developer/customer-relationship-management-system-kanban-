from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from ..viewsets.admin.board import BoardAdminViewSet
from ..viewsets.admin.column import StagesViewSet, ColumnsWithAccountsViewSet, \
    BoardGetTransitionsViewSet, BoardGetSubprocessViewSet
from ..viewsets.admin.other import BoardChangePermissionsView
from ..viewsets.admin.subprocess import SubprocessViewSet
from ..viewsets.admin.transition import TransitionsViewSet
from ..viewsets.admin.user import BoardUsersViewSet, UserColumnRelationView

router = DefaultRouter()
router.register('boards', BoardAdminViewSet, base_name='boards')
router.register('stages', StagesViewSet, base_name='stages')
# router.register('transitions', TransitionsViewSet, base_name='transitions')

urlpatterns = [
    url(r'^', include(router.get_urls())),
    url(r'^transitions/$', TransitionsViewSet.as_view({
        'post': 'create',
        'delete': 'destroy_transitions'
    })),
    url(r'^subprocess/$', SubprocessViewSet.as_view({
        'get': 'list',
        'post': 'create',
        'delete': 'custom_destroy'
    })),
    url(r'^boards/(?P<pk>\d+)/accounts/$', ColumnsWithAccountsViewSet.as_view({
        "get": "list"
    })),
    url(r'^boards/(?P<pk>\d+)/accounts/active/$', BoardUsersViewSet.as_view({
        "get": "list"
    })),
    url(r'^boards/(?P<pk>\d+)/modules/$', BoardChangePermissionsView.as_view()),
    url(r'^accounts/$', UserColumnRelationView.as_view()),
    url(r'^boards/(?P<pk>\d+)/transitions/$', BoardGetTransitionsViewSet.as_view({
        'get': 'list'
    })),
    url(r'^boards/(?P<pk>\d+)/subprocess/$', BoardGetSubprocessViewSet.as_view({
        'get': 'list'
    })),
]
