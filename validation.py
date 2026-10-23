"""Validation rules for the contact form."""
import re

MAX_SHORT_FIELD = 200
MAX_MESSAGE = 2000
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

FIELDS = ("name", "email", "subject", "message")


def validate_submission(data):
    """Validate contact form data.

    Args:
        data: mapping with keys name, email, subject, message (raw strings).

    Returns:
        dict of field -> error message for each invalid field; empty dict means valid.
    """
    errors = {}
    values = {field: (data.get(field) or "").strip() for field in FIELDS}

    for field in ("name", "email", "subject", "message"):
        if not values[field]:
            errors[field] = "This field is required."

    if "email" not in errors and not EMAIL_RE.match(values["email"]):
        errors["email"] = "Enter a valid email address."

    for field in ("name", "email", "subject"):
        if field not in errors and len(values[field]) > MAX_SHORT_FIELD:
            errors[field] = f"Must be {MAX_SHORT_FIELD} characters or fewer."

    if "message" not in errors and len(values["message"]) > MAX_MESSAGE:
        errors["message"] = f"Must be {MAX_MESSAGE} characters or fewer."

    return errors
