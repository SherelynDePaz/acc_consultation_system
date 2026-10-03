import os

from flask import Flask, redirect, render_template, session, url_for

import db as database
from config import Config
from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.expert import expert_bp
from routes.student import student_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.teardown_appcontext(database.close_db)

    # Blueprints double as the RBAC boundary: each role only ever reaches
    # the routes inside its own blueprint (enforced by decorators.py).
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(expert_bp, url_prefix="/expert")
    app.register_blueprint(student_bp, url_prefix="/student")

    @app.route("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("auth.dashboard_redirect"))
        return render_template("index.html")

    @app.context_processor
    def inject_user():
        return {
            "current_user_name": session.get("full_name"),
            "current_user_role": session.get("role"),
        }

    return app


app = create_app()

if __name__ == "__main__":
    db_exists = os.path.exists(app.config["DATABASE"])
    if not db_exists:
        database.init_db(app)
    database.seed_super_admin(app)
    app.run(debug=True)
