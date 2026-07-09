import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        username="admin", email="admin@pms.local", password="admin12345", role=User.Role.ADMIN
    )


@pytest.fixture
def pm_user(db):
    return User.objects.create_user(
        username="pm", email="pm@pms.local", password="pm12345", role=User.Role.PROJECT_MANAGER
    )


@pytest.fixture
def member_user(db):
    return User.objects.create_user(
        username="member", email="member@pms.local", password="member12345", role=User.Role.MEMBER
    )


@pytest.fixture
def authed_client(api_client):
    """Return a callable that yields an APIClient authenticated as the given user."""

    def _make(user=None):
        if user is None:
            return api_client
        api_client.force_authenticate(user=user)
        return api_client

    return _make
