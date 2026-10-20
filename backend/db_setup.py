"""Database initialisation that is safe to run on every start-up.

1. Creates any missing tables (fresh SQLite file or fresh PostgreSQL database).
2. Adds columns that were introduced after an older local database was made
   (for example `user.role`), so existing `hostel.db` files keep working.
3. Optionally creates or promotes an admin account from the ADMIN_EMAIL /
   ADMIN_PASSWORD environment variables. No admin credentials are hardcoded.
"""
import logging
import os

from sqlalchemy import inspect, text

from db import db
from models import User

log = logging.getLogger(__name__)


def _add_missing_columns():
    engine = db.engine
    inspector = inspect(engine)
    preparer = engine.dialect.identifier_preparer
    for table in db.metadata.sorted_tables:
        if not inspector.has_table(table.name):
            continue
        existing = {col["name"] for col in inspector.get_columns(table.name)}
        for column in table.columns:
            if column.name in existing:
                continue
            col_type = column.type.compile(dialect=engine.dialect)
            ddl = f"ALTER TABLE {preparer.quote(table.name)} ADD COLUMN {preparer.quote(column.name)} {col_type}"
            if column.server_default is not None:
                default = column.server_default.arg
                default_sql = default.text if hasattr(default, "text") else f"'{default}'"
                ddl += f" DEFAULT {default_sql} NOT NULL"
            with engine.begin() as conn:
                conn.execute(text(ddl))
            log.info("Added missing column %s.%s", table.name, column.name)


def ensure_admin(email, password, name="Administrator"):
    """Create an admin account, or promote an existing account to admin.

    An existing account's password is not changed.
    Returns a short status string.
    """
    from security import MIN_PASSWORD_LENGTH, valid_email
    from sqlalchemy import func

    email = (email or "").strip().lower()
    if not valid_email(email):
        raise ValueError("ADMIN_EMAIL is not a valid email address")
    user = User.query.filter(func.lower(User.email) == email).first()
    if user:
        if user.role != "admin":
            user.role = "admin"
            db.session.commit()
            return "promoted"
        return "exists"
    if not password or len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"ADMIN_PASSWORD must be at least {MIN_PASSWORD_LENGTH} characters")
    user = User(username=(name or "Administrator").strip()[:80], email=email, role="admin")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return "created"


def init_database(app):
    with app.app_context():
        db.create_all()
        _add_missing_columns()

        admin_email = os.environ.get("ADMIN_EMAIL", "").strip()
        admin_password = os.environ.get("ADMIN_PASSWORD", "")
        if admin_email:
            try:
                status = ensure_admin(admin_email, admin_password, os.environ.get("ADMIN_NAME", "Administrator"))
                log.info("Admin account from ADMIN_EMAIL: %s", status)
            except ValueError as exc:
                log.error("Could not set up admin account: %s", exc)
        elif not User.query.filter_by(role="admin").first():
            log.warning(
                "No admin account exists. Set ADMIN_EMAIL and ADMIN_PASSWORD, "
                "or run `flask --app app create-admin` from the backend folder."
            )
        db.session.remove()
        # Do not share pooled connections with forked gunicorn workers.
        db.engine.dispose()
