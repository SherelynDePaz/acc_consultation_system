from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from decorators import role_required
from db import get_db

expert_bp = Blueprint("expert", __name__)


@expert_bp.route("/dashboard")
@role_required("medical_expert")
def dashboard():
    db = get_db()
    expert_id = session["user_id"]

    pending = db.execute(
        """SELECT c.*, s.full_name AS student_name FROM consultations c
           JOIN users s ON s.id = c.student_id
           WHERE c.expert_id = ? AND c.status = 'pending'
           ORDER BY c.preferred_date ASC""",
        (expert_id,),
    ).fetchall()

    upcoming = db.execute(
        """SELECT c.*, s.full_name AS student_name FROM consultations c
           JOIN users s ON s.id = c.student_id
           WHERE c.expert_id = ? AND c.status = 'accepted'
           ORDER BY c.preferred_date ASC""",
        (expert_id,),
    ).fetchall()

    unassigned = db.execute(
        """SELECT c.*, s.full_name AS student_name FROM consultations c
           JOIN users s ON s.id = c.student_id
           WHERE c.expert_id IS NULL AND c.status = 'pending'
           ORDER BY c.created_at ASC"""
    ).fetchall()

    return render_template(
        "expert/dashboard.html", pending=pending, upcoming=upcoming, unassigned=unassigned
    )


@expert_bp.route("/consultation/<int:cid>/claim")
@role_required("medical_expert")
def claim(cid):
    db = get_db()
    db.execute(
        "UPDATE consultations SET expert_id = ? WHERE id = ? AND expert_id IS NULL",
        (session["user_id"], cid),
    )
    db.commit()
    flash("Consultation request claimed. Please review and respond.", "success")
    return redirect(url_for("expert.dashboard"))


@expert_bp.route("/consultation/<int:cid>", methods=["GET", "POST"])
@role_required("medical_expert")
def consultation(cid):
    db = get_db()
    record = db.execute(
        """SELECT c.*, s.full_name AS student_name, s.email AS student_email
           FROM consultations c JOIN users s ON s.id = c.student_id
           WHERE c.id = ?""",
        (cid,),
    ).fetchone()

    if not record or record["expert_id"] != session["user_id"]:
        flash("Consultation not found or not assigned to you.", "danger")
        return redirect(url_for("expert.dashboard"))

    if request.method == "POST":
        action = request.form.get("action")
        notes = request.form.get("expert_notes", "").strip()

        if action == "accept":
            db.execute(
                "UPDATE consultations SET status='accepted', expert_notes=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (notes, cid),
            )
            flash("Consultation accepted.", "success")
        elif action == "decline":
            db.execute(
                "UPDATE consultations SET status='declined', expert_notes=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (notes, cid),
            )
            flash("Consultation declined.", "info")
        elif action == "complete":
            db.execute(
                "UPDATE consultations SET status='completed', expert_notes=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (notes, cid),
            )
            flash("Consultation marked as completed.", "success")

        db.commit()
        return redirect(url_for("expert.consultation", cid=cid))

    return render_template("expert/consultation.html", c=record)
