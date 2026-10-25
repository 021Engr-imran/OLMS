"""OLMS Release 1: run python app.py --create-staff, then python app.py."""
from pathlib import Path
from functools import wraps
import getpass
import secrets
import sqlite3
import sys
from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE = Path(__file__).resolve().parent
DATA = BASE / "instance"
DATA.mkdir(exist_ok=True)
SECRET_FILE = DATA / "secret.key"
if not SECRET_FILE.exists():
    SECRET_FILE.write_text(secrets.token_hex(32), encoding="utf-8")
app = Flask(__name__)
app.config.update(SECRET_KEY=SECRET_FILE.read_text().strip(),
    DATABASE=str(DATA / "olms.sqlite3"), SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax", MAX_CONTENT_LENGTH=65536)

SCHEMA = """
CREATE TABLE IF NOT EXISTS staff (
 id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE COLLATE NOCASE,
 password_hash TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS books (
 id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, author TEXT NOT NULL,
 edition TEXT NOT NULL DEFAULT '', active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1)));
CREATE TABLE IF NOT EXISTS copies (
 id INTEGER PRIMARY KEY AUTOINCREMENT, book_id INTEGER NOT NULL REFERENCES books(id),
 status TEXT NOT NULL DEFAULT 'available' CHECK(status IN ('available','on_loan')));
CREATE TABLE IF NOT EXISTS members (
 id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
 active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1)));
"""

def db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"], timeout=10)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()

def init_db():
    db().executescript(SCHEMA)
    db().commit()

with app.app_context():
    init_db()

def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(32)
    return session["csrf"]
app.jinja_env.globals["csrf_token"] = csrf_token

@app.before_request
def protect_forms():
    if request.method == "POST":
        expected = session.get("csrf", "")
        supplied = request.form.get("csrf_token", "")
        if not expected or not secrets.compare_digest(expected.encode(), supplied.encode()):
            abort(400, "Form expired. Reload the page and try again.")

def login_required(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        if "staff_id" not in session:
            return redirect(url_for("login"))
        return function(*args, **kwargs)
    return wrapped

def field(name, required=True, maximum=160):
    value = request.form.get(name, "").strip()
    if required and not value:
        raise ValueError(f"{name.title()} is required.")
    if len(value) > maximum:
        raise ValueError(f"{name.title()} must be {maximum} characters or fewer.")
    return value

def copy_count():
    try:
        count = int(request.form.get("count", "1"))
    except ValueError:
        raise ValueError("Copy quantity must be a whole number.")
    if not 1 <= count <= 100:
        raise ValueError("Add between 1 and 100 copies at a time.")
    return count

def get_book(book_id):
    row = db().execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
    if row is None:
        abort(404)
    return row

def get_member(member_id):
    row = db().execute("SELECT * FROM members WHERE id=?", (member_id,)).fetchone()
    if row is None:
        abort(404)
    return row

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        staff = db().execute("SELECT * FROM staff WHERE username=?",
                            (request.form.get("username", "").strip(),)).fetchone()
        if staff and check_password_hash(staff["password_hash"], request.form.get("password", "")):
            session.clear()
            session.update(staff_id=staff["id"], username=staff["username"])
            return redirect(url_for("catalogue"))
        flash("Incorrect username or password.")
    return render_template("login.html", title="Staff login")

@app.post("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.get("/")
@login_required
def catalogue():
    query = request.args.get("q", "").strip()
    inactive = request.args.get("inactive") == "1"
    books = db().execute("""
      SELECT b.*, (SELECT COUNT(*) FROM copies c WHERE c.book_id=b.id) AS total,
      (SELECT COUNT(*) FROM copies c WHERE c.book_id=b.id
       AND c.status='available' AND b.active=1) AS available
      FROM books b WHERE (?=1 OR b.active=1)
      AND (?='' OR instr(lower(b.title),lower(?))>0 OR instr(lower(b.author),lower(?))>0)
      ORDER BY b.id DESC
    """, (int(inactive), query, query, query)).fetchall()
    return render_template("catalogue.html", title="Book catalogue",
                           books=books, query=query, include_inactive=inactive)

@app.route("/books/add", methods=["GET", "POST"])
@login_required
def add_book():
    if request.method == "POST":
        try:
            title, author = field("title"), field("author")
            edition, count = field("edition", False, 60), copy_count()
            with db():
                cursor = db().execute("INSERT INTO books(title,author,edition) VALUES(?,?,?)",
                                      (title, author, edition))
                book_id = cursor.lastrowid
                db().executemany("INSERT INTO copies(book_id) VALUES(?)", [(book_id,)] * count)
            flash(f"Book B-{book_id} registered with {count} physical copies.")
            return redirect(url_for("book_details", book_id=book_id))
        except ValueError as error:
            flash(str(error))
    return render_template("add_book.html", title="Register a book")

@app.route("/books/<int:book_id>", methods=["GET", "POST"])
@login_required
def book_details(book_id):
    book = get_book(book_id)
    if request.method == "POST":
        try:
            title, author = field("title"), field("author")
            edition = field("edition", False, 60)
            with db():
                db().execute("UPDATE books SET title=?,author=?,edition=? WHERE id=?",
                             (title, author, edition, book_id))
            flash("Book details updated. Book and copy IDs are unchanged.")
            return redirect(url_for("book_details", book_id=book_id))
        except ValueError as error:
            flash(str(error))
    copies = db().execute("SELECT * FROM copies WHERE book_id=? ORDER BY id", (book_id,)).fetchall()
    return render_template("book_details.html", title=f"Book B-{book_id}", book=book, copies=copies)

@app.post("/books/<int:book_id>/status")
@login_required
def book_status(book_id):
    get_book(book_id)
    active = request.form.get("active")
    if active not in ("0", "1"):
        abort(400)
    with db():
        db().execute("UPDATE books SET active=? WHERE id=?", (int(active), book_id))
    flash("Book status updated. Existing records were preserved.")
    return redirect(url_for("book_details", book_id=book_id))

@app.post("/books/<int:book_id>/copies")
@login_required
def add_copies(book_id):
    book = get_book(book_id)
    if not book["active"]:
        flash("Reactivate the book before adding copies.")
        return redirect(url_for("book_details", book_id=book_id))
    try:
        count = copy_count()
        with db():
            db().executemany("INSERT INTO copies(book_id) VALUES(?)", [(book_id,)] * count)
        flash(f"{count} new physical copies added.")
    except ValueError as error:
        flash(str(error))
    return redirect(url_for("book_details", book_id=book_id))

@app.route("/members", methods=["GET", "POST"])
@login_required
def members():
    if request.method == "POST":
        try:
            name = field("name")
            active = request.form.get("active", "1")
            if active not in ("0", "1"):
                raise ValueError("Choose Active or Inactive.")
            with db():
                cursor = db().execute("INSERT INTO members(name,active) VALUES(?,?)", (name, int(active)))
            flash(f"Member M-{cursor.lastrowid} registered.")
            return redirect(url_for("members"))
        except ValueError as error:
            flash(str(error))
    rows = db().execute("SELECT * FROM members ORDER BY id DESC").fetchall()
    return render_template("members.html", title="Library members", rows=rows)

@app.post("/members/<int:member_id>/status")
@login_required
def member_status(member_id):
    get_member(member_id)
    active = request.form.get("active")
    if active not in ("0", "1"):
        abort(400)
    with db():
        db().execute("UPDATE members SET active=? WHERE id=?", (int(active), member_id))
    flash("Member status updated.")
    return redirect(url_for("members"))

@app.get("/members/<int:member_id>/eligibility")
@login_required
def eligibility(member_id):
    return render_template("eligibility.html", title="Member eligibility", member=get_member(member_id))

def create_staff():
    print("Create a staff account. Password typing is hidden.")
    username = input("Username: ").strip()
    if not username or len(username) > 80:
        raise SystemExit("Username must contain 1 to 80 characters.")
    password = getpass.getpass("Password (at least 8 characters): ")
    confirmation = getpass.getpass("Repeat password: ")
    if len(password) < 8 or password != confirmation:
        raise SystemExit("Passwords must match and contain at least 8 characters. Try again.")
    with app.app_context():
        try:
            with db():
                db().execute("INSERT INTO staff(username,password_hash) VALUES(?,?)",
                             (username, generate_password_hash(password)))
        except sqlite3.IntegrityError:
            raise SystemExit("Username already exists. Choose another.")
    print("Staff account created. Run: python app.py")

if __name__ == "__main__":
    if sys.argv[1:] == ["--create-staff"]:
        create_staff()
    elif sys.argv[1:]:
        raise SystemExit("Usage: python app.py [--create-staff]")
    else:
        with app.app_context():
            if not db().execute("SELECT COUNT(*) FROM staff").fetchone()[0]:
                raise SystemExit("Create your account first: python app.py --create-staff")
        print("Open http://127.0.0.1:5000 in your browser.")
        app.run(host="127.0.0.1", port=5000, debug=False)
