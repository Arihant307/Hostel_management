from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash
import hmac

from db import db

# Password hashes produced by Werkzeug start with the method name.
_HASH_PREFIXES = ("scrypt:", "pbkdf2:")


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Stores the person's full name. It is not unique: two students may share a name.
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    # Werkzeug scrypt hashes are ~160 characters, so 255 leaves room.
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    # Used by the admin Students page as the student's assigned room number.
    room_preference = db.Column(db.String(20))
    address = db.Column(db.String(200))
    role = db.Column(db.String(20), nullable=False, default="student", server_default="student")

    @property
    def is_admin(self):
        return self.role == "admin"

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        """Verify a password.

        Databases created by the earlier version of this project stored
        passwords in plain text. Those rows are still accepted once and then
        upgraded to a hash, so existing local accounts keep working.
        """
        stored = self.password or ""
        if stored.startswith(_HASH_PREFIXES):
            return check_password_hash(stored, raw_password)
        if stored and hmac.compare_digest(stored.encode(), raw_password.encode()):
            self.set_password(raw_password)  # upgrade legacy plaintext
            return True
        return False


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(10), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    room_type = db.Column(db.String(20))


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=_utcnow)
