import pytest
from django.urls import reverse

from brivo.users.models import User

pytestmark = pytest.mark.django_db


class TestUserAdmin:
    def test_changelist(self, admin_client):
        url = reverse("admin:users_user_changelist")
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_search(self, admin_client):
        url = reverse("admin:users_user_changelist")
        response = admin_client.get(url, data={"q": "test"})
        assert response.status_code == 200

    # Profile etc. cannot be add
    # def test_add(self, admin_client):
    #     url = reverse("admin:users_user_add")
    #     response = admin_client.get(url)
    #     assert response.status_code == 200

    #     response = admin_client.post(
    #         url,
    #         data={
    #             "email": "example@test.com",
    #             "username": "test",
    #             "password": "My_R@ndom-P@ssw0rd",
    #         },
    #     )
    #     assert response.status_code == 200
    #     assert User.objects.filter(username="test").exists()

    # def test_view_user(self, admin_client):
    #     user = User.objects.get(username="admin")
    #     url = reverse("admin:users_user_change", kwargs={"object_id": user.pk})
    #     response = admin_client.get(url)
    #     assert response.status_code == 200
