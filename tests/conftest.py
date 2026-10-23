import base64

import pytest

import app as app_module


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_USERNAME", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "secret")
    db_path = str(tmp_path / "contact.db")
    flask_app = app_module.create_app(db_path=db_path)
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as test_client:
        yield test_client


def basic_auth_header(username, password):
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}
