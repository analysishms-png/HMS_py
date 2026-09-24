"""AreaMast CRUD (VB6: MembershipMast.frm aadi use karte hain).

HISTORY: AreaMast.CityCode varchar(5) tha, par City.CityCode varchar(6) -
asli codes (KK0002...) 6-char hain. Original VB6 app me bhi Area me real
City assign karna impossible tha (isi se table khaali thi).
2026-09-18: USER APPROVAL se varchar(6) me widen kiya gaya
(migration: tools/migrate_area_citycode.py, backup AreaMast_bak_20260918).
Ab LIMITS city=6 (schema ke barabar).

Audit pattern VB6 jaisa: U_Name + U_EntDt(getdate()) + U_AE ('A'/'E').
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
LIMITS = {"code": 5, "name": 25, "city": 6}   # city=6: post-migration schema
SELECT_COLS = "AreaCODE, AreaNAME, CityCode, U_Name, U_EntDt, U_AE"


def _map(r) -> dict:
    return {"code": r.AreaCODE, "name": r.AreaNAME or "",
            "city": r.CityCode or "", "u_name": r.U_Name or "",
            "u_ae": r.U_AE or ""}


def _validate(rec: dict, cn=None):
    if len(rec.get("code", "")) > LIMITS["code"]:
        raise ValueError(f"AreaCODE max {LIMITS['code']} chars")
    if not rec.get("code", "").strip():
        raise ValueError("AreaCODE zaroori hai")
    if len(rec.get("name", "")) > LIMITS["name"]:
        raise ValueError(f"AreaNAME max {LIMITS['name']} chars")
    if not rec.get("name", "").strip():
        raise ValueError("AreaNAME zaroori hai")
    if len(rec.get("city", "")) > LIMITS["city"]:
        raise ValueError(f"CityCode max {LIMITS['city']} chars")
    if not rec.get("city", "").strip():
        raise ValueError("CityCode zaroori hai (NOT NULL)")
    # FK sanity: CityCode City me hona chahiye
    if not db.query("SELECT 1 FROM City WHERE CityCode = ?",
                    (rec["city"],), cn=cn):
        raise ValueError(f"CityCode '{rec['city']}' City table me nahi mila")


def list_all(cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM AreaMast ORDER BY AreaCODE", cn=cn)
    return [_map(r) for r in rows]


def get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM AreaMast WHERE AreaCODE = ?", (code,),
        cn=cn)
    return _map(rows[0]) if rows else None


def exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM AreaMast WHERE AreaCODE = ?",
                         (code,), cn=cn))


def insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec, cn=cn)
    db.require_absent("AreaMast", "AreaCODE", rec["code"], "Area Code")
    return db.execute(
        "INSERT INTO AreaMast (AreaCODE, AreaNAME, CityCode, Site_Code, "
        "U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"], rec["city"],
         SITE_CODE, USER, SITE_CODE), cn=cn, commit=commit)


def update(code: str, rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec, cn=cn)
    return db.execute(
        "UPDATE AreaMast SET AreaNAME = ?, CityCode = ?, U_Name = ?, "
        "U_EntDt = getdate(), U_AE = 'E' WHERE AreaCODE = ?",
        (rec["name"], rec["city"], USER, code), cn=cn, commit=commit)


def delete(code: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM AreaMast WHERE AreaCODE = ?", (code,),
                      cn=cn, commit=commit)
