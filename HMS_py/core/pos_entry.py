"""POS Entry (POSEnt) core module - VB6 POSEnt_Click logic ported.

This module handles the POS Entry menu operations from VB6 HMS.bas
at lines 142C7E4 onwards. The POSEnt_Click event has extensive logic
handling various POS operations: KOT entry, table changes, sales bills,
advance deposits, etc.

The original VB6 handler is at HMS.bas:142C7E4-856 with 21 sub-cases
(index 0 to &H12 = 18) based on the var_106 variable.
"""
from __future__ import annotations

from HMS_py.core import db
from HMS_py.core.menu import menu_name_allowed

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")


def _safe_table_rows(cn, sql: str, params=(), limit: int | None = None):
    """Table existence check + safe row read for optional POS tables."""
    if cn is None:
        return []
    try:
        cur = cn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        if limit is not None and rows:
            rows = rows[:limit]
        return rows
    except Exception:
        return []


def posent_click(index: int, cn=None, user: str = "SA",
                 form_registry: dict | None = None) -> dict | None:
    """VB6 POSEnt_Click logic ported to Python using permissions and safe DB checks.

    form_registry: pass the UI form registry dict. If None, skips UI form lookup.
    """
    cases = {
        0: "Change Rest",
        1: "Table Change",
        2: "Sale Bill",
        3: "Item wise Sale",
        4: "POS Bill Reprint",
        5: "Sale Bill Split",
        6: "POS Display",
        7: "Booking Entry",
        8: "Advance Deposit",
        10: "KOT Transfer",
        11: "Token Entry",
        12: "Assign Delivery",
        13: "Payment Receipt",
    }

    form_name = cases.get(index)
    if form_name is not None:
        if not menu_name_allowed(form_name, user):
            return {
                "action": "access_denied",
                "form": form_name,
                "message": f"'{form_name}' ko user rights mein nahi hai",
                "index": index,
            }
        if form_registry is not None:
            opener = form_registry.get(form_name)
            if opener is not None:
                return {"action": "open_form", "form": form_name, "opener": opener, "index": index}
        if index in (3, 10, 12, 13):
            # some POS handlers are not UI-backed yet but still valid operational actions
            if index == 3:
                try:
                    rows = db.query("SELECT COUNT(*) FROM Depart WHERE Site_Code = ?", (SITE_CODE,))
                    count = rows[0][0] if rows else 0
                    return {
                        "action": "item_wise_sale",
                        "department_valid": count > 0,
                        "message": "Item wise sale department validation",
                        "index": index,
                    }
                except Exception as e:
                    return {"action": "exception", "message": str(e), "index": index}
            if index == 10:
                rows = db.query("SELECT TOP 1 * FROM Enviro WHERE Site_Code = ?", (SITE_CODE,))
                return {
                    "action": "kot_transfer",
                    "data": dict(rows[0]._asdict()) if rows and hasattr(rows[0], "_asdict") else {},
                    "index": index,
                }
            if index == 12:
                rows = _safe_table_rows(cn, "SELECT Code AS DeliveryBoy, Name AS Status FROM DeliveryBoy WHERE Site_Code = ?", (SITE_CODE,), limit=20)
                return {
                    "action": "assign_delivery",
                    "data": [{"boy": getattr(r, "DeliveryBoy", None), "status": getattr(r, "Status", None)} for r in rows] if rows else [],
                    "index": index,
                }
            return {
                "action": "payment_receipt",
                "message": "Payment receipt - POS operation mapped",
                "index": index,
            }
        return {"action": "form_not_ready", "form": form_name, "message": f"'{form_name}' not available", "index": index}

    return {"action": "unknown_pos_entry", "index": index, "message": f"POSEnt index {index} not mapped"}


def posent_click_legacy(index: int) -> str:
    """Legacy: Return human-readable description for POSEnt index."""
    names = {
        0: "Rest Change",
        1: "Table Change",
        2: "Sale Bill",
        3: "Item wise Sale",
        4: "POS Bill Reprint",
        5: "Sale Bill Split",
        6: "POS Display",
        7: "Booking Entry",
        8: "Advance Deposit",
        10: "KOT Transfer",
        11: "Token Entry",
        12: "Assign Delivery",
        13: "Payment Receipt",
    }
    return names.get(index, f"Unknown POSEnt index: {index}")