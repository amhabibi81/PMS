import pytest

from apps.accounts.models import User


@pytest.mark.django_db
def test_register_creates_member(api_client):
    resp = api_client.post("/api/v1/auth/register/", {
        "username": "newuser",
        "email": "new@pms.local",
        "password": "securepass123",
    }, format="json")
    assert resp.status_code == 201
    assert resp.data["username"] == "newuser"
    assert resp.data["role"] == User.Role.MEMBER
    assert "password" not in resp.data


@pytest.mark.django_db
def test_register_rejects_duplicate_username(api_client, member_user):
    resp = api_client.post("/api/v1/auth/register/", {
        "username": "member",
        "email": "other@pms.local",
        "password": "securepass123",
    }, format="json")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_login_returns_jwt(api_client, member_user):
    resp = api_client.post("/api/v1/auth/login/", {
        "username": "member",
        "password": "member12345",
    }, format="json")
    assert resp.status_code == 200
    assert "access" in resp.data
    assert "refresh" in resp.data


@pytest.mark.django_db
def test_login_wrong_password(api_client, member_user):
    resp = api_client.post("/api/v1/auth/login/", {
        "username": "member",
        "password": "wrong",
    }, format="json")
    assert resp.status_code == 401


@pytest.mark.django_db
def test_me_requires_auth(api_client):
    resp = api_client.get("/api/v1/auth/me/")
    assert resp.status_code == 401


@pytest.mark.django_db
def test_me_returns_current_user(authed_client, member_user):
    client = authed_client(member_user)
    resp = client.get("/api/v1/auth/me/")
    assert resp.status_code == 200
    assert resp.data["username"] == "member"
