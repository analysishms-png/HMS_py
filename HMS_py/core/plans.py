"""PlanMast CRUD (Company-Plan master) - CompMast.frm ke SQL pattern par.
Table: PlanMast (Code, Name, Total, Site_Code, U_Name, U_EntDt, U_AE...)
Audit fields VB6 jaise hi: U_Name + U_EntDt(getdate()) + U_AE ('A'/'E').
Code VB6 me 'P' prefix hota tha (evidence: CompMast Proc_22_79 SQL).
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")  # Analysis.ini key 7
USER = db.get_user()
# Column limits (schema evidence): Code varchar(5), Name varchar(25),
# Plan_Package varchar(7), U_Name varchar(10), ActiveYN varchar(3)
LIMITS = {"code": 5, "name": 25, "package": 7}


def list_plans(cn=None) -> list:
    return db.query(
        "SELECT Code, Name, Total, Plan_Package, ActiveYN FROM PlanMast "
        "ORDER BY Code", cn=cn)


# Alias for standard UI interface (same as list_plans)
def list_all(cn=None) -> list:
    """Standard list_all alias - UI modules use this."""
    rows = list_plans(cn=cn)
    result = []
    for r in rows:
        try:
            result.append({
                "code": r.Code or "",
                "name": (r.Name or "").strip(),
                "total": float(r.Total or 0),
                "package": r.Plan_Package or "",
                "active": r.ActiveYN or "Y",
            })
        except AttributeError:
            result.append({
                "code": r[0] or "",
                "name": (r[1] or "").strip(),
                "total": float(r[2] or 0),
                "package": r[3] or "",
                "active": r[4] or "Y",
            })
    return result


def get(code: str, cn=None):
    rows = db.query(
        "SELECT Code, Name, Total, Plan_Package, PercentApp, ActiveYN, "
        "U_Name, U_EntDt, U_AE "
        "FROM PlanMast WHERE Code = ?", (code,), cn=cn)
    return rows[0] if rows else None


def exists(code: str, cn=None) -> bool:
    rows = db.query("SELECT 1 FROM PlanMast WHERE Code = ?", (code,), cn=cn)
    return bool(rows)


def _validate(code: str, name: str, package: str):
    if len(code) > LIMITS["code"]:
        raise ValueError(f"Code max {LIMITS['code']} chars")
    if len(name) > LIMITS["name"]:
        raise ValueError(f"Name max {LIMITS['name']} chars")
    if len(package) > LIMITS["package"]:
        raise ValueError(f"Package max {LIMITS['package']} chars")


def insert(code: str, name: str, total: float, package: str = "",
           active: str = "Y", cn=None, commit: bool = True) -> int:
    """Naya plan. U_AE='A' (Add) - VB6 audit pattern."""
    db.require_absent("PlanMast", "Code", code,
              "Plan Code")
    _validate(code, name, package)
    # NOT NULL cols (schema evidence): Code, App_Date, Tariff
    return db.execute(
        "INSERT INTO PlanMast (Code, Name, Total, Plan_Package, ActiveYN, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code, App_Date, Tariff) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?, getdate(), ?)",
        (code, name, total, package, active, SITE_CODE, USER, SITE_CODE,
         ""),  # Tariff varchar(25) - VB6 me bhi blank default
        cn=cn, commit=commit)


def update(code: str, name: str, total: float, package: str = "",
           active: str = "Y", cn=None, commit: bool = True) -> int:
    """Existing plan update. U_AE='E' (Edit) - VB6 audit pattern."""
    _validate(code, name, package)
    return db.execute(
        "UPDATE PlanMast SET Name = ?, Total = ?, Plan_Package = ?, "
        "ActiveYN = ?, U_Name = ?, U_EntDt = getdate(), U_AE = 'E' "
        "WHERE Code = ?",
        (name, total, package, active, USER, code), cn=cn, commit=commit)


def delete(code: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM PlanMast WHERE Code = ?", (code,),
                      cn=cn, commit=commit)
