"""Unit master CRUD (VB6: 'Unit Master' - Main Setup, POS section).

Schema evidence (live): UnitMast: Name varchar(6) PK (no Code col!),
Site_Code(2), U_Name(10), U_EntDt, U_AE(1), LogSite_Code(2),
PriceType smallint, Status varchar(10). Rows live: 32.
Audit pattern VB6 jaisa: U_Name + U_EntDt(getdate()) + U_AE ('A'/'E').
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
LIMITS = {"code": 6, "status": 10}
SELECT_COLS = ("Name, PriceType, Status, "
               "U_Name, U_EntDt, U_AE")


def _map(r) -> dict:
    return {"code": r.Name, "pricetype": r.PriceType or 0,
            "status": r.Status or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}


def _validate(rec: dict):
    if not rec.get("code", "").strip():
        raise ValueError("Unit Name zaroori hai")
    if len(rec["code"]) > LIMITS["code"]:
        raise ValueError(f"Unit Name max {LIMITS['code']} chars")
    if len(rec.get("status", "")) > LIMITS["status"]:
        raise ValueError(f"status max {LIMITS['status']} chars")


def list_all(cn=None) -> list[dict]:
    rows = db.query(f"SELECT {SELECT_COLS} FROM UnitMast WHERE (LOGSITE_CODE = ? OR LOGSITE_CODE = 'HO' OR ISNULL(LOGSITE_CODE,'')='') ORDER BY Name",
                    cn=cn)
    return [_map(r) for r in rows]


def get(code: str, cn=None) -> dict | None:
    rows = db.query(f"SELECT {SELECT_COLS} FROM UnitMast WHERE Name = ?",
                    (code,), cn=cn)
    return _map(rows[0]) if rows else None


def exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM UnitMast WHERE Name = ?", (code,),
                         cn=cn))


def insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    return db.execute(
        "INSERT INTO UnitMast (Name, PriceType, Status, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], int(rec.get("pricetype") or 0),
         rec.get("status", ""), SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def update(code: str, rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    return db.execute(
        "UPDATE UnitMast SET PriceType = ?, Status = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Name = ?",
        (int(rec.get("pricetype") or 0), rec.get("status", ""),
         USER, code), cn=cn, commit=commit)


def delete(code: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM UnitMast WHERE Name = ?", (code,),
                      cn=cn, commit=commit)
