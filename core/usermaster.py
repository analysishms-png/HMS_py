"""User Master CRUD (VB6: 'User Master' / Utility -> User Master).

Schema evidence (live): UserMast table.
  USER_NAME varchar(10) PK, PASSWD varchar(50) (encrypted - VB6 auth.py se),
  LABEL varchar(30), ShortName varchar(10), ActiveYN varchar(1),
  GodCode varchar(6), FloorCode varchar(6), AllowDtChng varchar(1),
  BackColor int.

WARNING: PASSWD is VB6-encrypted (core/auth.py encrypt/decrypt use karo).
UI mein plaintext lena + encrypt karke store karo.
"""
from __future__ import annotations

from HMS_py.core import db, auth

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
LIMITS = {
    "username": 10, "label": 30, "short": 10,
}
SELECT_COLS = "USER_NAME, LABEL, ShortName, ActiveYN"


def _map(r) -> dict:
    lbl = r.LABEL
    sn = r.ShortName
    return {
        "username": r.USER_NAME or "",
        "label": (lbl.strip() if isinstance(lbl, str) else str(lbl or "")),
        "short": (sn.strip() if isinstance(sn, str) else str(sn or "")),
        "active": r.ActiveYN or "Y",
    }


def _validate(rec: dict):
    if not rec.get("username", "").strip():
        raise ValueError("USER_NAME zaroori hai")
    if len(rec["username"]) > LIMITS["username"]:
        raise ValueError(f"USER_NAME max {LIMITS['username']} chars")
    if len(rec.get("label", "")) > LIMITS["label"]:
        raise ValueError(f"LABEL max {LIMITS['label']} chars")
    if len(rec.get("short", "")) > LIMITS["short"]:
        raise ValueError(f"ShortName max {LIMITS['short']} chars")


def list_all(cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM UserMast ORDER BY USER_NAME", cn=cn)
    return [_map(r) for r in rows]


def get(username: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM UserMast WHERE USER_NAME = ?",
        (username,), cn=cn)
    return _map(rows[0]) if rows else None


def exists(username: str, cn=None) -> bool:
    return bool(db.query(
        "SELECT 1 FROM UserMast WHERE USER_NAME = ?", (username,), cn=cn))


def _label_column_is_int(cn=None) -> bool:
    """Live DB schema check: UserMast.LABEL smallint hai? (schema-drift guard;
    VB6 doc me LABEL varchar(30) tha, kuch live DBs me smallint hai)."""
    try:
        rows = db.query(
            "SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS "
            "WHERE TABLE_NAME = 'UserMast' AND COLUMN_NAME = 'LABEL'", cn=cn)
        return bool(rows) and str(rows[0][0]).lower() in ("smallint", "int")
    except Exception:
        return False


def _label_value(label: str, cn=None):
    """LABEL value column-type ke hisab se: smallint -> 0, varchar -> text."""
    return 0 if _label_column_is_int(cn) else (label or "")


def insert(rec: dict, plain_password: str = "", cn=None,
           commit: bool = True) -> int:
    """Naya user. Password plaintext dena hai - encrypt hokar store hoga.

    PASSWD bind: CAST(? AS varchar(50)) + latin-1 bytes — VB6 encrypt ke
    >127 chars varchar codepage conversion me lossy nahi hote (E2E fix
    2026-09-23; SA ka VB6-era password isi path se byte-exact aata hai).
    """
    _validate(rec)
    enc = auth.enc_bytes(plain_password) if plain_password else auth.enc_bytes("")
    return db.execute(
        "INSERT INTO UserMast (USER_NAME, PASSWD, LABEL, ShortName, ActiveYN) "
        "VALUES (?, CAST(? AS varchar(50)), ?, ?, ?)",
        (rec["username"].upper(), enc,
         _label_value(rec.get("label", ""), cn),
         rec.get("short", ""),
         rec.get("active", "Y")),
        cn=cn, commit=commit)


def update(username: str, rec: dict, plain_password: str | None = None,
           cn=None, commit: bool = True) -> int:
    """Existing user update. plain_password=None to password nahi badlega."""
    _validate(rec)
    lbl = _label_value(rec.get("label", ""), cn)
    if plain_password is not None:
        enc = auth.enc_bytes(plain_password)
        return db.execute(
            "UPDATE UserMast SET PASSWD = CAST(? AS varchar(50)), LABEL = ?, "
            "ShortName = ?, "
            "ActiveYN = ? WHERE USER_NAME = ?",
            (enc, lbl, rec.get("short", ""),
             rec.get("active", "Y"), username.upper()),
            cn=cn, commit=commit)
    else:
        return db.execute(
            "UPDATE UserMast SET LABEL = ?, ShortName = ?, ActiveYN = ? "
            "WHERE USER_NAME = ?",
            (lbl, rec.get("short", ""),
             rec.get("active", "Y"), username.upper()),
            cn=cn, commit=commit)


def set_password(username: str, plain_password: str, cn=None,
                 commit: bool = True) -> int:
    """Sirf password change karo (VB6 password-reset pattern)."""
    encrypted = auth.enc_bytes(plain_password)
    return db.execute(
        "UPDATE UserMast SET PASSWD = CAST(? AS varchar(50)) WHERE USER_NAME = ?",
        (encrypted, username.upper()), cn=cn, commit=commit)


def delete(username: str, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM UserMast WHERE USER_NAME = ?",
        (username.upper(),), cn=cn, commit=commit)
