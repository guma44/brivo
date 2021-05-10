import re
from collections import OrderedDict
from django.contrib.auth import get_user_model
from rest_framework import serializers

from measurement.measures import Weight, Temperature, Volume

from brivo.utils.functions import get_user_units
from brivo.utils.measures import BeerColor, BeerGravity
from brivo.brew import models
from brivo.users.api.serializers import UserNameSerializer


# Non-field imports, but public API
from rest_framework.fields import (  # NOQA # isort:skip
    CreateOnlyDefault, CurrentUserDefault, SkipField, empty
)
from rest_framework.relations import Hyperlink, PKOnlyObject  # NOQA # isort:skip


def measurement_field_factory(mclass, munit):

    class MeasurementField(serializers.Field):

        def to_representation(self, obj):
            unit = get_user_units(self.root.user)[munit]
            value = getattr(obj, unit)
            return f"{value} {unit}"

        def to_internal_value(self, data):
            units = mclass.UNITS.keys() | mclass.ALIAS.keys()
            if str(mclass).split(".")[-1][:-2] == "Mass":
                units = units | {"kg", "kilogram"}
            pattern = re.compile(r'^(?P<value>(\d+|\d+\.\d+))\s?(?P<unit>(%s))$' % '|'.join(units))
            match = pattern.match(data)
            if match is None:
                raise serializers.ValidationError("%s is not a valid %s" % (data, mclass.__name__))
            kwargs = {match.group('unit').lower(): match.group('value')}
            return mclass(**kwargs)

        # def get_attribute(self, obj):
        #     return obj

    return MeasurementField


class CustomSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    # Add user also to ListSerializer
    @classmethod
    def many_init(cls, *args, **kwargs):
        allow_empty = kwargs.pop('allow_empty', None)
        child_serializer = cls(*args, **kwargs)
        list_kwargs = {
            'child': child_serializer,
        }
        if allow_empty is not None:
            list_kwargs['allow_empty'] = allow_empty
        list_kwargs.update({
            key: value for key, value in kwargs.items()
            if key in serializers.LIST_SERIALIZER_KWARGS
        })
        meta = getattr(cls, 'Meta', None)
        list_serializer_class = getattr(meta, 'list_serializer_class', serializers.ListSerializer)
        lserializer = list_serializer_class(*args, **list_kwargs)
        lserializer.user = child_serializer.user
        return lserializer


    def get_field_names(self, declared_fields, info):
        expanded_fields = super(CustomSerializer, self).get_field_names(declared_fields, info)

        if getattr(self.Meta, 'extra_fields', None):
            return expanded_fields + self.Meta.extra_fields
        else:
            return expanded_fields


class AddIDMixin:
    def to_internal_value(self, data):
        ret = super(AddIDMixin, self).to_internal_value(data)

        id_attr = getattr(self.Meta, 'update_lookup_field', 'id')
        try:
            method = getattr(self.context["request"], "method", "")
        except KeyError:
            method = ""

        if method in ('PUT', 'PATCH') and id_attr:
            id_field = self.fields[id_attr]
            id_value = id_field.get_value(data)
            ret[id_attr] = id_value

        return ret

class CountrySerializer(CustomSerializer):
    class Meta:
        model = models.Country
        fields = ("id", "name", "code")


class FermentableSerializer(CustomSerializer):
    color = measurement_field_factory(BeerColor, "color_units")()
    class Meta:
        model = models.Fermentable
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at", "slug"]



class ExtraSerializer(CustomSerializer):
    class Meta:
        model = models.Extra
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at", "slug"]


class YeastSerializer(CustomSerializer):
    temp_min = measurement_field_factory(Temperature, "temperature_units")()
    temp_max = measurement_field_factory(Temperature, "temperature_units")()
    class Meta:
        model = models.Yeast
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at", "slug"]


class HopSerializer(CustomSerializer):
    class Meta:
        model = models.Hop
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at", "slug"]

    def to_representation(self, instance):
        self.fields['country'] =  CountrySerializer(read_only=True)
        return super(HopSerializer, self).to_representation(instance)


class TagSerializer(CustomSerializer):
    class Meta:
        model = models.Tag
        fields = ["id", "name"]


class StyleSerializer(CustomSerializer):
    og_min = measurement_field_factory(BeerGravity, "gravity_units")()
    og_max = measurement_field_factory(BeerGravity, "gravity_units")()
    fg_min = measurement_field_factory(BeerGravity, "gravity_units")()
    fg_max = measurement_field_factory(BeerGravity, "gravity_units")()
    color_min = measurement_field_factory(BeerColor, "color_units")()
    color_max = measurement_field_factory(BeerColor, "color_units")()
    tags = TagSerializer(many=True)
    class Meta:
        model = models.Style
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at", "slug"]


class StyleNameSerializer(CustomSerializer):
    class Meta:
        model = models.Style
        fields = ["id", "name"]


class IngredientFermentableSerializer(AddIDMixin, CustomSerializer):
    amount = measurement_field_factory(Weight, "mass_units")()
    color = measurement_field_factory(BeerColor, "color_units")()
    class Meta:
        model = models.IngredientFermentable
        fields = ["id", "name", "amount", "use", "type", "color", "extraction"]


class IngredientHopSerializer(AddIDMixin, CustomSerializer):
    amount = measurement_field_factory(Weight, "mass_units")()
    class Meta:
        model = models.IngredientHop
        fields = ["id", "name", "amount", "use", "alpha_acids", "time", "time_unit"]


class IngredientYeastSerializer(AddIDMixin, CustomSerializer):
    amount = measurement_field_factory(Weight, "mass_units")()
    class Meta:
        model = models.IngredientYeast
        fields = ["id", "name", "amount", "type", "lab", "attenuation", "form"]


class IngredientExtraSerializer(AddIDMixin, CustomSerializer):
    amount = measurement_field_factory(Weight, "mass_units")()
    class Meta:
        model = models.IngredientExtra
        fields = ["id", "name", "amount", "type", "use", "time", "time_unit"]


class MashStepSerializer(AddIDMixin, CustomSerializer):
    temperature = measurement_field_factory(Temperature, "temperature_units")()
    class Meta:
        model = models.MashStep
        fields = ["id", "temperature", "time", "note"]


class RecipeSerializer(CustomSerializer):
    fermentables = IngredientFermentableSerializer(many=True)
    hops = IngredientHopSerializer(many=True)
    yeasts = IngredientYeastSerializer(many=True)
    extras = IngredientExtraSerializer(many=True)
    mash_steps = MashStepSerializer(many=True)
    expected_beer_volume = measurement_field_factory(Volume, "volume_units")()
    initial_volume = measurement_field_factory(Volume, "volume_units")(source="get_initial_volume", read_only=True)
    boil_volume = measurement_field_factory(Volume, "volume_units")(source="get_boil_volume", read_only=True)
    preboil_gravity = measurement_field_factory(BeerGravity, "gravity_units")(source="get_preboil_gravity", read_only=True)
    primary_volume = measurement_field_factory(Volume, "volume_units")(source="get_primary_volume", read_only=True)
    secondary_volume = measurement_field_factory(Volume, "volume_units")(source="get_secondary_volume", read_only=True)
    color = measurement_field_factory(BeerColor, "color_units")(source="get_color", read_only=True)
    gravity = measurement_field_factory(BeerGravity, "gravity_units")(source="get_gravity", read_only=True)
    biterness_ratio = serializers.DecimalField(5, 1, source="get_bitterness_ratio", read_only=True)
    abv = serializers.DecimalField(5, 1, source="get_abv", read_only=True)
    ibu = serializers.DecimalField(5, 1, source="get_ibu", read_only=True)
    class Meta:
        model = models.Recipe
        fields = [
            "id",
            "name",
            "style",
            "type",
            "expected_beer_volume",
            "fermentables",
            "hops",
            "yeasts",
            "extras",
            "mash_steps",
            "boil_time",
            "evaporation_rate",
            "boil_loss",
            "trub_loss",
            "dry_hopping_loss",
            "mash_efficiency",
            "liquor_to_grist_ratio",
            "note",
            "is_public",
            "ibu",
            "expected_beer_volume",
            "initial_volume",
            "boil_volume",
            "preboil_gravity",
            "primary_volume",
            "secondary_volume",
            "color",
            "abv",
            "gravity",
            "biterness_ratio",
        ]
        read_only_fields = [
            "id"
            "created_at",
            "updated_at"
        ]


    def create(self, validated_data):
        fermentables_data = validated_data.pop('fermentables', [])
        hops_data = validated_data.pop('hops', [])
        yeasts_data = validated_data.pop('yeasts', [])
        extras_data = validated_data.pop('extras', [])
        mash_steps_data = validated_data.pop('mash_steps', [])
        validated_data["user"] = self.user
        recipe = models.Recipe.objects.create(**validated_data)
        for fermentable_data in fermentables_data:
            fermentable_data["recipe"] = recipe
            models.IngredientFermentable.objects.create(**fermentable_data)
        for hop_data in hops_data:
            hop_data["recipe"] = recipe
            models.IngredientHop.objects.create(**hop_data)
        for yeast_data in yeasts_data:
            yeast_data["recipe"] = recipe
            models.IngredientYeast.objects.create(**yeast_data)
        for extra_data in extras_data:
            extra_data["recipe"] = recipe
            models.IngredientExtra.objects.create(**extra_data)
        for mash_step_data in mash_steps_data:
            mash_step_data["recipe"] = recipe
            models.MashStep.objects.create(**mash_step_data)    
        return recipe

    def _update_ingredient(self, instance, data, attr, iclass):

        item_ids = [item["id"] for item in data] # if "id" in item]
        # Delete items not included in the request
        for item in getattr(instance, attr).all():
            if item.id not in item_ids:
                item.delete()
        # Create or update page instances that are in the request
        for item_data in data:
            item_data.update({"recipe": instance})
            if "id" in item_data:
                obj_id = item_data.pop("id")
                try:
                    obj = iclass.objects.get(id=obj_id, recipe=instance)
                    for field, value in item_data.items():
                        setattr(obj, field, value)
                    obj.save(update_fields=item_data.keys())
                except iclass.DoesNotExist:
                    item = iclass(**item_data)
                    item.save()
            else:
                item = iclass(**item_data)
                item.save()

    def update(self, instance, validated_data):
        if 'fermentables' in validated_data:
            fermentables_data = validated_data.pop('fermentables')
            self._update_ingredient(instance, fermentables_data, "fermentables", models.IngredientFermentable)
        if 'hops' in validated_data:
            hops_data = validated_data.pop('hops')
            self._update_ingredient(instance, hops_data, "hops", models.IngredientHop)
        if 'yeasts' in validated_data:
            yeasts_data = validated_data.pop('yeasts')
            self._update_ingredient(instance, yeasts_data, "yeasts", models.IngredientYeast)
        if 'extras' in validated_data:
            extras_data = validated_data.pop('extras')
            self._update_ingredient(instance, extras_data, "extras", models.IngredientExtra)
        if 'mash_steps' in validated_data:
            mash_steps_data = validated_data.pop('mash_steps')
            self._update_ingredient(instance, mash_steps_data, "mash_steps", models.MashStep)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save(update_fields=validated_data.keys())
        return instance


class RecipeReadSerializer(RecipeSerializer):
    style = StyleNameSerializer()
    user = UserNameSerializer()

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["user"]
