"""Tests for authentication service and routes."""
import json


class TestAuthRoutes:
    """Test auth endpoints."""

    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "password": "password123"},
        )
        assert response.status_code == 201
        data = response.get_json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "test@example.com"

    def test_register_duplicate_email(self, client):
        """Test registration with existing email."""
        client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "password": "password123"},
        )
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "password": "password456"},
        )
        assert response.status_code == 409

    def test_register_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "invalid", "password": "password123"},
        )
        assert response.status_code == 422

    def test_register_short_password(self, client):
        """Test registration with too short password."""
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "password": "12345"},
        )
        assert response.status_code == 422

    def test_login_success(self, client):
        """Test successful login."""
        client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "password": "password123"},
        )
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password123"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "access_token" in data

    def test_login_wrong_password(self, client):
        """Test login with wrong password."""
        client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "password": "password123"},
        )
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "wrong"},
        )
        assert response.status_code == 401

    def test_me_authenticated(self, client):
        """Test getting current user info."""
        reg = client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "password": "password123"},
        )
        token = reg.get_json()["access_token"]
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.get_json()["user"]["email"] == "test@example.com"

    def test_me_unauthenticated(self, client):
        """Test getting current user without token."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
