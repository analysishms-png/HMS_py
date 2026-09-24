"""Season Master CRUD (VB6: 'Season Master' - Main Setup -> Front Office).

Schema evidence (live HMS DB): SeasonMast table.
  FromDate datetime, ToDate datetime, RateCode varchar(10),
  Site_Code varchar(2), U_Name varchar(10), U_EntDt datetime,
  U_AE varchar(1), LogSite_Code varchar(2).
Audit pattern VB6 jaisa: U_Name + U_EntDt(getdate()) + U_AE ('A'/'E').
"""
from __future__ import annotations

import datetime

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
LIMITS = {"ratecode": 2}
SELECT_COLS = "FromDate, ToDate, RateCode, U_Name, U_EntDt, U_AE"


def _dt(v):
    if v is None:
        return None
    if isinstance(v, datetime.datetime):
        return v.date()
    return v


def _map(r) -> dict:
    return {
        "fromdate": _dt(r.FromDate), "todate": _dt(r.ToDate),
        "ratecode": r.RateCode or "",
        "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
    }


def _validate(rec: dict):
    if not rec.get("ratecode", "").strip():
        raise ValueError("RateCode zaroori hai")
    if len(rec["ratecode"]) > LIMITS["ratecode"]:
        raise ValueError(f"RateCode max {LIMITS['ratecode']} chars")


def list_all(cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM SeasonMast ORDER BY FromDate", cn=cn)
    return [_map(r) for r in rows]


def get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM SeasonMast WHERE RateCode = ?",
        (code,), cn=cn)
    return _map(rows[0]) if rows else None


def exists(code: str, cn=None) -> bool:
    return bool(db.query(
        "SELECT 1 FROM SeasonMast WHERE RateCode = ?", (code,), cn=cn))


def insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    db.require_absent("SeasonMast", "RateCode", rec["ratecode"], "Season RateCode")
    fd = rec.get("fromdate") or datetime.date.today()
    td = rec.get("todate") or datetime.date.today()
    return db.execute(
        "INSERT INTO SeasonMast (FromDate, ToDate, RateCode, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (fd, td, rec["ratecode"], SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def update(code: str, rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    fd = rec.get("fromdate") or datetime.date.today()
    td = rec.get("todate") or datetime.date.today()
    return db.execute(
        "UPDATE SeasonMast SET FromDate = ?, ToDate = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE RateCode = ?",
        (fd, td, USER, code),
        cn=cn, commit=commit)


def delete(code: str, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM SeasonMast WHERE RateCode = ?", (code,), cn=cn,
        commit=commit)
