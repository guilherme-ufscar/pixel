"""Authentication routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError

from app.schemas import RegisterSchema, LoginSchema
from app.services.auth_service import AuthService
from app.extensions import limiter

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5/minute")
def register():
    """Register a new user."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body is required", "code": "BAD_REQUEST"}), 400

    schema = RegisterSchema(**data)
    result = AuthService.register(schema.email, schema.password)
    return jsonify(result), 201


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10/minute")
def login():
    """Authenticate user and return tokens."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body is required", "code": "BAD_REQUEST"}), 400

    schema = LoginSchema(**data)
    result = AuthService.login(schema.email, schema.password)
    return jsonify(result), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    user_id = get_jwt_identity()
    result = AuthService.refresh(user_id)
    return jsonify(result), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """Get current user info."""
    user_id = int(get_jwt_identity())
    user = AuthService.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found", "code": "NOT_FOUND"}), 404
    return jsonify({"user": user}), 200
