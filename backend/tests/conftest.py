"""Backend tests."""
import pytest
from app import create_app
from app.config import TestConfig
from app.extensions import db as _db


@pytest.fixture
def app():
    """Create test application."""
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def db(app):
    """Get database session."""
    return _db
