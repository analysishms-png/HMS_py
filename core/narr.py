# P0 FIX HO fallback pending - master SELECT should add WHERE (LOGSITE_CODE=? OR HO)
"""NarrMast CRUD (VB6: FaNarrMast.frm isko manage karta hai).
Schema evidence: Code varchar(6), Name varchar(255) + audit cols.
NOT NULL: Code, Name.  Narration master - F&B/voucher narratives.
Audit pattern VB6 jaisa: U_Name + U_EntDt(getdate()) + U_AE ('A'/'E').
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
LIMITS = {"code": 6, "name": 255}
SELECT_COLS = "Code, Name, U_Name, U_EntDt, U_AE"


def _map(r) -> dict:
    return {"code": r.Code, "name": r.Name or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}


def _validate(rec: dict):
    if len(rec.get("code", "")) > LIMITS["code"]:
        raise ValueError(f"Code max {LIMITS['code']} chars")
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if len(rec.get("name", "")) > LIMITS["name"]:
        raise ValueError(f"Name max {LIMITS['name']} chars")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai (NOT NULL)")


def list_all(cn=None) -> list[dict]:
    rows = db.query(f"SELECT {SELECT_COLS} FROM NarrMast ORDER BY Code",
                    cn=cn)
    return [_map(r) for r in rows]


def get(code: str, cn=None) -> dict | None:
    rows = db.query(f"SELECT {SELECT_COLS} FROM NarrMast WHERE Code = ?",
                    (code,), cn=cn)
    return _map(rows[0]) if rows else None


def exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM NarrMast WHERE Code = ?",
                         (code,), cn=cn))


def insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    db.require_absent("NarrMast", "Code", rec["code"],
              "Narration Code")
    return db.execute(
        "INSERT INTO NarrMast (Code, Name, Site_Code, U_Name, U_EntDt, "
        "U_AE, LogSite_Code) VALUES (?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"], SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def update(code: str, rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    return db.execute(
        "UPDATE NarrMast SET Name = ?, U_Name = ?, U_EntDt = getdate(), "
        "U_AE = 'E' WHERE Code = ?",
        (rec["name"], USER, code), cn=cn, commit=commit)


def delete(code: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM NarrMast WHERE Code = ?", (code,),
                      cn=cn, commit=commit)
