import pytest
import json

from model_bakery import baker

from brivo.brewery.models import Extra, Country


pytestmark = pytest.mark.django_db


@pytest.fixture
def extra_json():
    return {
        "name": "Allspice",
        "type": "SPICE",
        "use": "BOIL"
    }


@pytest.fixture
def extra_instance(extra_json):
    return Extra.objects.create(**extra_json)


class TestExtrasAPI:

    endpoint = "/api/extras/"

    def test_list_not_logged_in(self, api_client):
        baker.make(Extra, _quantity=3)
        response = api_client().get(self.endpoint)
        assert response.status_code == 403

    def test_list_logged_in(self, api_client, user):
        baker.make(Extra, _quantity=3)
        client = api_client()
        client.force_authenticate(user)
        response = client.get(self.endpoint)
        assert response.status_code == 200
        assert len(json.loads(response.content)["results"]) == 3

    def test_create_regular_user(self, api_client, user, extra_json):
        client = api_client()
        client.force_authenticate(user)
        response = client.post(self.endpoint, extra_json)
        assert response.status_code == 403, response.content

    def test_create_admin_user(self, api_client, admin_user, extra_json):
        client = api_client()
        client.force_authenticate(admin_user)
        response = client.post(self.endpoint, data=extra_json, format="json")
        assert response.status_code == 201, response.content
        response = client.get(self.endpoint)
        assert len(json.loads(response.content)["results"]) == 1
        assert (
            json.loads(response.content)["results"][0]["name"]
            == extra_json["name"]
        ), response.content

    def test_retrieve(self, api_client, user):
        obj = baker.make(Extra)
        client = api_client()
        client.force_authenticate(user)
        response = client.get(f"{self.endpoint}{obj.id}/")
        assert response.status_code == 200, response.content

    def test_update(self, api_client, admin_user, extra_json):
        obj = Extra.objects.create(**extra_json)
        client = api_client()
        client.force_authenticate(admin_user)
        response = client.get(f"{self.endpoint}{obj.id}/")
        assert json.loads(response.content)["type"] == "SPICE"
        extra_json["type"] = "FLAVOR"
        response = client.put(f"{self.endpoint}{obj.id}/", data=extra_json, format="json")
        assert response.status_code == 200
        assert json.loads(response.content)["type"] == "FLAVOR"

    def test_parallel_update(self, api_client, admin_user, extra_json):
        obj = Extra.objects.create(**extra_json)
        client = api_client()
        client.force_authenticate(admin_user)
        response = client.get(f"{self.endpoint}{obj.id}/")
        assert json.loads(response.content)["type"] == "SPICE"
        assert json.loads(response.content)["name"] == "Allspice"
        response = client.patch(
            f"{self.endpoint}{obj.id}/", data={"type": "FLAVOR"}, format="json"
        )
        assert response.status_code == 200, response.content
        assert json.loads(response.content)["type"] == "FLAVOR"
        assert json.loads(response.content)["name"] == "Allspice"

    def test_delete(self, api_client, admin_user, extra_instance):
        client = api_client()
        client.force_authenticate(admin_user)
        assert Extra.objects.all().count() == 1
        response = client.delete(f"{self.endpoint}{extra_instance.id}/")
        assert response.status_code == 204, response.content
        assert Extra.objects.all().count() == 0
