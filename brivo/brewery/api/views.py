from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
)
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAdminUser, SAFE_METHODS, IsAuthenticated

from brivo.brewery import models
from brivo.brewery.api import serializers


class IsAdminUserOrReadOnly(IsAdminUser):
    def has_permission(self, request, view):
        is_admin = super().has_permission(request, view)
        return (
            request.method in SAFE_METHODS or is_admin
        ) and request.user.is_authenticated


class IsOwnerOrReadOnly(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS and getattr(obj, "is_public", False):
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return self.has_permission(request, view) and obj.user == request.user


class AddUserMixin:
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs["context"] = self.get_serializer_context()
        kwargs["user"] = self.request.user
        return serializer_class(*args, **kwargs)


class FermentableViewSet(
    AddUserMixin,
    RetrieveModelMixin,
    ListModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = serializers.FermentableSerializer
    queryset = models.Fermentable.objects.all()
    lookup_field = "id"
    permission_classes = (IsAdminUserOrReadOnly,)


class ExtraViewSet(
    AddUserMixin,
    RetrieveModelMixin,
    ListModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = serializers.ExtraSerializer
    queryset = models.Extra.objects.all()
    lookup_field = "id"
    permission_classes = (IsAdminUserOrReadOnly,)


class YeastViewSet(
    AddUserMixin,
    RetrieveModelMixin,
    ListModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = serializers.YeastSerializer
    queryset = models.Yeast.objects.all()
    lookup_field = "id"
    permission_classes = (IsAdminUserOrReadOnly,)


class HopViewSet(
    AddUserMixin,
    RetrieveModelMixin,
    ListModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = serializers.HopSerializer
    queryset = models.Hop.objects.all()
    lookup_field = "id"
    permission_classes = (IsAdminUserOrReadOnly,)


class StyleViewSet(
    AddUserMixin,
    RetrieveModelMixin,
    ListModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = serializers.StyleSerializer
    queryset = models.Style.objects.all()
    lookup_field = "id"
    permission_classes = (IsAdminUserOrReadOnly,)


class RecipeViewSet(
    AddUserMixin,
    RetrieveModelMixin,
    ListModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = serializers.RecipeSerializer
    queryset = models.Recipe.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)
    lookup_field = "id"

    def get_queryset(self):
        return models.Recipe.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        request.data.update({"user": request.user.id})
        return super(RecipeViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        request.data.update({"user": request.user.id})
        return super(RecipeViewSet, self).update(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method in ["GET"]:
            return serializers.RecipeReadSerializer
        return serializers.RecipeSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs["context"] = self.get_serializer_context()
        kwargs["user"] = self.request.user
        return serializer_class(*args, **kwargs)


class BatchViewSet(
    AddUserMixin,
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    GenericViewSet,
):
    queryset = models.Batch.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)
    lookup_field = "id"

    def get_queryset(self):
        return models.Batch.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        request.data.update({"user": request.user.id})
        return super(BatchViewSet, self).create(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "init":
            return serializers.BatchInitSerializer
        elif self.action == "mash":
            return serializers.BatchMashSerializer
        elif self.action == "boil":
            return serializers.BatchBoilSerializer
        elif self.action == "primary":
            return serializers.BatchPrimarySerializer
        elif self.action == "secondary":
            return serializers.BatchSecondarySerializer
        elif self.action == "packaging":
            return serializers.BatchPackagingSerializer
        else:
            return serializers.BatchSerializer

    def _get_stage_or_update(self, request, id=None):
        sc = self.get_serializer_class()
        obj = self.get_queryset().get(pk=id)
        serializer_context = {
            "request": request,
        }
        if self.request.method == "PUT":
            ser = sc(obj, data=request.data, user=obj.user, context=serializer_context)
            if not ser.is_valid():
                return Response(ser.errors, status=400)
            ser.save()
            return Response(ser.data)
        elif self.request.method == "PATCH":
            ser = sc(
                obj,
                data=request.data,
                user=obj.user,
                context=serializer_context,
                partial=True,
            )
            if not ser.is_valid():
                return Response(ser.errors, status=400)
            ser.save()
            return Response(ser.data)
        else:
            ser = sc(obj, user=obj.user, context=serializer_context)
        return Response(ser.data)

    @action(methods=["post"], detail=False)
    def init(self, request):
        sc = self.get_serializer_class()
        request.data.update({"user": request.user.id})
        serializer_context = {
            "request": request,
        }
        ser = sc(data=request.data, user=request.user, context=serializer_context)
        if not ser.is_valid():
            return Response(ser.errors, status=400)
        ser.save()
        return Response(ser.data, status=201)

    @action(methods=["get", "put", "patch"], detail=True)
    def mash(self, request, id=None):
        return self._get_stage_or_update(request=request, id=id)

    @action(methods=["get", "put", "patch"], detail=True)
    def boil(self, request, id=None):
        return self._get_stage_or_update(request=request, id=id)

    @action(methods=["get", "put", "patch"], detail=True)
    def primary(self, request, id=None):
        return self._get_stage_or_update(request=request, id=id)

    @action(methods=["get", "put", "patch"], detail=True)
    def secondary(self, request, id=None):
        return self._get_stage_or_update(request=request, id=id)

    @action(methods=["get", "put", "patch"], detail=True)
    def packaging(self, request, id=None):
        return self._get_stage_or_update(request=request, id=id)

    @action(methods=["post"], detail=True)
    def finish(self, request, id=None):
        sc = self.get_serializer_class()
        obj = self.get_queryset().get(pk=id)
        serializer_context = {
            "request": request,
        }
        ser = sc(obj, user=obj.user, context=serializer_context)
        data = {k:v for k, v in ser.data.items() if v is not None}
        data["stage"] = "FINISHED"
        ser = sc(data=data, user=obj.user, context=serializer_context)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        else:
            return Response(ser.errors)
