import re
from django.contrib.auth import get_user_model
from rest_framework import serializers

from measurement.measures import Weight, Temperature, Volume

from brivo.utils.functions import get_units_for_user
from brivo.utils.measures import BeerColor, BeerGravity
from brivo.brew import models
from brivo.users.api.serializers import UserNameSerializer


def measurement_field_factory(mclass, munit):

    class MeasurementField(serializers.Field):

        def to_representation(self, obj):
            user = self.context["request"].user
            display_unit = get_units_for_user(user)
            unit = display_unit[munit][0].lower()
            value = getattr(obj, unit)
            return f"{value} {unit}"

        def to_internal_value(self, data):
            units = mclass.UNITS.keys() | mclass.ALIAS.keys()
            pattern = re.compile(r'^(?P<value>(\d+|\d+\.\d+))\s?(?P<unit>(%s))$' % '|'.join(units))
            print(pattern)
            match = pattern.match(data)
            if match is None:
                raise serializers.ValidationError("%s is not a valid %s" % (data, mclass.__name__))
            kwargs = {match.group('unit').lower(): match.group('value')}
            return mclass(**kwargs)
    return MeasurementField


class CustomSerializer(serializers.ModelSerializer):

    def get_field_names(self, declared_fields, info):
        expanded_fields = super(CustomSerializer, self).get_field_names(declared_fields, info)

        if getattr(self.Meta, 'extra_fields', None):
            return expanded_fields + self.Meta.extra_fields
        else:
            return expanded_fields

class CountrySerializer(CustomSerializer):
    class Meta:
        model = models.Country
        fields = ("id", "name", "code")


class FermentableSerializer(CustomSerializer):
    color = measurement_field_factory(BeerColor, "color_units")()
    class Meta:
        model = models.Fermentable
        fields = "__all__"
        extra_fields = ["url"]
        read_only_fields = ["created_at", "updated_at", "slug"]

        extra_kwargs = {
            "url": {"view_name": "api:fermentable-detail", "lookup_field": "pk"}
        }


class ExtraSerializer(CustomSerializer):
    class Meta:
        model = models.Extra
        fields = "__all__"
        extra_fields = ["url"]
        read_only_fields = ["created_at", "updated_at", "slug"]
        extra_kwargs = {
            "url": {"view_name": "api:extras-detail", "lookup_field": "id"}
        }


class YeastSerializer(CustomSerializer):
    temp_min = measurement_field_factory(Temperature, "temp_units")()
    temp_max = measurement_field_factory(Temperature, "temp_units")()
    class Meta:
        model = models.Yeast
        fields = "__all__"
        extra_fields = ["url"]
        read_only_fields = ["created_at", "updated_at", "slug"]
        extra_kwargs = {
            "url": {"view_name": "api:yeast-detail", "lookup_field": "pk"}
        }


class HopSerializer(CustomSerializer):
    country = CountrySerializer()
    class Meta:
        model = models.Hop
        fields = "__all__"
        extra_fields = ["url"]
        read_only_fields = ["created_at", "updated_at", "slug"]
        extra_kwargs = {
            "url": {"view_name": "api:hop-detail", "lookup_field": "pk"}
        }


class TagSerializer(CustomSerializer):
    class Meta:
        model = models.Tag
        fields = ["id", "name", "url"]
        extra_kwargs = {
            "url": {"view_name": "api:hop-detail", "lookup_field": "pk"}
        }


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
        extra_fields = ["url"]
        read_only_fields = ["created_at", "updated_at", "slug"]
        extra_kwargs = {
            "url": {"view_name": "api:style-detail", "lookup_field": "id"}
        }


class StyleNameSerializer(CustomSerializer):
    class Meta:
        model = models.Style
        fields = ["id", "name"]


class IngredientFermentableSerializer(CustomSerializer):
    amount = measurement_field_factory(Weight, "big_weight")()
    color = measurement_field_factory(BeerColor, "color_units")()
    class Meta:
        model = models.IngredientFermentable
        fields = ["name", "amount", "use", "type", "color", "extraction"]


class IngredientHopSerializer(CustomSerializer):
    amount = measurement_field_factory(Weight, "big_weight")()
    class Meta:
        model = models.IngredientHop
        fields = ["name", "amount", "use", "alpha_acids", "time", "time_unit"]


class IngredientYeastSerializer(CustomSerializer):
    amount = measurement_field_factory(Weight, "big_weight")()
    class Meta:
        model = models.IngredientYeast
        fields = ["name", "amount", "type", "lab", "attenuation", "form"]



class IngredientExtraSerializer(CustomSerializer):
    amount = measurement_field_factory(Weight, "big_weight")()
    class Meta:
        model = models.IngredientExtra
        fields = ["name", "amount", "type", "use", "time", "time_unit"]


class MashStepSerializer(CustomSerializer):
    temperature = measurement_field_factory(Temperature, "temp_units")()
    class Meta:
        model = models.MashStep
        fields = ["temperature", "time", "note"]



class RecipeSerializer(CustomSerializer):
    style = StyleNameSerializer()
    user = UserNameSerializer()
    fermentables = IngredientFermentableSerializer(many=True)
    hops = IngredientHopSerializer(many=True)
    yeasts = IngredientYeastSerializer(many=True)
    extras = IngredientExtraSerializer(many=True)
    mash_steps = MashStepSerializer(many=True)
    expected_beer_volume = measurement_field_factory(Volume, "volume")(read_only=True)
    initial_volume = measurement_field_factory(Volume, "volume")(source="get_initial_volume", read_only=True)
    boil_volume = measurement_field_factory(Volume, "volume")(source="get_boil_volume", read_only=True)
    preboil_gravity = measurement_field_factory(BeerGravity, "gravity_units")(source="get_preboil_gravity", read_only=True)
    primary_volume = measurement_field_factory(Volume, "volume")(source="get_primary_volume", read_only=True)
    secondary_volume = measurement_field_factory(Volume, "volume")(source="get_secondary_volume", read_only=True)
    color = measurement_field_factory(BeerColor, "color_units")(source="get_color", read_only=True)
    gravity = measurement_field_factory(BeerGravity, "gravity_units")(source="get_gravity", read_only=True)
    biterness_ratio = serializers.DecimalField(5, 1, source="get_bitterness_ratio", read_only=True)
    abv = serializers.DecimalField(5, 1, source="get_abv", read_only=True)
    ibu = serializers.DecimalField(5, 1, source="get_ibu", read_only=True)
    class Meta:
        model = models.Recipe
        fields = [
            "id",
            "user",
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
            "url",
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
            "user",
            "created_at",
            "updated_at",
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
        extra_kwargs = {
            "url": {"view_name": "api:recipe-detail", "lookup_field": "id"}
        }


    def update(self, instance, validated_data):
        if validated_data.get('fermentables'):
            fermentables = tuple({f.id: f for f in (instance.fermentables).all()})
            fermentables_data = validated_data.pop('fermentable')
            updated_fermentables = []
            for fermentable_data in fermentables_data:
                ingredient_fermentable_serializer = IngredientFermentableSerializer(data=fermentable_data)
                if ingredient_fermentable_serializer.id in fermentables:
                    if ingredient_fermentable_serializer.is_valid():
                        fermentable = ingredient_fermentable_serializer.update(
                            instance=fermentables[ingredient_fermentable_serializer.id],
                            validated_data=ingredient_fermentable_serializer.validated_data)
                        updated_fermentables.append(fermentable)
                else:
                    if ingredient_fermentable_serializer.is_valid():
                        fermentable = ingredient_fermentable_serializer.create(
                            validated_data=ingredient_fermentable_serializer.validated_data)
                        updated_fermentables.append(fermentable)
            validated_data['fermentables'] = updated_fermentables

        # instance.username = validated_data.get("username", instance.username)
        # instance.email = validated_data.get("email", instance.email)
        instance.save()
        return instance

