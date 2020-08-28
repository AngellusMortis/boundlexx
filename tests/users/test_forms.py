import pytest

from boundlexx.users.forms import UserCreationForm
from tests.users.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestUserCreationForm:
    def test_clean_username(self):
        # A user with proto_user params does not exist yet.
        proto_user = UserFactory.build()

        form = UserCreationForm(
            {
                "username": proto_user.username,
                "password1": proto_user._password,  # pylint: disable=protected-access # noqa E501
                "password2": proto_user._password,  # pylint: disable=protected-access # noqa E501
            }
        )

        assert form.is_valid()
        assert form.clean_username() == proto_user.username

        # Creating a user.
        form.save()

        # The user with proto_user params already exists,
        # hence cannot be created.
        form = UserCreationForm(
            {
                "username": proto_user.username,
                "password1": proto_user._password,  # pylint: disable=protected-access # noqa E501
                "password2": proto_user._password,  # pylint: disable=protected-access # noqa E501
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert "username" in form.errors
