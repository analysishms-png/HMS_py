"""Finance Environment Settings (VB6: FaEnviro - Finance -> FA Parameter).

Table: FAEnviro (58 cols, single-row settings)
- Ageing buckets (Age1-6, Amt1-6)
- Tagada headers/footers (5 headers + 5 footers)
- Credit/Debit limits, display options
- Stock opening/closing values
- Site_Code + LogSite_Code composite PK

Schema: verified from live KailashData2526 DB.
Single-row table: UPDATE only (VB6 pattern - no INSERT).
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()


def get(cn=None) -> dict:
    """Read FAEnviro settings (single-row)."""
    rows = db.query(
        "SELECT Age1, Age2, Age3, Age4, Age5, Age6, "
        "Amt1, Amt2, Amt3, Amt4, Amt5, Amt6, "
        "TagadaHeader1, TagadaHeader2, TagadaHeader3, TagadaHeader4, TagadaHeader5, "
        "TagadaFooter1, TagadaFooter2, TagadaFooter3fa, TagadaFooter4, TagadaFooter5, "
        "CreditLimit, DebitLimit, NegativeCashBalance, ShowGroup, DonotShowGroup, "
        "ShowCurrentBalance, VerticleBalanceSheet, ShowQty, ShowCityName, "
        "LedDivCode, LedSiteCode, LedPrefix, daterfill, titlerfill, pagenofill, "
        "RunPIF, FilterAC, AddressHelp, DateLock, CashBookBalance, MonthTotal, "
        "OnLineAdjustment, linefiller, OpStockQTY, OpStockValue, ClStockQTY, "
        "ClStockValue, CashBookPage, CityNameDisp, ToBy, RepToBy, PreBal, PDCDt, "
        "Site_Code, LogSite_Code, TagadaFooter3 "
        "FROM FAEnviro WHERE Site_Code = ? OR LogSite_Code = 'HO'",
        (SITE_CODE,), cn=cn)
    if not rows:
        raise ValueError("FAEnviro row hi nahi mila")
    r = rows[0]
    if hasattr(r, "keys"):
        return {k: r[k] for k in r.keys()}
    cols = [c[0] for c in db.query(
        "SELECT name FROM sys.columns WHERE object_id = "
        "OBJECT_ID('FAEnviro') ORDER BY column_id", cn=cn)]
    return dict(zip(cols, r))


def get_setting(key: str, default="", cn=None):
    """Single setting read."""
    row = db.query(
        f"SELECT [{key}] FROM FAEnviro WHERE Site_Code = ? "
        "OR LogSite_Code = 'HO'",
        (SITE_CODE,), cn=cn)
    if not row or row[0][0] is None:
        return default
    v = row[0][0]
    if isinstance(v, bytes):
        return default
    return v


def update_settings(changes: dict, user: str = USER, cn=None,
                    commit: bool = True) -> int:
    """Multi-setting update (single-row UPDATE pattern)."""
    if not changes:
        raise ValueError("Khaali changes")
    own = cn is None
    cn = cn or db.connect()
    try:
        sets = ", ".join(f"[{k}] = ?" for k in changes)
        params = tuple(changes.values()) + (SITE_CODE,)
        n = db.execute(
            f"UPDATE FAEnviro SET {sets} WHERE Site_Code = ? "
            "OR LogSite_Code = 'HO'",
            params, cn=cn, commit=False)
        print(f"[fa_enviro] {user} updated: "
              + ", ".join(f"{k}={v!r}" for k, v in changes.items()))
        if commit:
            cn.commit()
        return n
    finally:
        if own:
            cn.close()


def update_setting(key: str, value, user: str = USER, cn=None,
                   commit: bool = True) -> int:
    """Single setting update."""
    return update_settings({key: value}, user=user, cn=cn, commit=commit)


def snapshot(cn=None) -> dict:
    """Pre-update snapshot of all settings."""
    return get(cn=cn)


class _FAEnviroAPI:
    @staticmethod
    def get(cn=None): return get(cn)
    @staticmethod
    def get_setting(key, default="", cn=None): return get_setting(key, default, cn)
    @staticmethod
    def update_settings(changes, user=USER, cn=None, commit=True):
        return update_settings(changes, user, cn, commit)
    @staticmethod
    def update_setting(key, value, user=USER, cn=None, commit=True):
        return update_setting(key, value, user, cn, commit)
    @staticmethod
    def snapshot(cn=None): return snapshot(cn)

FAEnviroAPI = _FAEnviroAPI()
