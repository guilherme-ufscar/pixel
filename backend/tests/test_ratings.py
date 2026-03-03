"""Tests for rating service and routes."""


def _register_and_get_token(client):
    """Helper to register a user and return the access token."""
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "password123"},
    )
    return response.get_json()["access_token"]


class TestRatingRoutes:
    """Test rating endpoints."""

    def test_create_rating(self, client):
        """Test creating a new rating."""
        token = _register_and_get_token(client)
        response = client.post(
            "/api/v1/ratings",
            json={"movie_id": 550, "score": 4, "movie_title": "Fight Club", "poster_path": "/poster.jpg"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["rating"]["score"] == 4
        assert data["action"] == "created"

    def test_update_rating(self, client):
        """Test updating an existing rating (idempotent upsert)."""
        token = _register_and_get_token(client)
        client.post(
            "/api/v1/ratings",
            json={"movie_id": 550, "score": 4, "movie_title": "Fight Club"},
            headers={"Authorization": f"Bearer {token}"},
        )
        response = client.post(
            "/api/v1/ratings",
            json={"movie_id": 550, "score": 5, "movie_title": "Fight Club"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["rating"]["score"] == 5
        assert data["action"] == "updated"

    def test_delete_rating(self, client):
        """Test deleting a rating."""
        token = _register_and_get_token(client)
        client.post(
            "/api/v1/ratings",
            json={"movie_id": 550, "score": 4, "movie_title": "Fight Club"},
            headers={"Authorization": f"Bearer {token}"},
        )
        response = client.delete(
            "/api/v1/ratings/550",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

    def test_delete_nonexistent_rating(self, client):
        """Test deleting a rating that doesn't exist."""
        token = _register_and_get_token(client)
        response = client.delete(
            "/api/v1/ratings/999",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    def test_get_rating(self, client):
        """Test getting a specific rating."""
        token = _register_and_get_token(client)
        client.post(
            "/api/v1/ratings",
            json={"movie_id": 550, "score": 4, "movie_title": "Fight Club"},
            headers={"Authorization": f"Bearer {token}"},
        )
        response = client.get(
            "/api/v1/ratings/550",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.get_json()["rating"]["score"] == 4

    def test_get_nonexistent_rating(self, client):
        """Test getting a rating that doesn't exist."""
        token = _register_and_get_token(client)
        response = client.get(
            "/api/v1/ratings/999",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.get_json()["rating"] is None

    def test_list_ratings(self, client):
        """Test listing all user ratings."""
        token = _register_and_get_token(client)
        client.post(
            "/api/v1/ratings",
            json={"movie_id": 550, "score": 4, "movie_title": "Fight Club"},
            headers={"Authorization": f"Bearer {token}"},
        )
        client.post(
            "/api/v1/ratings",
            json={"movie_id": 680, "score": 5, "movie_title": "Pulp Fiction"},
            headers={"Authorization": f"Bearer {token}"},
        )
        response = client.get(
            "/api/v1/ratings",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["ratings"]) == 2

    def test_invalid_score(self, client):
        """Test creating a rating with invalid score."""
        token = _register_and_get_token(client)
        response = client.post(
            "/api/v1/ratings",
            json={"movie_id": 550, "score": 6, "movie_title": "Fight Club"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 422

    def test_rating_requires_auth(self, client):
        """Test that ratings require authentication."""
        response = client.post(
            "/api/v1/ratings",
            json={"movie_id": 550, "score": 4, "movie_title": "Fight Club"},
        )
        assert response.status_code == 401
