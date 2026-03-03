"""Rating service."""
import logging
from typing import Optional
from app.extensions import db
from app.models.rating import Rating
from app.utils.errors import NotFoundError

logger = logging.getLogger(__name__)


class RatingService:
    """Service for movie rating operations."""

    @staticmethod
    def upsert_rating(
        user_id: int,
        movie_id: int,
        score: int,
        movie_title: str = "",
        poster_path: Optional[str] = None,
    ) -> dict:
        """Create or update a rating (idempotent upsert)."""
        rating = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()

        if rating:
            rating.score = score
            if movie_title:
                rating.movie_title = movie_title
            if poster_path is not None:
                rating.poster_path = poster_path
            action = "updated"
        else:
            rating = Rating(
                user_id=user_id,
                movie_id=movie_id,
                score=score,
                movie_title=movie_title,
                poster_path=poster_path,
            )
            db.session.add(rating)
            action = "created"

        db.session.commit()
        logger.info(f"Rating {action}: user={user_id}, movie={movie_id}, score={score}")
        return {"rating": rating.to_dict(), "action": action}

    @staticmethod
    def delete_rating(user_id: int, movie_id: int) -> None:
        """Delete a user's rating for a movie."""
        rating = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()
        if not rating:
            raise NotFoundError("Rating not found")

        db.session.delete(rating)
        db.session.commit()
        logger.info(f"Rating deleted: user={user_id}, movie={movie_id}")

    @staticmethod
    def get_rating(user_id: int, movie_id: int) -> Optional[dict]:
        """Get a user's rating for a specific movie."""
        rating = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()
        if not rating:
            return None
        return rating.to_dict()

    @staticmethod
    def get_user_ratings(
        user_id: int,
        sort_by: str = "updated_at",
        order: str = "desc",
    ) -> list[dict]:
        """Get all ratings for a user, sorted by specified field."""
        query = Rating.query.filter_by(user_id=user_id)

        sort_column = getattr(Rating, sort_by, Rating.updated_at)
        if order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        ratings = query.all()
        return [r.to_dict() for r in ratings]
