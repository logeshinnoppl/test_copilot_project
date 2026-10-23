import db


def test_insert_and_fetch(tmp_path):
    db_path = str(tmp_path / "contact.db")
    db.init_db(db_path)

    db.insert_submission(db_path, "Alice", "alice@example.com", "Hi", "Hello")

    rows = db.fetch_all_submissions(db_path)
    assert len(rows) == 1
    assert rows[0]["name"] == "Alice"
    assert rows[0]["email"] == "alice@example.com"
    assert rows[0]["subject"] == "Hi"
    assert rows[0]["message"] == "Hello"
    assert rows[0]["created_at"]


def test_fetch_empty_table_returns_empty_list(tmp_path):
    db_path = str(tmp_path / "contact.db")
    db.init_db(db_path)

    rows = db.fetch_all_submissions(db_path)
    assert rows == []


def test_fetch_orders_newest_first(tmp_path):
    db_path = str(tmp_path / "contact.db")
    db.init_db(db_path)

    db.insert_submission(db_path, "First", "first@example.com", "S1", "M1")
    db.insert_submission(db_path, "Second", "second@example.com", "S2", "M2")

    rows = db.fetch_all_submissions(db_path)
    assert [row["name"] for row in rows] == ["Second", "First"]
