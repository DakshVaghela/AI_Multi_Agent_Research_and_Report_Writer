from unittest.mock import MagicMock
from fastapi.testclient import TestClient
import pytest
from backend.main import app
from backend.services.db_service import db_service
from backend.utils.auth import hash_password

client = TestClient(app)

def test_auth_signup_and_login(monkeypatch):
    # Mock database storage
    mock_db = {}

    def mock_get_user_by_email(email):
        return mock_db.get(email.lower().strip())

    def mock_create_user(email, hashed_password):
        user_doc = {
            "email": email.lower().strip(),
            "password": hashed_password,
        }
        mock_db[email.lower().strip()] = user_doc
        return user_doc

    # Apply monkeypatching to the db_service methods to bypass actual MongoDB connection
    monkeypatch.setattr(db_service, "get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr(db_service, "create_user", mock_create_user)

    # 1. Test Signup Success
    response = client.post(
        "/api/auth/signup",
        json={"email": "newuser@example.com", "password": "securepassword123"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "newuser@example.com"
    assert response.json()["message"] == "User registered successfully"

    # 2. Test Duplicate Signup Rejection
    response = client.post(
        "/api/auth/signup",
        json={"email": "newuser@example.com", "password": "differentpassword"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email is already registered"

    # 3. Test Login Success
    response = client.post(
        "/api/auth/login",
        json={"email": "newuser@example.com", "password": "securepassword123"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Login successful"

    # 4. Test Login Incorrect Password
    response = client.post(
        "/api/auth/login",
        json={"email": "newuser@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

    # 5. Test Login Non-existent User
    response = client.post(
        "/api/auth/login",
        json={"email": "nonexistent@example.com", "password": "somepassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"
