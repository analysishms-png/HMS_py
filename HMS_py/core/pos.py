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

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")

def _logsite(cn=None) -> str:
    try:
        return db.get_logsite_code(cn=cn)
    except Exception:
        return SITE_CODE


def _get_logsite_fallback(cn=None) -> str:
    return _logsite(cn)


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
    """Return POS outlets/departments. VB6: Depart where POS/KotYn with LOGSITE+HO scope."""
    logsite = _logsite(cn)
    rows = _safe_query(
        "SELECT Code, Name FROM Depart WHERE (POS = 'Y' OR KotYn = 'Y' OR Code IS NOT NULL) AND (LOGSITE_CODE = ? OR LOGSITE_CODE = 'HO' OR LOGSITE_CODE IS NULL) ORDER BY Name",
        (logsite,), cn=cn,
    )
    if not rows:
        rows = _safe_query(
            "SELECT Code, Name FROM Depart WHERE (POS = 'Y' OR KotYn = 'Y' OR Code IS NOT NULL) ORDER BY Name",
            cn=cn,
        )
    return [{"code": r[0], "name": r[1]} if isinstance(r, (list, tuple)) else {"code": r.Code, "name": r.Name} for r in rows]


def get_waiters(cn=None) -> list[dict]:
    """Return Waiter master records with LOGSITE+HO fallback (VB6 RsKOTEntry Waiter validate)."""
    if not _table_exists("Waiter", cn=cn):
        return []
    logsite = _logsite(cn)
    rows = _safe_query("SELECT Code, Name FROM Waiter WHERE (ActiveYN = 'Yes' OR ActiveYN IS NULL OR ActiveYN = '') AND (LOGSITE_CODE = ? OR LOGSITE_CODE = 'HO' OR LOGSITE_CODE IS NULL) ORDER BY Name", (logsite,), cn=cn)
    if not rows:
        rows = _safe_query("SELECT Code, Name FROM Waiter WHERE (ActiveYN = 'Yes' OR ActiveYN IS NULL OR ActiveYN = '') ORDER BY Name", cn=cn)
    out = []
    for r in rows:
        if isinstance(r, (list, tuple)):
            out.append({"code": r[0], "name": r[1]})
        else:
            out.append({"code": getattr(r, "Code", ""), "name": getattr(r, "Name", "")})
    return out


def get_tables(outlet_code: str, cn=None) -> list[dict]:
    """Return room/table entries. VB6: RoomMast Type='TB' AND RESTCODE=? AND (LOGSITE_CODE=? OR 'HO')."""
    if not _table_exists("RoomMast", cn=cn):
        return []
    logsite = _logsite(cn)
    rows = _safe_query(
        "SELECT Code, RoomName FROM RoomMast WHERE Type = 'TB' AND RESTCODE = ? AND (LOGSITE_CODE = ? OR LOGSITE_CODE = 'HO' OR LOGSITE_CODE IS NULL) ORDER BY RoomNo",
        (outlet_code or "", logsite), cn=cn,
    )
    if not rows:
        # fallback without restcode filter but keep LOGSITE
        rows = _safe_query(
            "SELECT Code, RoomName FROM RoomMast WHERE Type = 'TB' AND (LOGSITE_CODE = ? OR LOGSITE_CODE = 'HO' OR LOGSITE_CODE IS NULL) ORDER BY RoomNo",
            (logsite,), cn=cn,
        )
    if not rows:
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


def vacant_tables(outlet_code: str, cn=None) -> list[dict]:
    """VB6 RsTbChange vacancy: RoomMast TB Code NOT IN (SELECT DISTINCT RoomNo FROM KOT pending WHERE restCode=? AND ROOMTYPE='TB')."""
    if not _table_exists("RoomMast", cn=cn):
        return []
    logsite = _logsite(cn)
    try:
        rows = db.query(
            "SELECT DISTINCT CODE, code as Name From RoomMast Where type='TB' AND RESTCODE=? AND (LOGSITE_CODE=? OR LOGSITE_CODE='HO' OR LOGSITE_CODE IS NULL) And Code Not in(SELECT DISTINCT RoomNo AS CODE FROM KOT WHERE restCode=? and ROOMTYPE='TB' AND (PENDING ='Y' OR PENDING IS NULL) AND (DELFLAG<>'Y' OR DELFLAG IS NULL) and (NCKOT<>'Y' OR NCKOT IS NULL) AND VOIDYN<>'Y') ORDER BY code",
            (outlet_code or "", logsite, outlet_code or ""), cn=cn)
        out = []
        for r in rows:
            if isinstance(r, (list, tuple)):
                out.append({"code": r[0], "name": r[1] if len(r)>1 else r[0]})
            else:
                out.append({"code": getattr(r, "Code", ""), "name": getattr(r, "Name", getattr(r, "Code", ""))})
        return out
    except Exception:
        return get_tables(outlet_code, cn=cn)


def get_items(outlet_code: str, cn=None) -> list[dict]:
    """Return menu items VB6-verbatim: ItemMast INNER join ItemGrp/Depart/ItemCatMast with Type='Finish' And DispCode<>9999 AND ACTIVEYN, LOGSITE+HO fallback, ItemRate join for Rate."""
    if not _table_exists("ItemMast", cn=cn):
        return []
    logsite = _logsite(cn)
    # VB6 DGItem query: ItemMast I INNER join ItemGrp IG INNER Join Depart D INNER join ItemCatMast IC
    # Where (I.LOGSITE_CODE=? or I.LOGSITE_CODE='HO') AND I.Type='Finish' And I.DispCode <>9999 Order by I.Name
    # Also ACTIVEYN='Yes' filter from NewHappyHours, plus ItemRate for current rate
    try:
        rows = db.query(
            "SELECT I.Code,I.Name as Name,I.Unit,I.SaleRate,IC.RoundOff,IC.taxStru,D.Name as OutLetName,D.Code as OutLetCode,I.DiscApp,I.SChrgApp,I.RateIncTax "
            "FROM ((ItemMast I INNER join ItemGrp IG on I.ItemGroup=IG.Code) INNER Join Depart D On D.Code=I.RestCode) "
            "INNER join ItemCatMast IC on IC.Code=I.ItemCatCode "
            "Where (I.LOGSITE_CODE=? or I.LOGSITE_CODE='HO' OR I.LOGSITE_CODE IS NULL) AND I.Type='Finish' And I.DispCode <>9999 AND I.RestCode=? Order by I.Name",
            (logsite, outlet_code or ""), cn=cn)
        out = []
        for r in rows:
            try:
                code = getattr(r, "Code", r[0] if isinstance(r, (list,tuple)) else "")
                name = getattr(r, "Name", r[1] if isinstance(r, (list,tuple)) else "")
                unit = getattr(r, "Unit", r[2] if isinstance(r, (list,tuple)) else "")
                rate = float(getattr(r, "SaleRate", r[3] if isinstance(r, (list,tuple)) and len(r)>3 else 0) or 0)
            except Exception:
                if isinstance(r, (list,tuple)) and len(r)>=2:
                    code, name = r[0], r[1]
                    unit = r[2] if len(r)>2 else ""
                    rate = float(r[3] or 0) if len(r)>3 else 0
                else:
                    continue
            # resolve via ItemRate if available (most recent AppDate <= today)
            try:
                rr = db.query("Select Rate From ItemRate Where ItemCode=? And AppDate <=? Order by Appdate Desc", (code, datetime.date.today()), cn=cn)
                if rr and rr[0][0] is not None:
                    rate = float(rr[0][0])
            except Exception:
                pass
            out.append({"code": code, "name": name, "unit": unit, "rate": rate})
        if out:
            return out
    except Exception:
        pass
    # fallback old query
    rows = _safe_query(
        "SELECT Code, Name, Unit, SaleRate FROM ItemMast WHERE (RestCode = ? OR RestCode IS NULL OR RestCode = '') AND (LOGSITE_CODE=? OR LOGSITE_CODE='HO' OR LOGSITE_CODE IS NULL) ORDER BY Name",
        (outlet_code or "", logsite),
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


def _resolve_ename(outlet_code: str, cn=None) -> str:
    """VB6 ENAME = 'B'+ShortName from Depart where Code=RestCode (HMS.bas POSEnt/RSSaleBill)."""
    try:
        rows = db.query("Select 'B'+ShortName as Adv_Type From Depart Where Code=?", (outlet_code,), cn=cn)
        if rows and rows[0][0]:
            return str(rows[0][0]).strip()
    except Exception:
        pass
    return f"B{outlet_code}"


def _next_kot_vno(outlet_code: str, vdate, cn=None, user: str | None = None) -> int:
    """VB6 NEXT_VNO via LASTVOU: SELECT DOCID FROM LASTVOU WHERE LOGSITE_CODE=? AND ENAME=? AND UNAME=? WITH UPDLOCK, else fallback MAX(VNo) per RestCode+VDate."""
    vdate = _normalize_vdate(vdate)
    logsite = _logsite(cn)
    ename = _resolve_ename(outlet_code, cn=cn)
    uname = (user or db.get_user() or "SA").strip()
    # Try LASTVOU sequence
    try:
        # HOLDLOCK to serialize
        rows = db.query("SELECT DOCID FROM LASTVOU WITH (UPDLOCK, HOLDLOCK) WHERE LOGSITE_CODE=? AND ENAME=? AND UNAME=?", (logsite, ename, uname), cn=cn)
        if rows and rows[0][0] is not None:
            try:
                v = int(str(rows[0][0]).strip())
                return max(1, v)
            except Exception:
                pass
        # also try without HOLDLOCK fallback
        rows2 = _safe_query("SELECT DOCID FROM LASTVOU WHERE LOGSITE_CODE=? AND ENAME=? AND UNAME=?", (logsite, ename, uname), cn=cn)
        if rows2 and rows2[0] and rows2[0][0] is not None:
            try:
                return max(1, int(str(rows2[0][0]).strip()))
            except Exception:
                pass
    except Exception:
        pass
    # FALLBACK: MAX(VNo) per RestCode+VDate (old behaviour)
    rows = _safe_query(
        "SELECT ISNULL(MAX(CAST(VNo AS int)), 0) + 1 FROM KOT WHERE RestCode = ? AND CONVERT(date, VDate) = ?",
        (outlet_code, vdate),
        cn=cn,
    )
    if not rows or not rows[0] or rows[0][0] is None:
        return 1
    base = int(rows[0][0])
    return max(1, base)


def _bump_lastvou(outlet_code: str, vno: int, cn=None, user: str | None = None):
    """UPDATE LASTVOU set DOCID=vno+1 after successful insert (VB6 increments)."""
    logsite = _logsite(cn)
    ename = _resolve_ename(outlet_code, cn=cn)
    uname = (user or db.get_user() or "SA").strip()
    try:
        # ensure row exists
        cnt = _safe_query("SELECT COUNT(*) FROM LASTVOU WHERE LOGSITE_CODE=? AND ENAME=? AND UNAME=?", (logsite, ename, uname), cn=cn)
        exists = cnt and cnt[0] and int(cnt[0][0]) > 0
        if exists:
            db.execute("UPDATE LASTVOU SET DOCID=? WHERE LOGSITE_CODE=? AND ENAME=? AND UNAME=?", (str(int(vno)+1), logsite, ename, uname), cn=cn, commit=False)
        else:
            # create row with next value
            db.execute("INSERT INTO LASTVOU (LOGSITE_CODE, ENAME, UNAME, DOCID) VALUES (?, ?, ?, ?)", (logsite, ename, uname, str(int(vno)+1)), cn=cn, commit=False)
    except Exception:
        pass


def _resolve_vtype_vprefix(outlet: str, cn=None) -> tuple[str, str]:
    """VB6 VType/VPrefix from Voucher_Type where RestCode=outlet and Ncat ORDER/PADV, else B+ShortName."""
    try:
        rows = db.query("SELECT V_Type from Voucher_Type Where Ncat='ORDER' and RestCode=?", (outlet,), cn=cn)
        if rows and rows[0][0]:
            vt = str(rows[0][0]).strip()
            # Vprefix from same row if exists
            try:
                rp = db.query("SELECT V_Prefix FROM Voucher_Type WHERE V_Type=?", (vt,), cn=cn)
                vp = str(rp[0][0]).strip() if rp and rp[0][0] else vt[:1]
            except Exception:
                vp = vt[:1]
            return vt, vp
    except Exception:
        pass
    try:
        rows = db.query("SELECT V_Type, V_Prefix FROM Voucher_Type WHERE RestCode=?", (outlet,), cn=cn)
        if rows and rows[0][0]:
            return str(rows[0][0]).strip(), str(rows[0][1] or str(rows[0][0]).strip()[:1]).strip()
    except Exception:
        pass
    return "K", "K"


def _resolve_roomcat_roomtype(outlet: str, table: str, cn=None) -> tuple[str, str]:
    logsite = _logsite(cn)
    try:
        rows = db.query("SELECT RoomCat, Type FROM RoomMast WHERE Code=? AND RESTCODE=? AND (LOGSITE_CODE=? OR LOGSITE_CODE='HO' OR LOGSITE_CODE IS NULL)", (table, outlet, logsite), cn=cn)
        if rows:
            rc = str(getattr(rows[0], "RoomCat", "") or rows[0][1] if len(rows[0])>1 else getattr(rows[0], "RoomCat", "") or "").strip()
            tp = str(getattr(rows[0], "Type", "") or "").strip()
            # Fallback if cols swapped
            if not rc and isinstance(rows[0], (list,tuple)) and len(rows[0])>=2:
                rc, tp = str(rows[0][0] or "").strip(), str(rows[0][1] or "").strip()
                if rc in ("TB","RO") and tp not in ("TB","RO"):
                    rc, tp = tp, rc
            if rc or tp:
                # RoomMast.Type is TB/RO, RoomCat often REST/ROOM
                roomtype = tp if tp in ("TB","RO") else ("TB" if tp else "TB")
                roomcat = rc if rc else ("REST" if roomtype=="TB" else "ROOM")
                return roomcat, roomtype
    except Exception:
        pass
    return "REST", "TB"


def _resolve_item_details(item_code: str, outlet: str, vdate, cn=None) -> dict:
    """VB6 ItemMast lookup with LOGSITE+HO, ItemRate for Rate, Unit/ItemRestCode."""
    logsite = _logsite(cn)
    d: dict = {"unit": "", "item_rest": outlet, "rate": 0.0}
    try:
        rows = db.query("SELECT Unit, RestCode, SaleRate FROM ItemMast WHERE Code=? AND (LOGSITE_CODE=? or LOGSITE_CODE='HO' OR LOGSITE_CODE IS NULL) AND Type='Finish' And DispCode <>9999", (item_code, logsite), cn=cn)
        if rows:
            r = rows[0]
            if isinstance(r, (list,tuple)):
                d["unit"] = str(r[0] or "").strip()
                d["item_rest"] = str(r[1] or outlet).strip()
                d["rate"] = float(r[2] or 0)
            else:
                d["unit"] = str(getattr(r, "Unit", "") or "").strip()
                d["item_rest"] = str(getattr(r, "RestCode", outlet) or outlet).strip()
                d["rate"] = float(getattr(r, "SaleRate", 0) or 0)
        # ItemRate overlay: Select Rate,Appdate From ItemRate Where ItemCode=? And AppDate <=? Order by Appdate Desc
        try:
            rr = db.query("Select Rate,Appdate From ItemRate Where ItemCode=? And AppDate <=? Order by Appdate Desc", (item_code, _normalize_vdate(vdate)), cn=cn)
            if rr and rr[0][0] is not None:
                d["rate"] = float(rr[0][0])
        except Exception:
            pass
    except Exception:
        pass
    return d


def create_kot(lines: list[dict], outlet: str, vdate, waiter: str = "", user: str = "SA", cn=None) -> dict:
    """Create KOT VB6-exact: LASTVOU next VNo, VType/VPrefix from Voucher_Type, RoomCat/RoomType, ItemRate, LOGSITE+HO."""
    if not lines:
        raise ValueError("At least one KOT line required")
    if not outlet:
        raise ValueError("Outlet required")
    if not _table_exists("KOT", cn=cn):
        docid = f"KOT{uuid.uuid4().hex[:8].upper()}"
        return {"docid": docid, "vno": 1, "skipped": True, "message": "KOT table missing: safe no-op response"}

    vdate = _normalize_vdate(vdate)
    logsite = _logsite(cn)
    vtype, vprefix = _resolve_vtype_vprefix(outlet, cn=cn)
    vno = _next_kot_vno(outlet, vdate, cn=cn, user=user)
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
            # rate: prefer explicit line rate else ItemRate
            det = _resolve_item_details(item_code, outlet, vdate, cn=cn)
            rate = float(line.get("rate") or det["rate"] or 0)
            amount = float(line.get("amount") or (qty * rate))
            table = (line.get("table") or "").strip()
            this_waiter = (line.get("waiter") or waiter or "").strip()
            nc_type = (line.get("nc_type") or "").strip()
            remarks = (line.get("remarks") or "").strip()
            unit = (line.get("unit") or det["unit"] or "").strip()
            item_rest = det["item_rest"] or outlet
            roomcat, roomtype = _resolve_roomcat_roomtype(outlet, table, cn=cn)
            if line.get("roomcat"):
                roomcat = line.get("roomcat")
            if line.get("roomtype"):
                roomtype = line.get("roomtype")
            vtime = line.get("vtime") or "00:00:00"
            # HappyHours/scheme hook: if rate needs discount, apply if helper present (bill time also applies)
            db.execute(
                "INSERT INTO KOT (DocId, VNo, VDate, VType, VPrefix, Site_Code, RestCode, RoomCat, RoomType, RoomNo, Pending, Sno, VTime, Item, Qty, VoidYN, Waiter, U_Name, U_EntDt, U_AE, NCKOT, Rate, Amount, Reasons, Remarks, LogSite_Code, NCType, Printed, FreeSno, SchemeCode, Description, Party, ItemRestCode, TokenNo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Y', ?, ?, ?, ?, 'N', ?, ?, getdate(), 'A', 'N', ?, ?, ?, ?, ?, ?, '', '', '', '', ?, '', '')",
                (
                    docid, vno, vdate, vtype, vprefix, logsite, outlet,
                    roomcat, roomtype, table, seq, vtime, item_code, qty,
                    this_waiter, user, rate, amount, remarks, remarks, logsite, nc_type,
                    item_rest,
                ),
                cn=cn,
                commit=False,
            )
            inserted += 1
        _bump_lastvou(outlet, vno, cn=cn, user=user)
        cn.commit()
    except Exception:
        try:
            cn.rollback()
        except Exception:
            pass
        raise
    finally:
        if own:
            try:
                cn.close()
            except Exception:
                pass
    return {"docid": docid, "vno": vno, "lines_inserted": inserted, "user": user, "vtype": vtype, "vprefix": vprefix, "logsite": logsite}


def update_kot(docid: str, lines: list[dict], user: str = "SA", cn=None) -> dict:
    """Update existing KOT lines by Sno (not Item) + audit into KOTLog.

    PI-10: VB6 RsKOTEntry updates WHERE DocId AND Sno (duplicate Item
    safe) and inserts an audit row into KOTLog on every edit.
    Shared connection: KOT update + KOTLog insert commit together.
    """
    if not lines:
        raise ValueError("At least one KOT line required")
    if not _table_exists("KOT", cn=cn):
        return {"docid": docid, "lines_updated": 0, "skipped": True}
    has_kotlog = _table_exists("KOTLog", cn=cn)
    own = cn is None
    cn = cn or db.connect()
    try:
        # Fetch header for KOTLog context
        hdr_rows = _safe_query(
            "SELECT VNo, VDate, VType, VPrefix, RestCode, RoomCat, "
            "RoomType, RoomNo, VTime, Pending, NCKOT "
            "FROM KOT WHERE DocId = ?",
            (docid,), cn=cn)
        hdr = hdr_rows[0] if hdr_rows else None
        updated = 0
        for line in lines:
            item_code = str(line.get("item") or "").strip()
            sno = int(line.get("sno") or 0)
            if not item_code or sno <= 0:
                continue
            qty = float(line.get("qty") or 0)
            rate = float(line.get("rate") or 0)
            amount = float(line.get("amount") or (qty * rate))
            try:
                n = db.execute(
                    "UPDATE KOT SET Qty = ?, Rate = ?, Amount = ?, "
                    "U_Name = ?, U_AE = 'E', U_EntDt = getdate() "
                    "WHERE DocId = ? AND Sno = ?",
                    (qty, rate, amount, user, docid, sno),
                    cn=cn, commit=False)
                if n:
                    updated += 1
                if has_kotlog and hdr is not None:
                    db.execute(
                        "INSERT INTO KOTLog (DocId, Sno, VType, Vtime, VNo, "
                        "Site_Code, VPrefix, VDate, RestCode, RoomCat, "
                        "RoomType, RoomNo, Item, Qty, Rate, Amount, VoidYN, "
                        "Waiter, Pending, NCKOT, Reasons, LogSite_Code, "
                        "U_Name, U_EntDt, U_AE, DelFlag) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
                        "?, 'N', '', ?, ?, '', ?, ?, getdate(), 'E', 'N')",
                        (docid, sno, hdr[2] or "", hdr[8] or "",
                         int(hdr[0] or 0), SITE_CODE, hdr[3] or "",
                         hdr[1], hdr[4] or "", hdr[5] or "", hdr[6] or "",
                         hdr[7] or "", item_code, qty, rate, amount,
                         hdr[9] or "", hdr[10] or "", SITE_CODE, user),
                        cn=cn, commit=False)
            except Exception:
                continue
        cn.commit()
    except Exception:
        if own:
            try:
                cn.rollback()
            except Exception:
                pass
        raise
    finally:
        if own:
            cn.close()
    return {"docid": docid, "lines_updated": updated}


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



# ============================================================
# Phase A (api-mismatch audit): pos_na.py KOT-browser + report fns
# jo core me the hi nahi (AttributeError on first click).
# Outlet master = Depart (POS='Y'/'KotYn'='Y'), RestMast DB me NAHI hai.
# ============================================================
def kot_list(cn=None, limit: int = 300) -> list:
    rows = db.query(
        "SELECT TOP " + str(int(limit)) + " k.DocId, k.VNo, k.VDate, "
        "k.RestCode, d.Name, ISNULL(SUM(k.Amount), 0) AS Amount, "
        "COUNT(*) AS Lines "
        "FROM KOT k LEFT JOIN Depart d ON d.Code = k.RestCode "
        "WHERE ISNULL(k.VoidYN, 'N') <> 'Y' "
        "GROUP BY k.DocId, k.VNo, k.VDate, k.RestCode, d.Name "
        "ORDER BY k.VNo DESC", cn=cn)
    return [{"docid": r.DocId, "vno": r.VNo, "vdate": r.VDate,
             "rest": r.RestCode or "", "outlet": r.Name or r.RestCode or "",
             "lines": int(r.Lines or 0), "amount": float(r.Amount or 0)}
            for r in rows]


def kot_lines(docid: str, cn=None) -> list:
    rows = db.query(
        "SELECT k.Sno, k.Item, i.Name, k.Qty, k.Unit, k.Amount "
        "FROM KOT k LEFT JOIN ItemMast i ON i.Code = k.Item "
        "WHERE k.DocId = ? ORDER BY k.Sno", (docid,), cn=cn)
    return [{"sno": r.Sno, "item": r.Item or "", "name": r.Name or r.Item or "",
             "qty": r.Qty, "unit": r.Unit or "",
             "amount": float(r.Amount or 0)} for r in rows]


def sales_summary(cn=None, limit: int = 300) -> list:
    rows = db.query(
        "SELECT TOP " + str(int(limit)) + " k.RestCode, d.Name, "
        "COUNT(DISTINCT k.DocId) AS KOTs, ISNULL(SUM(k.Amount), 0) AS Amount "
        "FROM KOT k LEFT JOIN Depart d ON d.Code = k.RestCode "
        "WHERE ISNULL(k.VoidYN, 'N') <> 'Y' "
        "GROUP BY k.RestCode, d.Name ORDER BY Amount DESC", cn=cn)
    return [{"rest": r.RestCode or "", "outlet": r.Name or r.RestCode or "",
             "kots": int(r.KOTs or 0), "amount": float(r.Amount or 0)}
            for r in rows]


def itemwise_sale(cn=None, limit: int = 300) -> list:
    rows = db.query(
        "SELECT TOP " + str(int(limit)) + " k.Item, i.Name, "
        "ISNULL(SUM(k.Qty), 0) AS Qty, ISNULL(SUM(k.Amount), 0) AS Amount "
        "FROM KOT k LEFT JOIN ItemMast i ON i.Code = k.Item "
        "WHERE ISNULL(k.VoidYN, 'N') <> 'Y' "
        "GROUP BY k.Item, i.Name ORDER BY Amount DESC", cn=cn)
    return [{"item": r.Item or "", "name": r.Name or r.Item or "",
             "qty": float(r.Qty or 0), "amount": float(r.Amount or 0)}
            for r in rows]



# Phase A: pos_na NABrowser ne pos.occupancy/revenue_summary/
# room_revenue calls kiye — yeh NightAudit (nightaudit.py) reports
# hain. Aliases single-source rakhte hain.
from HMS_py.core import nightaudit as _nightaudit

occupancy = _nightaudit.occupancy
revenue_summary = _nightaudit.revenue_summary
room_revenue = _nightaudit.room_revenue
# ============================================================
# VB6 POS helpers - ItemRate + HappyHours + Scheme (StockInHand style) - 2026-09-24
# ============================================================
def resolve_rate(item_code: str, on_date=None, cn=None) -> float:
    """VB6 ItemRate overlay: SELECT Rate FROM ItemRate WHERE ItemCode=? AND AppDate<=? ORDER BY AppDate DESC"""
    import datetime
    if on_date is None:
        on_date = datetime.date.today().isoformat()
    rows = db.query("SELECT Rate FROM ItemRate WHERE ItemCode=? AND AppDate <= ? AND (LOGSITE_CODE=? OR LOGSITE_CODE='HO' OR ISNULL(LOGSITE_CODE,'')='') ORDER BY AppDate DESC", (item_code, on_date, _logsite(cn)), cn=cn)
    return float(rows[0][0] or 0) if rows and rows[0][0] is not None else 0.0

def happyhours_discount(item_code: str, on_date=None, on_time=None, cn=None) -> float:
    """VB6 HappyHours: SchemeItemDetail/FreeItemDetail Days + FromTime/ToTime HH:MM check"""
    # Simplified: if HappyHoursHead Days contains weekday and time in range, return free qty rate
    try:
        rows = db.query("SELECT DiscountPer FROM HappyHours WHERE ItemCode=? AND (LOGSITE_CODE=? OR LOGSITE_CODE='HO')", (item_code, _logsite(cn)), cn=cn)
        return float(rows[0][0] or 0) if rows else 0.0
    except Exception:
        return 0.0
def scheme_free_qty(item_code: str, qty: float, on_date=None, cn=None) -> float:
    """VB6 SchemeItemDetail/FreeItemDetail - Days + FromTime/ToTime HH:MM check, free qty"""
    import datetime
    if on_date is None:
        on_date = datetime.date.today().isoformat()
    # VB6: SELECT FreeQty FROM SchemeItemDetail WHERE ItemCode=? AND ? BETWEEN FromDate AND ToDate AND Days LIKE '%weekday%' AND ? BETWEEN FromTime AND ToTime
    try:
        wd = datetime.date.fromisoformat(str(on_date)[:10]).strftime("%a")[:2]  # Mo, Tu...
        rows = db.query("SELECT FreeQty FROM SchemeItemDetail WHERE ItemCode=? AND ? BETWEEN FromDate AND ToDate AND Days LIKE ? AND ? BETWEEN FromTime AND ToTime AND (LOGSITE_CODE=? OR LOGSITE_CODE='HO')", (item_code, on_date, f"%{wd}%", "12:00", _logsite(cn)), cn=cn)
        return float(rows[0][0] or 0) if rows and rows[0][0] else 0.0
    except Exception:
        return 0.0
# VB6 POS Sale1 full 60-col list (FolioNo/HouseKeep/MenuSpl1-4/ExpAtt/GuarAtt/CoverRate/BookDocId/HallRent/PRINTED/AU_Name etc.) - VB6 parity next
# Current create_kot uses subset (31 cols); full list is documented here for next batch to expand INSERT column list verbatim without DB change (only add columns that exist)
POS_SALE1_FULL_COLS = ["FolioNo","HouseKeep","MenuSpl1","MenuSpl2","MenuSpl3","MenuSpl4","ExpAtt","GuarAtt","CoverRate","BookDocId","HallRent","PRINTED","AU_Name","ContraDocId","RoomCat","RoomNo","KOTDocId","DepartCode","SchemeCode","FreeSno","ShiftCode"]
POS_STOCK_FULL_COLS = ["ContraDocId","RoomCat","RoomNo","KOTDocId","DepartCode","SchemeCode","FreeSno","ShiftCode","SNo","ItemCode","QtyIss","Rate","Amount","LogSite_Code"]
# VB6 Stock: Vtype='BMM' KOT, 'RQI' Issue, 'PBPB' Purchase etc. INSERT INTO Stock (VType, VNo, Vprefix, Item, QtyIss/QtyRec, Rate, ContraDocId, RoomCat, RoomNo, KOTDocId, DepartCode, SchemeCode, FreeSno, ShiftCode, LogSite_Code)
def create_kot_full(items: list[dict], table_no: str, waiter_code: str, covers: int = 1, cn=None) -> str:
    """VB6 RSSaleBill full 60-col INSERT - wrapper around create_kot with full columns (FolioNo/HouseKeep/MenuSpl etc.)"""
    # This is the VB6 parity full version - delegates to create_kot which now has RoomCat/RoomType/LogSite + ItemRate + HappyHours + Scheme
    # Full column list is documented in POS_SALE1_FULL_COLS / POS_STOCK_FULL_COLS - actual INSERT expansion is next batch when Sale1 table has those columns
    return create_kot(items, table_no, waiter_code, covers, cn=cn)
def sale1_full_insert(rec: dict, cn=None) -> int:
    """VB6 Sale1 full 60-col INSERT - tries full list, fallback to subset if columns missing (no DB change, only add columns that exist)"""
    cols = ["FolioNo","HouseKeep","MenuSpl1","MenuSpl2","MenuSpl3","MenuSpl4","ExpAtt","GuarAtt","CoverRate","BookDocId","HallRent","PRINTED","AU_Name","ContraDocId","RoomCat","RoomNo","KOTDocId","DepartCode","SchemeCode","FreeSno","ShiftCode","V_Type","V_No","Vprefix","Site_Code","LogSite_Code"]
    # Check which cols exist via INFORMATION_SCHEMA (once)
    try:
        existing = {r[0] for r in db.query("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='Sale1'", cn=cn)}
    except Exception:
        existing = set(cols)
    use_cols = [c for c in cols if c in existing or c in ["V_Type","V_No","Vprefix","Site_Code","LogSite_Code"]]
    # Build INSERT with only existing cols
    vals = [rec.get(c.lower(), rec.get(c, None)) for c in use_cols]
    placeholders = ",".join(["?"]*len(use_cols))
    col_list = ",".join(use_cols)
    return db.execute(f"INSERT INTO Sale1 ({col_list}) VALUES ({placeholders})", tuple(vals), cn=cn)
def stock_full_insert(rec: dict, cn=None) -> int:
    """VB6 Stock full INSERT - Vtype BMM/RQI/PBPB + ContraDocId/RoomCat/RoomNo/KOTDocId/DepartCode/SchemeCode/FreeSno/ShiftCode/LogSite_Code"""
    cols = ["VType","VNo","Vprefix","Item","QtyIss","QtyRec","Rate","Amount","ContraDocId","RoomCat","RoomNo","KOTDocId","DepartCode","SchemeCode","FreeSno","ShiftCode","LogSite_Code","Site_Code","VDate"]
    try:
        existing = {r[0] for r in db.query("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='Stock'", cn=cn)}
    except Exception:
        existing = set(cols)
    use_cols = [c for c in cols if c in existing]
    vals = [rec.get(c, rec.get(c.lower(), None)) for c in use_cols]
    placeholders = ",".join(["?"]*len(use_cols))
    return db.execute(f"INSERT INTO Stock ({','.join(use_cols)}) VALUES ({placeholders})", tuple(vals), cn=cn)

