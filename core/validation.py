"""Shared field validators (VB6 ValidationModule.bas port).

ValidateRequiredField / ValidateNumericField / ValidateEmailField /
ValidatePhoneNumber / ValidateDateField — pure functions, no DB.
Return (ok: bool, message: str).
"""
from __future__ import annotations

import datetime as _dt
import re
from typing import Any

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]{2,}$")
_PHONE_RE = re.compile(r"^\+?[\d\s\-()]{7,20}$")


def validate_required_field(value: Any, label: str = "Field") -> tuple[bool, str]:
    if value is None or str(value).strip() == "":
        return False, f"{label} is required"
    return True, ""


def validate_numeric_field(value: Any, label: str = "Field",
                           minimum: float | None = None,
                           maximum: float | None = None) -> tuple[bool, str]:
    try:
        num = float(str(value).strip())
    except (TypeError, ValueError):
        return False, f"{label} must be numeric"
    if minimum is not None and num < minimum:
        return False, f"{label} must be >= {minimum}"
    if maximum is not None and num > maximum:
        return False, f"{label} must be <= {maximum}"
    return True, ""


def validate_email_field(value: Any, label: str = "Email") -> tuple[bool, str]:
    s = str(value or "").strip()
    if not s:
        return True, ""
    if not _EMAIL_RE.match(s):
        return False, f"{label} is invalid"
    return True, ""


def validate_phone_number(value: Any, label: str = "Phone") -> tuple[bool, str]:
    s = str(value or "").strip()
    if not s:
        return True, ""
    if not _PHONE_RE.match(s):
        return False, f"{label} must be 7-20 digits (optional + - ())"
    return True, ""


def validate_date_field(value: Any, label: str = "Date",
                        date_format: str = "%Y-%m-%d") -> tuple[bool, str]:
    if value is None or value == "":
        return True, ""
    if isinstance(value, (_dt.date, _dt.datetime)):
        return True, ""
    try:
        _dt.datetime.strptime(str(value).strip(), date_format)
        return True, ""
    except ValueError:
        return False, f"{label} must be date (YYYY-MM-DD)"


def validate_all(*checks: tuple[bool, str]) -> tuple[bool, str]:
    """First failing (ok, msg) wins; else (True, '')."""
    for ok, msg in checks:
        if not ok:
            return False, msg
    return True, ""


# ---------------------------------------------------------------------------
# DatabaseSecurityModule.bas port: SanitizeInput / ValidateSQL
# ---------------------------------------------------------------------------
_SQL_INJECTION_PATTERNS: tuple[str, ...] = (
    "';DROP", "DELETE", "INSERT", "UPDATE", "UNION", "SELECT",
    "EXEC", "EXECUTE", "ALTER", "CREATE", "TRUNCATE", "--", "/*", "*/",
)


def sanitize_input(value: Any) -> str:
    """VB6 SanitizeInput: keep printable ASCII, escape/danger-strip SQL chars."""
    if value is None:
        return ""
    s = str(value)
    out = "".join(ch for ch in s if " " <= ch <= "~")
    out = out.replace("'", "''")
    out = out.replace(";", "")
    out = out.replace("--", "")
    out = out.replace("/*", "")
    out = out.replace("*/", "")
    return out


def validate_sql(sql: Any) -> bool:
    """VB6 ValidateSQL: False when the string hits known injection patterns."""
    upper = str(sql or "").upper()
    for pattern in _SQL_INJECTION_PATTERNS:
        if pattern in upper:
            return False
    if "OR 1=1" in upper or "AND 1=1" in upper:
        return False
    return True
