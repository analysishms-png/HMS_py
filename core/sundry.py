"""SundryMast CRUD (VB6: FrmTaxMast.frm, DepartSundry.frm inhe use karte hain).
Schema evidence: Code varchar(6), Name varchar(20) NULL, Nature varchar(20)
NOT NULL, CalcSign varchar(1), SysYN varchar(1) + audit cols.
NOT NULL: Code, Nature.  Sample codes: KK0002, KKADD, KKADV (prefix KK).
Audit pattern VB6 jaisa: U_Name + U_EntDt(getdate()) + U_AE ('A'/'E').
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
LIMITS = {"code": 6, "name": 20, "nature": 20, "calc": 1}
SELECT_COLS = "Code, Name, Nature, CalcSign, SysYN, U_Name, U_EntDt, U_AE"


def _map(r) -> dict:
    return {"code": r.Code, "name": r.Name or "", "nature": r.Nature,
            "calc": r.CalcSign or "", "sysyn": r.SysYN or "",
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
    if len(rec.get("nature", "")) > LIMITS["nature"]:
        raise ValueError(f"Nature max {LIMITS['nature']} chars")
    if not rec.get("nature", "").strip():
        raise ValueError("Nature zaroori hai (NOT NULL)")
    if len(rec.get("calc", "")) > LIMITS["calc"]:
        raise ValueError(f"CalcSign max {LIMITS['calc']} char")


def list_all(cn=None) -> list[dict]:
    rows = db.query(f"SELECT {SELECT_COLS} FROM SundryMast WHERE (LOGSITE_CODE = ? OR LOGSITE_CODE = 'HO' OR ISNULL(LOGSITE_CODE,'')='') ORDER BY Code",
                    cn=cn)
    return [_map(r) for r in rows]


def get(code: str, cn=None) -> dict | None:
    rows = db.query(f"SELECT {SELECT_COLS} FROM SundryMast WHERE Code = ?",
                    (code,), cn=cn)
    return _map(rows[0]) if rows else None


def exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM SundryMast WHERE Code = ?",
                         (code,), cn=cn))


def insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    db.require_absent("SundryMast", "Code", rec["code"],
              "Sundry Code")
    return db.execute(
        "INSERT INTO SundryMast (Code, Name, Nature, CalcSign, SysYN, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"], rec["nature"], rec.get("calc", ""),
         rec.get("sysyn", ""), SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def update(code: str, rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    return db.execute(
        "UPDATE SundryMast SET Name = ?, Nature = ?, CalcSign = ?, "
        "SysYN = ?, U_Name = ?, U_EntDt = getdate(), U_AE = 'E' "
        "WHERE Code = ?",
        (rec["name"], rec["nature"], rec.get("calc", ""),
         rec.get("sysyn", ""), USER, code),
        cn=cn, commit=commit)


def delete(code: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM SundryMast WHERE Code = ?", (code,),
                      cn=cn, commit=commit)
