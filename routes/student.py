from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from decorators import role_required
from db import get_db

student_bp = Blueprint("student", __name__)


@student_bp.route("/dashboard")
@role_required("student")
def dashboard():
    db = get_db()
    consultations = db.execute(
        """SELECT c.*, e.full_name AS expert_name FROM consultations c
           LEFT JOIN users e ON e.id = c.expert_id
           WHERE c.student_id = ?
           ORDER BY c.created_at DESC""",
        (session["user_id"],),
    ).fetchall()
    return render_template("student/dashboard.html", consultations=consultations)


@student_bp.route("/book", methods=["GET", "POST"])
@role_required("student")
def book():
    db = get_db()
    experts = db.execute(
        """SELECT id, full_name, specialization FROM users
           WHERE role='medical_expert' AND is_approved=1 AND is_active=1
           ORDER BY full_name ASC"""
    ).fetchall()

    if request.method == "POST":
        expert_id = request.form.get("expert_id") or None
        reason = request.form.get("reason", "").strip()
        preferred_date = request.form.get("preferred_date", "").strip()

        if not reason or not preferred_date:
            flash("Please provide a reason and a preferred date.", "danger")
            return redirect(url_for("student.book"))

        db.execute(
            "INSERT INTO consultations (student_id, expert_id, reason, preferred_date) VALUES (?, ?, ?, ?)",
            (session["user_id"], expert_id, reason, preferred_date),
        )
        db.commit()
        flash("Your consultation request has been submitted.", "success")
        return redirect(url_for("student.dashboard"))

    return render_template("student/book.html", experts=experts)


@student_bp.route("/consultation/<int:cid>")
@role_required("student")
def consultation(cid):
    db = get_db()
    record = db.execute(
        """SELECT c.*, e.full_name AS expert_name FROM consultations c
           LEFT JOIN users e ON e.id = c.expert_id
           WHERE c.id = ? AND c.student_id = ?""",
        (cid, session["user_id"]),
    ).fetchone()

    if not record:
        flash("Consultation not found.", "danger")
        return redirect(url_for("student.dashboard"))

    return render_template("student/consultation.html", c=record)


@student_bp.route("/consultation/<int:cid>/cancel")
@role_required("student")
def cancel(cid):
    db = get_db()
    db.execute(
        """UPDATE consultations SET status='cancelled', updated_at=CURRENT_TIMESTAMP
           WHERE id=? AND student_id=? AND status='pending'""",
        (cid, session["user_id"]),
    )
    db.commit()
    flash("Consultation request cancelled.", "info")
    return redirect(url_for("student.dashboard"))
