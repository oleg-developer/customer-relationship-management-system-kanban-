from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from nc_clients.viewsets.client_meta import ClientMeta
from .viewsets.client import ClientViewSet, get_type_faces, client_relations
from .viewsets.employee import EmployeeViewSet
from .viewsets.group import GroupViewSet, client_group
from .viewsets.tag import TagViewSet, client_tag

client_router = DefaultRouter()
client_router.register('', ClientViewSet, base_name='clients')

employee_router = DefaultRouter()
employee_router.register('', EmployeeViewSet, base_name='employees')

group_router = DefaultRouter()
group_router.register('', GroupViewSet, base_name='groups')

tag_router = DefaultRouter()
tag_router.register('', TagViewSet, base_name='tags')

urlpatterns = [
    url(r'^type_faces/$', get_type_faces),
    url(r'^(?P<pk>[0-9]+)/relations/(?P<other_pk>[0-9]+)/$', client_relations),
    url(r'^(?P<client_pk>[0-9]+)/group/(?:(?P<group_pk>[0-9]+)/)?$', client_group),
    url(r'^(?P<client_pk>[0-9]+)/tag/(?:(?P<tag_pk>[0-9]+)/)?$', client_tag),
    url(r'^meta/(?P<client_type>\w+)/$', ClientMeta.as_view()),
    url(r'^employees/', include(employee_router.urls)),
    url(r'^groups/', include(group_router.urls)),
    url(r'^tags/', include(tag_router.urls)),
    url(r'^', include(client_router.urls)),
]
