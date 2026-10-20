import os
import sys

import pytest

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND)

# Make sure importing `app` (which builds a module-level app) never touches a
# real database file or picks up developer settings.
for var in ("DATABASE_URL", "ADMIN_EMAIL", "ADMIN_PASSWORD", "CORS_ORIGINS", "APP_ENV"):
    os.environ.pop(var, None)
os.environ["SECRET_KEY"] = "test-secret-key"
import tempfile  # noqa: E402
os.environ["SQLITE_PATH"] = os.path.join(tempfile.mkdtemp(), "import-time.db")


@pytest.fixture()
def make_app(tmp_path, monkeypatch):
    def _make(**env):
        monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "test.db"))
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        from app import create_app
        application = create_app({"TESTING": True})
        return application
    return _make


@pytest.fixture()
def app(make_app):
    return make_app(ADMIN_EMAIL="admin@example.test", ADMIN_PASSWORD="admin-pass-123")


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client, email, password, role=None):
    body = {"email": email, "password": password}
    if role:
        body["role"] = role
    return client.post("/auth/login", json=body)


@pytest.fixture()
def admin_client(app):
    c = app.test_client()
    assert login(c, "admin@example.test", "admin-pass-123", "admin").status_code == 200
    return c


@pytest.fixture()
def student_client(app):
    c = app.test_client()
    r = c.post("/auth/register", json={"fullname": "Demo Student", "email": "demo.student@example.test",
                                       "password": "student-pass-1", "room": "single"})
    assert r.status_code == 201
    assert login(c, "demo.student@example.test", "student-pass-1").status_code == 200
    return c
