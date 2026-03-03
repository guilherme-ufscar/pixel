"""Global error handlers and custom exceptions."""
import logging
from flask import jsonify, g
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base application error."""

    def __init__(self, message: str, status_code: int = 400, code: str = "BAD_REQUEST"):
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(message)


class NotFoundError(AppError):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404, "NOT_FOUND")


class ConflictError(AppError):
    """Resource conflict (e.g., duplicate)."""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, 409, "CONFLICT")


class TMDBError(AppError):
    """TMDB API error."""

    def __init__(self, message: str = "Failed to fetch data from TMDB"):
        super().__init__(message, 502, "TMDB_ERROR")


class CircuitOpenError(AppError):
    """Circuit breaker is open."""

    def __init__(self):
        super().__init__(
            "Service temporarily unavailable. Please try again later.",
            503,
            "SERVICE_UNAVAILABLE",
        )


def register_error_handlers(app):
    """Register global error handlers on the Flask app."""

    @app.errorhandler(AppError)
    def handle_app_error(error):
        request_id = g.get("request_id", "")
        logger.error(f"[{request_id}] AppError: {error.message} ({error.code})")
        return jsonify({"error": error.message, "code": error.code}), error.status_code

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        request_id = g.get("request_id", "")
        errors = []
        for err in error.errors():
            field = ".".join(str(loc) for loc in err["loc"])
            errors.append({"field": field, "message": err["msg"]})
        logger.warning(f"[{request_id}] Validation error: {errors}")
        return jsonify({"error": "Validation failed", "code": "VALIDATION_ERROR", "details": errors}), 422

    @app.errorhandler(400)
    def handle_400(error):
        return jsonify({"error": "Bad request", "code": "BAD_REQUEST"}), 400

    @app.errorhandler(404)
    def handle_404(error):
        return jsonify({"error": "Not found", "code": "NOT_FOUND"}), 404

    @app.errorhandler(405)
    def handle_405(error):
        return jsonify({"error": "Method not allowed", "code": "METHOD_NOT_ALLOWED"}), 405

    @app.errorhandler(429)
    def handle_429(error):
        return jsonify({"error": "Too many requests. Please try again later.", "code": "RATE_LIMITED"}), 429

    @app.errorhandler(500)
    def handle_500(error):
        request_id = g.get("request_id", "")
        logger.error(f"[{request_id}] Internal server error: {error}")
        return jsonify({"error": "Internal server error", "code": "INTERNAL_ERROR"}), 500
