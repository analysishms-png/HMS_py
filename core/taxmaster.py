# P0 FIX HO fallback pending - master SELECT should add WHERE (LOGSITE_CODE=? OR HO)
"""Tax Master CRUD (VB6: FrmTaxMast - Main Setup -> General Setup).

Schema: RevMast table filtered by FieldType='T' (NOT TaxStru, NOT TaxMast).
  Code varchar(6) PK, Name varchar(50), ShortName varchar(5),
  ACCode varchar(8) FK->SubGroup (ledger), PayableAc, UnregisteredAc,
  Sundry varchar(6), RoundOff varchar(3), Nature varchar(20),
  Active varchar(3), SysYN varchar(1), TaxStru varchar(6),
  Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code.
VB6 FrmTaxMast.frm evidence:
  SELECT ... FROM RevMast WHERE FieldType='T'
  INSERT INTO RevMast(..., FieldType, ...) VALUES (..., 'T', ...)
  SYSTEM ENTRY (SysYN='Y') can't be deleted.
Tax Structure lines live separately in TaxStru (see taxstru.py).
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
LIMITS = {
    "code": 6, "name": 50, "short": 5, "accode": 8, "payableac": 8,
    "unregisteredac": 8, "sundry": 6, "roundoff": 3, "nature": 20,
    "active": 3, "taxstru": 6,
}
SELECT_COLS = (
    "Code, Name, ShortName, ACCode, PayableAc, UnregisteredAc, Sundry, "
    "RoundOff, Nature, Active, TaxStru, SysYN"
)


def _map(r) -> dict:
    try:
        return {
            "code": r.Code,
            "name": (r.Name or "").strip(),
            "short": (r.ShortName or "").strip(),
            "accode": r.ACCode or "",
            "payableac": r.PayableAc or "",
            "unregisteredac": r.UnregisteredAc or "",
            "sundry": r.Sundry or "",
            "roundoff": r.RoundOff or "No",
            "nature": r.Nature or "",
            "active": r.Active or "Y",
            "taxstru": r.TaxStru or "",
            "sysyn": r.SysYN or "N",
        }
    except AttributeError:
        c, n, sn, ac, pa, ua, su, ro, na, act, ts, sy = r
        return {
            "code": c, "name": (n or "").strip(), "short": (sn or "").strip(),
            "accode": ac or "", "payableac": pa or "", "unregisteredac": ua or "",
            "sundry": su or "", "roundoff": ro or "No", "nature": na or "",
            "active": act or "Y", "taxstru": ts or "", "sysyn": sy or "N",
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
    if len(rec.get("short", "")) > LIMITS["short"]:
        raise ValueError(f"ShortName max {LIMITS['short']} chars")
    if len(rec.get("nature", "")) > LIMITS["nature"]:
        raise ValueError(f"Nature max {LIMITS['nature']} chars")


def list_all(cn=None) -> list[dict]:
    """List tax masters (RevMast rows where FieldType='T')."""
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM RevMast "
        "WHERE FieldType = ? ORDER BY Name",
        ("T",), cn=cn)
    return [_map(r) for r in rows]


def get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM RevMast "
        "WHERE Code = ? AND FieldType = ?",
        (code, "T"), cn=cn)
    return _map(rows[0]) if rows else None


def exists(code: str, cn=None) -> bool:
    return bool(db.query(
        "SELECT 1 FROM RevMast WHERE Code = ? AND FieldType = ?",
        (code, "T"), cn=cn))


def insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    db.require_absent("RevMast", "Code", rec["code"], "Tax Code")
    return db.execute(
        "INSERT INTO RevMast (Code, Name, ShortName, ACCode, PayableAc, "
        "UnregisteredAc, Sundry, RoundOff, Nature, Active, TaxStru, "
        "FieldType, Type, SysYN, Site_Code, U_Name, U_EntDt, U_AE, "
        "LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'T', 'Cr', 'N', ?, ?, "
        "getdate(), 'A', ?)",
        (rec["code"], rec["name"], rec.get("short", ""),
         rec.get("accode", ""), rec.get("payableac", ""),
         rec.get("unregisteredac", ""), rec.get("sundry", ""),
         rec.get("roundoff", "No"), rec.get("nature", ""),
         rec.get("active", "Y"), rec.get("taxstru", ""),
         SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def update(code: str, rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    return db.execute(
        "UPDATE RevMast SET Name = ?, ShortName = ?, ACCode = ?, "
        "PayableAc = ?, UnregisteredAc = ?, Sundry = ?, RoundOff = ?, "
        "Nature = ?, Active = ?, TaxStru = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' "
        "WHERE Code = ? AND FieldType = ?",
        (rec["name"], rec.get("short", ""), rec.get("accode", ""),
         rec.get("payableac", ""), rec.get("unregisteredac", ""),
         rec.get("sundry", ""), rec.get("roundoff", "No"),
         rec.get("nature", ""), rec.get("active", "Y"),
         rec.get("taxstru", ""), USER, code, "T"),
        cn=cn, commit=commit)


def delete(code: str, cn=None, commit: bool = True) -> int:
    """Delete tax master. System entries (SysYN='Y') protected (VB6)."""
    rows = db.query(
        "SELECT SysYN FROM RevMast WHERE Code = ? AND FieldType = ?",
        (code, "T"), cn=cn)
    if rows and (rows[0][0] or "").strip().upper() == "Y":
        raise ValueError("SYSTEM ENTRY CAN'T BE DELETED")
    return db.execute(
        "DELETE FROM RevMast WHERE Code = ? AND FieldType = ?",
        (code, "T"), cn=cn, commit=commit)
