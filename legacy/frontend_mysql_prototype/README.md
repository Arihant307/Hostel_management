# Legacy MySQL prototype (not used)

These files were originally in `frontend/`. They are an early prototype of the
API written against MySQL (`flask_mysqldb`). They were **never wired up** to the
current application:

- `app.py` concatenates several separate Flask apps into one file; the first
  routes reference `mysql` before it is defined, and the file redefines `app`
  three times, so it cannot run as-is.
- The `*_app.py` files are fully commented out.
- `flask_mysqldb`, `MySQLdb` and `flask_mail` are not installed by the project.

The working backend is `backend/app.py` (Flask + SQLAlchemy). Every endpoint
contract the frontend still uses from this prototype (`/add_payment`,
`/get_payments`, `/get_courses`, `/add_course`, `/edit_course/<id>`,
`/delete_course/<id>`) has been re-implemented there.

The files were moved here, not deleted. That keeps them out of the
deployed frontend folder, which would otherwise publish them as public static
files. Delete this folder whenever you no longer need it for reference.
