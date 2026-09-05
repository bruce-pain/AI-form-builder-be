import pytest
from fastapi import status

from app.core.config import settings
from app.features.auth.models import User
from app.features.auth.utils.google import GoogleClaims


@pytest.fixture
def test_user_data():
    return {"email": "test@example.com", "password": "testpassword123"}


@pytest.fixture
def registered_user(client, test_user_data):
    response = client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


class TestRegister:
    def test_register_success(self, client, test_user_data):
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["message"] == "User registered successfully"
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["data"]["email"] == test_user_data["email"]

    def test_register_duplicate_email(self, client, test_user_data):
        client.post("/api/v1/auth/register", json=test_user_data)
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["message"]

    def test_register_invalid_email(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "invalid-email", "password": "password123"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_missing_fields(self, client):
        response = client.post(
            "/api/v1/auth/register", json={"email": "test@example.com"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogin:
    def test_login_success(self, client, test_user_data):
        client.post("/api/v1/auth/register", json=test_user_data)
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "User logged in successfully"
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_invalid_email(self, client):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "password123"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid email" in response.json()["message"]

    def test_login_invalid_password(self, client, test_user_data):
        client.post("/api/v1/auth/register", json=test_user_data)
        response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": "wrongpassword"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid password" in response.json()["message"]

    def test_login_rejects_user_without_password(self, client, db_session):
        """A user with no password set (e.g. created via a social login) must not
        be able to authenticate through the email/password endpoint."""
        db_session.add(User(email="social@example.com", password=None))
        db_session.commit()

        response = client.post(
            "/api/v1/auth/login",
            json={"email": "social@example.com", "password": "anything"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid password" in response.json()["message"]
        assert "access_token" not in response.json()


class TestTokenRefresh:
    def test_refresh_token_success(self, client, registered_user):
        response = client.post(
            "/api/v1/auth/token/refresh",
            json={"refresh_token": registered_user["refresh_token"]},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()

    def test_refresh_token_invalid(self, client):
        response = client.post(
            "/api/v1/auth/token/refresh", json={"refresh_token": "invalid-token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetUser:
    def test_get_user_success(self, client, registered_user):
        access_token = registered_user["access_token"]
        response = client.get(
            "/api/v1/auth/user", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["email"] == "test@example.com"

    def test_get_user_unauthorized(self, client):
        response = client.get("/api/v1/auth/user")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_user_invalid_token(self, client):
        response = client.get(
            "/api/v1/auth/user", headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGoogleAuth:
    @staticmethod
    def _stub_google(monkeypatch, claims: GoogleClaims):
        """Replace ID-token verification with a stubbed response.

        The route's real error handling (403/503 paths) belongs to
        `verify_google_id_token` itself, which is tested in the util. Here the
        token is assumed already verified so the endpoint, service and database
        behaviour are exercised deterministically.
        """
        monkeypatch.setattr(
            "app.features.auth.routes.verify_google_id_token",
            lambda _token: claims,
        )

    def test_signup_creates_user(self, client, monkeypatch, db_session):
        self._stub_google(monkeypatch, GoogleClaims(sub="SUB-1", email="a@example.com"))

        response = client.post("/api/v1/auth/google", json={"id_token": "token"})
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["message"] == "User authenticated successfully"
        assert data["status_code"] == 200
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["data"]["email"] == "a@example.com"

        user = db_session.get(User, data["data"]["id"])
        assert user is not None
        assert user.google_sub == "SUB-1"
        assert user.password is None

    def test_repeat_login_returns_same_user(self, client, monkeypatch, db_session):
        self._stub_google(monkeypatch, GoogleClaims(sub="SUB-1", email="a@example.com"))

        first = client.post("/api/v1/auth/google", json={"id_token": "token"}).json()
        second = client.post("/api/v1/auth/google", json={"id_token": "token"}).json()

        assert second["data"]["id"] == first["data"]["id"]
        assert db_session.query(User).count() == 1

    def test_links_existing_password_user(self, client, monkeypatch, db_session):
        client.post(
            "/api/v1/auth/register",
            json={"email": "linked@example.com", "password": "password123"},
        )

        self._stub_google(
            monkeypatch, GoogleClaims(sub="SUB-2", email="linked@example.com")
        )
        response = client.post("/api/v1/auth/google", json={"id_token": "token"})
        assert response.status_code == status.HTTP_200_OK
        assert db_session.query(User).count() == 1

        user = db_session.query(User).filter(User.email == "linked@example.com").one()
        assert user.google_sub == "SUB-2"
        assert user.password is not None

        login = client.post(
            "/api/v1/auth/login",
            json={"email": "linked@example.com", "password": "password123"},
        )
        assert login.status_code == status.HTTP_200_OK

    def test_relinks_email_to_new_sub(self, client, monkeypatch, db_session):
        self._stub_google(
            monkeypatch, GoogleClaims(sub="SUB-OLD", email="r@example.com")
        )
        client.post("/api/v1/auth/google", json={"id_token": "token"})

        self._stub_google(
            monkeypatch, GoogleClaims(sub="SUB-NEW", email="r@example.com")
        )
        client.post("/api/v1/auth/google", json={"id_token": "token"})

        user = db_session.query(User).filter(User.email == "r@example.com").one()
        assert user.google_sub == "SUB-NEW"
        assert db_session.query(User).count() == 1

    def test_new_sub_with_new_email_creates_new_user(
        self, client, monkeypatch, db_session
    ):
        self._stub_google(monkeypatch, GoogleClaims(sub="SUB-A", email="a@example.com"))
        client.post("/api/v1/auth/google", json={"id_token": "token"})

        self._stub_google(monkeypatch, GoogleClaims(sub="SUB-B", email="b@example.com"))
        client.post("/api/v1/auth/google", json={"id_token": "token"})

        assert db_session.query(User).count() == 2

    def test_email_is_lowercased(self, client, monkeypatch, db_session):
        self._stub_google(
            monkeypatch, GoogleClaims(sub="SUB-3", email="MiXeD@Example.COM")
        )

        client.post("/api/v1/auth/google", json={"id_token": "token"})

        users = db_session.query(User).all()
        assert len(users) == 1
        assert users[0].email == "mixed@example.com"

    def test_empty_id_token_is_rejected(self, client):
        response = client.post("/api/v1/auth/google", json={"id_token": ""})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_id_token_is_rejected(self, client):
        response = client.post("/api/v1/auth/google", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_unconfigured_client_id_returns_503(self, client, monkeypatch):
        monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "")

        response = client.post("/api/v1/auth/google", json={"id_token": "token"})

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "not configured" in response.json()["message"]

    def test_real_verifier_is_called_when_configured(self, client, monkeypatch):
        """Without a stub, the endpoint must attempt a real verification rather
        than short-circuiting, once a client id is configured."""
        monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "test-client-id")

        response = client.post("/api/v1/auth/google", json={"id_token": "garbage"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid Google token" in response.json()["message"]
