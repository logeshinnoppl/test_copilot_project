import validation


def test_rejects_empty_required_fields():
    errors = validation.validate_submission(
        {"name": "", "email": "a@b.com", "subject": "", "message": "hi"}
    )
    assert "name" in errors
    assert "subject" in errors
    assert "email" not in errors


def test_rejects_invalid_email():
    errors = validation.validate_submission(
        {"name": "Alice", "email": "not-an-email", "subject": "Hi", "message": "hi"}
    )
    assert "email" in errors


def test_accepts_valid_submission():
    errors = validation.validate_submission(
        {"name": "Alice", "email": "alice@example.com", "subject": "Hi", "message": "hello"}
    )
    assert errors == {}


def test_rejects_oversized_short_field():
    errors = validation.validate_submission(
        {
            "name": "x" * 201,
            "email": "alice@example.com",
            "subject": "Hi",
            "message": "hello",
        }
    )
    assert "name" in errors


def test_rejects_oversized_message():
    errors = validation.validate_submission(
        {
            "name": "Alice",
            "email": "alice@example.com",
            "subject": "Hi",
            "message": "x" * 2001,
        }
    )
    assert "message" in errors


def test_strips_whitespace_only_as_empty():
    errors = validation.validate_submission(
        {"name": "   ", "email": "alice@example.com", "subject": "Hi", "message": "hello"}
    )
    assert "name" in errors
