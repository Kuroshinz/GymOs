import re
from typing import Any


def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_positive_number(value: Any) -> bool:
    try:
        return float(value) > 0
    except (ValueError, TypeError):
        return False


def validate_not_empty(value: Any) -> bool:
    return bool(value) if isinstance(value, str) else value is not None
