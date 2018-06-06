# coding: utf-8
from django.contrib.auth import authenticate, logout, get_user_model
from django.contrib.auth.hashers import make_password
from django.utils.translation import ugettext_lazy as _
from rest_framework import status, serializers
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..authentication import TokenAuthentication
from ..models import Token
from ..permissions import IsAuthenticated, TokenRequired
from ..serializers.sign import SignUpSerializer, ChangePasswordSerializer, SigninSerializer
from ..serializers.token import TokenSerializer
from ..serializers.user import UserDetailSerializer


class AuthViewSet(GenericViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        return {
                   'handshake': TokenSerializer,
                   'signin': SigninSerializer,
                   'signout': None,
                   'signup': SignUpSerializer,
                   'change_password': ChangePasswordSerializer,
               }.get(self.action, None) or serializers.Serializer

    @list_route(methods=['post'], permission_classes=())
    def handshake(self, request):
        if request.auth:
            auth = request.auth
            if not auth.user:
                return Response({}, status=status.HTTP_401_UNAUTHORIZED)
            serializer = UserDetailSerializer(auth.user)
            resp = Response(serializer.data)
        else:
            token_serializer = self.get_serializer(data=request.data, instance=request.auth)
            token_serializer.is_valid(raise_exception=True)
            token_serializer.save()
            auth = token_serializer.instance
            resp = Response({"data": ""}, status=status.HTTP_204_NO_CONTENT)
        resp['Authorization'] = auth.key
        return resp

    @list_route(methods=['post'], permission_classes=(TokenRequired,))
    def signin(self, request):
        if request.user.is_authenticated():
            return Response(UserDetailSerializer(request.user).data)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if user is None:
            return Response(
                {'detail': _('Wrong username/password')},
                status=status.HTTP_400_BAD_REQUEST
            )
        request.auth.user = user
        request.user = user
        request.auth.save()
        Token.objects.get_by_key.clear_cache(request.auth.key)

        return Response(UserDetailSerializer(user).data)

    @list_route(methods=['post'])
    def signout(self, request):
        if request.user.is_authenticated():
            request.auth.user = None
            request.auth.save()
            logout(request)

        return Response({'detail': _("You successfully logout")})

    @list_route(methods=['post'])
    def change_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_pass = serializer.validated_data['new_pass']
        request.user.password = make_password(new_pass)
        request.user.save()
        return Response({'detail': _("successful operation")}, status=status.HTTP_200_OK)

    @list_route(methods=['post'], permission_classes=(TokenRequired,))
    def signup(self, request, *args, **kwargs):
        """
        User registration
        """

        # TODO: Test
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        User = get_user_model()
        username_field = User.USERNAME_FIELD
        data = {username_field: serializer.validated_data.get('email'),
                'password': make_password(serializer.validated_data.get('password'))}
        if not User.objects.filter(**{username_field: data[username_field]}).exists():
            User.objects.create(**data)
            return Response({}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': _('User already exists')}, status=status.HTTP_400_BAD_REQUEST)
