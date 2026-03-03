"""Movie routes — TMDB proxy with caching."""
from flask import Blueprint, request, jsonify

from app.schemas import SearchQuerySchema
from app.services.tmdb_service import get_tmdb_service
from app.extensions import limiter

movies_bp = Blueprint("movies", __name__)


@movies_bp.route("/search", methods=["GET"])
@limiter.limit("30/minute")
def search_movies():
    """Search movies via TMDB API."""
    params = SearchQuerySchema(
        query=request.args.get("query", ""),
        page=int(request.args.get("page", 1)),
        genre=int(request.args.get("genre")) if request.args.get("genre") else None,
        year=int(request.args.get("year")) if request.args.get("year") else None,
    )

    tmdb = get_tmdb_service()
    result = tmdb.search_movies(
        query=params.query,
        page=params.page,
        genre=params.genre,
        year=params.year,
    )

    return jsonify(result), 200


@movies_bp.route("/<int:movie_id>", methods=["GET"])
def get_movie_details(movie_id: int):
    """Get movie details from TMDB."""
    tmdb = get_tmdb_service()
    result = tmdb.get_movie_details(movie_id)
    return jsonify(result), 200


@movies_bp.route("/<int:movie_id>/credits", methods=["GET"])
def get_movie_credits(movie_id: int):
    """Get movie credits from TMDB."""
    tmdb = get_tmdb_service()
    result = tmdb.get_movie_credits(movie_id)
    return jsonify(result), 200


@movies_bp.route("/genres", methods=["GET"])
def get_genres():
    """Get movie genres from TMDB."""
    tmdb = get_tmdb_service()
    result = tmdb.get_genres()
    return jsonify(result), 200
