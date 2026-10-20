"""Hostel Management System - Flask entry point.

Local:      python app.py                       (from the backend folder)
Production: gunicorn --chdir backend app:app    (see render.yaml / README)
"""
import getpass
import logging
import os

import click
from flask import Flask, abort, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

from config import FRONTEND_DIR, build_config
from db import db

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("hostel")

# Only these frontend files/folders are publicly served. Anything else in the
# repository (Python files, databases, .env) is never reachable over HTTP.
STATIC_DIRS = ("admin/", "student/")
STATIC_ROOT_FILES = {"index.html", "config.js"}
STATIC_EXTENSIONS = {
    ".html", ".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg",
    ".ico", ".webp", ".woff", ".woff2",
}
API_PREFIXES = ("/auth/", "/api/", "/add_payment", "/get_payments", "/get_courses",
                "/add_course", "/edit_course", "/delete_course", "/health")


def create_app(overrides=None):
    app = Flask(__name__)
    app.config.update(build_config())
    if overrides:
        app.config.update(overrides)

    # Render terminates HTTPS at its proxy; trust one hop of X-Forwarded-* headers.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    if app.config["CORS_ORIGINS"]:
        CORS(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True)

    db.init_app(app)
    Migrate(app, db)

    # Import models AFTER db.init_app to avoid circular issues
    import models  # noqa: F401
    from routes.auth import auth_bp
    from routes.courses import courses_bp
    from routes.dashboard import dashboard_bp
    from routes.payments import payments_bp
    from routes.rooms import room_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(room_bp, url_prefix='/api/rooms')
    app.register_blueprint(payments_bp)
    app.register_blueprint(courses_bp)

    _register_core_routes(app)
    _register_error_handlers(app)
    _register_cli(app)

    from db_setup import init_database
    init_database(app)
    return app


def _register_core_routes(app):
    @app.get("/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"status": "ok", "database": "ok"}), 200
        except SQLAlchemyError:
            log.exception("Health check database query failed")
            db.session.rollback()
            return jsonify({"status": "error", "database": "unavailable"}), 503

    if not app.config["SERVE_FRONTEND"]:
        @app.get("/")
        def api_root():
            return jsonify({"service": "hostel-management-api", "health": "/health"})
        return

    @app.get("/")
    def index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.get("/<path:filename>")
    def frontend_file(filename):
        allowed_location = filename in STATIC_ROOT_FILES or filename.startswith(STATIC_DIRS)
        ext = os.path.splitext(filename)[1].lower()
        if not allowed_location or ext not in STATIC_EXTENSIONS:
            abort(404)
        # send_from_directory rejects path traversal (../) itself.
        response = send_from_directory(FRONTEND_DIR, filename)
        if ext in {".html", ".js", ".css"}:
            response.headers["Cache-Control"] = "no-cache"
        return response

    @app.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response


def _wants_json():
    return request.path.startswith(API_PREFIXES) or request.is_json


def _register_error_handlers(app):
    @app.errorhandler(IntegrityError)
    def integrity_error(exc):
        db.session.rollback()
        log.warning("Integrity error on %s %s", request.method, request.path)
        msg = "This record conflicts with an existing one."
        return jsonify({"error": msg, "message": msg}), 400

    @app.errorhandler(HTTPException)
    def http_error(exc):
        if not _wants_json():
            return exc
        return jsonify({"error": exc.name, "message": exc.name}), exc.code

    @app.errorhandler(Exception)
    def unhandled_error(exc):
        # Log the full traceback server-side, never send it to the client.
        db.session.rollback()
        log.exception("Unhandled error on %s %s", request.method, request.path)
        msg = "An internal error occurred. Please try again."
        return jsonify({"error": msg, "message": msg}), 500


def _register_cli(app):
    @app.cli.command("init-db")
    def init_db_command():
        """Create tables / add missing columns."""
        from db_setup import init_database
        init_database(app)
        click.echo("Database initialised.")

    @app.cli.command("create-admin")
    @click.option("--email", prompt=True)
    @click.option("--name", default="Administrator", show_default=True)
    def create_admin_command(email, name):
        """Create an admin account (or promote an existing account)."""
        from db_setup import ensure_admin
        password = getpass.getpass("Password (min 8 chars): ")
        try:
            status = ensure_admin(email, password, name)
        except ValueError as exc:
            raise click.ClickException(str(exc))
        click.echo(f"Admin account {status}.")


app = create_app()


if __name__ == '__main__':
    debug = os.environ.get("FLASK_DEBUG", "0") == "1" and not app.config["IS_PRODUCTION"]
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=debug)
