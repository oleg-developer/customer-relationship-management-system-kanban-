from rest_framework.decorators import detail_route
from rest_framework.viewsets import ModelViewSet

from ..models import User
from ..permissions import BasePermission, IsAuthenticated, IsCompanyOwner
from ..serializers.user import UserAvatarSerializer, UserShortSerializer, UserDetailSerializer


class SelfUser(BasePermission):
    def has_permission_ex(self, request, view, obj):
        user_pk = view.kwargs.get(view.lookup_field, None)
        return user_pk and request.user.id == int(user_pk)


class UserViewSet(ModelViewSet):
    """
    Accepts `self` get param to add current session user to queryset
    """
    # permission_classes = (OrCombiner(IsCompanyOwner, SelfUser),)
    permission_classes = (IsAuthenticated, IsCompanyOwner,)
    queryset = User.objects.filter(is_active=True)

    def filter_queryset(self, queryset):
        queryset = queryset.filter(company_id=self.request.user.company_id)
        if "self" in self.request.GET:
            return queryset
        else:
            return queryset.exclude(id=self.request.user.id)

    def get_serializer_class(self, *args, **kwargs):
        return {
            'list': UserShortSerializer,
            'retrieve': UserDetailSerializer,

            'create': UserDetailSerializer,
            'update': UserDetailSerializer,
            'partial_update': UserDetailSerializer,

            'avatar': UserAvatarSerializer
        }.get(self.action, UserShortSerializer)

    @detail_route(methods=['put'])
    def avatar(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
