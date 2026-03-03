"""TMDB API service with caching and circuit breaker."""
import logging
import requests
from typing import Optional, Any

from app.utils.cache import create_cache
from app.utils.circuit_breaker import CircuitBreaker, CircuitState
from app.utils.errors import TMDBError, CircuitOpenError

logger = logging.getLogger(__name__)

# TTL constants (seconds)
TTL_SEARCH = 300       # 5 minutes
TTL_DETAILS = 3600     # 1 hour
TTL_CREDITS = 3600     # 1 hour
TTL_GENRES = 86400     # 24 hours


class TMDBService:
    """Service for interacting with the TMDB API."""

    def __init__(self, api_key: str, redis_url: str = ""):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.cache = create_cache(redis_url)
        self.circuit = CircuitBreaker(failure_threshold=5, reset_timeout=30, window=60)
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
        })

    def _make_request(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make a request to the TMDB API with circuit breaker protection."""
        if not self.circuit.is_available():
            raise CircuitOpenError()

        try:
            params = params or {}
            params["api_key"] = self.api_key
            params.setdefault("language", "pt-BR")

            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            self.circuit.record_success()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.circuit.record_failure()
            logger.error(f"TMDB API error: {e}")
            raise TMDBError(f"Failed to fetch data from TMDB: {str(e)}")

    def search_movies(
        self,
        query: str,
        page: int = 1,
        genre: Optional[int] = None,
        year: Optional[int] = None,
    ) -> dict:
        """Search movies via TMDB API. Uses discover endpoint when no query but filters are set."""
        cache_key = f"search:{query}:{page}:{genre}:{year}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        if query:
            params: dict[str, Any] = {"query": query, "page": page}
            if year:
                params["year"] = year
            result = self._make_request("/search/movie", params)
            # If genre filter is set, filter client-side for search endpoint
            if genre:
                result["results"] = [
                    m for m in result.get("results", [])
                    if genre in m.get("genre_ids", [])
                ]
        else:
            # Use discover endpoint when no query
            params = {"page": page, "sort_by": "popularity.desc"}
            if genre:
                params["with_genres"] = str(genre)
            if year:
                params["primary_release_year"] = year
            result = self._make_request("/discover/movie", params)

        self.cache.set(cache_key, result, TTL_SEARCH)
        return result

    def get_movie_details(self, movie_id: int) -> dict:
        """Get detailed movie information."""
        cache_key = f"movie:{movie_id}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        result = self._make_request(f"/movie/{movie_id}")
        self.cache.set(cache_key, result, TTL_DETAILS)
        return result

    def get_movie_credits(self, movie_id: int) -> dict:
        """Get movie cast and crew."""
        cache_key = f"credits:{movie_id}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        result = self._make_request(f"/movie/{movie_id}/credits")
        # Return only top 20 cast members to reduce payload
        if "cast" in result:
            result["cast"] = result["cast"][:20]
        self.cache.set(cache_key, result, TTL_CREDITS)
        return result

    def get_genres(self) -> dict:
        """Get list of movie genres."""
        cache_key = "genres"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        result = self._make_request("/genre/movie/list")
        self.cache.set(cache_key, result, TTL_GENRES)
        return result


# Singleton instance (initialized in app factory)
_tmdb_service: Optional[TMDBService] = None


def get_tmdb_service() -> TMDBService:
    """Get or create the TMDB service singleton."""
    global _tmdb_service
    if _tmdb_service is None:
        from flask import current_app
        _tmdb_service = TMDBService(
            api_key=current_app.config["TMDB_API_KEY"],
            redis_url=current_app.config.get("REDIS_URL", ""),
        )
    return _tmdb_service


def reset_tmdb_service() -> None:
    """Reset the singleton (for testing)."""
    global _tmdb_service
    _tmdb_service = None
