"""Country master CRUD (VB6: 'Country Master' - Main Setup).

Schema evidence (live MOONData2627.INFORMATION_SCHEMA):
Country: Code varchar(6) PK, Name varchar(30), ShortName varchar(6),
Type varchar(7) ('India'/'Foreign'), Nationality varchar(25),
Site_Code(2), U_Name(10), U_EntDt, U_AE(1), LogSite_Code(2).
Rows live: 9 (INDIA/INDIAN/FRANCE/AMERICA...).
Audit pattern VB6 jaisa: U_Name + U_EntDt(getdate()) + U_AE ('A'/'E').
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
LIMITS = {"code": 6, "name": 30, "short": 6, "type": 7, "nationality": 25}
SELECT_COLS = ("Code, Name, ShortName, Type, Nationality, "
               "U_Name, U_EntDt, U_AE")


def _map(r) -> dict:
    return {"code": r.Code, "name": (r.Name or "").strip(),
            "short": (r.ShortName or "").strip(),
            "type": r.Type or "",
            "nationality": (r.Nationality or "").strip(),
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
    for k in ("short", "type", "nationality"):
        if len(rec.get(k, "")) > LIMITS[k]:
            raise ValueError(f"{k} max {LIMITS[k]} chars")


def list_all(cn=None) -> list[dict]:
    rows = db.query(f"SELECT {SELECT_COLS} FROM Country ORDER BY Code",
                    cn=cn)
    return [_map(r) for r in rows]


def get(code: str, cn=None) -> dict | None:
    rows = db.query(f"SELECT {SELECT_COLS} FROM Country WHERE Code = ?",
                    (code,), cn=cn)
    return _map(rows[0]) if rows else None


def exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM Country WHERE Code = ?", (code,),
                         cn=cn))


def insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    db.require_absent("Country", "Code", rec["code"],
              "Country Code")
    return db.execute(
        "INSERT INTO Country (Code, Name, ShortName, Type, Nationality, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"], rec.get("short", ""),
         rec.get("type", ""), rec.get("nationality", ""),
         SITE_CODE, USER, SITE_CODE), cn=cn, commit=commit)


def update(code: str, rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    return db.execute(
        "UPDATE Country SET Name = ?, ShortName = ?, Type = ?, "
        "Nationality = ?, U_Name = ?, U_EntDt = getdate(), U_AE = 'E' "
        "WHERE Code = ?",
        (rec["name"], rec.get("short", ""), rec.get("type", ""),
         rec.get("nationality", ""), USER, code), cn=cn, commit=commit)


def delete(code: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM Country WHERE Code = ?", (code,),
                      cn=cn, commit=commit)
