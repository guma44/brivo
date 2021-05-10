import pytest
import json

from model_bakery import baker

from brivo.brew.models import Hop, IngredientHop, Country, Recipe


pytestmark = pytest.mark.django_db


@pytest.fixture
def country():
    return baker.make(Country)


@pytest.fixture
def hop_json():
    return {
        "name": "Admiral",
        "alpha_acids": 14,
        "alpha_min": 13,
        "alpha_max": 16,
        "beta_min": 4,
        "beta_max": 6,
        "co_humulone_min": 37,
        "co_humulone_max": 45,
        "total_oil_min": 23,
        "total_oil_max": 26,
        "myrcene_min": 43,
        "myrcene_max": 47,
        "humulene_min": 23,
        "humulene_max": 26,
        "caryophyllene_min": 6,
        "caryophyllene_max": 8,
        "farnesene_min": 1,
        "farnesene_max": 3,
        "type": "BITTERING",
        "active": True,
    }


@pytest.fixture
def hop_instance(hop_json, country):
    return Hop.objects.create(country=country, **hop_json)


class TestHopsAPI:

    endpoint = "/api/hops/"

    def test_list_not_logged_in(self, api_client):
        baker.make(Hop, _quantity=3)
        response = api_client().get(self.endpoint)
        assert response.status_code == 403

    def test_list_logged_in(self, api_client, user):
        baker.make(Hop, _quantity=3)
        client = api_client()
        client.force_authenticate(user)
        response = client.get(self.endpoint)
        assert response.status_code == 200
        assert len(json.loads(response.content)["results"]) == 3

    def test_create_regular_user(self, api_client, user, hop_json, country):
        client = api_client()
        client.force_authenticate(user)
        response = client.post(self.endpoint, hop_json)
        assert response.status_code == 403, response.content

    def test_create_admin_user(self, api_client, admin_user, hop_json, country):
        hop_json["country"] = country.pk
        client = api_client()
        client.force_authenticate(admin_user)
        response = client.post(self.endpoint, data=hop_json, format="json")
        assert response.status_code == 201, response.content
        response = client.get(self.endpoint)
        assert len(json.loads(response.content)["results"]) == 1
        assert (
            json.loads(response.content)["results"][0]["country"]["name"]
            == country.name
        ), response.content

    def test_retrieve(self, api_client, user):
        obj = baker.make(Hop)
        client = api_client()
        client.force_authenticate(user)
        response = client.get(f"{self.endpoint}{obj.id}/")
        assert response.status_code == 200, response.content

    def test_update(self, api_client, admin_user, hop_json, country):
        obj = Hop.objects.create(country=country, **hop_json)
        client = api_client()
        client.force_authenticate(admin_user)
        response = client.get(f"{self.endpoint}{obj.id}/")
        assert json.loads(response.content)["type"] == "BITTERING"
        hop_json["type"] = "AROMA"
        hop_json["country"] = country.pk
        response = client.put(f"{self.endpoint}{obj.id}/", data=hop_json, format="json")
        assert response.status_code == 200
        assert json.loads(response.content)["type"] == "AROMA"

    def test_parallel_update(self, api_client, admin_user, hop_json, country):
        obj = Hop.objects.create(country=country, **hop_json)
        client = api_client()
        client.force_authenticate(admin_user)
        response = client.get(f"{self.endpoint}{obj.id}/")
        assert json.loads(response.content)["type"] == "BITTERING"
        assert json.loads(response.content)["name"] == "Admiral"
        response = client.patch(
            f"{self.endpoint}{obj.id}/", data={"type": "AROMA"}, format="json"
        )
        assert response.status_code == 200
        assert json.loads(response.content)["type"] == "AROMA"
        assert json.loads(response.content)["name"] == "Admiral"

    def test_delete(self, api_client, admin_user, hop_instance):
        client = api_client()
        client.force_authenticate(admin_user)
        assert Hop.objects.all().count() == 1
        response = client.delete(f"{self.endpoint}{hop_instance.id}/")
        assert response.status_code == 204, response.content
        assert Hop.objects.all().count() == 0
