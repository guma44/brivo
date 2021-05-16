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
        response = client.post(
            f"{self.endpoint}init/", data={"recipe": recipe_id}, format="json"
        )
