"""Year-End Procedures (VB6: Year-end closing logic).

Tables used:
- SubGroupCurrBal: Current balance per subgroup
- ACGroupCurrBal: Current balance per account group
- LedgerLog: Ledger audit log
- LedgerMLog: Ledger master audit log
- LastVoucher: Last voucher tracking
- Budget: Budget master

Note: Company table in DB is a SQL Server Profiler trace table, NOT settings.
Year-end logic operates on financial data tables directly.

VB6 Pattern: Year-end closing involves:
1. Lock date checking (DATELOCK table)
2. Balance carry-forward (SubGroupCurrBal + ACGroupCurrBal)
3. Budget reset for new FY
4. Voucher prefix reset (VOUCHER_Prefix)
5. LastVoucher reset
"""
from __future__ import annotations

import datetime

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()


def get_fy_dates(fy_year: str = None, cn=None) -> dict:
    """Get financial year date range.
    Default: current FY (Apr 1 to Mar 31).
    fy_year format: '2025-26' -> 2025-04-01 to 2026-03-31
    """
    today = datetime.date.today()
    if fy_year:
        parts = fy_year.split("-")
        start_year = int(parts[0])
        end_year = start_year + 1
    else:
        if today.month >= 4:
            start_year = today.year
            end_year = today.year + 1
        else:
            start_year = today.year - 1
            end_year = today.year
    return {
        "fy": f"{start_year}-{str(end_year % 100).zfill(2)}",
        "start": datetime.date(start_year, 4, 1),
        "end": datetime.date(end_year, 3, 31),
    }


def check_datelock(vdate, cn=None) -> bool:
    """Check if date is locked (VB6 pattern: check DATELOCK before any entry).
    Returns True if date is LOCKED (entry not allowed).
    """
    rows = db.query(
        "SELECT TOP 1 flag FROM DATELOCK WHERE SDate <= ? AND EDate >= ? "
        "AND flag = 1",
        (vdate, vdate), cn=cn)
    return bool(rows)


def get_subgroup_balances(fy_start=None, fy_end=None,
                          cn=None, limit: int = 1000) -> list[dict]:
    """Get all subgroup current balances for year-end report."""
    sql = f"SELECT TOP {int(limit)} LogSite_Code, SubCode, V_Date, GroupCode, " \
          "Curr_Bal, Site_Code FROM SubGroupCurrBal WHERE LogSite_Code = ? "
    params: list = [SITE_CODE]
    if fy_start:
        sql += "AND V_Date >= ? "
        params.append(fy_start)
    if fy_end:
        sql += "AND V_Date <= ? "
        params.append(fy_end)
    sql += "ORDER BY SubCode"
    rows = db.query(sql, tuple(params), cn=cn)
    return [{"logsite": r[0], "subcode": r[1], "v_date": r[2],
             "groupcode": r[3], "curr_bal": float(r[4] or 0),
             "site_code": r[5]} for r in rows]


def get_acgroup_balances(fy_start=None, fy_end=None,
                         cn=None, limit: int = 500) -> list[dict]:
    """Get all account group current balances for year-end report."""
    sql = f"SELECT TOP {int(limit)} LogSite_Code, GroupCode, V_Date, " \
          "Curr_Bal, Site_Code FROM ACGroupCurrBal WHERE LogSite_Code = ? "
    params: list = [SITE_CODE]
    if fy_start:
        sql += "AND V_Date >= ? "
        params.append(fy_start)
    if fy_end:
        sql += "AND V_Date <= ? "
        params.append(fy_end)
    sql += "ORDER BY GroupCode"
    rows = db.query(sql, tuple(params), cn=cn)
    return [{"logsite": r[0], "groupcode": r[1], "v_date": r[2],
             "curr_bal": float(r[3] or 0), "site_code": r[4]} for r in rows]


def carry_forward_balances(new_fy_start, user: str = USER,
                           cn=None, commit: bool = True) -> dict:
    """Year-end balance carry-forward.
    1. Snapshot current balances
    2. Reset for new FY (set V_Date to new FY start)
    VB6 pattern: balances carry forward with V_Date = new FY start.
    """
    own = cn is None
    cn = cn or db.connect()
    try:
        # Update SubGroupCurrBal V_Date to new FY start
        n_sub = db.execute(
            "UPDATE SubGroupCurrBal SET V_Date = ? "
            "WHERE LogSite_Code = ?",
            (new_fy_start, SITE_CODE), cn=cn, commit=False)

        # Update ACGroupCurrBal V_Date to new FY start
        n_ac = db.execute(
            "UPDATE ACGroupCURRBal SET V_Date = ? "
            "WHERE LogSite_Code = ?",
            (new_fy_start, SITE_CODE), cn=cn, commit=False)

        # Reset LastVoucher for new FY
        db.execute(
            "UPDATE LastVoucher SET Last_Ent_Date = NULL, DocId = NULL, "
            "v_Prefix = NULL WHERE Site_Code = ?",
            (SITE_CODE,), cn=cn, commit=False)

        if commit:
            cn.commit()
        return {"subgroup_updated": n_sub, "acgroup_updated": n_ac}
    finally:
        if own:
            cn.close()


def reset_budget(new_fy_start, new_fy_end, user: str = USER,
                 cn=None, commit: bool = True) -> int:
    """Reset budget for new FY (copy existing budget with new dates)."""
    # Get existing budget
    rows = db.query(
        "SELECT FromDate, ToDate, SrNo, AcCode, AcGroupCode, "
        "BudgetDRAmt, BudgetCRAmt FROM Budget WHERE Site_Code = ?",
        (SITE_CODE,), cn=cn)
    if not rows:
        return 0

    own = cn is None
    cn = cn or db.connect()
    try:
        # Delete old budget
        db.execute(
            "DELETE FROM Budget WHERE Site_Code = ?",
            (SITE_CODE,), cn=cn, commit=False)

        # Insert with new FY dates
        count = 0
        for r in rows:
            db.execute(
                "INSERT INTO Budget (FromDate, ToDate, SrNo, AcCode, "
                "AcGroupCode, BudgetDRAmt, BudgetCRAmt, U_Name, "
                "U_EntDt, U_AE, Site_Code, LogSite_Code) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?, ?)",
                (new_fy_start, new_fy_end, r[2], r[3] or "", r[4] or "",
                 float(r[5] or 0), float(r[6] or 0),
                 user, SITE_CODE, SITE_CODE),
                cn=cn, commit=False)
            count += 1

        if commit:
            cn.commit()
        return count
    finally:
        if own:
            cn.close()


def year_end_summary(cn=None) -> dict:
    """Year-end summary report.
    Returns balances and statistics for year-end review.
    """
    fy = get_fy_dates(cn=cn)

    # Subgroup balances
    sub_bals = get_subgroup_balances(fy["start"], fy["end"], cn=cn)
    total_dr = sum(b["curr_bal"] for b in sub_bals if b["curr_bal"] > 0)
    total_cr = sum(abs(b["curr_bal"]) for b in sub_bals if b["curr_bal"] < 0)

    # ACGroup balances
    ac_bals = get_acgroup_balances(fy["start"], fy["end"], cn=cn)

    # Last voucher info
    last_vous = db.query(
        "SELECT user_name, V_Type, Last_Ent_Date, DocId "
        "FROM LastVoucher WHERE Site_Code = ?",
        (SITE_CODE,), cn=cn)

    return {
        "fy": fy,
        "subgroup_count": len(sub_bals),
        "total_dr": total_dr,
        "total_cr": total_cr,
        "balance": total_dr - total_cr,
        "acgroup_count": len(ac_bals),
        "last_vouchers": [{"user": r[0], "vtype": r[1],
                           "date": r[2], "docid": r[3]}
                          for r in last_vous],
    }


class _YearEndAPI:
    @staticmethod
    def get_fy_dates(fy_year=None, cn=None): return get_fy_dates(fy_year, cn)
    @staticmethod
    def check_datelock(vdate, cn=None): return check_datelock(vdate, cn)
    @staticmethod
    def get_subgroup_balances(fy_start=None, fy_end=None, cn=None, limit=1000):
        return get_subgroup_balances(fy_start, fy_end, cn, limit)
    @staticmethod
    def get_acgroup_balances(fy_start=None, fy_end=None, cn=None, limit=500):
        return get_acgroup_balances(fy_start, fy_end, cn, limit)
    @staticmethod
    def carry_forward_balances(new_fy_start, user=USER, cn=None, commit=True):
        return carry_forward_balances(new_fy_start, user, cn, commit)
    @staticmethod
    def reset_budget(new_fy_start, new_fy_end, user=USER, cn=None, commit=True):
        return reset_budget(new_fy_start, new_fy_end, user, cn, commit)
    @staticmethod
    def year_end_summary(cn=None): return year_end_summary(cn)

YearEndAPI = _YearEndAPI()
