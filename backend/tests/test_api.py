"""API tests. Run from the backend folder:  python -m pytest -q"""
import sqlite3

from conftest import login


# ---------- health / startup ----------

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok", "database": "ok"}


def test_fresh_database_has_all_tables(app):
    from sqlalchemy import inspect
    from db import db
    with app.app_context():
        tables = set(inspect(db.engine).get_table_names())
    assert {"user", "room", "course", "payment"} <= tables


def test_production_requires_secret_key(monkeypatch):
    import pytest
    from config import build_config
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError):
        build_config()


def test_postgres_url_is_normalised(monkeypatch):
    from config import build_config
    monkeypatch.setenv("DATABASE_URL", "postgres://u:p@host:5432/db")
    assert build_config()["SQLALCHEMY_DATABASE_URI"] == "postgresql://u:p@host:5432/db"


# ---------- registration / login ----------

def test_register_hashes_password(app, client):
    r = client.post("/auth/register", json={"fullname": "A B", "email": "ab@example.test", "password": "longenough1"})
    assert r.status_code == 201
    from models import User
    with app.app_context():
        u = User.query.filter_by(email="ab@example.test").one()
        assert u.password != "longenough1"
        assert u.password.startswith(("scrypt:", "pbkdf2:"))
        assert u.role == "student"


def test_register_validation(client):
    assert client.post("/auth/register", json={}).status_code == 400
    assert client.post("/auth/register", json={"fullname": "x", "email": "bad", "password": "longenough1"}).status_code == 400
    assert client.post("/auth/register", json={"fullname": "x", "email": "x@example.test", "password": "short"}).status_code == 400
    assert client.post("/auth/register", data="not json").status_code == 400


def test_register_duplicate_email_and_same_name_allowed(client):
    body = {"fullname": "Same Name", "email": "one@example.test", "password": "longenough1"}
    assert client.post("/auth/register", json=body).status_code == 201
    assert client.post("/auth/register", json=body).status_code == 400  # same email
    body2 = dict(body, email="two@example.test")
    assert client.post("/auth/register", json=body2).status_code == 201  # same name is fine


def test_register_cannot_create_admin(client):
    r = client.post("/auth/register", json={"fullname": "x", "email": "x@example.test",
                                            "password": "longenough1", "role": "admin"})
    assert r.status_code == 201
    assert login(client, "x@example.test", "longenough1").get_json()["role"] == "student"


def test_login_success_and_failure(client, student_client):
    assert login(client, "demo.student@example.test", "wrong-password").status_code == 401
    assert login(client, "nobody@example.test", "whatever123").status_code == 401
    r = login(client, "DEMO.Student@example.test", "student-pass-1")  # case-insensitive email
    assert r.status_code == 200
    assert r.get_json()["role"] == "student"


def test_student_cannot_use_admin_portal(client, student_client):
    r = login(client, "demo.student@example.test", "student-pass-1", role="admin")
    assert r.status_code == 403
    # and no session was created
    assert client.get("/auth/me").status_code == 401


def test_session_cookie_flags(client, student_client):
    r = login(client, "demo.student@example.test", "student-pass-1")
    cookie = r.headers.get("Set-Cookie", "")
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie


def test_logout(student_client):
    assert student_client.get("/auth/me").status_code == 200
    assert student_client.post("/auth/logout").status_code == 200
    assert student_client.get("/auth/me").status_code == 401


def test_legacy_plaintext_password_is_upgraded(app, client):
    from db import db
    from models import User
    with app.app_context():
        db.session.add(User(username="Old", email="old@example.test", password="plainpass"))
        db.session.commit()
    assert login(client, "old@example.test", "wrongpass").status_code == 401
    assert login(client, "old@example.test", "plainpass").status_code == 200
    with app.app_context():
        assert User.query.filter_by(email="old@example.test").one().password.startswith(("scrypt:", "pbkdf2:"))
    assert login(client, "old@example.test", "plainpass").status_code == 200


# ---------- authorization ----------

ADMIN_ENDPOINTS = [
    ("get", "/auth/students"), ("post", "/auth/students"), ("put", "/auth/students/1"),
    ("delete", "/auth/students/1"), ("get", "/auth/get_student_reports"),
    ("post", "/api/rooms/add"), ("get", "/api/rooms/get_room_occupancy"),
    ("get", "/api/dashboard/stats"), ("post", "/add_payment"), ("get", "/get_payments"),
    ("get", "/get_courses"), ("post", "/add_course"), ("put", "/edit_course/1"),
    ("delete", "/delete_course/1"),
]


def test_admin_endpoints_reject_anonymous(client):
    for method, url in ADMIN_ENDPOINTS:
        r = getattr(client, method)(url, json={})
        assert r.status_code == 401, (method, url, r.status_code)


def test_admin_endpoints_reject_students(student_client):
    for method, url in ADMIN_ENDPOINTS:
        r = getattr(student_client, method)(url, json={})
        assert r.status_code == 403, (method, url, r.status_code)


def test_profile_is_own_only(app, client, student_client):
    client.post("/auth/register", json={"fullname": "Other", "email": "other@example.test", "password": "longenough1"})
    assert client.get("/auth/profile").status_code == 401
    r = student_client.get("/auth/profile")
    assert r.get_json() == {"fullname": "Demo Student", "email": "demo.student@example.test"}
    assert student_client.get("/auth/profile?email=other@example.test").status_code == 403
    r = student_client.post("/auth/profile/update", json={"email": "other@example.test", "fullname": "Hacked"})
    assert r.status_code == 403
    r = student_client.post("/auth/profile/update", json={"email": "demo.student@example.test", "fullname": "New Name"})
    assert r.status_code == 200
    assert student_client.get("/auth/profile").get_json()["fullname"] == "New Name"


# ---------- admin bootstrap ----------

def test_no_admin_without_env(make_app):
    application = make_app()
    from models import User
    with application.app_context():
        assert User.query.filter_by(role="admin").count() == 0


def test_admin_env_promotes_existing_user(make_app):
    application = make_app()
    c = application.test_client()
    c.post("/auth/register", json={"fullname": "Boss", "email": "boss@example.test", "password": "longenough1"})
    application2 = make_app(ADMIN_EMAIL="boss@example.test", ADMIN_PASSWORD="")
    r = login(application2.test_client(), "boss@example.test", "longenough1", role="admin")
    assert r.status_code == 200


def test_admin_env_rejects_short_password(make_app):
    application = make_app(ADMIN_EMAIL="weak@example.test", ADMIN_PASSWORD="short")
    from models import User
    with application.app_context():
        assert User.query.filter_by(email="weak@example.test").count() == 0


# ---------- student management ----------

def test_students_crud(admin_client):
    r = admin_client.post("/auth/students", json={"name": "S1", "email": "s1@example.test", "phone": "123", "room": "101"})
    assert r.status_code == 201
    body = r.get_json()
    assert len(body["temporary_password"]) >= 8  # no shared default password
    sid = body["id"]

    students = admin_client.get("/auth/students").get_json()
    assert [s["email"] for s in students] == ["s1@example.test"]  # admin not listed
    assert set(students[0]) == {"id", "name", "email", "phone", "room"}

    assert admin_client.put(f"/auth/students/{sid}", json={"name": "S1b", "room": "102"}).status_code == 200
    s = admin_client.get("/auth/students").get_json()[0]
    assert (s["name"], s["room"], s["phone"]) == ("S1b", "102", "123")

    # temp password works for login
    c = admin_client.application.test_client()
    assert login(c, "s1@example.test", body["temporary_password"]).status_code == 200

    assert admin_client.delete(f"/auth/students/{sid}").status_code == 200
    assert admin_client.get("/auth/students").get_json() == []
    assert admin_client.delete(f"/auth/students/{sid}").status_code == 404


def test_admin_cannot_be_deleted_via_students_api(app, admin_client):
    from models import User
    with app.app_context():
        admin_id = User.query.filter_by(role="admin").one().id
    assert admin_client.delete(f"/auth/students/{admin_id}").status_code == 404


def test_edit_student_email_conflict(admin_client):
    a = admin_client.post("/auth/students", json={"name": "A", "email": "a@example.test"}).get_json()["id"]
    admin_client.post("/auth/students", json={"name": "B", "email": "b@example.test"})
    r = admin_client.put(f"/auth/students/{a}", json={"email": "b@example.test"})
    assert r.status_code == 400


# ---------- rooms / reports / dashboard ----------

def test_rooms_and_occupancy(admin_client, student_client):
    assert admin_client.post("/api/rooms/add", json={"number": "101", "capacity": "2", "type": "Double"}).status_code == 201
    assert admin_client.post("/api/rooms/add", json={"number": "101", "capacity": 2}).status_code == 400  # duplicate
    assert admin_client.post("/api/rooms/add", json={"number": "", "capacity": 2}).status_code == 400
    assert admin_client.post("/api/rooms/add", json={"number": "102", "capacity": 0}).status_code == 400
    assert admin_client.post("/api/rooms/add", json={"number": "102", "capacity": "abc"}).status_code == 400
    assert admin_client.post("/api/rooms/add", json={"number": "102", "capacity": 1}).status_code == 201

    admin_client.post("/auth/students", json={"name": "S", "email": "s@example.test", "room": "101"})

    rooms = admin_client.get("/api/rooms/").get_json()
    assert rooms[0] == {"id": rooms[0]["id"], "number": "101", "capacity": 2, "type": "double", "occupied": 1}
    assert student_client.get("/api/rooms/").status_code == 200  # any logged-in user can view rooms

    occ = admin_client.get("/api/rooms/get_room_occupancy").get_json()
    assert occ == {"room_types": ["101", "102"], "occupancy_counts": [1, 0]}

    stats = admin_client.get("/api/dashboard/stats").get_json()
    assert stats["total_students"] == 2
    assert stats["total_rooms"] == 2
    assert stats["available_rooms"] == 2
    assert stats["occupancy_rate"] == 33


def test_payments_and_reports(admin_client, student_client):
    students = admin_client.get("/auth/students").get_json()
    sid = students[0]["id"]
    reports = admin_client.get("/auth/get_student_reports").get_json()
    assert reports[0]["payment_status"] is False

    assert admin_client.post("/add_payment", json={"student_id": str(sid), "amount": "1500", "method": "upi"}).status_code == 201
    assert admin_client.post("/add_payment", json={"student_id": "demo.student@example.test", "amount": 500,
                                                   "method": "credit-card"}).status_code == 201
    assert admin_client.post("/add_payment", json={"student_id": "9999", "amount": 5, "method": "upi"}).status_code == 404
    assert admin_client.post("/add_payment", json={"student_id": str(sid), "amount": -5, "method": "upi"}).status_code == 400
    assert admin_client.post("/add_payment", json={"student_id": str(sid), "amount": 5, "method": "bitcoin"}).status_code == 400

    payments = admin_client.get("/get_payments").get_json()
    assert len(payments) == 2
    assert set(payments[0]) == {"id", "student_id", "student_name", "amount", "method", "date"}
    assert admin_client.get("/auth/get_student_reports").get_json()[0]["payment_status"] is True
    assert admin_client.get("/api/dashboard/stats").get_json()["total_revenue"] == 2000

    # deleting a student with payments works (no FK violation)
    assert admin_client.delete(f"/auth/students/{sid}").status_code == 200
    assert admin_client.get("/get_payments").get_json() == []


# ---------- courses ----------

def test_courses_crud(admin_client):
    assert admin_client.post("/add_course", json={"name": "CS"}).status_code == 400
    r = admin_client.post("/add_course", json={"name": "CS", "description": "Computing"})
    assert r.status_code == 201
    cid = r.get_json()["id"]
    assert admin_client.get("/get_courses").get_json() == [{"id": cid, "name": "CS", "description": "Computing"}]
    assert admin_client.put(f"/edit_course/{cid}", json={"name": "CS2", "description": "D"}).status_code == 200
    assert admin_client.get("/get_courses").get_json()[0]["name"] == "CS2"
    assert admin_client.delete(f"/delete_course/{cid}").status_code == 200
    assert admin_client.delete(f"/delete_course/{cid}").status_code == 404


# ---------- static frontend + hardening ----------

def test_frontend_is_served(client):
    assert client.get("/").status_code == 200
    assert client.get("/config.js").status_code == 200
    for page in ["admin/index1.html", "admin/admin-login.html", "admin/admin-dashboard.html",
                 "admin/students.css", "student/student-login.html", "student/profile.js"]:
        assert client.get("/" + page).status_code == 200, page


def test_non_frontend_files_are_not_served(client):
    for path in ["/app.py", "/settings.json", "/profile.html", "/backend/app.py", "/admin/../../backend/app.py",
                 "/admin/%2e%2e/%2e%2e/backend/app.py", "/student/../config.js/../../backend/instance/hostel.db",
                 "/legacy/frontend_mysql_prototype/app.py", "/.env", "/admin/missing.html"]:
        assert client.get(path).status_code == 404, path


def test_security_headers(client):
    r = client.get("/admin/index1.html")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"


def test_unknown_api_route_returns_json_404(client):
    r = client.get("/api/nope")
    assert r.status_code == 404 and r.is_json


def test_internal_errors_do_not_leak(app, client, monkeypatch):
    import routes.dashboard as dash

    def boom():
        raise RuntimeError("secret stack detail")

    app.view_functions["dashboard.dashboard_home"] = boom
    r = client.get("/api/dashboard/")
    assert r.status_code == 500
    assert b"secret stack detail" not in r.data
    assert b"Traceback" not in r.data


def test_cors_only_for_configured_origins(make_app):
    application = make_app(CORS_ORIGINS="https://frontend.example.test")
    c = application.test_client()
    r = c.get("/health", headers={"Origin": "https://frontend.example.test"})
    assert r.headers.get("Access-Control-Allow-Origin") == "https://frontend.example.test"
    assert r.headers.get("Access-Control-Allow-Credentials") == "true"
    r = c.get("/health", headers={"Origin": "https://evil.example.test"})
    assert "Access-Control-Allow-Origin" not in r.headers


def test_no_cors_in_production_by_default(make_app):
    application = make_app(APP_ENV="production")
    r = application.test_client().get("/health", headers={"Origin": "http://127.0.0.1:5500"})
    assert "Access-Control-Allow-Origin" not in r.headers


# ---------- upgrading a database made by the old version ----------

def test_old_database_schema_is_upgraded(tmp_path, monkeypatch):
    """Recreates the exact schema of the original backend/instance/hostel.db."""
    path = tmp_path / "old.db"
    con = sqlite3.connect(path)
    con.executescript("""
        CREATE TABLE user (id INTEGER NOT NULL, username VARCHAR(80) NOT NULL, email VARCHAR(100) NOT NULL,
            password VARCHAR(120) NOT NULL, PRIMARY KEY (id), UNIQUE (username), UNIQUE (email));
        CREATE TABLE room (id INTEGER NOT NULL, number VARCHAR(10) NOT NULL, capacity INTEGER NOT NULL, PRIMARY KEY (id));
        CREATE TABLE course (id INTEGER NOT NULL, name VARCHAR(100) NOT NULL, PRIMARY KEY (id));
        CREATE TABLE payment (id INTEGER NOT NULL, user_id INTEGER NOT NULL, amount FLOAT NOT NULL,
            PRIMARY KEY (id), FOREIGN KEY(user_id) REFERENCES user (id));
        INSERT INTO user (username, email, password) VALUES ('Legacy User', 'legacy@example.test', 'legacypass1');
        INSERT INTO room (number, capacity) VALUES ('A1', 3);
    """)
    con.commit()
    con.close()

    monkeypatch.setenv("SQLITE_PATH", str(path))
    monkeypatch.setenv("ADMIN_EMAIL", "admin@example.test")
    monkeypatch.setenv("ADMIN_PASSWORD", "admin-pass-123")
    from app import create_app
    application = create_app({"TESTING": True})

    cols = {row[1] for row in sqlite3.connect(path).execute("PRAGMA table_info(user)")}
    assert {"role", "phone", "room_preference", "address"} <= cols

    c = application.test_client()
    r = login(c, "legacy@example.test", "legacypass1")
    assert r.status_code == 200 and r.get_json()["role"] == "student"

    a = application.test_client()
    assert login(a, "admin@example.test", "admin-pass-123", "admin").status_code == 200
    assert a.get("/api/rooms/").get_json()[0]["number"] == "A1"
    assert a.post("/add_payment", json={"student_id": "legacy@example.test", "amount": 10, "method": "cash"}).status_code == 201
    assert a.post("/add_course", json={"name": "X", "description": "Y"}).status_code == 201
