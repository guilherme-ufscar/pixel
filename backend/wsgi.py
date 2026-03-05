"""WSGI entry point."""
from app import create_app
from app.extensions import db
from sqlalchemy import inspect, text

app = create_app()

# Create tables on first run (safe for multiple workers)
with app.app_context():
    try:
        inspector = inspect(db.engine)
        existing = inspector.get_table_names()
        if not existing:
            db.create_all()
        else:
            # Create only missing tables
            db.create_all()
    except Exception:
        # Table already exists — created by another worker, safe to ignore
        db.session.rollback()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
