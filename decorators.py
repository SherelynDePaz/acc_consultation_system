from functools import wraps

from flask import flash, redirect, session, url_for


def login_required(f):
    """Require any authenticated user."""

    @wraps(f)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return wrapped


def role_required(*roles):
    """Require the logged-in user to hold one of the given roles (RBAC gate)."""

    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("auth.login"))
            if session.get("role") not in roles:
                flash("You do not have permission to access that page.", "danger")
                return redirect(url_for("auth.dashboard_redirect"))
            return f(*args, **kwargs)

        return wrapped

    return decorator
