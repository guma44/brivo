import pytest
import json

from model_bakery import baker

from brivo.brewery.models import (
    Recipe,
    IngredientExtra,
    IngredientFermentable,
    IngredientHop,
    IngredientYeast,
)


pytestmark = pytest.mark.django_db


recipe_info = {
    "ibu": 36.1,
    "initial_volume": 31.05,
    "boil_volume": 34.155,
    "preboil_gravity": 10.063,
    "primary_volume": 28.35,
    "secondary_volume": 27.0,
    "color": 4.36,
    "abv": 4.3,
    "gravity": 11.035,
    "bitterness_ratio": 0.8,
}


@pytest.fixture
def fermentables():
    return [
        {
            "name": "Weyermann - Bohemian Pilsner Malt",
            "amount": "5.0 kg",
            "use": "MASHING",
            "type": "GRAIN",
            "color": "2.032 srm",
            "extraction": "81.00",
        },
        {
            "name": "Carahell",
            "amount": "0.5 kg",
            "use": "MASHING",
            "type": "GRAIN",
            "color": "13.208 srm",
            "extraction": "77.00",
        },
    ]


@pytest.fixture
def hops():
    return [
        {
            "name": "Marynka",
            "amount": "0.04 kg",
            "use": "BOIL",
            "alpha_acids": "10.50",
            "time": "60.00",
            "time_unit": "MINUTE",
        },
        {
            "name": "Marynka",
            "amount": "0.02 kg",
            "use": "BOIL",
            "alpha_acids": "10.50",
            "time": "0.00",
            "time_unit": "MINUTE",
        },
    ]


@pytest.fixture
def yeasts():
    return [
        {
            "name": "Wyeast - Bohemian Lager",
            "amount": "0.3 kg",
            "type": "LAGER",
            "lab": "Wyeast Labs",
            "attenuation": "75.00",
            "form": "LIQUID",
        }
    ]


@pytest.fixture
def extras():
    return [
        {
            "name": "Kwas mlekowy",
            "amount": "0.005 kg",
            "type": "WATER AGENT",
            "use": "BOIL",
            "time": "100.00",
            "time_unit": "MINUTE",
        },
        {
            "name": "Chlorek Sodu",
            "amount": "0.002 kg",
            "type": "WATER AGENT",
            "use": "BOIL",
            "time": "100.00",
            "time_unit": "MINUTE",
        },
    ]


@pytest.fixture
def mash_steps():
    return [
        {"temperature": "55.0 c", "time": "10.00", "note": None},
        {"temperature": "63.0 c", "time": "30.00", "note": None},
        {"temperature": "72.0 c", "time": "30.00", "note": None},
        {"temperature": "78.0 c", "time": "10.00", "note": None},
    ]


@pytest.fixture
def base_recipe_json(style):
    return {
        "name": "Test Pils",
        "style": style.id,
        "type": "ALL GRAIN",
        "expected_beer_volume": "27.0 l",
        "boil_time": 60,
        "evaporation_rate": "10.00",
        "boil_loss": "10.00",
        "trub_loss": "5.00",
        "dry_hopping_loss": "0.00",
        "mash_efficiency": "80.00",
        "liquor_to_grist_ratio": "4.20",
        "note": "",
        "is_public": True,
        "fermentables": [],
        "hops": [],
        "extras": [],
        "yeasts": [],
        "mash_steps": [],
    }


@pytest.fixture
def recipe_with_ingredients_json(
    base_recipe_json, fermentables, hops, yeasts, extras, mash_steps
):
    base_recipe_json.update(
        {
            "fermentables": fermentables,
            "hops": hops,
            "extras": extras,
            "yeasts": yeasts,
            "mash_steps": mash_steps,
        }
    )
    return base_recipe_json


class TestRecipeEndpoints:

    endpoint = "/api/brewery/recipes/"

    def test_list_not_logged_in(self, api_client):
        response = api_client().get(self.endpoint)
        assert response.status_code == 401

    def test_list(self, api_client, user):
        baker.make(Recipe, _quantity=3, user=user)
        client = api_client()
        client.force_authenticate(user)
        response = client.get(self.endpoint)
        assert response.status_code == 200
        assert len(json.loads(response.content)["results"]) == 3

    def test_list_many_users(self, api_client, user, other_user):
        user1_objects = baker.make(Recipe, _quantity=3, user=user)
        user2_objects = baker.make(Recipe, _quantity=2, user=other_user)
        client = api_client()
        client.force_authenticate(user)
        response = client.get(self.endpoint)
        assert response.status_code == 200
        user1_ids = [str(r["id"]) for r in json.loads(response.content)["results"]]
        assert len(user1_ids) == 3
        for u1o in user1_objects:
            assert str(u1o.pk) in user1_ids
        for u2o in user2_objects:
            assert str(u2o.id) not in user1_ids
        client2 = api_client()
        client2.force_authenticate(other_user)
        response = client2.get(self.endpoint)
        assert response.status_code == 200
        user2_ids = [str(r["id"]) for r in json.loads(response.content)["results"]]
        assert len(user2_ids) == 2
        for u1o in user1_objects:
            assert str(u1o.pk) not in user2_ids
        for u2o in user2_objects:
            assert str(u2o.id) in user2_ids

    def test_create(self, api_client, user, base_recipe_json):
        client = api_client()
        client.force_authenticate(user)
        response = client.post(self.endpoint, data=base_recipe_json, format="json")
        assert response.status_code == 201, response.content
        response = client.get(self.endpoint)
        assert len(json.loads(response.content)["results"]) == 1
        assert (
            json.loads(response.content)["results"][0]["style"]["name"]
            == "Czech Pale Lager"
        ), response.content

    def test_create_with_ingredients(
        self, api_client, user, recipe_with_ingredients_json
    ):
        client = api_client()
        client.force_authenticate(user)
        response = client.post(
            self.endpoint, data=recipe_with_ingredients_json, format="json"
        )
        assert response.status_code == 201, response.content
        response = client.get(self.endpoint)
        assert len(json.loads(response.content)["results"]) == 1
        recipe = json.loads(response.content)["results"][0]
        assert len(recipe["fermentables"]) == 2
        assert len(recipe["hops"]) == 2
        assert len(recipe["yeasts"]) == 1
        assert len(recipe["extras"]) == 2
        assert len(recipe["mash_steps"]) == 4
        measure_fields = [
            "color",
            "gravity",
            "initial_volume",
            "boil_volume",
            "preboil_gravity",
            "primary_volume",
            "secondary_volume",
        ]
        for field in measure_fields:
            assert (
                pytest.approx(float(recipe[field].split()[0]), rel=1e-4, abs=1e-2)
                == recipe_info[field]
            )
        for field in ["ibu", "abv", "bitterness_ratio"]:
            assert (
                pytest.approx(float(recipe[field]), rel=1e-4, abs=1e-2)
                == recipe_info[field]
            )

    def test_create_calculations(self, api_client, recipes):
        user, infos = recipes
        client = api_client()
        client.force_authenticate(user)
        measure_fields = [
            "color",
            "gravity",
            "boil_volume",
            "preboil_gravity",
            "primary_volume",
        ]
        for rid, info in infos.items():
            response = client.get(f"{self.endpoint}{rid}/")
            recipe = json.loads(response.content)
            for field in measure_fields:
                assert (
                    pytest.approx(float(recipe[field].split()[0]), rel=1e-4, abs=1e-1)
                    == info[field]
                ), f"{field} shold be {float(recipe[field].split()[0])} but is {info[field]} in recipe {recipe['name']}"

    def test_retrieve(self, api_client, user):
        obj = baker.make(Recipe, user=user)
        client = api_client()
        client.force_authenticate(user)
        response = client.get(f"{self.endpoint}{obj.id}/")
        assert response.status_code == 200, response.content

    def test_update(
        self,
        api_client,
        user,
        base_recipe_json,
        fermentables,
        hops,
        yeasts,
        extras,
        mash_steps,
    ):
        client = api_client()
        client.force_authenticate(user)
        response = client.post(self.endpoint, data=base_recipe_json, format="json")
        assert response.status_code == 201, response.content
        recipe_id = json.loads(response.content)["id"]
        response = client.get(f"{self.endpoint}{recipe_id}/")
        recipe = json.loads(response.content)
        assert len(recipe["fermentables"]) == 0
        assert len(recipe["hops"]) == 0
        assert len(recipe["yeasts"]) == 0
        assert len(recipe["extras"]) == 0
        assert len(recipe["mash_steps"]) == 0
        recipe["fermentables"] = fermentables
        recipe["hops"] = hops
        recipe["yeasts"] = yeasts
        recipe["extras"] = extras
        recipe["mash_steps"] = mash_steps
        recipe["style"] = recipe["style"]["id"]
        response = client.put(
            f"{self.endpoint}{recipe_id}/", data=recipe, format="json"
        )
        assert response.status_code == 200, response.content
        assert len(recipe["fermentables"]) == 2
        assert len(recipe["hops"]) == 2
        assert len(recipe["yeasts"]) == 1
        assert len(recipe["extras"]) == 2
        assert len(recipe["mash_steps"]) == 4

    def test_update_ingredients(self, api_client, user, recipe_with_ingredients_json):
        client = api_client()
        client.force_authenticate(user)
        response = client.post(
            self.endpoint, data=recipe_with_ingredients_json, format="json"
        )
        assert response.status_code == 201, response.content
        recipe_id = json.loads(response.content)["id"]
        response = client.get(f"{self.endpoint}{recipe_id}/")
        recipe = json.loads(response.content)
        recipe["style"] = recipe["style"]["id"]
        assert len(recipe["hops"]) == 2
        assert len(recipe["extras"]) == 2
        assert len(recipe["mash_steps"]) == 4
        print(recipe)
        # change something in fermentables
        recipe["fermentables"][0]["name"] = "Test Name"
        # remove one hop
        recipe["hops"] = [recipe["hops"][0]]
        # change yeasts totally i.e remove ID and change the name
        old_yeast_id = recipe["yeasts"][0]["id"]
        del recipe["yeasts"][0]["id"]
        recipe["yeasts"][0]["name"] = "New Yeasts"
        # remove extras
        recipe["extras"] = []
        # add additional mash_step
        recipe["mash_steps"].append(
            {"temperature": "80.0 c", "time": "5.00", "note": None},
        )
        response = client.put(
            f"{self.endpoint}{recipe_id}/", data=recipe, format="json"
        )
        assert response.status_code == 200, response.content
        mod_recipe = json.loads(response.content)
        assert mod_recipe["id"] == recipe["id"]
        assert mod_recipe["fermentables"][0]["name"] == "Test Name"
        assert mod_recipe["fermentables"][0]["id"] == recipe["fermentables"][0]["id"]
        assert mod_recipe["hops"][0]["id"] == recipe["hops"][0]["id"]
        assert len(mod_recipe["hops"]) == 1
        assert mod_recipe["yeasts"][0]["id"] != old_yeast_id
        assert mod_recipe["yeasts"][0]["name"] == "New Yeasts"
        assert len(mod_recipe["extras"]) == 0
        assert len(mod_recipe["mash_steps"]) == 5
        assert mod_recipe["mash_steps"][-1]["temperature"] == "80.0 c"

    # def test_parallel_update(self, api_client, user):
        # pass

    def test_delete(self, api_client, user):
        obj = baker.make(Recipe, user=user)
        client = api_client()
        client.force_authenticate(user)
        assert Recipe.objects.all().count() == 1
        response = client.delete(f"{self.endpoint}{obj.id}/")
        assert response.status_code == 204, response.content
        assert Recipe.objects.all().count() == 0