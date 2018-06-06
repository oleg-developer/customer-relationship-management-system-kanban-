from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from rest_framework_swagger.views import get_swagger_view

from nc_auth.viewsets import AuthViewSet
from nc_auth.viewsets.user import UserViewSet

schema_view = get_swagger_view(title='Nicecode Automation API')

router = DefaultRouter()

admin.autodiscover()

router.register('accounts', UserViewSet, base_name='accounts')
router.register('auth', AuthViewSet, base_name='auth')


def raise500(request):
    raise Exception("Ok, is that what you want?")


urlpatterns = [
    url(r'^apidocs/$', schema_view),
    url(r'^admin/', admin.site.urls),
    url(r'^jet/', include('jet.urls', namespace='jet')),
    url(r'^api/v1/', include(router.get_urls())),
    url(r'^api/v1/', include('nc_workflow.urls')),
    url(r'^api/v1/', include('nc_notes.urls')),
    url(r'^api/v1/admin/', include('nc_workflow.urls.admin')),
    url(r'^api/v1/clients/', include('nc_clients.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      url(r'^api/v1/500/$', raise500),
                      url(r'^__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
