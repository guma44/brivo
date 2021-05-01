from django.contrib.auth import get_user_model
from rest_framework import serializers
from brivo.users import models

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfile
        fields = [
            "pk",
            "image",
            "general_units",
            "temperature_units",
            "gravity_units",
            "color_units"]


class UserBrewerySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserBrewery
        fields = [
            "pk",
            "image",
            "name",
            "external_link",
            "number_of_batches"]


class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=True)
    brewery_profile = UserBrewerySerializer(required=True)

    class Meta:
        model = User
        fields = ["pk", "username", "email", "url", "profile", "brewery_profile"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "username"}
        }

    def update(self, instance, validated_data):
        if validated_data.get('profile'):
            profile_data = validated_data.pop('profile')
            profile_serializer = UserProfileSerializer(data=profile_data)

            if profile_serializer.is_valid():
                profile = profile_serializer.update(instance=instance.profile,
                                                    validated_data=profile_serializer.validated_data)
                validated_data['profile'] = profile

        if validated_data.get('brewery_profile'):
            brewery_profile_data = validated_data.pop('brewery_profile')
            brewery_profile_serializer = UserBrewerySerializer(data=brewery_profile_data)

            if brewery_profile_serializer.is_valid():
                brewery_profile = brewery_profile_serializer.update(instance=instance.brewery_profile,
                                                    validated_data=brewery_profile_serializer.validated_data)
                validated_data['brewery_profile'] = brewery_profile

        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.save()
        return instance
