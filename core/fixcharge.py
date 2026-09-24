"""Fixed Charge master CRUD (VB6: 'Charge Master' - Main Setup).

Schema evidence (live): FixedCharge: Code varchar(5) PK, Name varchar(30),
SName varchar(5), Revcode varchar(6), TaxInc varchar(3), TaxStru varchar(6),
PrintOption varchar(20), PostingMethod varchar(20), ChargeType varchar(20),
FlatRate float, Adult float, Child float... (1 live row).
NOTE: Site_Code/U_* audit cols schema me NahiN mile (minimal INSERT me
sirf data cols bhararte hain - evidence-first, extra guess nahi).
Audit pattern (jo cols hain): U_Name + U_EntDt(getdate()) + U_AE.
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
LIMITS = {"code": 5, "name": 30, "sname": 5, "revcode": 6, "taxinc": 3,
          "taxstru": 6, "printoption": 20, "postingmethod": 20,
          "chargetype": 20}
SELECT_COLS = ("Code, Name, SName, Revcode, TaxInc, TaxStru, "
               "PrintOption, PostingMethod, ChargeType, FlatRate, "
               "U_Name, U_EntDt, U_AE")


def _map(r) -> dict:
    return {"code": r.Code, "name": (r.Name or "").strip(),
            "sname": (r.SName or "").strip(),
            "revcode": r.Revcode or "", "taxinc": r.TaxInc or "",
            "taxstru": r.TaxStru or "",
            "printoption": r.PrintOption or "",
            "postingmethod": r.PostingMethod or "",
            "chargetype": r.ChargeType or "",
            "flatrate": r.FlatRate or 0.0,
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
    for k, lim in LIMITS.items():
        if k not in ("code", "name") and len(rec.get(k, "")) > lim:
            raise ValueError(f"{k} max {lim} chars")


def list_all(cn=None) -> list[dict]:
    rows = db.query(f"SELECT {SELECT_COLS} FROM FixedCharge ORDER BY Code",
                    cn=cn)
    return [_map(r) for r in rows]


def get(code: str, cn=None) -> dict | None:
    rows = db.query(f"SELECT {SELECT_COLS} FROM FixedCharge WHERE Code = ?",
                    (code,), cn=cn)
    return _map(rows[0]) if rows else None


def exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM FixedCharge WHERE Code = ?",
                         (code,), cn=cn))


def insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    db.require_absent("FixedCharge", "Code", rec["code"], "Fixed Charge Code")
    return db.execute(
        "INSERT INTO FixedCharge (Code, Name, SName, Revcode, TaxInc, "
        "TaxStru, PrintOption, PostingMethod, ChargeType, FlatRate, "
        "U_Name, U_EntDt, U_AE) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A')",
        (rec["code"], rec["name"], rec.get("sname", ""),
         rec.get("revcode", ""), rec.get("taxinc", ""),
         rec.get("taxstru", ""), rec.get("printoption", ""),
         rec.get("postingmethod", ""), rec.get("chargetype", ""),
         float(rec.get("flatrate") or 0.0), USER), cn=cn, commit=commit)


def update(code: str, rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    return db.execute(
        "UPDATE FixedCharge SET Name = ?, SName = ?, Revcode = ?, "
        "TaxInc = ?, TaxStru = ?, PrintOption = ?, PostingMethod = ?, "
        "ChargeType = ?, FlatRate = ?, U_Name = ?, U_EntDt = getdate(), "
        "U_AE = 'E' WHERE Code = ?",
        (rec["name"], rec.get("sname", ""), rec.get("revcode", ""),
         rec.get("taxinc", ""), rec.get("taxstru", ""),
         rec.get("printoption", ""), rec.get("postingmethod", ""),
         rec.get("chargetype", ""), float(rec.get("flatrate") or 0.0),
         USER, code), cn=cn, commit=commit)


def delete(code: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM FixedCharge WHERE Code = ?", (code,),
                      cn=cn, commit=commit)
