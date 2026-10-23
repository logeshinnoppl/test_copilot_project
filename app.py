"""Flask app for the contact submission form."""
import hmac
import os
from functools import wraps

from flask import Flask, Response, redirect, render_template, request, url_for

import db
import validation

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instance", "contact.db")


def create_app(db_path=None):
    """Build and configure the Flask app.

    Fails fast if ADMIN_USERNAME/ADMIN_PASSWORD are not set, since those
    credentials gate the admin submissions page.
    """
    admin_username = os.environ.get("ADMIN_USERNAME")
    admin_password = os.environ.get("ADMIN_PASSWORD")
    if not admin_username or not admin_password:
        raise RuntimeError(
            "ADMIN_USERNAME and ADMIN_PASSWORD environment variables must be set "
            "before starting the app (see .env.example)."
        )

    app = Flask(__name__)
    app.config["DB_PATH"] = db_path or DB_PATH
    app.config["ADMIN_USERNAME"] = admin_username
    app.config["ADMIN_PASSWORD"] = admin_password

    db.init_db(app.config["DB_PATH"])

    def require_basic_auth(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            auth = request.authorization
            valid = (
                auth is not None
                and hmac.compare_digest(auth.username or "", app.config["ADMIN_USERNAME"])
                and hmac.compare_digest(auth.password or "", app.config["ADMIN_PASSWORD"])
            )
            if not valid:
                return Response(
                    "Authentication required.",
                    401,
                    {"WWW-Authenticate": 'Basic realm="Admin"'},
                )
            return view(*args, **kwargs)

        return wrapped

    @app.get("/")
    def index():
        return redirect(url_for("contact"))

    @app.get("/contact")
    def contact():
        empty_values = {field: "" for field in validation.FIELDS}
        return render_template("contact.html", errors={}, values=empty_values)

    @app.post("/submit")
    def submit():
        data = request.form
        errors = validation.validate_submission(data)
        values = {field: (data.get(field) or "") for field in validation.FIELDS}
        if errors:
            return render_template("contact.html", errors=errors, values=values), 200
        try:
            db.insert_submission(
                app.config["DB_PATH"],
                values["name"].strip(),
                values["email"].strip(),
                values["subject"].strip(),
                values["message"].strip(),
            )
        except Exception:
            app.logger.exception("Failed to store contact submission")
            form_error = {"form": "Something went wrong while saving your message. Please try again later."}
            return render_template("contact.html", errors=form_error, values=values), 500
        return redirect(url_for("thank_you"))

    @app.get("/thank-you")
    def thank_you():
        return render_template("thank_you.html")

    @app.get("/admin/submissions")
    @require_basic_auth
    def admin_submissions():
        submissions = db.fetch_all_submissions(app.config["DB_PATH"])
        return render_template("admin_submissions.html", submissions=submissions)

    return app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    db_path = os.environ.get("CONTACT_DB_PATH")
    create_app(db_path=db_path).run(debug=False, port=port)
