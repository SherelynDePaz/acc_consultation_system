import os
import sqlite3

from flask import current_app, g
from werkzeug.security import generate_password_hash


def get_db():
    """Open a new database connection for the current request context."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Create the database file and tables from schema.sql."""
    os.makedirs(os.path.dirname(app.config["DATABASE"]), exist_ok=True)
    with app.app_context():
        db = get_db()
        with open(app.config["SCHEMA_PATH"], "r") as f:
            db.executescript(f.read())
        db.commit()
    print("[ACC Consultation System] Database initialized.")


def seed_super_admin(app):
    """Ensure at least one super admin account exists."""
    with app.app_context():
        db = get_db()
        existing = db.execute(
            "SELECT id FROM users WHERE role = 'super_admin' LIMIT 1"
        ).fetchone()
        if existing is None:
            db.execute(
                """INSERT INTO users
                   (full_name, email, password_hash, role, is_approved, is_active)
                   VALUES (?, ?, ?, 'super_admin', 1, 1)""",
                (
                    "System Administrator",
                    "admin@acc.edu",
                    generate_password_hash("Admin@123"),
                ),
            )
            db.commit()
            print("=" * 60)
            print(" DEFAULT SUPER ADMIN ACCOUNT CREATED")
            print(" Email:    admin@acc.edu")
            print(" Password: Admin@123")
            print(" Please log in and change this password/user in production.")
            print("=" * 60)
