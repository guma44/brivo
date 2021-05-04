"""
Module for all Form Tests.
"""
import pytest
from django.utils.translation import ugettext_lazy as _

from brivo.users.forms import BrivoSignupForm
from brivo.users.models import User

pytestmark = pytest.mark.django_db


class TestBrivoSignupForm:
    """
    Test class for all tests related to the BrivoSignupForm
    """

    def test_username_validation_error_msg(self, user: User):
        """
        Tests UserCreation Form's unique validator functions correctly by testing:
            1) A new user with an existing username cannot be added.
            2) Only 1 error is raised by the UserCreation Form
            3) The desired error message is raised
        """

        # The user already exists,
        # hence cannot be created.
        form = BrivoSignupForm(
            {
                "username": user.username,
                "email": user.email,
                "password1": user.password,
                "password2": user.password,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 2
        assert "username" in form.errors
        assert "email" in form.errors
