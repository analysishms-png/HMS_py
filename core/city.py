"""City master CRUD (VB6: City masahij forms - 311 live rows).
Schema evidence: CityCode varchar(6) PK (only NOT NULL), CityName varchar(35),
ShortName(6), ZipCode(11), State(6). App-level: CityName required.
Audit pattern VB6 jaisa: U_Name + U_EntDt(getdate()) + U_AE ('A'/'E').
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
LIMITS = {"code": 6, "name": 35, "short": 6, "zip": 11, "state": 6}
SELECT_COLS = ("CityCode, CityName, ShortName, ZipCode, State, "
               "U_Name, U_EntDt, U_AE")


def _map(r) -> dict:
    return {"code": r.CityCode, "name": r.CityName or "",
            "short": r.ShortName or "", "zip": r.ZipCode or "",
            "state": r.State or "", "u_name": r.U_Name or "",
            "u_ae": r.U_AE or ""}


def _validate(rec: dict):
    if len(rec.get("code", "")) > LIMITS["code"]:
        raise ValueError(f"CityCode max {LIMITS['code']} chars")
    if not rec.get("code", "").strip():
        raise ValueError("CityCode zaroori hai")
    if len(rec.get("name", "")) > LIMITS["name"]:
        raise ValueError(f"CityName max {LIMITS['name']} chars")
    if not rec.get("name", "").strip():
        raise ValueError("CityName zaroori hai")
    for k, lim in (("short", "short"), ("zip", "zip"), ("state", "state")):
        if len(rec.get(k, "")) > LIMITS[lim]:
            raise ValueError(f"{lim} max {LIMITS[lim]} chars")


def list_all(cn=None) -> list[dict]:
    rows = db.query(f"SELECT {SELECT_COLS} FROM City ORDER BY CityCode",
                    cn=cn)
    return [_map(r) for r in rows]


def get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM City WHERE CityCode = ?", (code,), cn=cn)
    return _map(rows[0]) if rows else None


def exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM City WHERE CityCode = ?", (code,),
                         cn=cn))


def insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    db.require_absent("City", "CityCode", rec["code"],
              "City Code")
    return db.execute(
        "INSERT INTO City (CityCode, CityName, ShortName, ZipCode, State, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"], rec.get("short", ""),
         rec.get("zip", ""), rec.get("state", ""),
         SITE_CODE, USER, SITE_CODE), cn=cn, commit=commit)


def update(code: str, rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    return db.execute(
        "UPDATE City SET CityName = ?, ShortName = ?, ZipCode = ?, "
        "State = ?, U_Name = ?, U_EntDt = getdate(), U_AE = 'E' "
        "WHERE CityCode = ?",
        (rec["name"], rec.get("short", ""), rec.get("zip", ""),
         rec.get("state", ""), USER, code), cn=cn, commit=commit)


def delete(code: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM City WHERE CityCode = ?", (code,),
                      cn=cn, commit=commit)
