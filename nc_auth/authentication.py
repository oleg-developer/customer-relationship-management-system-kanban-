from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication as BaseTokenAuthentication

from nc_auth.models import Token


class TokenAuthentication(BaseTokenAuthentication):
    model = Token

    def authenticate(self, request):
        if settings.DEBUG and request.META["HTTP_HOST"].split(":")[0] in ("localhost", "127.0.0.1"):
            if "HTTP_AUTHORIZATION" not in request.META and "Authorization" in request.COOKIES:
                request.META["HTTP_AUTHORIZATION"] = request.COOKIES.get("Authorization", b"")
        return super(TokenAuthentication, self).authenticate(request)

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.get_by_key(key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if token.user and not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        return token.user or AnonymousUser(), token
