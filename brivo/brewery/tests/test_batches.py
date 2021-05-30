import pytest
import json

from model_bakery import baker

from brivo.brewery.models import Batch

pytestmark = pytest.mark.django_db


class TestBatchEndpoints:

    endpoint = "/api/brewery/batches/"

    def test_list_not_logged_in(self, api_client):
        response = api_client().get(self.endpoint)
        assert response.status_code == 403

    def test_list(self, api_client, user):
        baker.make(Batch, _quantity=3, user=user)
        client = api_client()
        client.force_authenticate(user)
        response = client.get(self.endpoint)
        assert response.status_code == 200
        assert len(json.loads(response.content)["results"]) == 3

    def test_create(self, api_client, recipes):
        user, infos = recipes
        recipe_id = list(infos.keys())[0]
        client = api_client()
        client.force_authenticate(user)
        data = {
            "grain_temperature": "20.0 c",
            "sparging_temperature": "78.0 c",
            "gravity_before_boil": "22.0 plato",
            "initial_gravity": "24.0 plato",
            "wort_volume": "20.0 l",
            "boil_loss": "0.0 l",
            "primary_fermentation_temperature": "20 c",
            "secondary_fermentation_temperature": "10 c",
            "post_primary_gravity": "8.0 plato",
            "end_gravity": "6.5 plato",
            "beer_volume": "20.0 l",
            "name": "Test",
            "stage": "FINISHED",
            "batch_number": 8,
            "brewing_day": "2016-04-22",
            "primary_fermentation_start_day": "2016-04-22",
            "secondary_fermentation_start_day": "2016-05-04",
            "dry_hops_start_day": None,
            "packaging_date": "2016-07-30",
            "carbonation_type": "REFERMENTATION",
            "carbonation_level": "1.80",
            "recipe": recipe_id,
        }
        response = client.post(f"{self.endpoint}", data=data, format="json")
        assert response.status_code == 201, json.loads(response.content)
        assert json.loads(response.content)["stage"] == "FINISHED"

    def test_create_in_mash(self, api_client, recipes):
        user, infos = recipes
        recipe_id = list(infos.keys())[0]
        client = api_client()
        client.force_authenticate(user)
        data = {
            "name": "Session IPA",
            "batch_number": 68,
            "brewing_day": "2020-05-06",
            "grain_temperature": "20.0 c",
            "sparging_temperature": "78.0 c",
            "recipe": recipe_id,
            "stage": "MASHING",
        }
        response = client.post(f"{self.endpoint}", data=data, format="json")
        assert response.status_code == 201, json.loads(response.content)
        assert json.loads(response.content)["stage"] == "MASHING"

    def test_create_in_boil(self, api_client, recipes):
        user, infos = recipes
        recipe_id = list(infos.keys())[0]
        client = api_client()
        client.force_authenticate(user)
        data = {
            "name": "Session IPA",
            "batch_number": 68,
            "brewing_day": "2020-05-06",
            "grain_temperature": "20.0 c",
            "sparging_temperature": "78.0 c",
            "recipe": recipe_id,
            "stage": "BOIL",
        }
        response = client.post(f"{self.endpoint}", data=data, format="json")
        assert response.status_code == 400, json.loads(response.content)
        data["gravity_before_boil"] = "12.0 plato"
        response = client.post(f"{self.endpoint}", data=data, format="json")
        assert response.status_code == 201, json.loads(response.content)
        assert json.loads(response.content)["stage"] == "BOIL"
        assert json.loads(response.content)["gravity_before_boil"] == "12.0 plato"

    def test_create_in_primary(self, api_client, recipes):
        user, infos = recipes
        recipe_id = list(infos.keys())[0]
        client = api_client()
        client.force_authenticate(user)
        data = {
            "name": "Session IPA",
            "batch_number": 68,
            "brewing_day": "2020-05-06",
            "grain_temperature": "20.0 c",
            "sparging_temperature": "78.0 c",
            "gravity_before_boil": "11 plato",
            "boil_loss": "3 l",
            "initial_gravity": "12 plato",
            "wort_volume": "20 l",
            "recipe": recipe_id,
            "stage": "PRIMARY_FERMENTATION",
        }
        response = client.post(f"{self.endpoint}", data=data, format="json")
        assert response.status_code == 400, json.loads(response.content)
        data["primary_fermentation_start_day"] = "2020-05-06"
        response = client.post(f"{self.endpoint}", data=data, format="json")
        assert response.status_code == 201, json.loads(response.content)
        assert json.loads(response.content)["stage"] == "PRIMARY_FERMENTATION"

    def test_create_in_secondary(self, api_client, recipes):
        user, infos = recipes
        recipe_id = list(infos.keys())[0]
        client = api_client()
        client.force_authenticate(user)
        data = {
            "name": "Session IPA",
            "batch_number": 68,
            "brewing_day": "2020-05-06",
            "grain_temperature": "20.0 c",
            "sparging_temperature": "78.0 c",
            "gravity_before_boil": "11 plato",
            "boil_loss": "3 l",
            "initial_gravity": "12 plato",
            "wort_volume": "20 l",
            "primary_fermentation_start_day": "2020-05-06",
            "recipe": recipe_id,
            "stage": "SECONDARY_FERMENTATION",
        }
        response = client.post(f"{self.endpoint}", data=data, format="json")
        assert response.status_code == 201, json.loads(response.content)
        assert json.loads(response.content)["stage"] == "SECONDARY_FERMENTATION"

    def test_create_in_packaging(self, api_client, recipes):
        user, infos = recipes
        recipe_id = list(infos.keys())[0]
        client = api_client()
        client.force_authenticate(user)
        data = {
            "name": "Session IPA",
            "batch_number": 68,
            "brewing_day": "2020-05-06",
            "grain_temperature": "20.0 c",
            "sparging_temperature": "78.0 c",
            "gravity_before_boil": "11 plato",
            "boil_loss": "3 l",
            "initial_gravity": "12 plato",
            "wort_volume": "20 l",
            "primary_fermentation_start_day": "2020-05-06",
            "packaging_date": "2016-07-30",
            "carbonation_type": "REFERMENTATION",
            "carbonation_level": "1.80",
            "beer_volume": "20.0 l",
            "recipe": recipe_id,
            "stage": "PACKAGING",
        }
        response = client.post(f"{self.endpoint}", data=data, format="json")
        assert response.status_code == 400, json.loads(response.content)
        data["end_gravity"] = "6.5 plato"
        response = client.post(f"{self.endpoint}", data=data, format="json")
        assert response.status_code == 201, json.loads(response.content)
        assert json.loads(response.content)["stage"] == "PACKAGING"

    def test_init(self, api_client, recipes):
        user, infos = recipes
        recipe_id = list(infos.keys())[0]
        client = api_client()
        client.force_authenticate(user)
        response = client.post(
            f"{self.endpoint}init/", data={"recipe": recipe_id}, format="json"
        )
        assert response.status_code == 201, json.loads(response.content)
        batch_id = json.loads(response.content)["id"]
        response = client.get(f"{self.endpoint}{batch_id}/")
        assert response.status_code == 200, json.loads(response.content)
        assert json.loads(response.content)["stage"] == "MASHING"

    def test_updates(self, api_client, recipes):
        user, infos = recipes
        recipe_id = list(infos.keys())[0]
        client = api_client()
        client.force_authenticate(user)
        response = client.post(
            f"{self.endpoint}init/", data={"recipe": recipe_id}, format="json"
        )
        batch_id = json.loads(response.content)["id"]
        # MASHING
        data = {
            "name": "Session IPA",
            "batch_number": 68,
            "brewing_day": "2020-05-06",
            "grain_temperature": "20.0 c",
            "sparging_temperature": "78.0 c",
        }

        response = client.put(
            f"{self.endpoint}{batch_id}/mash/", data=data, format="json"
        )

        assert response.status_code == 200, json.loads(response.content)
        assert json.loads(response.content)["stage"] == "MASHING"
        for k, v in data.items():
            content = json.loads(response.content)
            assert v == content[k]

        # BOIL
        data = {
            "gravity_before_boil": "10.0 plato",
        }

        response = client.put(
            f"{self.endpoint}{batch_id}/boil/", data=data, format="json"
        )
        assert response.status_code == 200, json.loads(response.content)
        assert json.loads(response.content)["stage"] == "BOIL", json.loads(
            response.content
        )
        for k, v in data.items():
            content = json.loads(response.content)
            assert v == content[k]

        # PRIMARY
        data = {
            "initial_gravity": "24.0 plato",
            "wort_volume": "20.0 l",
            "boil_loss": "0.0 l",
            "primary_fermentation_temperature": "15.0 c",
            "primary_fermentation_start_day": "2016-04-22",
        }

        response = client.put(
            f"{self.endpoint}{batch_id}/primary/", data=data, format="json"
        )
        assert response.status_code == 200, json.loads(response.content)
        assert (
            json.loads(response.content)["stage"] == "PRIMARY_FERMENTATION"
        ), json.loads(response.content)
        for k, v in data.items():
            content = json.loads(response.content)
            assert v == content[k]

        # SECONDARY
        data = {
            "secondary_fermentation_temperature": "10.0 c",
            "post_primary_gravity": "8.0 plato",
            "secondary_fermentation_start_day": "2016-05-04",
            "dry_hops_start_day": "2016-05-07",
        }

        response = client.put(
            f"{self.endpoint}{batch_id}/secondary/", data=data, format="json"
        )
        assert response.status_code == 200, json.loads(response.content)
        assert (
            json.loads(response.content)["stage"] == "SECONDARY_FERMENTATION"
        ), json.loads(response.content)
        for k, v in data.items():
            content = json.loads(response.content)
            assert v == content[k]

        # PACKAGING
        data = {
            "packaging_date": "2016-07-30",
            "carbonation_type": "REFERMENTATION",
            "carbonation_level": "1.80",
            "end_gravity": "6.5 plato",
            "beer_volume": "20.0 l",
        }

        response = client.put(
            f"{self.endpoint}{batch_id}/packaging/", data=data, format="json"
        )
        assert response.status_code == 200, json.loads(response.content)
        assert json.loads(response.content)["stage"] == "PACKAGING", json.loads(
            response.content
        )
        for k, v in data.items():
            content = json.loads(response.content)
            assert v == content[k]

        # FINISH

        response = client.post(f"{self.endpoint}{batch_id}/finish/")
        assert response.status_code == 200, json.loads(response.content)
        assert json.loads(response.content)["stage"] == "FINISHED", json.loads(
            response.content
        )
