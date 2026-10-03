from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from db import get_db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        role = request.form.get("role", "")
        specialization = request.form.get("specialization", "").strip()
        student_id_number = request.form.get("student_id_number", "").strip()

        if not full_name or not email or not password or role not in ("student", "medical_expert"):
            flash("Please fill in all required fields correctly.", "danger")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return redirect(url_for("auth.register"))

        db = get_db()
        existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            flash("An account with that email already exists.", "danger")
            return redirect(url_for("auth.register"))

        # Students are auto-approved; medical experts need super admin approval (RBAC gate).
        is_approved = 1 if role == "student" else 0

        db.execute(
            """INSERT INTO users
               (full_name, email, password_hash, role, specialization, student_id_number, is_approved)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                full_name,
                email,
                generate_password_hash(password),
                role,
                specialization or None,
                student_id_number or None,
                is_approved,
            ),
        )
        db.commit()

        if role == "medical_expert":
            flash(
                "Registration submitted. Your account must be approved by a super admin before you can log in.",
                "info",
            )
        else:
            flash("Registration successful. You may now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))

        if not user["is_active"]:
            flash("This account has been deactivated. Please contact the super admin.", "danger")
            return redirect(url_for("auth.login"))

        if not user["is_approved"]:
            flash("Your account is still pending approval by a super admin.", "warning")
            return redirect(url_for("auth.login"))

        session.clear()
        session["user_id"] = user["id"]
        session["full_name"] = user["full_name"]
        session["role"] = user["role"]

        flash(f"Welcome back, {user['full_name']}!", "success")
        return redirect(url_for("auth.dashboard_redirect"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/dashboard")
def dashboard_redirect():
    """Sends each role to its own dashboard - the core of the RBAC routing."""
    role = session.get("role")
    if role == "super_admin":
        return redirect(url_for("admin.dashboard"))
    elif role == "medical_expert":
        return redirect(url_for("expert.dashboard"))
    elif role == "student":
        return redirect(url_for("student.dashboard"))
    return redirect(url_for("auth.login"))
