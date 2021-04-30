from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAdminUser, SAFE_METHODS

from brivo.brew import models
from brivo.brew.api import serializers


class IsAdminUserOrReadOnly(IsAdminUser):

    def has_permission(self, request, view):
        is_admin = super().has_permission(request, view)
        return (request.method in SAFE_METHODS or is_admin) and request.user.is_authenticated


class FermentableViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = serializers.FermentableSerializer
    queryset = models.Fermentable.objects.all()
    lookup_field = "pk"
    permission_classes = (IsAdminUserOrReadOnly,)


class ExtraViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = serializers.ExtraSerializer
    queryset = models.Extra.objects.all()
    lookup_field = "pk"
    permission_classes = (IsAdminUserOrReadOnly,)


class YeastViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = serializers.YeastSerializer
    queryset = models.Yeast.objects.all()
    lookup_field = "pk"
    permission_classes = (IsAdminUserOrReadOnly,)

    def get_serializer_context(self):
        context = super(YeastViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context


class HopViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = serializers.HopSerializer
    queryset = models.Hop.objects.all()
    lookup_field = "pk"
    permission_classes = (IsAdminUserOrReadOnly,)