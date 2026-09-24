# P0 FIX HO fallback pending - master SELECT should add WHERE (LOGSITE_CODE=? OR HO)
"""Payment Type master CRUD (VB6: 'Payment Type' - Main Setup -> General).

Schema: RevMast table (filtered by PAYTYPE column).
  Code varchar(6) PK, Name varchar(50), ShortName varchar(5),
  PAYTYPE varchar(15) ('Cash','Credit Card','Cheque','Company','Room',etc),
  FieldType varchar(1) ('P' = Payment), Type varchar(2) ('Dr'),
  Active varchar(3).
VB6 evidence: fdPaymentCharge.frm uses RevMast WHERE PayType<>''
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
LIMITS = {"code": 6, "name": 50, "paytype": 15}
SELECT_COLS = "Code, Name, ShortName, PAYTYPE, FieldType, Type, Active"


def _map(r) -> dict:
    try:
        return {
            "code": r.Code, "name": (r.Name or "").strip(),
            "short": (r.ShortName or "").strip(),
            "paytype": r.PAYTYPE or "",
            "fieldtype": r.FieldType or "",
            "type": r.Type or "",
            "active": r.Active or "Y",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        c, n, sn, pt, ft, tp, act = r
        return {
            "code": c, "name": (n or "").strip(),
            "short": (sn or "").strip(), "paytype": pt or "",
            "fieldtype": ft or "", "type": tp or "",
            "active": act or "Y",
            "u_name": "", "u_ae": "",
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
    if len(rec.get("paytype", "")) > LIMITS["paytype"]:
        raise ValueError(f"PayType max {LIMITS['paytype']} chars")


def list_all(cn=None) -> list[dict]:
    """List payment types (RevMast rows where PAYTYPE is not empty)."""
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM RevMast "
        "WHERE PAYTYPE IS NOT NULL AND PAYTYPE != '' ORDER BY Name", cn=cn)
    return [_map(r) for r in rows]


def get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM RevMast WHERE Code = ? AND PAYTYPE IS NOT NULL",
        (code,), cn=cn)
    return _map(rows[0]) if rows else None


def exists(code: str, cn=None) -> bool:
    return bool(db.query(
        "SELECT 1 FROM RevMast WHERE Code = ? AND PAYTYPE IS NOT NULL",
        (code,), cn=cn))


def insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    db.require_absent("RevMast", "Code", rec["code"], "Payment Type Code")
    return db.execute(
        "INSERT INTO RevMast (Code, Name, ShortName, PAYTYPE, FieldType, "
        "Type, Active, Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"], rec.get("short", ""),
         rec.get("paytype", ""), rec.get("fieldtype", "P"),
         rec.get("type", "Dr"), rec.get("active", "Y"),
         SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def update(code: str, rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    return db.execute(
        "UPDATE RevMast SET Name = ?, ShortName = ?, PAYTYPE = ?, "
        "FieldType = ?, Type = ?, Active = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec["name"], rec.get("short", ""), rec.get("paytype", ""),
         rec.get("fieldtype", "P"), rec.get("type", "Dr"),
         rec.get("active", "Y"), USER, code),
        cn=cn, commit=commit)


def delete(code: str, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM RevMast WHERE Code = ? AND PAYTYPE IS NOT NULL",
        (code,), cn=cn, commit=commit)
