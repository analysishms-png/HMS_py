"""Check-Out core (VB6: Front Office -> Check-Out / Reverse Check-Out).

LIVE DB EVIDENCE:
- GuestFolio table does NOT contain CheckOutYN / CheckOutDate / CheckOutUser.
- Actual checkout state is tracked on RoomOcc via ChkOutDate, ChkOutTime,
  ChkoutUser, Type='O' for occupied rows; reverse checkout reopens by setting
  ChkOutDate=NULL, ChkOutTime='', Type='' (or NULL) and preserving the row.
- Before checkout: balance verification (AmtDr - AmtCr in PayCharge for
  this folio's DocId = outstanding balance).
- FolioLog: flag='C' (Checkout) on checkout, 'R' on Reverse Checkout.
- PYT-guard: production check-outs VB6 EXE se hi; hum PYT* folios test.
"""
from __future__ import annotations

import datetime

from HMS_py.core import db, checkin

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()


def _get_checkout_type(cn=None) -> str:
    """Read checkout validation type from the live Enviro settings.

    Live schema evidence: the column is named 'Checkout' (with the same
    value used by VB6 for the checkout-time rule label), not 'CheckOutType'.
    Some legacy code references a non-existent column, so we fall back safely.

    BUG-016 fix: f-string column probing ki jagah ek hi parameterized
    query jo sirf existing columns ko try karti hai; pehla non-empty
    value return hota hai. Non-column errors swallow nahi hote.
    """
    # Live DB me jo column exist karta hai wahi order me try karo.
    # Each candidate pe ek targeted query - 'Invalid column name'
    # errors pe hi next candidate, baaki errors propagate.
    for col in ("Checkout", "CheckOutType", "CheckoutType", "CheckOut"):
        try:
            rows = db.query(
                f"SELECT [{col}] FROM Enviro WHERE LogSite_Code = ? OR LogSite_Code = 'HO'",
                (SITE_CODE,), cn=cn,
            )
        except db.pyodbc.Error as e:
            # SQL Server error 207 = Invalid column name -> next candidate
            if "207" in str(e) or "Invalid column name" in str(e):
                continue
            raise
        if rows and rows[0][0] not in (None, ""):
            return str(rows[0][0])
    return "Standard"


def folio_balance(folio: int, cn=None,
                  vprefix: str = "2026") -> dict:
    """Outstanding balance for a folio (Dr - Cr from PayCharge).

    Returns: {folio, docid, charges_dr, payments_cr, balance, currency}
    Positive balance = guest owes money.
    """
    rec = checkin.get(folio, cn=cn, vprefix=vprefix)
    if not rec:
        raise ValueError(f"Folio #{folio} nahi mila")
    rows = db.query(
        "SELECT ISNULL(SUM(AmtDr),0), ISNULL(SUM(AmtCr),0) "
        "FROM PayCharge WHERE FolioNoDocid = ? AND Site_Code = ?",
        (rec["docid"], SITE_CODE), cn=cn)
    dr = float(rows[0][0]) if rows else 0.0
    cr = float(rows[0][1]) if rows else 0.0
    return {
        "folio": folio, "docid": rec["docid"],
        "charges_dr": dr, "payments_cr": cr,
        "balance": round(dr - cr, 2),
        "name": rec["name"], "depdate": rec["depdate"],
    }


def list_active_folios(cn=None, vprefix: str = "2026",
                       top: int = 200) -> list[dict]:
    """Checked-in folios still open in RoomOcc (ChkOutDate IS NULL)."""
    rows = db.query(
        f"SELECT TOP {int(top)} ro.DocId, gf.FolioNo, gf.Name, gf.GuestProf, gf.City, "
        "gf.NoDays, gf.DepDate, ro.ChkOutDate, ro.ChkoutUser, gf.U_Name, gf.U_AE, ro.RoomNo "
        "FROM RoomOcc ro INNER JOIN GuestFolio gf ON gf.DocId = ro.DocId "
        "WHERE ro.Site_Code = ? AND ro.Vprefix = ? AND ro.ChkOutDate IS NULL "
        "ORDER BY gf.FolioNo DESC",
        (SITE_CODE, vprefix), cn=cn)
    out = []
    for r in rows:
        doc, fno, name, gp, city, nod, dep, cod, cou, un, uae, room = r
        out.append({
            "docid": doc, "folio": fno,
            "name": (name or "").strip(),
            "guestprof": gp or "", "city": city or "",
            "roomno": (room or "").strip(),
            "nodays": nod or 0,
            "depdate": dep.date() if isinstance(dep, datetime.datetime) else dep,
            "checkout_date": cod,
            "checkout_user": cou or "",
            "u_name": un or "", "u_ae": uae or "",
        })
    return out


def list_checked_out(cn=None, vprefix: str = "2026",
                     top: int = 200) -> list[dict]:
    """Already checked-out folios via RoomOcc.ChkOutDate IS NOT NULL."""
    rows = db.query(
        "SELECT TOP (?) ro.DocId, gf.FolioNo, gf.Name, gf.DepDate, ro.ChkOutDate, ro.ChkoutUser "
        "FROM RoomOcc ro INNER JOIN GuestFolio gf ON gf.DocId = ro.DocId "
        "WHERE ro.Site_Code = ? AND ro.Vprefix = ? AND ro.ChkOutDate IS NOT NULL "
        "ORDER BY gf.FolioNo DESC",
        (int(top), SITE_CODE, vprefix), cn=cn)
    out = []
    for r in rows:
        doc, fno, name, dep, cod, cou = r
        out.append({
            "docid": doc, "folio": fno,
            "name": (name or "").strip(),
            "depdate": dep.date() if isinstance(dep, datetime.datetime) else dep,
            "checkout_date": cod.date() if isinstance(cod, datetime.datetime) else cod,
            "checkout_user": cou or "",
        })
    return out


def do_checkout(folio: int, user: str = USER, cn=None,
                commit: bool = True, vprefix: str = "2026",
                site: str = SITE_CODE) -> dict:
    """VB6 checkout flow using the live RoomOcc status fields.

    1. Folio exists and is currently active.
    2. Validate checkout type from Enviro settings.
    3. Mark RoomOcc row as checked out: ChkOutDate=getdate(), ChkoutUser=user,
       ChkOutTime=now, Type='O'.
    4. FolioLog: flag='C'.
    Returns balance info dict.
    """
    rec = checkin.get(folio, cn=cn, vprefix=vprefix)
    if not rec:
        raise ValueError(f"Folio #{folio} nahi mila")

    rows = db.query(
        "SELECT DocId, ChkOutDate, Type FROM RoomOcc WHERE Site_Code = ? AND "
        "Vprefix = ? AND FolioNo = ? AND ChkOutDate IS NULL ORDER BY SNo",
        (site, vprefix, folio), cn=cn)
    if not rows:
        raise ValueError(f"Folio #{folio} checked-out ya room row missing hai")

# Validate checkout type from Enviro (VB6 FdCheckOut.frm:3202)
    checkout_type = _get_checkout_type(cn=cn)
    bal = folio_balance(folio, cn=cn, vprefix=vprefix)

    # VB6 FdCheckOut.frm:3202 — checkout blocks while guest balance != 0
    # ONLY for "Strict" type. "Standard" type allows non-zero balance
    # (Settlement is the separate fdReSetlement flow).
    if checkout_type == "Strict" and abs(bal["balance"]) > 0.005:
        raise ValueError(f"Checkout type '{checkout_type}' requires zero balance")

    # VB6 FdCheckOut.frm:3465-3482: RoomCheckOutClearanceYN enabled hone
    # par clearance pending ho to checkout block.
    clr = check_clearance(folio, cn=cn)
    if clr["enabled"] and not clr["cleared"]:
        raise ValueError("Room Check Out Clearance Is Still Pending.")

    own = cn is None
    cn_use = cn or db.connect()
    try:
        db.execute(
            "UPDATE RoomOcc SET ChkOutDate = getdate(), ChkOutTime = CONVERT(varchar(5), getdate(), 108), "
            "ChkoutUser = ?, Type = 'O', U_Name = ?, U_EntDt = getdate(), U_AE = 'E' "
            "WHERE Site_Code = ? AND Vprefix = ? AND FolioNo = ? AND ChkOutDate IS NULL",
            (user, user, site, vprefix, folio),
            cn=cn_use, commit=False)

        log_rows = db.query(
            "SELECT MAX(Id) FROM FolioLog WHERE LogSite_Code = ?",
            (site,), cn=cn_use)
        logid = (log_rows[0][0] or 0) + 1 if log_rows and log_rows[0][0] else 1
        db.execute(
            "INSERT INTO FolioLog (Id, FolionoDocid, Flag, Site_Code, "
            "U_Name, U_EntDt, U_AE, LogSite_Code) "
            "VALUES (?, ?, 'C', ?, ?, getdate(), 'A', ?)",
            (logid, rec["docid"], site, user, site),
            cn=cn_use, commit=False)

        if commit:
            cn_use.commit()
        return bal
    finally:
        if own:
            cn_use.close()


def reverse_checkout(folio: int, user: str = USER, cn=None,
                     commit: bool = True, vprefix: str = "2026",
                     site: str = SITE_CODE) -> int:
    """VB6 reverse checkout: reopen the live RoomOcc row."""
    rows = db.query(
        "SELECT DocId, ChkOutDate FROM RoomOcc WHERE Site_Code = ? AND "
        "Vprefix = ? AND FolioNo = ? AND ChkOutDate IS NOT NULL ORDER BY SNo",
        (site, vprefix, folio), cn=cn)
    if not rows:
        raise ValueError(f"Folio #{folio} checked-out nahi hai")

    own = cn is None
    cn_use = cn or db.connect()
    try:
        n = db.execute(
            "UPDATE RoomOcc SET ChkOutDate = NULL, ChkOutTime = '', "
            "ChkoutUser = NULL, UserChkOutDate = NULL, Type = '', "
            "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' "
            "WHERE Site_Code = ? AND Vprefix = ? AND FolioNo = ? AND ChkOutDate IS NOT NULL",
            (user, site, vprefix, folio), cn=cn_use, commit=False)

        # VB6 FdRevCheckOut.frm:1482: group members (MFolioNoDocid link)
        # bhi reverse - UserChkOutDate/ChkOutUser clear on Type='O' rows.
        gf = db.query(
            "SELECT MFolioNoDocid FROM GuestFolio WHERE DocId = ?",
            (rows[0][0],), cn=cn_use)
        mfdocid = (gf[0][0] or "").strip() if gf and gf[0][0] else ""
        if mfdocid:
            db.execute(
                "UPDATE RoomOcc SET ChkOutDate = NULL, ChkOutTime = '', "
                "ChkoutUser = NULL, UserChkOutDate = NULL, Type = '', "
                "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' "
                "WHERE Site_Code = ? AND Type = 'O' AND DocId IN ("
                "SELECT DocId FROM GuestFolio WHERE MFolioNoDocid = ?)",
                (user, site, mfdocid), cn=cn_use, commit=False)

        # VB6 FdRevCheckOut.frm:1490-1503: settle marks reverse
        db.execute(
            "UPDATE PayCharge SET SettleDate = NULL, Bill_No = NULL "
            "WHERE Site_Code = ? AND VPrefix = ? AND FolioNo = ? AND "
            "Vtype NOT IN ('ARRES', 'ADRES')",
            (site, vprefix, folio), cn=cn_use, commit=False)
        db.execute(
            "UPDATE PayCharge SET ModeSet = '' WHERE Site_Code = ? AND "
            "VPrefix = ? AND FolioNo = ? AND ModeSet = 'S' AND "
            "PayCode <> ?",
            (site, vprefix, folio, "KKROFF"), cn=cn_use, commit=False)
        db.execute(
            "UPDATE FOMBillDetails SET Status = 'CANCEL', U_Name = ?, "
            "U_EntDt = getdate(), U_AE = 'E' WHERE FolioNo = ? AND "
            "SiteCode = ? AND Status = 'SETTLE'",
            (user, folio, site), cn=cn_use, commit=False)

        log_rows = db.query(
            "SELECT MAX(Id) FROM FolioLog WHERE LogSite_Code = ?",
            (site,), cn=cn_use)
        logid = (log_rows[0][0] or 0) + 1 if log_rows and log_rows[0][0] else 1
        db.execute(
            "INSERT INTO FolioLog (Id, FolionoDocid, Flag, Site_Code, "
            "U_Name, U_EntDt, U_AE, LogSite_Code) "
            "VALUES (?, ?, 'R', ?, ?, getdate(), 'A', ?)",
            (logid, rows[0][0], site, user, site),
            cn=cn_use, commit=False)

        if commit:
            cn_use.commit()
        return n
    finally:
        if own:
            cn_use.close()


# ============================================================
# Checkout Clearance (VB6: HRoomCheckOutClearance)
# ============================================================

def get_clearance_flag(cn=None) -> str:
    """Read RoomCheckOutClearanceYN from Enviro. Returns 'Yes'/'No'."""
    rows = db.query(
        "SELECT RoomCheckOutClearanceYN FROM Enviro WHERE LogSite_Code = ?",
        (SITE_CODE,), cn=cn)
    if rows and rows[0][0]:
        return str(rows[0][0]).strip()
    return "No"


def check_clearance(folio: int, cn=None) -> dict:
    """Check checkout clearance for a folio (VB6 HRoomCheckOutClearance).

    Returns: {
        "enabled": bool,        # Is clearance required?
        "cleared": bool,        # All checks passed?
        "bill_settled": bool,   # FOMBillDetails status = SETTLE
        "balance_zero": bool,   # Outstanding balance = 0
        "bill_status": str,     # SETTLE/PENDING/NONE
        "balance": float,       # Outstanding amount
        "message": str,         # Human-readable status
    }
    """
    flag = get_clearance_flag(cn=cn)
    enabled = flag.lower() == "yes"

    # Check FOMBillDetails status
    bill_rows = db.query(
        "SELECT TOP 1 Status, BillAmt FROM FOMBillDetails "
        "WHERE FolioNo = ? AND SiteCode = ? ORDER BY Bill_No DESC",
        (folio, SITE_CODE), cn=cn)
    if bill_rows:
        bill_status = str(bill_rows[0][0] or "").strip().upper()
        bill_settled = bill_status == "SETTLE"
    else:
        bill_status = "NONE"
        bill_settled = True  # No bill = no issue

    # Check outstanding balance
    try:
        bal_info = folio_balance(folio, cn=cn)
        balance = bal_info.get("balance", 0)
    except ValueError:
        balance = 0  # Folio not found = no outstanding
    balance_zero = abs(balance) < 0.01

    cleared = bill_settled and balance_zero

    if not enabled:
        msg = "Clearance not required (RoomCheckOutClearanceYN=No)"
    elif cleared:
        msg = "All cleared - OK to checkout"
    else:
        issues = []
        if not bill_settled:
            issues.append(f"Bill status={bill_status}")
        if not balance_zero:
            issues.append(f"Balance outstanding={balance:.2f}")
        msg = "NOT cleared: " + "; ".join(issues)

    return {
        "enabled": enabled,
        "cleared": cleared,
        "bill_settled": bill_settled,
        "balance_zero": balance_zero,
        "bill_status": bill_status,
        "balance": balance,
        "message": msg,
    }


def clearance_list(cn=None, top: int = 100) -> list:
    """List recent settled bills for clearance review (FOMBillDetails browse)."""
    rows = db.query(
        f"SELECT TOP {int(top)} Bill_No, Bill_Date, FolioNo, Guestname, "
        "BillAmt, SettMode, SettAmt, Status "
        "FROM FOMBillDetails WHERE SiteCode = ? "
        "ORDER BY Bill_Date DESC, Bill_No DESC",
        (SITE_CODE,), cn=cn)
    return [{"bill_no": r.Bill_No or "", "bill_date": r.Bill_Date,
             "folio": r.FolioNo, "guest": (r.Guestname or "").strip(),
             "bill_amt": float(r.BillAmt or 0),
             "sett_mode": (r.SettMode or "").strip(),
             "sett_amt": float(r.SettAmt or 0),
             "status": (r.Status or "").strip()} for r in rows]
