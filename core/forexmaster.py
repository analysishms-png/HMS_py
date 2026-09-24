"""Forex Master CRUD (VB6: 'Forex Master' - Main Setup -> FO).

Schema evidence (live HMS DB): ForEx table.
  Code varchar(6) PK, Name varchar(30), Rate float,
  Site_Code varchar(2), U_Name varchar(10), U_EntDt datetime,
  U_AE varchar(1), LogSite_Code varchar(2).
VB6 use: Foreign currency exchange (USD/EUR/GBP -> INR) at check-in.
Audit pattern VB6 jaisa: U_Name + U_EntDt(getdate()) + U_AE ('A'/'E').
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
LIMITS = {"code": 6, "name": 30}
SELECT_COLS = "Code, Name, Rate, U_Name, U_EntDt, U_AE"


def _map(r) -> dict:
    return {
        "code": r.Code, "name": (r.Name or "").strip(),
        "rate": float(r.Rate or 0),
        "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
    }


def _validate(rec: dict):
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if len(rec["code"]) > LIMITS["code"]:
        raise ValueError(f"Code max {LIMITS['code']} chars")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    if len(rec["name"]) > LIMITS["name"]:
        raise ValueError(f"Name max {LIMITS['name']} chars")


def list_all(cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM ForEx ORDER BY Code", cn=cn)
    return [_map(r) for r in rows]


def get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM ForEx WHERE Code = ?",
        (code,), cn=cn)
    return _map(rows[0]) if rows else None


def exists(code: str, cn=None) -> bool:
    return bool(db.query(
        "SELECT 1 FROM ForEx WHERE Code = ?", (code,), cn=cn))


def insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    return db.execute(
        "INSERT INTO ForEx (Code, Name, Rate, Site_Code, U_Name, "
        "U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"], float(rec.get("rate") or 0),
         SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def update(code: str, rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    return db.execute(
        "UPDATE ForEx SET Name = ?, Rate = ?, U_Name = ?, "
        "U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec["name"], float(rec.get("rate") or 0), USER, code),
        cn=cn, commit=commit)


def delete(code: str, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM ForEx WHERE Code = ?", (code,),
        cn=cn, commit=commit)
