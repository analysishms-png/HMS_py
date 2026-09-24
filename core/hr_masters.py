"""HR / Payroll Masters (VB6: Main Setup -> HR/Payroll).

Database evidence (live HMS):
- EmpCategory: Employee categories - EXISTS (4 rows)
  Schema: Code varchar(6) PK, Name varchar(30), Type varchar(10),
  Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code
- Holiday: Holiday calendar - EXISTS (0 rows, seasonal)
  Schema: Vdate datetime PK, Remarks varchar(100),
  Site_Code, U_name varchar(10), U_EntDt, U_AE, LogSite_Code
  NOTE: PK = date itself (one row per holiday)
- Employee: Full employee master - EXISTS (120 rows)
  Schema: Code varchar(6) PK, Name varchar(50), Sex varchar(1),
  Designation varchar(30), Category varchar(6) FK->EmpCategory,
  F_Name varchar(50), Birth_Date datetime, Add1/Add2 varchar(50),
  Marital varchar(10), Joining_Date datetime, Resign_Date datetime,
  ESI_Code varchar(20), PF_Code varchar(20),
  Basic/DA/HRA/Income_Tax/Other_Allow/Other_Deduc float,
  Phone varchar(20), PAN varchar(15), AC_Code varchar(10),
  BankAcNo varchar(30), Department varchar(6), ActiveYN varchar(1),
  Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code

NOTE: DesignationMast table does NOT exist (Designation is varchar field
in Employee). Category table exists but is VB6-era, EmpCategory is used.
"""
from __future__ import annotations

import datetime
from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()


# ============================================================
# Employee Category Master
# ============================================================
EMPCAT_LIMITS = {"code": 6, "name": 30, "type": 10}
EMPCAT_COLS = "Code, Name, Type, U_Name, U_EntDt, U_AE"


def _map_empcat(r) -> dict:
    try:
        return {"code": r.Code, "name": (r.Name or "").strip(),
                "type": r.Type or "",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        c, n, t, un, _, uae = r
        return {"code": c, "name": (n or "").strip(), "type": t or "",
                "u_name": un or "", "u_ae": uae or ""}


def empcat_list(cn=None) -> list[dict]:
    return [_map_empcat(r) for r in db.query(
        f"SELECT {EMPCAT_COLS} FROM EmpCategory ORDER BY Code", cn=cn)]


def empcat_get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {EMPCAT_COLS} FROM EmpCategory WHERE Code = ?", (code,), cn=cn)
    return _map_empcat(rows[0]) if rows else None


def empcat_exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM EmpCategory WHERE Code = ?", (code,), cn=cn))


def empcat_insert(rec: dict, cn=None, commit=True) -> int:
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "INSERT INTO EmpCategory (Code, Name, Type, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"], rec.get("type", ""),
         SITE_CODE, USER, SITE_CODE), cn=cn, commit=commit)


def empcat_update(code: str, rec: dict, cn=None, commit=True) -> int:
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "UPDATE EmpCategory SET Name = ?, Type = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec["name"], rec.get("type", ""), USER, code), cn=cn, commit=commit)


def empcat_delete(code: str, cn=None, commit=True) -> int:
    return db.execute(
        "DELETE FROM EmpCategory WHERE Code = ?", (code,), cn=cn, commit=commit)


class _EmpCatAPI:
    LIMITS = EMPCAT_LIMITS
    @staticmethod
    def list_all(cn=None): return empcat_list(cn)
    @staticmethod
    def get(code, cn=None): return empcat_get(code, cn)
    @staticmethod
    def exists(code, cn=None): return empcat_exists(code, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return empcat_insert(rec, cn, commit)
    @staticmethod
    def update(code, rec, cn=None, commit=True): return empcat_update(code, rec, cn, commit)
    @staticmethod
    def delete(code, cn=None, commit=True): return empcat_delete(code, cn, commit)

EmpCatAPI = _EmpCatAPI()


# ============================================================
# Holiday Master (Vdate = PK, one row per holiday)
# ============================================================
HOLIDAY_COLS = "Vdate, Remarks, U_name, U_EntDt, U_AE"


def _map_holiday(r) -> dict:
    def _dt(v):
        if v is None: return None
        return v.date() if isinstance(v, datetime.datetime) else v
    try:
        return {"code": str(_dt(r.Vdate) or ""), "name": (r.Remarks or "").strip(),
                "vdate": _dt(r.Vdate),
                "u_name": r.U_name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        vd, rem, un, _, uae = r
        return {"code": str(_dt(vd) or ""), "name": (rem or "").strip(),
                "vdate": _dt(vd),
                "u_name": un or "", "u_ae": uae or ""}


def holiday_list(cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {HOLIDAY_COLS} FROM Holiday ORDER BY Vdate DESC", cn=cn)
    return [_map_holiday(r) for r in rows]


def holiday_get(vdate_str: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {HOLIDAY_COLS} FROM Holiday WHERE CONVERT(varchar,Vdate,23) = ?",
        (vdate_str,), cn=cn)
    return _map_holiday(rows[0]) if rows else None


def holiday_exists(vdate_str: str, cn=None) -> bool:
    return bool(db.query(
        "SELECT 1 FROM Holiday WHERE CONVERT(varchar,Vdate,23) = ?",
        (vdate_str,), cn=cn))


def holiday_insert(rec: dict, cn=None, commit=True) -> int:
    """rec: {code: 'YYYY-MM-DD', name: remarks}"""
    vdate = rec.get("code") or rec.get("vdate")
    if not vdate:
        raise ValueError("Date zaroori hai (YYYY-MM-DD format)")
    remarks = rec.get("name") or rec.get("remarks", "")
    return db.execute(
        "INSERT INTO Holiday (Vdate, Remarks, Site_Code, "
        "U_name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, getdate(), 'A', ?)",
        (vdate, remarks, SITE_CODE, USER, SITE_CODE), cn=cn, commit=commit)


def holiday_update(vdate_str: str, rec: dict, cn=None, commit=True) -> int:
    remarks = rec.get("name") or rec.get("remarks", "")
    return db.execute(
        "UPDATE Holiday SET Remarks = ?, U_name = ?, "
        "U_EntDt = getdate(), U_AE = 'E' "
        "WHERE CONVERT(varchar,Vdate,23) = ?",
        (remarks, USER, vdate_str), cn=cn, commit=commit)


def holiday_delete(vdate_str: str, cn=None, commit=True) -> int:
    return db.execute(
        "DELETE FROM Holiday WHERE CONVERT(varchar,Vdate,23) = ?",
        (vdate_str,), cn=cn, commit=commit)


class _HolidayAPI:
    LIMITS = {"code": 10, "name": 100}
    pk_key = "code"
    @staticmethod
    def list_all(cn=None): return holiday_list(cn)
    @staticmethod
    def get(code, cn=None): return holiday_get(code, cn)
    @staticmethod
    def exists(code, cn=None): return holiday_exists(code, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return holiday_insert(rec, cn, commit)
    @staticmethod
    def update(code, rec, cn=None, commit=True): return holiday_update(code, rec, cn, commit)
    @staticmethod
    def delete(code, cn=None, commit=True): return holiday_delete(code, cn, commit)

HolidayAPI = _HolidayAPI()


# ============================================================
# Employee Master (full payroll data - READ/BROWSE + basic edit)
# ============================================================
EMP_LIMITS = {"code": 6, "name": 50, "designation": 30,
              "category": 6, "dept": 6, "phone": 20, "pan": 15}
EMP_BROWSE_COLS = ("Code, Name, Sex, Designation, Category, Department, "
                   "Joining_Date, Resign_Date, Phone, PAN, ActiveYN, "
                   "U_Name, U_EntDt, U_AE")


def _map_emp(r) -> dict:
    def _dt(v):
        if v is None: return None
        return v.date() if isinstance(v, datetime.datetime) else v
    try:
        return {"code": r.Code, "name": (r.Name or "").strip(),
                "sex": r.Sex or "", "designation": (r.Designation or "").strip(),
                "category": r.Category or "", "dept": r.Department or "",
                "joining": _dt(r.Joining_Date), "resign": _dt(r.Resign_Date),
                "phone": (r.Phone or "").strip(), "pan": (r.PAN or "").strip(),
                "active": r.ActiveYN or "Y",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        c, n, sx, des, cat, dep, jd, rd, ph, pan, act, un, _, uae = r
        return {"code": c, "name": (n or "").strip(), "sex": sx or "",
                "designation": (des or "").strip(), "category": cat or "",
                "dept": dep or "",
                "joining": _dt(jd), "resign": _dt(rd),
                "phone": (ph or "").strip(), "pan": (pan or "").strip(),
                "active": act or "Y", "u_name": un or "", "u_ae": uae or ""}


def emp_list(cn=None, top: int = 300) -> list[dict]:
    return [_map_emp(r) for r in db.query(
        f"SELECT TOP {int(top)} {EMP_BROWSE_COLS} FROM Employee ORDER BY Code",
        cn=cn)]


def emp_get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {EMP_BROWSE_COLS} FROM Employee WHERE Code = ?", (code,), cn=cn)
    return _map_emp(rows[0]) if rows else None


def emp_exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM Employee WHERE Code = ?", (code,), cn=cn))


def emp_insert(rec: dict, cn=None, commit=True) -> int:
    """Minimal insert - core HR fields only."""
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    join_date = rec.get("joining") or datetime.date.today()
    return db.execute(
        "INSERT INTO Employee (Code, Name, Sex, Designation, Category, "
        "Department, Joining_Date, Phone, PAN, ActiveYN, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"], rec.get("sex", ""),
         rec.get("designation", ""), rec.get("category", ""),
         rec.get("dept", ""), join_date,
         rec.get("phone", ""), rec.get("pan", ""),
         rec.get("active", "Y"), SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def emp_update(code: str, rec: dict, cn=None, commit=True) -> int:
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "UPDATE Employee SET Name = ?, Sex = ?, Designation = ?, "
        "Category = ?, Department = ?, Phone = ?, PAN = ?, ActiveYN = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec["name"], rec.get("sex", ""), rec.get("designation", ""),
         rec.get("category", ""), rec.get("dept", ""),
         rec.get("phone", ""), rec.get("pan", ""),
         rec.get("active", "Y"), USER, code), cn=cn, commit=commit)


def emp_delete(code: str, cn=None, commit=True) -> int:
    if not code.upper().startswith("PYT"):
        raise ValueError("Safety: sirf PYT* test employees delete ho sakte hain")
    return db.execute(
        "DELETE FROM Employee WHERE Code = ?", (code,), cn=cn, commit=commit)


class _EmployeeAPI:
    LIMITS = EMP_LIMITS
    @staticmethod
    def list_all(cn=None): return emp_list(cn)
    @staticmethod
    def get(code, cn=None): return emp_get(code, cn)
    @staticmethod
    def exists(code, cn=None): return emp_exists(code, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return emp_insert(rec, cn, commit)
    @staticmethod
    def update(code, rec, cn=None, commit=True): return emp_update(code, rec, cn, commit)
    @staticmethod
    def delete(code, cn=None, commit=True): return emp_delete(code, cn, commit)

EmployeeAPI = _EmployeeAPI()


# ============================================================
# Designation Master
# Table: Desig - Code varchar PK, Name varchar, audit cols
# ============================================================
DESIG_LIMITS = {"code": 6, "name": 30}
DESIG_COLS = "Code, Name, U_Name, U_EntDt, U_AE"


def _map_desig(r) -> dict:
    try:
        return {"code": r.Code, "name": (r.Name or "").strip(),
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        c, n, un, _, uae = r
        return {"code": c, "name": (n or "").strip(),
                "u_name": un or "", "u_ae": uae or ""}


def desig_list(cn=None) -> list[dict]:
    return [_map_desig(r) for r in db.query(
        f"SELECT {DESIG_COLS} FROM Desig ORDER BY Code", cn=cn)]


def desig_get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {DESIG_COLS} FROM Desig WHERE Code = ?", (code,), cn=cn)
    return _map_desig(rows[0]) if rows else None


def desig_exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM Desig WHERE Code = ?", (code,), cn=cn))


def desig_insert(rec: dict, cn=None, commit=True) -> int:
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "INSERT INTO Desig (Code, Name, Site_Code, U_Name, U_EntDt, "
        "U_AE, LogSite_Code) VALUES (?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"], SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def desig_update(code: str, rec: dict, cn=None, commit=True) -> int:
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "UPDATE Desig SET Name = ?, U_Name = ?, U_EntDt = getdate(), "
        "U_AE = 'E' WHERE Code = ?",
        (rec["name"], USER, code), cn=cn, commit=commit)


def desig_delete(code: str, cn=None, commit=True) -> int:
    return db.execute(
        "DELETE FROM Desig WHERE Code = ?", (code,), cn=cn, commit=commit)


class _DesigAPI:
    LIMITS = DESIG_LIMITS
    @staticmethod
    def list_all(cn=None): return desig_list(cn)
    @staticmethod
    def get(code, cn=None): return desig_get(code, cn)
    @staticmethod
    def exists(code, cn=None): return desig_exists(code, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return desig_insert(rec, cn, commit)
    @staticmethod
    def update(code, rec, cn=None, commit=True): return desig_update(code, rec, cn, commit)
    @staticmethod
    def delete(code, cn=None, commit=True): return desig_delete(code, cn, commit)

DesigAPI = _DesigAPI()
