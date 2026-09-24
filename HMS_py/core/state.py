"""State master CRUD (VB6: 'State Master' - Main Setup).

Schema evidence (live): State: Code varchar(6) PK, Name varchar(30),
ShortName varchar(6) (state-code number jaise '35'), Country varchar(6) FK
-> Country.Code, Site_Code(2), U_Name(10), U_EntDt, U_AE(1), LogSite_Code(2).
Rows live: 36 (ANDAMAN..), sab Country='KK0002' (INDIA).
Audit pattern VB6 jaisa: U_Name + U_EntDt(getdate()) + U_AE ('A'/'E').
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
LIMITS = {"code": 6, "name": 30, "short": 6, "country": 6}
SELECT_COLS = ("Code, Name, ShortName, Country, "
               "U_Name, U_EntDt, U_AE")


def _map(r) -> dict:
    return {"code": r.Code, "name": (r.Name or "").strip(),
            "short": (r.ShortName or "").strip(),
            "country": r.Country or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}


def _validate(rec: dict):
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if len(rec["code"]) > LIMITS["code"]:
        raise ValueError(f"Code max {LIMITS['code']} chars")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    if len(rec["name"]) > LIMITS["name"]:
        raise ValueError(f"Name max {LIMITS['name']} chars")
    if len(rec.get("country", "")) > LIMITS["country"]:
        raise ValueError(f"country max {LIMITS['country']} chars")


def list_all(cn=None) -> list[dict]:
    rows = db.query(f"SELECT {SELECT_COLS} FROM State WHERE (LOGSITE_CODE = ? OR LOGSITE_CODE = 'HO' OR ISNULL(LOGSITE_CODE,'')='') ORDER BY Code", cn=cn)
    return [_map(r) for r in rows]


def get(code: str, cn=None) -> dict | None:
    rows = db.query(f"SELECT {SELECT_COLS} FROM State WHERE Code = ?",
                    (code,), cn=cn)
    return _map(rows[0]) if rows else None


def exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM State WHERE Code = ?", (code,),
                         cn=cn))


def insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    db.require_absent("State", "Code", rec["code"],
              "State Code")
    return db.execute(
        "INSERT INTO State (Code, Name, ShortName, Country, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"], rec.get("short", ""),
         rec.get("country", ""), SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def update(code: str, rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    return db.execute(
        "UPDATE State SET Name = ?, ShortName = ?, Country = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec["name"], rec.get("short", ""), rec.get("country", ""),
         USER, code), cn=cn, commit=commit)


def delete(code: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM State WHERE Code = ?", (code,),
                      cn=cn, commit=commit)
