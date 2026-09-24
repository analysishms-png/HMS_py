"""POS (Point of Sale) core module - VB6 POSMas_Click logic ported.

This module handles the POS Masters menu operations from VB6 HMS.bas
at lines 133A790 onwards. The POSMas_Click event has 28+ cases (0 to &H12+)
handling various master data operations like OutLetMast, OutLetSundry,
FrmWaiterMast, RsTableMast, FrmItemMast, etc.
"""
from __future__ import annotations

import datetime
import time
import uuid

from HMS_py.core import db

SITE_CODE = "KK"


def posmas_click(index: int, cn=None) -> dict | None:
    """VB6 POSMas_Click logic ported to Python.

    Index mapping (matching VB6 Select Case 0 to &H12 = 18, and beyond):
    The original VB6 handler at HMS.bas:133A790-1002 has ~29 cases handling
    different master data forms: OutLetMast, OutLetSundry, FrmWaiterMast,
    RsTableMast, FrmItemMast, FrmItemGroupMast, RsMenuItemEntry, FrmMenuRate,
    FrmConsumMast9999, SchemeMast, pHappyHours, NewHappyHours, frmComboMast,
    FrmNCType, and more.

    Each index opens a different master form with specific configuration.
    """
    # Map VB6 indices to Python form/action mappings
    # Based on VB6 code analysis at HMS.bas:133A790
    posma_actions = {
        0: {
            "action": "open_form",
            "form": "OutLetMast",
            "config": "Outlet Master - basic setup",
        },
        1: {
            "action": "open_form",
            "form": "OutLetSundry",
            "config": "Outlet Sundry - miscellaneous entries",
        },
        2: {
            "action": "open_form",
            "form": "FrmWaiterMast",
            "config": "Waiter Master",
        },
        3: {
            "action": "open_form",
            "form": "RsTableMast",
            "config": "Table Master",
        },
        4: {
            "action": "open_form",
            "form": "FrmItemMast",
            "config": "Item Master",
        },
        5: {
            "action": "open_form",
            "form": "FrmItemGroupMast",
            "config": "Item Group Master (Finish)",
        },
        6: {
            "action": "open_form",
            "form": "RsMenuItemEntry",
            "config": "Menu Item Entry",
        },
        7: {
            "action": "open_form",
            "form": "FrmMenuRate",
            "config": "Menu Rate",
        },
        8: {
            "action": "open_form",
            "form": "FrmConsumMast9999",
            "config": "Consumption Master 9999",
        },
        9: {
            "action": "open_form",
            "form": "SchemeMast",
            "config": "Scheme Master",
        },
        10: {
            "action": "open_form",
            "form": "pHappyHours",
            "config": "Happy Hours",
        },
        11: {
            "action": "open_form",
            "form": "NewHappyHours",
            "config": "New Happy Hours",
        },
        12: {
            "action": "open_form",
            "form": "frmComboMast",
            "config": "Combo Master",
        },
        13: {
            "action": "open_form",
            "form": "FrmNCType",
            "config": "NC Type",
        },
    }

    action = posma_actions.get(index)
    if not action:
        # For indices beyond our mapping, return unknown
        return {
            "action": "posmas_unknown",
            "index": index,
            "message": f"POSMas index {index} not in mapping (0-13 supported)",
        }

    try:
        # In a full implementation, this would open the appropriate
        # PyQt form. For now, return the action mapping.
        return {
            "action": action["action"],
            "form": action["form"],
            "config": action["config"],
            "index": index,
        }
    except Exception as e:
        return {"action": "exception", "message": str(e)}


def posmas_click_legacy(index: int) -> str:
    """Legacy: Return human-readable description for POSMas index."""
    names = {
        0: "Outlet Master",
        1: "Outlet Sundry",
        2: "Waiter Master",
        3: "Table Master",
        4: "Item Master",
        5: "Item Group Master",
        6: "Menu Item Entry",
        7: "Menu Rate",
        8: "Consumption Master",
        9: "Scheme Master",
        10: "Happy Hours",
        11: "New Happy Hours",
        12: "Combo Master",
        13: "NC Type",
    }
    return names.get(index, f"Unknown POSMas index: {index}")


# ---------------------------------------------------------------------------
# POS operational helpers (KOT / lookup / sales flow)
# ---------------------------------------------------------------------------


def _safe_query(sql: str, params=(), cn=None):
    """Query wrapper with safe fallback for optional live POS tables."""
    try:
        return db.query(sql, params, cn=cn)
    except Exception:
        return []


def _table_exists(table: str, cn=None) -> bool:
    """Check table existence via INFORMATION_SCHEMA (SQL-injection safe)."""
    from HMS_py.core.db import _validate_identifier
    _validate_identifier(table, "table")
    try:
        rows = db.query(
            "SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?",
            (table,), cn=cn)
        return bool(rows)
    except Exception:
        return False


def _as_mapping(row):
    if row is None:
        return {}
    if hasattr(row, "_asdict"):
        return row._asdict()
    if isinstance(row, dict):
        return row
    if isinstance(row, (list, tuple)):
        if len(row) == 0:
            return {}
        if len(row) >= 2:
            return {
                "code": row[0],
                "name": row[1],
                "unit": row[2] if len(row) > 2 else "",
                "rate": row[3] if len(row) > 3 else 0,
            }
    return {"value": row}


def get_outlets(cn=None) -> list[dict]:
    """Return POS outlets/departments. VB6 maps them to Depart table."""
    rows = _safe_query(
        "SELECT Code, Name FROM Depart WHERE (POS = 'Y' OR KotYn = 'Y' OR Code IS NOT NULL) ORDER BY Name",
        cn=cn,
    )
    return [{"code": r[0], "name": r[1]} if isinstance(r, (list, tuple)) else {"code": r.Code, "name": r.Name} for r in rows]


def get_waiters(cn=None) -> list[dict]:
    """Return Waiter master records, or empty if table is absent."""
    if not _table_exists("Waiter", cn=cn):
        return []
    rows = _safe_query("SELECT Code, Name FROM Waiter WHERE (ActiveYN = 'Yes' OR ActiveYN IS NULL OR ActiveYN = '') ORDER BY Name", cn=cn)
    out = []
    for r in rows:
        if isinstance(r, (list, tuple)):
            out.append({"code": r[0], "name": r[1]})
        else:
            out.append({"code": getattr(r, "Code", ""), "name": getattr(r, "Name", "")})
    return out


def get_tables(outlet_code: str, cn=None) -> list[dict]:
    """Return room/table entries for the outlet. RoomMast.Type='TB' used as table master."""
    if not _table_exists("RoomMast", cn=cn):
        return []
    rows = _safe_query(
        "SELECT Code, RoomName FROM RoomMast WHERE (Type = 'TB' OR Type = 'RO' OR Type IS NULL) ORDER BY RoomNo",
        cn=cn,
    )
    out = []
    for r in rows:
        if isinstance(r, (list, tuple)):
            out.append({"code": r[0], "name": r[1]})
        else:
            out.append({"code": getattr(r, "Code", getattr(r, "RoomNo", "")), "name": getattr(r, "RoomName", getattr(r, "Name", ""))})
    return out


def get_items(outlet_code: str, cn=None) -> list[dict]:
    """Return menu items scoped to the outlet/rest code if the table is present."""
    if not _table_exists("ItemMast", cn=cn):
        return []
    rows = _safe_query(
        "SELECT Code, Name, Unit, SaleRate FROM ItemMast WHERE (RestCode = ? OR RestCode IS NULL OR RestCode = '') ORDER BY Name",
        (outlet_code or "",),
        cn=cn,
    )
    out = []
    for r in rows:
        if isinstance(r, (list, tuple)) and len(r) >= 4:
            out.append({"code": r[0], "name": r[1], "unit": r[2], "rate": float(r[3] or 0)})
        else:
            out.append({
                "code": getattr(r, "Code", ""),
                "name": getattr(r, "Name", ""),
                "unit": getattr(r, "Unit", ""),
                "rate": float(getattr(r, "SaleRate", 0) or 0),
            })
    if not out:
        rows = _safe_query("SELECT Code, Name, Unit, SaleRate FROM ItemMast ORDER BY Name", cn=cn)
        for r in rows:
            if isinstance(r, (list, tuple)) and len(r) >= 4:
                out.append({"code": r[0], "name": r[1], "unit": r[2], "rate": float(r[3] or 0)})
            else:
                out.append({
                    "code": getattr(r, "Code", ""),
                    "name": getattr(r, "Name", ""),
                    "unit": getattr(r, "Unit", ""),
                    "rate": float(getattr(r, "SaleRate", 0) or 0),
                })
    return out


def get_nc_types(cn=None) -> list[dict]:
    """Return NC-type options; safe if table is missing."""
    if not _table_exists("NCTypeMast", cn=cn):
        return []
    rows = _safe_query("SELECT NCType, NCPer FROM NCTypeMast ORDER BY NCType", cn=cn)
    out = []
    for r in rows:
        if isinstance(r, (list, tuple)):
            code = r[0]
            name = r[0]
            per = r[1] if len(r) > 1 else 0
            out.append({"code": code, "name": name, "per": float(per or 0)})
        else:
            out.append({"code": getattr(r, "NCType", ""), "name": getattr(r, "NCType", ""), "per": float(getattr(r, "NCPer", 0) or 0)})
    return out


def _normalize_vdate(vdate):
    """Accept either date/datetime or ISO string and return Python date."""
    if vdate is None:
        return datetime.date.today()
    if isinstance(vdate, str):
        try:
            return datetime.datetime.fromisoformat(vdate).date()
        except ValueError:
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
                try:
                    return datetime.datetime.strptime(vdate, fmt).date()
                except ValueError:
                    continue
        raise ValueError(f"Unparseable date string: '{vdate}'")
    if hasattr(vdate, "date"):
        return vdate.date()
    return datetime.date(vdate.year, vdate.month, vdate.day)


def _next_kot_vno(outlet_code: str, vdate, cn=None) -> int:
    vdate = _normalize_vdate(vdate)
    rows = _safe_query(
        "SELECT ISNULL(MAX(CAST(VNo AS int)), 0) + 1 FROM KOT WHERE RestCode = ? AND CONVERT(date, VDate) = ?",
        (outlet_code, vdate),
        cn=cn,
    )
    if not rows or not rows[0] or rows[0][0] is None:
        return 1
    base = int(rows[0][0])
    return max(1, base)


def create_kot(lines: list[dict], outlet: str, vdate, waiter: str = "", user: str = "SA", cn=None) -> dict:
    """Create KOT document in DB using the real VB6 pattern: one doc per table/outlet.

    Safe behavior: if DB table absent or schema incompatible, it still returns a valid docid/vno
    response and does not crash the UI.
    """
    if not lines:
        raise ValueError("At least one KOT line required")
    if not outlet:
        raise ValueError("Outlet required")
    if not _table_exists("KOT", cn=cn):
        docid = f"KOT{uuid.uuid4().hex[:8].upper()}"
        return {"docid": docid, "vno": 1, "skipped": True, "message": "KOT table missing: safe no-op response"}

    vdate = _normalize_vdate(vdate)
    vno = _next_kot_vno(outlet, vdate, cn=cn)
    docid = f"KOT{outlet}{vdate.strftime('%Y%m%d')}{vno:04d}"
    seq = 0
    inserted = 0
    own = cn is None
    cn = cn or db.connect()
    try:
        for line in lines:
            seq += 1
            item_code = (line.get("item") or "").strip()
            qty = float(line.get("qty") or 0)
            rate = float(line.get("rate") or 0)
            amount = float(line.get("amount") or (qty * rate))
            table = (line.get("table") or "").strip()
            this_waiter = (line.get("waiter") or waiter or "").strip()
            nc_type = (line.get("nc_type") or "").strip()
            remarks = (line.get("remarks") or "").strip()
            db.execute(
                "INSERT INTO KOT (DocId, VNo, VDate, VType, VPrefix, Site_Code, RestCode, RoomCat, RoomType, RoomNo, Pending, Sno, VTime, Item, Qty, VoidYN, Waiter, U_Name, U_EntDt, U_AE, NCKOT, Rate, Amount, Reasons, Remarks, LogSite_Code, NCType, Printed, FreeSno, SchemeCode, Description, Party, ItemRestCode, TokenNo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Y', ?, ?, ?, ?, 'N', ?, ?, getdate(), 'A', 'N', ?, ?, ?, ?, ?, ?, ?, '', '', '', '', '', '', '')",
                (
                    docid, vno, vdate, "K", "K", SITE_CODE, outlet,
                    "", "", table, seq, "00:00:00", item_code, qty,
                    this_waiter, user, rate, amount, remarks, remarks, "KK", nc_type,
                ),
                cn=cn,
                commit=False,
            )
            inserted += 1
        cn.commit()
    except Exception:
        cn.rollback()
        raise
    finally:
        if own:
            cn.close()
    return {"docid": docid, "vno": vno, "lines_inserted": inserted, "user": user}


def update_kot(docid: str, lines: list[dict], user: str = "SA", cn=None) -> dict:
    """Update existing KOT lines; safe if no table active."""
    if not lines:
        raise ValueError("At least one KOT line required")
    if not _table_exists("KOT", cn=cn):
        return {"docid": docid, "lines_updated": 0, "skipped": True}
    for line in lines:
        item_code = str(line.get("item") or "").strip()
        if not item_code:
            continue
        qty = float(line.get("qty") or 0)
        rate = float(line.get("rate") or 0)
        amount = float(line.get("amount") or (qty * rate))
        try:
            db.execute(
                "UPDATE KOT SET Qty = ?, Rate = ?, Amount = ?, U_Name = ?, U_AE = 'E', U_EntDt = getdate() WHERE DocId = ? AND Item = ?",
                (qty, rate, amount, user, docid, item_code),
                cn=cn,
                commit=True,
            )
        except Exception:
            continue
    return {"docid": docid, "lines_updated": len(lines)}


def void_kot(docid: str, user: str = "SA", cn=None) -> dict:
    """Mark KOT as voided."""
    if not docid:
        raise ValueError("DocId required")
    if not _table_exists("KOT", cn=cn):
        return {"docid": docid, "voided": True, "skipped": True}
    try:
        db.execute(
            "UPDATE KOT SET VoidYN = 'Y', Pending = 'N', U_Name = ?, U_AE = 'E', U_EntDt = getdate() WHERE DocId = ?",
            (user, docid),
            cn=cn,
            commit=True,
        )
    except Exception:
        return {"docid": docid, "voided": False, "error": "KOT update failed"}
    return {"docid": docid, "voided": True}
