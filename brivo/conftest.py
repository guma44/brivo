import pytest

from rest_framework.test import APIClient
from model_bakery import baker
from measurement.measures import Volume, Mass, Temperature

from brivo.utils.measures import BeerColor, BeerGravity
from brivo.users.models import User, UserProfile, UserBrewery
from brivo.users.tests.factories import UserFactory


baker.generators.add('brivo.brew.fields.BeerColorField', lambda: BeerColor(srm=10))
baker.generators.add('brivo.brew.fields.BeerGravityField', lambda: BeerGravity(plato=10))
baker.generators.add('brivo.brew.fields.VolumeField', lambda: Volume(l=10))
baker.generators.add('brivo.brew.fields.MassField', lambda: Mass(kg=1))
baker.generators.add('brivo.brew.fields.TemperatureField', lambda: Temperature(c=10))


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> User:
    user = UserFactory()
    user.profile = UserProfile(user=user)
    user.brewery = UserBrewery(user=user)
    return user



@pytest.fixture()
def admin_user(db, django_user_model, django_username_field):
    """A Django admin user.
    This uses an existing user with username "admin", or creates a new one with
    password "password".
    """
    UserModel = django_user_model
    username_field = django_username_field
    username = "admin@example.com" if username_field == "email" else "admin"

    try:
        # The default behavior of `get_by_natural_key()` is to look up by `username_field`.
        # However the user model is free to override it with any sort of custom behavior.
        # The Django authentication backend already assumes the lookup is by username,
        # so we can assume so as well.
        user = UserModel._default_manager.get_by_natural_key(username)
    except UserModel.DoesNotExist:
        user_data = {}
        user_data["email"] = "admin@example.com"
        user_data["password"] = "password"
        user_data["username"] = username
        user = UserModel._default_manager.create_superuser(**user_data)
    return user


@pytest.fixture
def api_client():
    return APIClient