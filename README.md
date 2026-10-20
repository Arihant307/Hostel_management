# HostelHub – Hostel Management System

A Flask + HTML/CSS/JavaScript hostel management system with an **admin portal**
(rooms, students, payments, reports, courses) and a **student portal**
(registration, login, profile).

```
backend/             Flask API (entry point: backend/app.py)
  routes/            auth, rooms, dashboard, payments, courses blueprints
  models.py          SQLAlchemy models (User, Room, Course, Payment)
  config.py          all settings come from environment variables
  db_setup.py        creates tables / upgrades old databases / creates admin
  tests/             pytest suite
frontend/            static site (served by Flask in production)
  config.js          API base URL + shared fetch helpers (loaded first)
  index.html         redirects to admin/index1.html (the home page)
  admin/  student/   the two portals
legacy/              old unused MySQL prototype, kept for reference only
render.yaml          Render Blueprint (free web service + free Postgres)
```

## Architecture choice: one service

Flask serves both the API and the frontend files from **one Render web
service**. One service was chosen over two because:

* Login uses an HttpOnly session cookie. When the page and API share an origin,
  the cookie works with the default `SameSite=Lax`. Two `*.onrender.com`
  services count as *different sites* (`onrender.com` is on the Public Suffix
  List). That would need `SameSite=None` third-party cookies, which Safari and
  some Chrome configurations block.
* There is no CORS to configure, and only one URL to share.
* It uses one free instance instead of two, and only one service has to wake up
  from sleep.

Only `frontend/index.html`, `frontend/config.js`, and files inside
`frontend/admin/` and `frontend/student/` with web extensions are served.
Python files, databases and `.env` are never reachable over HTTP.

A separately hosted frontend is still supported (see
[Separate frontend](#optional-separate-frontend-static-site)).

---

## Local setup

Requirements: Python 3.13 (3.11+ works). Commands are run from the project root.

**Windows (PowerShell)**
```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
copy ..\.env.example ..\.env      # then edit ..\.env
python app.py
```

**macOS / Linux**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp ../.env.example ../.env        # then edit ../.env
python app.py
```

Open <http://127.0.0.1:5000/>. The SQLite database is created automatically
at `backend/instance/hostel.db` on first start. No manual step is needed.

**Create your admin account** (there are no built-in credentials). Use either
method:

* Set `ADMIN_EMAIL` and `ADMIN_PASSWORD` (8+ characters) in `.env` and restart.
* Or run `flask --app app create-admin` from `backend/`, which prompts for
  email and password.

If the email already belongs to an account, that account is promoted to admin
and its password is left unchanged.

**VS Code Live Server** still works. Run `python app.py`, then open the
frontend with Live Server (port 5500/5501). `config.js` detects this and calls
`http://<same host>:5000`, and those origins are allowed by CORS in
development. Use the same hostname for both (`127.0.0.1` *or* `localhost`).

**Existing local databases** from the earlier version are upgraded
automatically on start-up: missing columns such as `user.role` are added.
Old plain-text passwords still work and are re-hashed at that user's next
login.

### Run the tests
```bash
cd backend
python -m pytest -q
```

---

## Upload to GitHub

The project folder had no Git repository when it was received. These commands
create one and push it. Replace the URL with your own **empty** GitHub repo.

```bash
cd "hostel management system final"
git init
git add .
git status            # confirm: no .venv/, no .env, no *.db, no __pycache__/
git commit -m "Prepare Hostel Management System for Render deployment"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

If you already have a repository for this project, copy the updated files into
it instead. Then run `git add . && git status && git commit -m "..." && git push`.
Do **not** run `git init` again in that case.

`.gitignore` excludes `.venv/`, `venv/`, `__pycache__/`, `.env`, all `*.db`
files and `instance/` folders. If a database or `.venv` was committed before,
remove it from Git without deleting it locally:
```bash
git rm -r --cached .venv instance backend/instance backend/hostel.db
git commit -m "Stop tracking local env and databases"
```

---

## Deploying to Render

### Option A: Blueprint (recommended)
1. Push the repo to GitHub (above).
2. Render Dashboard → **New → Blueprint** → connect your GitHub account → pick
   the repo. Render reads `render.yaml`.
3. When prompted, enter `ADMIN_EMAIL` and `ADMIN_PASSWORD` (choose your own;
   the password needs 8+ characters).
4. Click **Apply**. Render creates the free Postgres database and the web
   service, and connects them.
5. When the deploy finishes, open `https://<service-name>.onrender.com/health`.
   It should return `{"database":"ok","status":"ok"}`.

> Render allows **one free Postgres database per workspace**. If you already
> have one, creating the Blueprint's database will fail. Delete the old one first, or use Option B.

### Option B: Manual web service
Render Dashboard → **New → Web Service** → connect the GitHub repo:

| Setting | Value |
|---|---|
| Runtime / language | Python 3 |
| Branch | `main` |
| Root Directory | *(leave empty: repository root)* |
| Build Command | `pip install -r backend/requirements.txt` |
| Start Command | `gunicorn --chdir backend --preload --workers 2 --timeout 60 --bind 0.0.0.0:$PORT app:app` |
| Instance type | Free |
| Health Check Path | `/health` (under *Advanced*) |

Python 3.13 is selected by the `.python-version` file. Render's current
default is 3.14.

Then add the environment variables below under **Environment**. For
persistent data, also create **New → Postgres** (Free) and paste its
**Internal Database URL** into `DATABASE_URL`.

### Environment variables

Set these in Render → your service → **Environment** (or in `.env` locally).

| Variable | Required | Value |
|---|---|---|
| `APP_ENV` | yes | `production` |
| `SECRET_KEY` | yes | Long random string (Blueprint generates one). The app refuses to start in production without it. |
| `DATABASE_URL` | recommended | Postgres *Internal* URL (Blueprint fills it in). If empty, SQLite is used (data is lost, see below). |
| `ADMIN_EMAIL` | first deploy | Admin login email |
| `ADMIN_PASSWORD` | first deploy | Admin password, 8+ chars. Only used when the account is first created. |
| `ADMIN_NAME` | no | Display name for the admin (default "Administrator") |
| `CORS_ORIGINS` | no | Only for a separately hosted frontend, e.g. `https://hostel-frontend.onrender.com` |
| `SESSION_COOKIE_SAMESITE` | no | `Lax` (default). `None` only for a separate frontend. |
| `SESSION_LIFETIME_HOURS` | no | Default `8` |

`PORT` is provided by Render automatically. Never commit real values; only
`.env.example` (placeholders) belongs in Git.

---

## Database and persistence

| | SQLite (default when `DATABASE_URL` is empty) | Render free Postgres |
|---|---|---|
| Cost | Free | Free |
| Data survives restart/redeploy | **No** | Yes |
| Limits | n/a | 1 GB, **expires 30 days after creation**, 14-day grace period to upgrade, then deleted; no backups |

**SQLite on Render is temporary.** Render's free web services have an
ephemeral filesystem, so the SQLite file is wiped on every redeploy, restart,
**and spin-down after 15 minutes without traffic**. The tables (and the admin
account from `ADMIN_EMAIL`/`ADMIN_PASSWORD`) are recreated automatically, so
the app keeps working, but students, rooms and payments disappear. That is
acceptable only for a quick throw-away demo.

**Free Postgres** (what `render.yaml` sets up) keeps data across restarts, but
Render expires it **30 days** after creation. Before then, you can do one of
the following:
* Upgrade it to a paid plan (from about $6/month on Render's Basic tier;
  check current pricing).
* Delete it, create a new free one, and update `DATABASE_URL`. The data is
  lost, but the tables are recreated automatically on the next start.
* Point `DATABASE_URL` at another free Postgres provider (e.g. Neon or
  Supabase). No code changes are needed; use a `postgresql://` URL.

The same models work on both databases. The app converts `postgres://` URLs to
`postgresql://` automatically, quotes the `user` table name for Postgres, and
uses a 255-character password column for hashes. There is no data migration
from your local SQLite file: production starts with an empty database.

Schema changes: `db_setup.py` creates missing tables and adds missing columns
on start-up. Flask-Migrate is installed if you later need full Alembic
migrations (`flask --app app db init`, from `backend/`).

---

## Optional: separate frontend (Static Site)

Only use this if you specifically need it; the single service above is simpler.

1. In `frontend/config.js`, set
   `CONFIGURED_API_BASE_URL = "https://<api-service>.onrender.com"`.
2. Render → **New → Static Site** → same repo. Leave **Build Command** empty
   and set **Publish Directory** to `frontend`.
3. On the API service, set `CORS_ORIGINS=https://<static-site>.onrender.com`,
   `SESSION_COOKIE_SAMESITE=None` (requires HTTPS, enabled automatically), and
   optionally `SERVE_FRONTEND=false`.
4. Browsers that block third-party cookies (Safari by default) will not keep
   users logged in with this setup. This is why the single-service setup is
   recommended.

---

## API overview

| Method & path | Access | Purpose |
|---|---|---|
| `GET /health` | public | Health check (`{"status":"ok","database":"ok"}`) |
| `POST /auth/register` | public | Student registration (`fullname,email,password`) |
| `POST /auth/login` | public | Login (`email,password`, optional `role:"admin"`) → sets session cookie |
| `POST /auth/logout` | any | End session |
| `GET /auth/me` | logged in | Current user |
| `GET /auth/profile`, `POST /auth/profile/update` | logged in | Own profile |
| `GET/POST /auth/students`, `PUT/DELETE /auth/students/<id>` | admin | Student management |
| `GET /auth/get_student_reports` | admin | Report table |
| `GET /api/rooms/` | logged in | Room list (with type and occupancy) |
| `POST /api/rooms/add` | admin | Add room |
| `GET /api/rooms/get_room_occupancy` | admin | Chart data |
| `GET /api/dashboard/stats` | admin | Dashboard overview numbers |
| `POST /add_payment`, `GET /get_payments` | admin | Payments (student ID or email) |
| `GET /get_courses`, `POST /add_course`, `PUT /edit_course/<id>`, `DELETE /delete_course/<id>` | admin | Courses |

All authorization is enforced on the server. Hiding links in the frontend is
only cosmetic.

## Known limitations

These pages are UI-only, with no backend. They were kept as they were, not
removed:
* **Student "Book a Room"** shows a success alert but stores nothing.
* **Attendance**, **Access Log**, **Room Details**, **Edit Room**,
  **Admin Profile** and the **admin dashboard "Recent Bookings"** card display
  hardcoded sample data.
* **Forgot password** and **OTP login** (`otp-login.js`, not loaded by any
  page) need an email service; there are no backend endpoints for them.

Other gaps:
* `admin.html` / `manage-users.html` reference `admin.css`, which was never in
  the project, so they render unstyled.
* **Manage Courses** works but is not linked from the dashboard menu. Open
  `/admin/manage-courses.html` directly.
* The student registration "Room preference" is not stored. The
  `room_preference` column holds the room number an admin assigns on the
  Students page, as in the original code.
* Rooms can be added but not edited or deleted (no UI existed for it).
* Free Render services sleep after 15 idle minutes; the first request then
  takes about a minute.
* An old local SQLite file keeps its original `UNIQUE(username)` constraint, so
  two students with the same name cannot register there. Fresh databases do
  not have this restriction.
