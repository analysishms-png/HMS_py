"""TDS Category Master CRUD (VB6: FaTDSCat.frm - Finance -> TDS Category).
Schema evidence (live HMS DB): TDSCat table - 9 columns.
Code varchar(6) PK, Name varchar(25), TDSLimit float, TDSPercentage float,
Site_Code varchar(2), U_Name varchar(10), U_EntDt datetime, U_AE varchar(1),
LogSite_Code varchar(2).
VB6: Used for TDS deduction configuration on payments.
Audit pattern VB6 jaisa: U_Name + U_EntDt(getdate()) + U_AE ('A'/'E')."""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
LIMITS = {"code": 6, "name": 25}
SELECT_COLS = "Code, Name, TDSLimit, TDSPercentage, U_Name, U_EntDt, U_AE"


def _map(r) -> dict:
    try:
        return {
            "code": r.Code, "name": (r.Name or "").strip(),
            "tdslimit": float(r.TDSLimit or 0),
            "tdsper": float(r.TDSPercentage or 0),
            "uname": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        code, name, tdslim, tdsper, un, _, uae = r
        return {
            "code": code, "name": (name or "").strip(),
            "tdslimit": float(tdslim or 0), "tdsper": float(tdsper or 0),
            "uname": un or "", "u_ae": uae or "",
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
    for k in ("tdslimit", "tdsper"):
        try:
            float(rec.get(k) or 0)
        except (ValueError, TypeError):
            raise ValueError(f"{k} numeric hona chahiye")


def list_all(cn=None) -> list[dict]:
    rows = db.query(f"SELECT {SELECT_COLS} FROM TDSCat ORDER BY Code", cn=cn)
    return [_map(r) for r in rows]


def get(code: str, cn=None) -> dict | None:
    rows = db.query(f"SELECT {SELECT_COLS} FROM TDSCat WHERE Code = ?", (code,), cn=cn)
    return _map(rows[0]) if rows else None


def exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM TDSCat WHERE Code = ?", (code,), cn=cn))


def insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    db.require_absent("TDSCat", "Code", rec["code"], "TDS Category Code")
    return db.execute(
        "INSERT INTO TDSCat (Code, Name, TDSLimit, TDSPercentage, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"], float(rec.get("tdslimit") or 0),
         float(rec.get("tdsper") or 0), SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def update(code: str, rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    return db.execute(
        "UPDATE TDSCat SET Name = ?, TDSLimit = ?, TDSPercentage = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec["name"], float(rec.get("tdslimit") or 0),
         float(rec.get("tdsper") or 0), USER, code),
        cn=cn, commit=commit)


def delete(code: str, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM TDSCat WHERE Code = ?", (code,),
        cn=cn, commit=commit)