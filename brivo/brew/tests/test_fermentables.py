import pytest
import json

from model_bakery import baker


from brivo.brew.models import Fermentable, Country


pytestmark = pytest.mark.django_db


@pytest.fixture
def country():
    return baker.make(Country)


@pytest.fixture
def fermentable_json():
    return     {
        "active": 1,
        "color": 1,
        "description": "",
        "extraction": 71.25,
        "max_use": 100,
        "name": "American Six-row Pale",
        "type": "GRAIN"
    }


@pytest.fixture
def fermentable_instance(fermentable_json, country):
    return Fermentable.objects.create(country=country, **fermentable_json)


class TestFermentablesAPI:

    endpoint = "/api/fermentables/"

    def test_list_not_logged_in(self, api_client):
        baker.make(Fermentable, _quantity=3)
        response = api_client().get(self.endpoint)
        assert response.status_code == 403

    def test_list_logged_in(self, api_client, user):
        baker.make(Fermentable, _quantity=3)
        client = api_client()
        client.force_authenticate(user)
        response = client.get(self.endpoint)
        assert response.status_code == 200
        assert len(json.loads(response.content)["results"]) == 3

    def test_create_regular_user(self, api_client, user, fermentable_json, country):
        client = api_client()
        client.force_authenticate(user)
        response = client.post(self.endpoint, fermentable_json)
        assert response.status_code == 403, response.content

    def test_create_admin_user(self, api_client, admin_user, fermentable_json, country):
        fermentable_json["country"] = country.pk
        fermentable_json["color"] = "1 srm"
        client = api_client()
        client.force_authenticate(admin_user)
        response = client.post(self.endpoint, data=fermentable_json, format="json")
        assert response.status_code == 201, response.content
        response = client.get(self.endpoint)
        assert len(json.loads(response.content)["results"]) == 1
        assert (
            json.loads(response.content)["results"][0]["country"]["name"]
            == country.name
        ), response.content

    def test_retrieve(self, api_client, user):
        obj = baker.make(Fermentable)
        client = api_client()
        client.force_authenticate(user)
        response = client.get(f"{self.endpoint}{obj.id}/")
        assert response.status_code == 200, response.content

    def test_update(self, api_client, admin_user, fermentable_json, country):
        obj = Fermentable.objects.create(country=country, **fermentable_json)
        client = api_client()
        client.force_authenticate(admin_user)
        response = client.get(f"{self.endpoint}{obj.id}/")
        assert json.loads(response.content)["type"] == "GRAIN"
        fermentable_json["type"] = "ADJUNCT"
        fermentable_json["country"] = country.pk
        fermentable_json["color"] = "1 srm"
        response = client.put(f"{self.endpoint}{obj.id}/", data=fermentable_json, format="json")
        assert response.status_code == 200
        assert json.loads(response.content)["type"] == "ADJUNCT"

    def test_parallel_update(self, api_client, admin_user, fermentable_json, country):
        obj = Fermentable.objects.create(country=country, **fermentable_json)
        client = api_client()
        client.force_authenticate(admin_user)
        response = client.get(f"{self.endpoint}{obj.id}/")
        assert json.loads(response.content)["type"] == "GRAIN"
        assert json.loads(response.content)["name"] == "American Six-row Pale"
        response = client.patch(
            f"{self.endpoint}{obj.id}/", data={"type": "ADJUNCT"}, format="json"
        )
        assert response.status_code == 200
        assert json.loads(response.content)["type"] == "ADJUNCT"
        assert json.loads(response.content)["name"] == "American Six-row Pale"

    def test_delete(self, api_client, admin_user, fermentable_instance):
        client = api_client()
        client.force_authenticate(admin_user)
        assert Fermentable.objects.all().count() == 1
        response = client.delete(f"{self.endpoint}{fermentable_instance.id}/")
        assert response.status_code == 204, response.content
        assert Fermentable.objects.all().count() == 0
