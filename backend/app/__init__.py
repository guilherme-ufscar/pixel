"""Flask application factory."""
import os
import uuid
import logging
from flask import Flask, g, request, jsonify
from flask_cors import CORS

from app.extensions import db, jwt, migrate, limiter
from app.config import Config


def create_app(config_class=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    if config_class:
        app.config.from_object(config_class)
    else:
        app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    # CORS
    cors_origins = app.config.get("CORS_ORIGINS", "http://localhost:5173")
    CORS(app, origins=cors_origins.split(","), supports_credentials=True)

    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Request ID middleware
    @app.before_request
    def add_request_id():
        g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    # Security headers
    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["X-Request-ID"] = g.get("request_id", "")
        return response

    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired", "code": "TOKEN_EXPIRED"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Invalid token", "code": "TOKEN_INVALID"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"error": "Authentication required", "code": "AUTH_REQUIRED"}), 401

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.movies import movies_bp
    from app.routes.ratings import ratings_bp

    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(movies_bp, url_prefix="/api/v1/movies")
    app.register_blueprint(ratings_bp, url_prefix="/api/v1/ratings")

    # Global error handlers
    from app.utils.errors import register_error_handlers
    register_error_handlers(app)

    # Health check
    @app.route("/api/v1/health")
    def health():
        return jsonify({"status": "ok"})

    return app
