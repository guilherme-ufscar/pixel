"""Rating routes — CRUD for user movie ratings."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.schemas import RatingSchema
from app.services.rating_service import RatingService

ratings_bp = Blueprint("ratings", __name__)


@ratings_bp.route("", methods=["POST"])
@jwt_required()
def upsert_rating():
    """Create or update a rating (idempotent upsert)."""
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body is required", "code": "BAD_REQUEST"}), 400

    schema = RatingSchema(**data)
    result = RatingService.upsert_rating(
        user_id=user_id,
        movie_id=schema.movie_id,
        score=schema.score,
        movie_title=schema.movie_title,
        poster_path=schema.poster_path,
    )
    status_code = 200 if result["action"] == "updated" else 201
    return jsonify(result), status_code


@ratings_bp.route("/<int:movie_id>", methods=["DELETE"])
@jwt_required()
def delete_rating(movie_id: int):
    """Delete a user's rating for a movie."""
    user_id = int(get_jwt_identity())
    RatingService.delete_rating(user_id, movie_id)
    return jsonify({"message": "Rating deleted"}), 200


@ratings_bp.route("/<int:movie_id>", methods=["GET"])
@jwt_required()
def get_rating(movie_id: int):
    """Get user's rating for a specific movie."""
    user_id = int(get_jwt_identity())
    rating = RatingService.get_rating(user_id, movie_id)
    if not rating:
        return jsonify({"rating": None}), 200
    return jsonify({"rating": rating}), 200


@ratings_bp.route("", methods=["GET"])
@jwt_required()
def get_user_ratings():
    """List all rated movies for the current user."""
    user_id = int(get_jwt_identity())
    sort_by = request.args.get("sort_by", "updated_at")
    order = request.args.get("order", "desc")

    # Validate sort_by
    allowed_sorts = {"score", "created_at", "updated_at"}
    if sort_by not in allowed_sorts:
        sort_by = "updated_at"
    if order not in {"asc", "desc"}:
        order = "desc"

    ratings = RatingService.get_user_ratings(user_id, sort_by, order)
    return jsonify({"ratings": ratings}), 200
