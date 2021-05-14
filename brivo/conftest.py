import json
from pathlib import Path
import pytest

from rest_framework.test import APIClient
from model_bakery import baker
from model_bakery.generators import random_gen
from measurement.measures import Volume, Mass, Temperature

from brivo.utils.measures import BeerColor, BeerGravity
from brivo.users.models import User, UserProfile, UserBrewery
from brivo.brew.models import Style
from brivo.users.tests.factories import UserFactory


baker.generators.add('brivo.brew.fields.BeerColorField', lambda: BeerColor(srm=10))
baker.generators.add('brivo.brew.fields.BeerGravityField', lambda: BeerGravity(plato=10))
baker.generators.add('brivo.brew.fields.VolumeField', lambda: Volume(l=10))
baker.generators.add('brivo.brew.fields.MassField', lambda: Mass(kg=1))
baker.generators.add('brivo.brew.fields.TemperatureField', lambda: Temperature(c=10))
baker.generators.add('modelcluster.fields.ParentalKey', random_gen.gen_related)


ROOT_DIR = Path(__file__).resolve(strict=True).parent

@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user():
    user = UserFactory()
    user.profile = UserProfile(user=user)
    user.brewery = UserBrewery(user=user)
    return user


@pytest.fixture
def other_user():
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

@pytest.fixture
def style():
    style_input = {
        "category_id": "3A",
        "category": "Czech Lager",
        "name": "Czech Pale Lager",
        "og_min": BeerGravity(sg=1.028),
        "og_max": BeerGravity(sg=1.044),
        "fg_min": BeerGravity(sg=1.008),
        "fg_max": BeerGravity(sg=1.014),
        "ibu_min": 20,
        "ibu_max": 35,
        "color_min": BeerColor(srm=3),
        "color_max": BeerColor(srm=6),
        "alcohol_min": 3.0,
        "alcohol_max": 4.1,
        "ferm_type": "Lager",
        "desc_aroma": "Light to moderate bready-rich malt combined with light to moderate spicy or herbal hop bouquet, the balance between the malt and hops may vary. Faint hint of caramel is acceptable. Light (but never intrusive) diacetyl and light, fruity hop-derived esters are acceptable, but need not be present. No sulfur.",
        "desc_appe": "Light gold to deep gold color. Brilliant to very clear, with a long-lasting, creamy white head. ",
        "desc_flavor": "Medium-low to medium bready-rich malt flavor with a rounded, hoppy finish. Low to medium-high spicy or herbal hop flavor. Bitterness is prominent but never harsh. Flavorful and refreshing. Diacetyl or fruity esters are acceptable at low levels, but need not be present and should never be overbearing.",
        "desc_mouth": "Medium-light to medium body. Moderate carbonation. ",
        "desc_overall": "A lighter-bodied, rich, refreshing, hoppy, bitter pale Czech lager having the familiar flavors of the stronger Czech Premium Pale Lager (Pilsner-type) beer but in a lower alcohol, lighter-bodied, and slightly less intense format.",
        "desc_comment": "The Czech name of the style is svìtlé výèepní pivo. ",
        "desc_ingre": "Soft water with low sulfate and carbonate content, Saazer-type hops, Czech Pilsner malt, Czech lager yeast. Low ion water provides a distinctively soft, rounded hop profile despite high hopping rates. ",
        "desc_history": "Josef Groll initially brewed two types of beer in 1842–3, a výèepní and a ležák, with the smaller beer having twice the production, Evan Rail speculates that these were probably 10 °P and 12 °P beers, but that the výèepní could have been weaker. This is the most consumed type of beer in the Czech Republic at present.",
        "desc_style_comp": "A lighter-bodied, lower-intensity, refreshing, everyday version of Czech Premium Pale Lager.",
        "commercial_exam": "Bøezòák Svìtlé výèepní pivo, Notch Session Pils, Pivovar Kout na Šumavì Koutská 10°, Únìtické pivo 10°",
        "active": True
    }
    return Style.objects.create(**style_input)


@pytest.fixture
def recipes(api_client, user, style):
    client = api_client()
    client.force_authenticate(user)
    with open(ROOT_DIR.joinpath("brew/tests/data/recipes_with_info.json")) as fin:
        data = json.load(fin)
    infos = {}
    for recipe in data:
        extra_info = recipe.pop("extra_info")
        recipe["style"] = style.pk
        response = client.post("/api/recipes/", data=recipe, format="json")
        recipe_json = json.loads(response.content)
        infos[recipe_json["id"]] = extra_info
    return user, infos
