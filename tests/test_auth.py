import uuid

from fastapi.testclient import TestClient

from backend.main import app
from backend.services.db_service import db_service

client = TestClient(app)


def test_auth_signup_and_login(monkeypatch):
    # In-memory stand-in for the MongoDB users collection.
    mock_db = {}

    def mock_get_user_by_email(email):
        return mock_db.get(email.lower().strip())

    def mock_create_user(email, hashed_password, name=None):
        user_doc = {
            "_id": uuid.uuid4().hex,
            "email": email.lower().strip(),
            "password": hashed_password,
            "name": name or "",
        }
        mock_db[email.lower().strip()] = user_doc
        return user_doc

    # Bypass the real MongoDB connection.
    monkeypatch.setattr(db_service, "get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr(db_service, "create_user", mock_create_user)

    # 1. Signup succeeds and echoes back the created user.
    response = client.post(
        "/api/auth/signup",
        json={"email": "newuser@example.com", "password": "securepassword123"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "newuser@example.com"
    assert response.json()["id"]

    # 2. Duplicate signup is rejected.
    response = client.post(
        "/api/auth/signup",
        json={"email": "newuser@example.com", "password": "differentpassword"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email is already registered"

    # 3. Login succeeds with the correct password.
    response = client.post(
        "/api/auth/login",
        json={"email": "newuser@example.com", "password": "securepassword123"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "newuser@example.com"

    # 4. Login fails with the wrong password.
    response = client.post(
        "/api/auth/login",
        json={"email": "newuser@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

    # 5. Login fails for an unknown user.
    response = client.post(
        "/api/auth/login",
        json={"email": "nonexistent@example.com", "password": "somepassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"
