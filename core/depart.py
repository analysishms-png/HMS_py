"""Depart CRUD (F&B outlets/departments - 9 live rows: ANNAPURNA, DISPENSE BAR...).
Schema evidence: Code varchar(6) PK, Name varchar(35), KotYn varchar(1),
POS varchar(1), Header1/Header2 varchar(50), Phone varchar(50).
App-level: Code+Name required. Audit pattern VB6 jaisa:
U_Name + U_EntDt(getdate()) + U_AE ('A'/'E').
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
LIMITS = {"code": 6, "name": 35, "flag": 1, "header": 50, "phone": 50}
SELECT_COLS = "Code, Name, KotYn, POS, Phone, U_Name, U_EntDt, U_AE"


def _map(r) -> dict:
    return {"code": r.Code, "name": r.Name or "", "kotyn": r.KotYn or "",
            "pos": r.POS or "", "phone": r.Phone or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}


def _validate(rec: dict):
    if len(rec.get("code", "")) > LIMITS["code"]:
        raise ValueError(f"Code max {LIMITS['code']} chars")
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if len(rec.get("name", "")) > LIMITS["name"]:
        raise ValueError(f"Name max {LIMITS['name']} chars")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    for k in ("kotyn", "pos"):
        v = (rec.get(k) or "").strip().upper()
        if v and v not in ("Y", "N"):
            raise ValueError(f"{k} sirf Y/N ho sakta hai")
    if len(rec.get("phone", "")) > LIMITS["phone"]:
        raise ValueError(f"Phone max {LIMITS['phone']} chars")


def list_all(cn=None) -> list[dict]:
    rows = db.query(f"SELECT {SELECT_COLS} FROM Depart WHERE (LOGSITE_CODE = ? OR LOGSITE_CODE = 'HO' OR ISNULL(LOGSITE_CODE,'')='') ORDER BY Code",
                    cn=cn)
    return [_map(r) for r in rows]


def get(code: str, cn=None) -> dict | None:
    rows = db.query(f"SELECT {SELECT_COLS} FROM Depart WHERE Code = ?",
                    (code,), cn=cn)
    return _map(rows[0]) if rows else None


def exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM Depart WHERE Code = ?", (code,),
                         cn=cn))


def insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    db.require_absent("Depart", "Code", rec["code"],
              "Department Code")
    return db.execute(
        "INSERT INTO Depart (Code, Name, KotYn, POS, Phone, Site_Code, "
        "U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"],
         (rec.get("kotyn") or "").upper(), (rec.get("pos") or "").upper(),
         rec.get("phone", ""), SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def update(code: str, rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    return db.execute(
        "UPDATE Depart SET Name = ?, KotYn = ?, POS = ?, Phone = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec["name"], (rec.get("kotyn") or "").upper(),
         (rec.get("pos") or "").upper(), rec.get("phone", ""), USER, code),
        cn=cn, commit=commit)


def delete(code: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM Depart WHERE Code = ?", (code,),
                      cn=cn, commit=commit)



# Phase A: UI inventory.py depart_list() call karta tha.
depart_list = list_all
