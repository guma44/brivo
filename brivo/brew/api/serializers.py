import re
from django.contrib.auth import get_user_model
from rest_framework import serializers

from measurement.measures import Weight, Temperature

from brivo.utils.functions import get_units_for_user
from brivo.utils.measures import BeerColor, BeerGravity
from brivo.brew import models



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


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Country
        fields = ("id", "name", "code")
        read_only_fields = ["created_at", "updated_at"]


class FermentableSerializer(serializers.ModelSerializer):
    color = measurement_field_factory(BeerColor, "color_units")()
    class Meta:
        model = models.Fermentable
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

        extra_kwargs = {
            "url": {"view_name": "api:fermentable-detail", "lookup_field": "pk"}
        }


class ExtraSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Extra
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]
        extra_kwargs = {
            "url": {"view_name": "api:extras-detail", "lookup_field": "id"}
        }


class YeastSerializer(serializers.ModelSerializer):
    temp_min = measurement_field_factory(Temperature, "temp_units")()
    temp_max = measurement_field_factory(Temperature, "temp_units")()
    class Meta:
        model = models.Yeast
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]
        extra_kwargs = {
            "url": {"view_name": "api:yeast-detail", "lookup_field": "pk"}
        }


class HopSerializer(serializers.ModelSerializer):
    country = CountrySerializer()
    class Meta:
        model = models.Hop
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]
        extra_kwargs = {
            "url": {"view_name": "api:hop-detail", "lookup_field": "pk"}
        }


class StyleSerializer(serializers.ModelSerializer):
    og_min = measurement_field_factory(BeerGravity, "gravity_units")()
    og_max = measurement_field_factory(BeerGravity, "gravity_units")()
    fg_min = measurement_field_factory(BeerGravity, "gravity_units")()
    fg_max = measurement_field_factory(BeerGravity, "gravity_units")()
    color_min = measurement_field_factory(BeerColor, "color_units")()
    color_max = measurement_field_factory(BeerColor, "color_units")()
    class Meta:
        model = models.Style
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]
        extra_kwargs = {
            "url": {"view_name": "api:style-detail", "lookup_field": "id"}
        }