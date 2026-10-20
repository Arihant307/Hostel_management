"""Session helpers, authorization decorators and input validation."""
import re
from functools import wraps

from flask import jsonify, request, session

from db import db
from models import User

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    user = db.session.get(User, user_id)
    if user is None:
        session.clear()
    return user


def login_user(user):
    session.clear()
    session.permanent = True
    session["user_id"] = user.id
    session["role"] = user.role


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if current_user() is None:
            return jsonify({"error": "Login required", "message": "Login required"}), 401
        return view(*args, **kwargs)

    return wrapper


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        user = current_user()
        if user is None:
            return jsonify({"error": "Login required", "message": "Login required"}), 401
        if not user.is_admin:
            return jsonify({"error": "Admin access required", "message": "Admin access required"}), 403
        return view(*args, **kwargs)

    return wrapper


def get_json():
    """Return the request JSON body as a dict, or an empty dict."""
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def clean_str(value, max_len):
    if value is None:
        return ""
    return str(value).strip()[:max_len]


def valid_email(email):
    return bool(email) and len(email) <= 100 and bool(EMAIL_RE.match(email))
