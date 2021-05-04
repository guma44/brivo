from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin, CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAdminUser, SAFE_METHODS

from brivo.brew import models
from brivo.brew.api import serializers


class IsAdminUserOrReadOnly(IsAdminUser):

    def has_permission(self, request, view):
        is_admin = super().has_permission(request, view)
        return (request.method in SAFE_METHODS or is_admin) and request.user.is_authenticated


class FermentableViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = serializers.FermentableSerializer
    queryset = models.Fermentable.objects.all()
    lookup_field = "id"
    permission_classes = (IsAdminUserOrReadOnly,)


class ExtraViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = serializers.ExtraSerializer
    queryset = models.Extra.objects.all()
    lookup_field = "id"
    permission_classes = (IsAdminUserOrReadOnly,)


class YeastViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = serializers.YeastSerializer
    queryset = models.Yeast.objects.all()
    lookup_field = "id"
    permission_classes = (IsAdminUserOrReadOnly,)


class HopViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = serializers.HopSerializer
    queryset = models.Hop.objects.all()
    lookup_field = "id"
    permission_classes = (IsAdminUserOrReadOnly,)


class StyleViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = serializers.StyleSerializer
    queryset = models.Style.objects.all()
    lookup_field = "id"
    permission_classes = (IsAdminUserOrReadOnly,)


class MashStepViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = serializers.MashStepSerializer
    queryset = models.MashStep.objects.all()
    lookup_field = "id"


class RecipeViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = serializers.RecipeSerializer
    queryset = models.Recipe.objects.all()
    lookup_field = "id"

    def get_queryset(self):
        return models.Recipe.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        request.data.update({'user': request.user.id})
        return super(RecipeViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        request.data.update({'user': request.user.id})
        return super(RecipeViewSet, self).update(request, *args, **kwargs)


    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return serializers.RecipeReadSerializer
        return serializers.RecipeSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        kwargs['user'] = self.request.user
        return serializer_class(*args, **kwargs)
    