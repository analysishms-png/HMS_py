"""Business Source master CRUD (VB6: 'Business Source' - Main Setup -> FO).

Schema evidence (live HMS DB): BussSource table.
  Code varchar(5) PK, Name varchar(20),
  Active varchar(3),
  Site_Code varchar(2), U_Name varchar(10), U_EntDt datetime,
  U_AE varchar(1), LogSite_Code varchar(2).
VB6 use: Where did the booking come from? (Walk-In, Phone, Email, Agent, OTA)
Audit pattern VB6 jaisa: U_Name + U_EntDt(getdate()) + U_AE ('A'/'E').
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
LIMITS = {"code": 5, "name": 20}
SELECT_COLS = "Code, Name, Active, U_Name, U_EntDt, U_AE"


def _map(r) -> dict:
    try:
        return {
            "code": r.Code, "name": (r.Name or "").strip(),
            "active": r.Active or "Y",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        bc, bn, act, un, _, uae = r
        return {
            "code": bc, "name": (bn or "").strip(),
            "active": act or "Y",
            "u_name": un or "", "u_ae": uae or "",
        }


def _validate(rec: dict):
    if not rec.get("code", "").strip():
        raise ValueError("BusCode zaroori hai")
    if len(rec["code"]) > LIMITS["code"]:
        raise ValueError(f"BusCode max {LIMITS['code']} chars")
    if not rec.get("name", "").strip():
        raise ValueError("BusName zaroori hai")
    if len(rec["name"]) > LIMITS["name"]:
        raise ValueError(f"BusName max {LIMITS['name']} chars")


def list_all(cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM BussSource WHERE (LOGSITE_CODE = ? OR LOGSITE_CODE = 'HO' OR ISNULL(LOGSITE_CODE,'')='') ORDER BY Code", cn=cn)
    return [_map(r) for r in rows]


def get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM BussSource WHERE Code = ?",
        (code,), cn=cn)
    return _map(rows[0]) if rows else None


def exists(code: str, cn=None) -> bool:
    return bool(db.query(
        "SELECT 1 FROM BussSource WHERE Code = ?", (code,), cn=cn))


def insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    db.require_absent("BussSource", "Code", rec["code"],
              "Business Source Code")
    return db.execute(
        "INSERT INTO BussSource (Code, Name, Active, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"],
         rec.get("active", "Y"), SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def update(code: str, rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    return db.execute(
        "UPDATE BussSource SET Name = ?, Active = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec["name"], rec.get("active", "Y"),
         USER, code), cn=cn, commit=commit)


def delete(code: str, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM BussSource WHERE Code = ?", (code,),
        cn=cn, commit=commit)
