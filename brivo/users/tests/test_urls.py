import pytest
from django.urls import resolve, reverse

from brivo.users.models import User

pytestmark = pytest.mark.django_db


def test_settings(user: User):
    assert (
        reverse("users:settings", kwargs={"username": user.username})
        == f"/users/{user.username}/"
    )
    assert resolve(f"/users/{user.username}/").view_name == "users:settings"


def test_redirect():
    assert reverse("users:redirect") == "/users/~redirect/"
    assert resolve("/users/~redirect/").view_name == "users:redirect"
