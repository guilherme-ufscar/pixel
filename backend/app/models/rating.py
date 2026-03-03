"""Rating model."""
from datetime import datetime, timezone
from app.extensions import db


class Rating(db.Model):
    """Movie rating by a user."""

    __tablename__ = "ratings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    movie_id = db.Column(db.Integer, nullable=False, index=True)
    score = db.Column(db.Integer, nullable=False)
    movie_title = db.Column(db.String(500), nullable=False, default="")
    poster_path = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "movie_id", name="uq_user_movie"),
        db.CheckConstraint("score >= 1 AND score <= 5", name="ck_score_range"),
    )

    def to_dict(self) -> dict:
        """Serialize rating to dict."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "movie_id": self.movie_id,
            "score": self.score,
            "movie_title": self.movie_title,
            "poster_path": self.poster_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
