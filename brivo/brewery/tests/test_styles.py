import pytest
import json

from model_bakery import baker

from brivo.brewery.models import Style


pytestmark = pytest.mark.django_db


@pytest.fixture
def style_json():
    return {
        "category_id": "1A",
        "category": "Standard American Beer",
        "name": "American Light Lager",
        "og_min": "1.028",
        "og_max": "1.040",
        "fg_min": "0.998",
        "fg_max": "1.008",
        "ibu_min": "8",
        "ibu_max": "12",
        "color_min": "2",
        "color_max": "3",
        "alcohol_min": "2.8",
        "alcohol_max": "4.2",
        "ferm_type": "Lager",
        "desc_aroma": "Low to no malt aroma, although it can be percei",
        "desc_mouth": "Very light (sometimes watery) body.",
        "desc_overall": "Highly carbonated, very light-bodied",
        "desc_comment": "Designed to appeal to as",
        "desc_ingre": "Two- or six-row barley with.",
        "desc_history": "Coors briefly made  to diet-conscious d",
        "desc_style_comp": "A lighter-bodied",
        "commercial_exam": "Bud Light, Coors ",
        "active": True
    }


@pytest.fixture
def style_instance(style_json):
    return Style.objects.create(**style_json)

@pytest.fixture
def style_with_measures(style_json):
    style_json["og_min"] = style_json["og_min"] + " sg"
    style_json["og_max"] = style_json["og_max"] + " sg"
    style_json["fg_min"] = style_json["fg_min"] + " sg"
    style_json["fg_max"] = style_json["fg_max"] + " sg"
    style_json["color_min"] = style_json["color_min"] + " srm"
    style_json["color_max"] = style_json["color_max"] + " srm"
    return style_json


class TestStylesAPI:

    endpoint = "/api/brewery/styles/"

    def test_list_not_logged_in(self, api_client):
        baker.make(Style, _quantity=3)
        response = api_client().get(self.endpoint)
        assert response.status_code == 401

    def test_list_logged_in(self, api_client, user):
        baker.make(Style, _quantity=3)
        client = api_client()
        client.force_authenticate(user)
        response = client.get(self.endpoint)
        assert response.status_code == 200
        assert len(json.loads(response.content)["results"]) == 3

    def test_create_regular_user(self, api_client, user, style_json):
        client = api_client()
        client.force_authenticate(user)
        response = client.post(self.endpoint, style_json)
        assert response.status_code == 403, response.content

    def test_create_admin_user(self, api_client, admin_user, style_with_measures):
        client = api_client()
        client.force_authenticate(admin_user)
        response = client.post(self.endpoint, data=style_with_measures, format="json")
        assert response.status_code == 201, response.content
        response = client.get(self.endpoint)
        assert len(json.loads(response.content)["results"]) == 1
        assert (
            json.loads(response.content)["results"][0]["name"]
            == style_with_measures["name"]
        ), response.content

    def test_retrieve(self, api_client, user):
        obj = baker.make(Style)
        client = api_client()
        client.force_authenticate(user)
        response = client.get(f"{self.endpoint}{obj.id}/")
        assert response.status_code == 200, response.content

    def test_update(self, api_client, admin_user, style_instance, style_with_measures):
        obj = style_instance
        client = api_client()
        client.force_authenticate(admin_user)
        response = client.get(f"{self.endpoint}{obj.id}/")
        assert json.loads(response.content)["ferm_type"] == "Lager"
        style_with_measures["ferm_type"] = "Ale"
        response = client.put(f"{self.endpoint}{obj.id}/", data=style_with_measures, format="json")
        assert response.status_code == 200
        assert json.loads(response.content)["ferm_type"] == "Ale"

    def test_parallel_update(self, api_client, admin_user, style_json):
        obj = Style.objects.create(**style_json)
        client = api_client()
        client.force_authenticate(admin_user)
        response = client.get(f"{self.endpoint}{obj.id}/")
        assert json.loads(response.content)["ferm_type"] == "Lager"
        assert json.loads(response.content)["name"] == "American Light Lager"
        response = client.patch(
            f"{self.endpoint}{obj.id}/", data={"ferm_type": "Ale"}, format="json"
        )
        assert response.status_code == 200, response.content
        assert json.loads(response.content)["ferm_type"] == "Ale"
        assert json.loads(response.content)["name"] == "American Light Lager"

    def test_delete(self, api_client, admin_user, style_instance):
        client = api_client()
        client.force_authenticate(admin_user)
        assert Style.objects.all().count() == 1
        response = client.delete(f"{self.endpoint}{style_instance.id}/")
        assert response.status_code == 204, response.content
        assert Style.objects.all().count() == 0
