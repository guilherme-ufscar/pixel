"""Authentication service."""
import logging
from typing import Optional
from flask_jwt_extended import create_access_token, create_refresh_token
from app.extensions import db
from app.models.user import User
from app.utils.errors import AppError, ConflictError

logger = logging.getLogger(__name__)


class AuthService:
    """Service for user authentication operations."""

    @staticmethod
    def register(email: str, password: str) -> dict:
        """Register a new user."""
        existing = User.query.filter_by(email=email).first()
        if existing:
            raise ConflictError("An account with this email already exists")

        user = User(email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        logger.info(f"User registered: {email}")
        return {
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    @staticmethod
    def login(email: str, password: str) -> dict:
        """Authenticate a user and return tokens."""
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            raise AppError("Invalid email or password", 401, "INVALID_CREDENTIALS")

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        logger.info(f"User logged in: {email}")
        return {
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    @staticmethod
    def refresh(user_id: str) -> dict:
        """Generate a new access token from a refresh token."""
        access_token = create_access_token(identity=user_id)
        return {"access_token": access_token}

    @staticmethod
    def get_user(user_id: int) -> Optional[dict]:
        """Get user by ID."""
        user = User.query.get(user_id)
        if not user:
            return None
        return user.to_dict()
