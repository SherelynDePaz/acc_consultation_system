from flask import Blueprint, flash, redirect, render_template, request, url_for

from decorators import role_required
from db import get_db

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/dashboard")
@role_required("super_admin")
def dashboard():
    db = get_db()
    stats = {
        "total_students": db.execute(
            "SELECT COUNT(*) c FROM users WHERE role='student'"
        ).fetchone()["c"],
        "total_experts": db.execute(
            "SELECT COUNT(*) c FROM users WHERE role='medical_expert' AND is_approved=1"
        ).fetchone()["c"],
        "pending_experts": db.execute(
            "SELECT COUNT(*) c FROM users WHERE role='medical_expert' AND is_approved=0"
        ).fetchone()["c"],
        "total_consultations": db.execute(
            "SELECT COUNT(*) c FROM consultations"
        ).fetchone()["c"],
        "pending_consultations": db.execute(
            "SELECT COUNT(*) c FROM consultations WHERE status='pending'"
        ).fetchone()["c"],
    }
    recent = db.execute(
        """SELECT c.*, s.full_name AS student_name, e.full_name AS expert_name
           FROM consultations c
           JOIN users s ON s.id = c.student_id
           LEFT JOIN users e ON e.id = c.expert_id
           ORDER BY c.created_at DESC LIMIT 5"""
    ).fetchall()
    return render_template("admin/dashboard.html", stats=stats, recent=recent)


@admin_bp.route("/experts")
@role_required("super_admin")
def manage_experts():
    db = get_db()
    experts = db.execute(
        "SELECT * FROM users WHERE role='medical_expert' ORDER BY is_approved ASC, created_at DESC"
    ).fetchall()
    return render_template("admin/manage_experts.html", experts=experts)


@admin_bp.route("/experts/<int:user_id>/approve")
@role_required("super_admin")
def approve_expert(user_id):
    db = get_db()
    db.execute(
        "UPDATE users SET is_approved = 1 WHERE id = ? AND role = 'medical_expert'",
        (user_id,),
    )
    db.commit()
    flash("Medical expert account approved.", "success")
    return redirect(url_for("admin.manage_experts"))


@admin_bp.route("/experts/<int:user_id>/reject")
@role_required("super_admin")
def reject_expert(user_id):
    db = get_db()
    db.execute(
        "DELETE FROM users WHERE id = ? AND role = 'medical_expert' AND is_approved = 0",
        (user_id,),
    )
    db.commit()
    flash("Medical expert application rejected and removed.", "info")
    return redirect(url_for("admin.manage_experts"))


@admin_bp.route("/users/<int:user_id>/toggle-active")
@role_required("super_admin")
def toggle_active(user_id):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if user and user["role"] != "super_admin":
        new_status = 0 if user["is_active"] else 1
        db.execute("UPDATE users SET is_active = ? WHERE id = ?", (new_status, user_id))
        db.commit()
        flash("User account status updated.", "success")
    return redirect(request.referrer or url_for("admin.dashboard"))


@admin_bp.route("/students")
@role_required("super_admin")
def manage_students():
    db = get_db()
    students = db.execute(
        "SELECT * FROM users WHERE role='student' ORDER BY created_at DESC"
    ).fetchall()
    return render_template("admin/manage_students.html", students=students)


@admin_bp.route("/consultations")
@role_required("super_admin")
def all_consultations():
    db = get_db()
    consultations = db.execute(
        """SELECT c.*, s.full_name AS student_name, e.full_name AS expert_name
           FROM consultations c
           JOIN users s ON s.id = c.student_id
           LEFT JOIN users e ON e.id = c.expert_id
           ORDER BY c.created_at DESC"""
    ).fetchall()
    return render_template("admin/all_consultations.html", consultations=consultations)
