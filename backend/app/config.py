"""Application configuration from environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///pixel_movies.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET", "jwt-secret-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = 900  # 15 minutes
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days

    # TMDB
    TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
    TMDB_BASE_URL = "https://api.themoviedb.org/3"

    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "")

    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173")

    # Rate limiting
    RATELIMIT_DEFAULT = "200/hour"
    RATELIMIT_STORAGE_URI = os.getenv("REDIS_URL", "memory://")


class TestConfig(Config):
    """Test configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-jwt-secret"
    TMDB_API_KEY = "test-api-key"
