import sqlite3

import pytest

import app as app_module
from tests.conftest import basic_auth_header

VALID_FORM = {
    "name": "Alice",
    "email": "alice@example.com",
    "subject": "Hello",
    "message": "This is a test message.",
}


def test_create_app_fails_fast_without_admin_env_vars(tmp_path, monkeypatch):
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    with pytest.raises(RuntimeError):
        app_module.create_app(db_path=str(tmp_path / "contact.db"))


def test_get_contact_renders_required_fields(client):
    resp = client.get("/contact")
    assert resp.status_code == 200
    for field in (b"name", b"email", b"subject", b"message"):
        assert field in resp.data
    assert b"required" in resp.data


def test_post_submit_valid_redirects_and_persists(client):
    resp = client.post("/submit", data=VALID_FORM)
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/thank-you"

    follow = client.get(resp.headers["Location"])
    assert follow.status_code == 200
    assert b"Thank you" in follow.data


def test_post_submit_missing_field_does_not_persist(client):
    data = dict(VALID_FORM, name="")
    resp = client.post("/submit", data=data)
    assert resp.status_code == 200
    assert b"required" in resp.data.lower() or b"This field is required" in resp.data

    admin_resp = client.get("/admin/submissions", headers=basic_auth_header("admin", "secret"))
    assert b"No submissions yet" in admin_resp.data


def test_post_submit_invalid_email_does_not_persist(client):
    data = dict(VALID_FORM, email="not-an-email")
    resp = client.post("/submit", data=data)
    assert resp.status_code == 200
    assert b"valid email" in resp.data

    admin_resp = client.get("/admin/submissions", headers=basic_auth_header("admin", "secret"))
    assert b"No submissions yet" in admin_resp.data


def test_post_submit_db_failure_shows_generic_error_without_leaking_details(client, monkeypatch):
    def raise_db_error(*args, **kwargs):
        raise sqlite3.OperationalError("disk I/O error")

    monkeypatch.setattr(app_module.db, "insert_submission", raise_db_error)

    resp = client.post("/submit", data=VALID_FORM)

    assert resp.status_code == 500
    assert b"Something went wrong" in resp.data
    assert b"Traceback" not in resp.data
    assert b"OperationalError" not in resp.data


def test_admin_requires_auth_rejects_missing_and_wrong_credentials(client):
    resp = client.get("/admin/submissions")
    assert resp.status_code == 401

    resp = client.get("/admin/submissions", headers=basic_auth_header("admin", "wrong"))
    assert resp.status_code == 401


def test_admin_shows_empty_state_when_no_submissions(client):
    resp = client.get("/admin/submissions", headers=basic_auth_header("admin", "secret"))
    assert resp.status_code == 200
    assert b"No submissions yet" in resp.data


def test_admin_lists_submissions_newest_first(client):
    client.post("/submit", data=dict(VALID_FORM, name="First"))
    client.post("/submit", data=dict(VALID_FORM, name="Second"))

    resp = client.get("/admin/submissions", headers=basic_auth_header("admin", "secret"))
    assert resp.status_code == 200
    body = resp.data.decode()
    assert body.index("Second") < body.index("First")
