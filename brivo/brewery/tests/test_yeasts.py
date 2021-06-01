import pytest
import json

from model_bakery import baker

from brivo.brewery.models import Yeast


pytestmark = pytest.mark.django_db


@pytest.fixture
def yeast_json():
    return {
        "name": "German Ale",
        "lab": "Wyeast",
        "lab_id": "1007",
        "type": "ALE",
        "form": "LIQUID",
        "atten_min": "73",
        "atten_max": "77",
        "flocc": "Low",
        "temp_min": "13",
        "temp_max": "20",
        "alco_toler": "11",
        "styles": "American Wheat, Berliner Weisse, Bi?re de Garde, Düsseldorf Altbier, Kolsch, Northern German Altbier",
        "desc": "A true top cropping yeast with low ester formation and a broad temperature range. Fermentation at higher temperatures may produce mild fruitiness. This powdery strain results in yeast that remains in suspension post fermentation. Beers mature rapidly, even when cold fermentation is used. Low or no detectable diacetyl.",
        "external_link": "https://www.wyeastlab.com/rw_yeaststrain_detail.cfm?ID=150",
        "active": True
    }


@pytest.fixture
def yeast_instance(yeast_json):
    return Yeast.objects.create(**yeast_json)


@pytest.fixture
def yeast_with_measures(yeast_json):
    yeast_json["temp_min"] = yeast_json["temp_min"] + " c"
    yeast_json["temp_max"] = yeast_json["temp_max"] + " c"
    return yeast_json


class TestYeastsAPI:

    endpoint = "/api/brewery/yeasts/"

    def test_list_not_logged_in(self, api_client):
        baker.make(Yeast, _quantity=3)
        response = api_client().get(self.endpoint)
        assert response.status_code == 401

    def test_list_logged_in(self, api_client, user):
        baker.make(Yeast, _quantity=3)
        client = api_client()
        client.force_authenticate(user)
        response = client.get(self.endpoint)
        assert response.status_code == 200
        assert len(json.loads(response.content)["results"]) == 3

    def test_create_regular_user(self, api_client, user, yeast_json):
        client = api_client()
        client.force_authenticate(user)
        response = client.post(self.endpoint, yeast_json)
        assert response.status_code == 403, response.content

    def test_create_admin_user(self, api_client, admin_user, yeast_with_measures):
        client = api_client()
        client.force_authenticate(admin_user)
        response = client.post(self.endpoint, data=yeast_with_measures, format="json")
        assert response.status_code == 201, response.content
        response = client.get(self.endpoint)
        assert len(json.loads(response.content)["results"]) == 1
        assert (
            json.loads(response.content)["results"][0]["name"]
            == yeast_with_measures["name"]
        ), response.content

    def test_retrieve(self, api_client, user):
        obj = baker.make(Yeast)
        client = api_client()
        client.force_authenticate(user)
        response = client.get(f"{self.endpoint}{obj.id}/")
        assert response.status_code == 200, response.content

    def test_update(self, api_client, admin_user, yeast_instance, yeast_with_measures):
        obj = yeast_instance
        client = api_client()
        client.force_authenticate(admin_user)
        response = client.get(f"{self.endpoint}{obj.id}/")
        assert json.loads(response.content)["type"] == "ALE"
        yeast_with_measures["type"] = "LAGER"
        response = client.put(f"{self.endpoint}{obj.id}/", data=yeast_with_measures, format="json")
        assert response.status_code == 200
        assert json.loads(response.content)["type"] == "LAGER"

    def test_parallel_update(self, api_client, admin_user, yeast_json):
        obj = Yeast.objects.create(**yeast_json)
        client = api_client()
        client.force_authenticate(admin_user)
        response = client.get(f"{self.endpoint}{obj.id}/")
        assert json.loads(response.content)["type"] == "ALE"
        assert json.loads(response.content)["name"] == "German Ale"
        response = client.patch(
            f"{self.endpoint}{obj.id}/", data={"type": "LAGER"}, format="json"
        )
        assert response.status_code == 200, response.content
        assert json.loads(response.content)["type"] == "LAGER"
        assert json.loads(response.content)["name"] == "German Ale"

    def test_delete(self, api_client, admin_user, yeast_instance):
        client = api_client()
        client.force_authenticate(admin_user)
        assert Yeast.objects.all().count() == 1
        response = client.delete(f"{self.endpoint}{yeast_instance.id}/")
        assert response.status_code == 204, response.content
        assert Yeast.objects.all().count() == 0
