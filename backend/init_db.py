"""Initialise the database manually: `python init_db.py` (from backend/).

The app also does this automatically on every start-up, so running this script
is optional. It is kept for convenience and for backwards compatibility.
"""
from app import app  # importing the app runs create_all + column upgrades

if __name__ == "__main__":
    with app.app_context():
        from db import db
        db.create_all()
    print("Tables created successfully.")
