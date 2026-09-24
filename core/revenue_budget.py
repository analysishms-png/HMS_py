"""Revenue Group Setting & Budget Entry (VB6: RevenueGroup + BudgetEntry port).
Handles missing tables gracefully for schema compatibility.
"""

from __future__ import annotations
from datetime import date
from HMS_py.core import db

SITE_CODE = db.get_site_code()


def _table_missing_err() -> ValueError:
    return ValueError(
        "RevenueGroup/Budget table not present in this DB. "
        "Feature is disabled for schema compatibility."
    )


def _query_safe(sql: str, params=(), cn=None):
    """Execute query, return empty list if table missing."""
    try:
        return db.query(sql, params, cn=cn)
    except Exception as exc:
        msg = str(exc)
        if ("Invalid object name 'RevenueGroup'" in msg or 
            "Invalid object name 'Budget'" in msg or
            "RevenueGroup" in msg and "does not exist" in msg or
            "Budget" in msg and "does not exist" in msg):
            return []
        raise


# ============================================================
# Revenue Group Table
# ============================================================
def _map_rev_group(r) -> dict:
    try:
        return {
            "rev_code": r.RevCode or "",
            "rev_name": r.RevName or "",
            "group_code": r.GroupCode or "",
            "group_nature": r.GroupNature or "",
            "u_name": r.U_Name or "",
            "u_ae": r.U_AE or "",
        }
    except AttributeError:
        rc, rn, gc, gn, un, _, uae, lgs = r
        return {
            "rev_code": rc or "",
            "rev_name": rn or "",
            "group_code": gc or "",
            "group_nature": gn or "",
            "u_name": un or "",
            "u_ae": uae or "",
        }


def _validate_rev_group(rec: dict):
    if not rec.get("rev_code", "").strip():
        raise ValueError("Rev Code zaroori hai")
    if not rec.get("rev_name", "").strip():
        raise ValueError("Rev Name zaroori hai")


def revenue_group_list(cn=None, limit: int = 500) -> list[dict]:
    rows = _query_safe(
        f"SELECT TOP {int(limit)} RevCode, RevName, GroupCode, GroupNature, "
        "U_Name, U_EntDt, U_AE, LogSite_Code "
        "FROM RevenueGroup ORDER BY RevCode", cn=cn)
    return [_map_rev_group(r) for r in rows]


def revenue_group_get(rev_code: str, cn=None) -> dict | None:
    rows = _query_safe(
        "SELECT RevCode, RevName, GroupCode, GroupNature, "
        "U_Name, U_EntDt, U_AE, LogSite_Code "
        "FROM RevenueGroup WHERE RevCode = ?", (rev_code,), cn=cn)
    return _map_rev_group(rows[0]) if rows else None


def revenue_group_insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate_rev_group(rec)
    # Check if table exists before trying INSERT
    if not _query_safe("SELECT 1 FROM RevenueGroup WHERE 1=0", cn=cn):
        raise _table_missing_err()
    return db.execute(
        "INSERT INTO RevenueGroup (RevCode, RevName, GroupCode, GroupNature, "
        "U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["rev_code"], rec["rev_name"], rec.get("group_code", ""),
         rec.get("group_nature", ""), rec.get("u_name", "PYADMIN"), SITE_CODE),
        cn=cn, commit=commit)


def revenue_group_update(rev_code: str, rec: dict, cn=None, commit: bool = True) -> int:
    _validate_rev_group(rec)
    # Check if table exists
    if not _query_safe("SELECT 1 FROM RevenueGroup WHERE 1=0", cn=cn):
        raise _table_missing_err()
    return db.execute(
        "UPDATE RevenueGroup SET RevName = ?, GroupCode = ?, GroupNature = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'A' "
        "WHERE RevCode = ?",
        (rec["rev_name"], rec.get("group_code", ""), rec.get("group_nature", ""),
         rec.get("u_name", "PYADMIN"), rev_code),
        cn=cn, commit=commit)


def revenue_group_delete(rev_code: str, cn=None, commit: bool = True) -> int:
    # Check if table exists
    if not _query_safe("SELECT 1 FROM RevenueGroup WHERE 1=0", cn=cn):
        raise _table_missing_err()
    return db.execute(
        "DELETE FROM RevenueGroup WHERE RevCode = ?",
        (rev_code,), cn=cn, commit=commit)


# ============================================================
# Budget Table
# PK: FromDate + ToDate + SrNo
# ============================================================
def _map_budget(r) -> dict:
    try:
        return {
            "from_date": r.FromDate,
            "to_date": r.ToDate,
            "sr_no": r.SrNo or 0,
            "group_code": r.GroupCode or "",
            "amount": float(r.Amount or 0),
            "u_name": r.U_Name or "",
            "u_ae": r.U_AE or "",
        }
    except AttributeError:
        fd, td, sn, gc, amt, un, _, uae, lgs = r
        return {
            "from_date": fd,
            "to_date": td,
            "sr_no": sn or 0,
            "group_code": gc or "",
            "amount": float(amt or 0),
            "u_name": un or "",
            "u_ae": uae or "",
        }


def _validate_budget(rec: dict):
    if not rec.get("from_date"):
        raise ValueError("From Date zaroori hai")
    if not rec.get("to_date"):
        raise ValueError("To Date zaroori hai")
    if not rec.get("group_code", "").strip():
        raise ValueError("Group Code zaroori hai")


def budget_list(cn=None, limit: int = 500) -> list[dict]:
    rows = _query_safe(
        f"SELECT TOP {int(limit)} FromDate, ToDate, SrNo, GroupCode, Amount, "
        "U_Name, U_EntDt, U_AE, LogSite_Code "
        "FROM Budget ORDER BY FromDate, ToDate, SrNo", cn=cn)
    return [_map_budget(r) for r in rows]


def budget_get(from_date, to_date, sr_no: int, cn=None) -> dict | None:
    rows = _query_safe(
        "SELECT FromDate, ToDate, SrNo, GroupCode, Amount, "
        "U_Name, U_EntDt, U_AE, LogSite_Code "
        "FROM Budget WHERE FromDate = ? AND ToDate = ? AND SrNo = ?",
        (from_date, to_date, sr_no), cn=cn)
    return _map_budget(rows[0]) if rows else None


def budget_insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate_budget(rec)
    # Check if table exists before trying INSERT
    if not _query_safe("SELECT 1 FROM Budget WHERE 1=0", cn=cn):
        raise _table_missing_err()
    return db.execute(
        "INSERT INTO Budget (FromDate, ToDate, SrNo, GroupCode, Amount, "
        "U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["from_date"], rec["to_date"], rec.get("sr_no", 1),
         rec["group_code"], float(rec.get("amount", 0)),
         rec.get("u_name", "PYADMIN"), SITE_CODE),
        cn=cn, commit=commit)


def budget_delete(from_date, to_date, sr_no: int, cn=None, commit: bool = True) -> int:
    # Check if table exists
    if not _query_safe("SELECT 1 FROM Budget WHERE 1=0", cn=cn):
        raise _table_missing_err()
    return db.execute(
        "DELETE FROM Budget WHERE FromDate = ? AND ToDate = ? AND SrNo = ?",
        (from_date, to_date, sr_no), cn=cn, commit=commit)


# ============================================================
# API Class
# ============================================================
class _RevenueBudgetAPI:
    @staticmethod
    def revenue_group_list(cn=None, limit=500):
        return revenue_group_list(cn, limit)

    @staticmethod
    def revenue_group_get(rev_code, cn=None):
        return revenue_group_get(rev_code, cn)

    @staticmethod
    def revenue_group_insert(rec, cn=None, commit=True):
        return revenue_group_insert(rec, cn, commit)

    @staticmethod
    def revenue_group_update(rev_code, rec, cn=None, commit=True):
        return revenue_group_update(rev_code, rec, cn, commit)

    @staticmethod
    def revenue_group_delete(rev_code, cn=None, commit=True):
        return revenue_group_delete(rev_code, cn, commit)

    @staticmethod
    def budget_list(cn=None, limit=500):
        return budget_list(cn, limit)

    @staticmethod
    def budget_get(from_date, to_date, sr_no, cn=None):
        return budget_get(from_date, to_date, sr_no, cn)

    @staticmethod
    def budget_insert(rec, cn=None, commit=True):
        return budget_insert(rec, cn, commit)

    @staticmethod
    def budget_delete(from_date, to_date, sr_no, cn=None, commit=True):
        return budget_delete(from_date, to_date, sr_no, cn, commit)


REVENUEBUDGET_API = _RevenueBudgetAPI()
