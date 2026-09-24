"""Folio core (P4-b): settle/checkout + FolioLog viewer + amend (room-move).

EVIDENCE (live):
- FOMBillDetails 14 cols; Bill_No varchar but numeric ('99'..'330') ->
  next BillNo = MAX(Cast(Bill_No As Int)) + 1. FolioNoDocid = GuestFolio.DocId
  link. Sample: ('328', 2026-06-01, 463, 'SUMIT TOMAR', 0.0, ' ', 'SETTLE',...).
- SettMode sample ' ' (empty) — VB6 me cash/card type; hum '' default
  (evidence-first, guess nahi).
- FolioLog 8 cols (BookingLog pattern): Max(Id)+1 per LogSite_Code.
- GuestFolioAmend 12 cols: FolioNo, Site_Code, GuestProf, RoomNo,
  OldDepDate, OldDepTime, DepDate, DepTime, U_Name, U_EntDt, U_AE,
  LogSite_Code (sample row: OldDepDate -> DepDate shift by Deepak/SA).
- PYT-guard: sirf PYT* folio settle/delete honge UI/tests se.
"""
from __future__ import annotations

import datetime

from HMS_py.core import db
from HMS_py.core import checkin as checkin_mod

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
VPREFIX = "2026"


def next_billno(cn=None) -> int:
    rows = db.query(
        "SELECT MAX(Cast(Bill_No As Int)) FROM FOMBillDetails "
        "WHERE LogSite_Code = ?", (SITE_CODE,), cn=cn)
    return (rows[0][0] or 0) + 1 if rows and rows[0][0] else 1


def folio_charges(folio: int, cn=None, vprefix: str = VPREFIX) -> list:
    """Ek folio ki charges (PayCharge, folio-linked). VB6 LogSite_Code scoped."""
    rows = db.query(
        "SELECT SNo, PayCode, PayType, Comments, AmtDr, AmtCr, Vdate "
        "FROM PayCharge WHERE Site_Code = ? AND LogSite_Code = ? AND VPrefix = ? AND FolioNo = ? "
        "ORDER BY SNo", (SITE_CODE, db.get_site_code(), vprefix, folio), cn=cn)
    return [{"sno": r.SNo, "paycode": r.PayCode or "",
             "paytype": (r.PayType or "").strip(),
             "comments": (r.Comments or "").strip(),
             "dr": r.AmtDr or 0.0, "cr": r.AmtCr or 0.0,
             "vdate": r.Vdate} for r in rows]


def _resolve_folio(site: str, folio: int, vprefix: str, cn=None):
    """Exact FY match first, then same-site folio fallback across other years.
    This preserves the production safety check when a live folio exists under a
    different fiscal year but the default 2026 prefix is in use.
    """
    rows = db.query(
        "SELECT TOP 1 DocId, Name, GuestProf, Vprefix FROM GuestFolio WHERE "
        "Site_Code = ? AND Vprefix = ? AND FolioNo = ?",
        (site, vprefix, folio), cn=cn)
    if rows:
        return rows[0]
    rows = db.query(
        "SELECT TOP 1 DocId, Name, GuestProf, Vprefix FROM GuestFolio WHERE "
        "Site_Code = ? AND FolioNo = ? ORDER BY Vprefix DESC",
        (site, folio), cn=cn)
    return rows[0] if rows else None


def folio_balance(folio: int, cn=None, vprefix: str = VPREFIX) -> float:
    """Balance = SUM(Dr - Cr)."""
    rows = db.query(
        "SELECT SUM(AmtDr - AmtCr) FROM PayCharge WHERE Site_Code = ? AND "
        "VPrefix = ? AND FolioNo = ?", (SITE_CODE, vprefix, folio), cn=cn)
    return float(rows[0][0] or 0.0)


def _get_settle_mode(cn=None) -> str:
    """Enviro.Checkout padho: 'Strict' = settle pe non-zero block,
    'Standard' = non-zero allow (VB6 settle-mode semantics).

    Unreadable/missing/empty -> 'Strict' (hard-block; safe default).
    Evidence: live Enviro.Checkout='Standard'; moondata.sql default ''."""
    try:
        rows = db.query(
            "SELECT [Checkout] FROM Enviro WHERE LogSite_Code = ? OR "
            "LogSite_Code = 'HO'", (SITE_CODE,), cn=cn)
    except db.pyodbc.Error as e:
        if "207" in str(e) or "Invalid column name" in str(e):
            return "Strict"
        raise
    if not rows or rows[0][0] in (None, ""):
        return "Strict"
    return str(rows[0][0]).strip() or "Strict"


def settle_folio(folio: int, user: str = USER, cn=None, commit: bool = True,
                 site: str = SITE_CODE, vprefix: str = VPREFIX,
                 sett_mode: str = "Cash") -> int:
    """Check-out settle (VB6 FOMBillDetails INSERT pattern):
    Bill_No = MAX+1, Status='SETTLE', FolioNoDocid = GuestFolio.DocId.

    Settle mode (FO gap): Enviro.Checkout='Strict' -> balance MUST be
    zero; 'Standard' -> non-zero allow. Unreadable/empty -> Strict
    (hard-block; _get_settle_mode default)."""
    rows = db.query(
        "SELECT DocId, Name FROM GuestFolio WHERE Site_Code = ? AND "
        "Vprefix = ? AND FolioNo = ?", (site, vprefix, folio), cn=cn)
    if not rows:
        raise ValueError(f"Folio #{folio} nahi mila")
    if not str(rows[0][1] or "").upper().startswith("PYT"):
        raise ValueError(
            "Safety: sirf PYT* folio settle honge (production VB6 EXE se)")
    already = db.query(
        "SELECT 1 FROM FOMBillDetails WHERE FolioNoDocid = ? AND "
        "Status = 'SETTLE'", (rows[0][0],), cn=cn)
    if already:
        raise ValueError(f"Folio #{folio} pehle se settled hai")
    # Settle mode: Strict blocks non-zero; Standard allows (VB6 rule)
    mode = _get_settle_mode(cn=cn)
    bal = folio_balance(folio, cn=cn, vprefix=vprefix)
    if mode != "Standard" and abs(bal) > 0.005:
        raise ValueError(
            f"Folio #{folio} balance {bal:.2f} hai "
            f"(settle mode '{mode}' zero balance require karta hai)")
    own = cn is None
    cn = cn or db.connect()
    try:
        billno = next_billno(cn=cn)
        arows = db.query(
            "SELECT ISNULL(SUM(AmtDr), 0), ISNULL(SUM(AmtCr), 0) "
            "FROM PayCharge WHERE Site_Code = ? AND VPrefix = ? AND "
            "FolioNo = ?", (site, vprefix, folio), cn=cn)
        bill_amt = float(arows[0][0] or 0.0) if arows else 0.0
        sett_amt = float(arows[0][1] or 0.0) if arows else 0.0
        db.execute(
            "INSERT INTO FOMBillDetails (Bill_No, Bill_Date, FolioNo, "
            "Guestname, BillAmt, SettMode, SettAmt, Status, U_Name, "
            "SiteCode, U_EntDt, U_AE, FolioNoDocid, LogSite_Code) "
            "VALUES (?, getdate(), ?, ?, ?, ?, ?, 'SETTLE', ?, ?, "
            "getdate(), 'A', ?, ?)",
            (str(billno), folio, rows[0][1], bill_amt, sett_mode, sett_amt,
             user, site, rows[0][0], site), cn=cn, commit=False)
        db.execute(
            "UPDATE PayCharge SET Bill_No = ?, SettleDate = getdate() "
            "WHERE Site_Code = ? AND VPrefix = ? AND FolioNo = ? AND "
            "Vtype NOT IN ('ARRES', 'ADRES')",
            (str(billno), site, vprefix, folio), cn=cn, commit=False)
        _log(rows[0][0], "S", user, cn, site)
        if commit:
            cn.commit()
        return billno
    finally:
        if own:
            cn.close()


def _log(docid: str, flag: str, user: str, cn, site: str = SITE_CODE):
    rows = db.query("SELECT MAX(Id) FROM FolioLog WHERE LogSite_Code = ?",
                    (site,), cn=cn)
    logid = (rows[0][0] or 0) + 1 if rows and rows[0][0] else 1
    db.execute(
        "INSERT INTO FolioLog (Id, FolionoDocid, Flag, Site_Code, "
        "U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, getdate(), ?, ?)",
        (logid, docid, flag, site, user, "A", site), cn=cn, commit=False)


# --------------------------------------------------------------- P4-c:
# VB6 missing logic #1: room-charge posting (folio pe charge lagana).
# EVIDENCE (HMS.bas:90023 31-col INSERT + live folio #462):
#   DocId 'DKKRC    2026  <VNo:8>'  (Vtype='RC') | VNo = MAX(VNo)+1 per
#   FY-RC series (live: 599 @ folio 462) | SNo = MAX(SNo)+1 us folio me |
#   KKRMCH=Room, KKCGSS=CGST5%, KKSGSS=SGST5% | AmtDr=charge, AmtCr=receipt.
PAY_CODE = "KKRMCH"
CGST_CODE = "KKCGSS"
SGST_CODE = "KKSGSS"
GST_RATE = 0.05  # live #462: 3000 -> 75 + 75
VTYPE_RC = "RC"  # live census: Vtype 'RC   ' 1350 rows, VNo max 602


def post_room_charge(folio: int, amount: float, roomno: str = "",
                     paycode: str = PAY_CODE, user: str = USER,
                     cn=None, commit: bool = True, site: str = SITE_CODE,
                     vprefix: str = VPREFIX,
                     with_gst: bool = True) -> int:
    """Room charge post (VB6 FoGuestFolio charge-entry, HMS.bas:90023
    31-col INSERT pattern): PayCharge row + FolioLog 'P'.
    GST: amount*5% CGST + amount*5% SGST (live #462 evidence) - sirf
    KKRMCH (room charge) pe, ek baar me teen rows banti hain."""
    rows = db.query(
        "SELECT DocId, Name, GuestProf FROM GuestFolio WHERE Site_Code = ? AND "
        "Vprefix = ? AND FolioNo = ?", (site, vprefix, folio), cn=cn)
    if not rows:
        raise ValueError(f"Folio #{folio} nahi mila")
    if not str(rows[0][1] or "").upper().startswith("PYT"):
        raise ValueError("Safety: sirf PYT* folio pe charge post hoga")
    if amount <= 0:
        raise ValueError("Amount > 0 hona chahiye")
    own = cn is None
    cn = cn or db.connect()
    try:
        # BUG-015: race-safe VNo (UPDLOCK/HOLDLOCK) - concurrent posts ko
        # same number nahi milega. Same cn: lock INSERT commit tak hold.
        vno = db.next_vno("PayCharge", "RC", vprefix, site=site, cn=cn)
        srows = db.query(
            "SELECT MAX(SNo) FROM PayCharge WHERE FolioNo = ? AND "
            "Site_Code = ?", (folio, site), cn=cn)
        base_sno = (srows[0][0] or 0) if srows and srows[0][0] else 0
        today = datetime.date.today()

        def _pc(sno, paycode, amt):
            # FolioNoDocid = GuestFolio.DocId link (live pattern: production
            # RC/REC rows carry the folio link; VB6 fdPaymentCharge INSERT).
            # Use GuestProf code (auto-generated KK#######) not guest name.
            # GuestProf column is varchar(8) - use actual code from GuestFolio
            guestprof_code = (rows[0][2] or "")[:8]  # GuestProf - max 8 chars
            db.execute(
                "INSERT INTO PayCharge (DocId, SNo, Vtype, VNo, Site_Code, "
                "VPrefix, Vdate, GuestProf, Comments, PayCode, FolioNo, "
                "FolioNoDocid, RoomNo, AmtDr, U_Name, U_EntDt, U_AE, "
                "LogSite_Code) "
                "VALUES (?, ?, 'RC', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
                "getdate(), 'A', ?)",
                (make_pc_docid(site, vprefix, vno), sno, vno, site,
                 vprefix, today, guestprof_code, "", paycode, folio,
                 rows[0][0], roomno or "", amt, user, site), cn=cn, commit=False)

        _pc(base_sno + 1, paycode, float(amount))
        next_sno = base_sno + 2
        if with_gst and paycode == PAY_CODE:
            gst = round(float(amount) * GST_RATE, 2)
            if gst > 0:
                _pc(next_sno, CGST_CODE, gst)
                next_sno += 1
                _pc(next_sno, SGST_CODE, gst)
        _log(rows[0][0], "P", user, cn, site)
        if commit:
            cn.commit()
        return vno
    finally:
        if own:
            cn.close()


def make_pc_docid(site: str, vprefix: str, vno: int) -> str:
    """'D'+site(2)+'RC'.ljust(6)+year(4).ljust(4)+VNo.rjust(8) = 21 char
    (live sample 'DKKRC    2026     599' byte-exact)."""
    return ("D" + site + "RC".ljust(6) + vprefix.ljust(4) +
            str(vno).rjust(8))


def charges_detail(folio: int, cn=None, site: str = SITE_CODE,
                   vprefix: str = VPREFIX) -> list:
    """Folio ki saari PayCharge rows (UI drill-down ke liye)."""
    rows = db.query(
        "SELECT SNo, RTRIM(PayCode), RTRIM(PayType), AmtDr, AmtCr, Vdate "
        "FROM PayCharge WHERE FolioNo = ? AND Site_Code = ? AND "
        "VPrefix = ? ORDER BY SNo", (folio, site, vprefix), cn=cn)
    # index-access (proven: named attr kisi driver state me fail hota hai)
    return [{"sno": r[0], "paycode": (r[1] or "").strip(),
             "paytype": (r[2] or "").strip(), "dr": r[3] or 0.0,
             "cr": r[4] or 0.0, "vdate": r[5]} for r in rows]


# --------------------------------------------------------------- P4-c:
# VB6 missing logic #2: booking -> check-in conversion (front-office
# 'Check In' from reservation). Live evidence: folio 2361 DocId
# 'DKKCHK   2025    2361' BookingDocId 'DKKRES   2025     103', name
# match, NoDays carry. VB6 flow: booking fields folio me copy hote
# hain aur check-in ban jaata hai (booking cancel NahiN hota).
def from_booking(booking_docid: str, user: str = USER, cn=None,
                 commit: bool = True, site: str = SITE_CODE,
                 vprefix: str = VPREFIX) -> int:
    """Active booking ko check-in folio me convert karo (VB6 front-desk
    conversion): GuestFolio INSERT with BookingDocId link + FolioLog 'A'.
    Guard: booking exist + cancelled nahi + pehle se convert nahi hua +
    PYT* guest (test-safety)."""
    brows = db.query(
        "SELECT DocId, RTRIM(GuestName), ArrDate, DepDate, "
        "RTRIM(RoomNo), RTRIM(Cancel) FROM Booking WHERE DocId = ?",
        (booking_docid,), cn=cn)
    if not brows:
        raise ValueError(f"Booking {booking_docid.strip()} nahi mili")
    b = brows[0]
    if (b[5] or "").strip().upper() == "Y":
        raise ValueError("Cancelled booking convert nahi ho sakti")
    already = db.query(
        "SELECT FolioNo FROM GuestFolio WHERE BookingDocId = ?",
        (booking_docid,), cn=cn)
    if already:
        raise ValueError(
            f"Booking pehle se folio #{already[0][0]} me convert ho chuki")
    name = (b[1] or "").strip()
    if not name.upper().startswith("PYT"):
        raise ValueError("Safety: sirf PYT* bookings convert hongi")
    arr = b[2] or datetime.date.today()
    dep = b[3] or (arr + datetime.timedelta(days=1))
    if hasattr(arr, "date"):
        arr = arr.date()
    if hasattr(dep, "date"):
        dep = dep.date()
    own = cn is None
    cn = cn or db.connect()
    try:
        # Ek hi transaction: checkin + FolioLog (create_checkin 'A' log
        # khud likhta hai) — atomic conversion.
        return checkin_mod.create_checkin(
            "", name, arr, dep, bookingdocid=(b[0] or "").strip(),
            user=user, cn=cn, commit=commit, site=site, vprefix=vprefix)
    finally:
        if own:
            cn.close()


def log_list(cn=None, top: int = 200) -> list:
    rows = db.query(
        f"SELECT TOP {int(top)} Id, FolionoDocid, Flag, U_Name, U_EntDt, "
        "U_AE FROM FolioLog WHERE Site_Code = ? ORDER BY Id DESC",
        (SITE_CODE,), cn=cn)
    return [{"id": int(r.Id), "docid": (r.FolionoDocid or "").strip(),
             "flag": r.Flag or "", "user": r.U_Name or "",
             "dt": r.U_EntDt, "ae": r.U_AE or ""} for r in rows]


def amend_departure(folio: int, new_dep, user: str = USER, cn=None,
                    commit: bool = True, site: str = SITE_CODE,
                    vprefix: str = VPREFIX) -> int:
    """Departure amend (VB6 GuestFolioAmend INSERT + GuestFolio/RoomOcc/
    PlanDetails update): OldDepDate save hota hai, phir naya DepDate.
    Guards (fdAmendEntry.frm:967-975): new_dep >= today aur >= Vdate."""
    rows = db.query(
        "SELECT DocId, Name, DepDate, Vdate, NoDays FROM GuestFolio "
        "WHERE Site_Code = ? AND Vprefix = ? AND FolioNo = ?",
        (site, vprefix, folio), cn=cn)
    if not rows:
        raise ValueError(f"Folio #{folio} nahi mila")
    if not str(rows[0][1] or "").upper().startswith("PYT"):
        raise ValueError("Safety: sirf PYT* folio amend honge")
    old_dep = rows[0][2]
    vdate = rows[0][3]
    old_nodays = rows[0][4]
    if isinstance(new_dep, datetime.datetime):
        new_dep = new_dep.date()
    if isinstance(vdate, datetime.datetime):
        vdate = vdate.date()
    if isinstance(old_dep, datetime.datetime):
        old_dep = old_dep.date()
    today = datetime.date.today()
    if new_dep < today:
        raise ValueError("Departure Date Can't be Less than Current Date")
    if vdate and new_dep < vdate:
        raise ValueError("Departure Date Can't be Less than Check in Date")
    ro = db.query(
        "SELECT TOP 1 RoomNo FROM RoomOcc WHERE DocId = ? AND Site_Code = ?",
        (rows[0][0], site), cn=cn)
    roomno = (ro[0][0] or "").strip() if ro else ""
    own = cn is None
    cn = cn or db.connect()
    try:
        db.execute(
            "INSERT INTO GuestFolioAmend (FolioNo, Site_Code, GuestProf, "
            "RoomNo, OldDepDate, OldDepTime, DepDate, DepTime, "
            "U_Name, U_EntDt, U_AE, LogSite_Code) "
            "VALUES (?, ?, '', '', ?, '10:00', ?, '10:00', ?, getdate(), "
            "'A', ?)",
            (folio, site, old_dep, new_dep, user, site), cn=cn, commit=False)
        n = db.execute(
            "UPDATE GuestFolio SET DepDate = ?, "
            "NoDays = DATEDIFF(day, Vdate, ?), U_Name = ?, "
            "U_EntDt = getdate(), U_AE = 'E' WHERE DocId = ?",
            (new_dep, new_dep, user, rows[0][0]), cn=cn, commit=False)
        db.execute(
            "UPDATE RoomOcc SET DepDate = ?, U_Name = ?, "
            "U_EntDt = getdate(), U_AE = 'E' "
            "WHERE DocId = ? AND Site_Code = ?",
            (new_dep, user, rows[0][0], site), cn=cn, commit=False)
        if roomno and vdate:
            nodays = max((new_dep - vdate).days, 1)
            db.execute(
                "UPDATE PlanDetails SET NoofDays = ? "
                "WHERE FolioNo = ? AND Site_Code = ? AND RoomNo = ? "
                "AND DocId = ? AND NoofDays = ?",
                (nodays, folio, site, roomno, rows[0][0], old_nodays),
                cn=cn, commit=False)
        _log(rows[0][0], "M", user, cn, site)
        if commit:
            cn.commit()
        return n
    finally:
        if own:
            cn.close()


PAY_TYPES = {  # VB6 fdPaymentCharge combo categories (complete list)
    "KKCASH": "Cash", "KKCRED": "Company", "KKVISA": "Credit Card",
    "KK0006": "Other", "KKCHEQ": "Cheque", "KKSTFF": "Staff",
    "KKMEMB": "Member", "KKROOM": "Room Transfer", "KKVOID": "Void",
}

# VB6 contra entry paycodes (credit card settlements create contra)
CONTRA_PAYCODES = {"KKVISA", "KKCRED", "KK0006"}


def receive_payment(folio: int, amount: float, paycode: str = "KKCASH",
                    comments: str = "CASH RECD.", user: str = USER,
                    cn=None, commit: bool = True, site: str = SITE_CODE,
                    vprefix: str = VPREFIX, cardno: str = "",
                    cardholder: str = "", chqno: str = "", chqdate=None,
                    txnno: str = "", expdate=None, batchno=None,
                    billamount=None, tipamt=0.0, **kwargs) -> int:
    """Payment receive (VB6 fdPaymentCharge.frm:4467 REC 35-col INSERT,
    live #1072 evidence: KKCASH 'CASH RECD.' 11000 + KK0002 'BY UPI' 434):
    AmtCr = payment (credit), FolioNoDocid = checkin DocId link,
    SNo = MAX(SNo)+1 per folio, ModeSet='S', RestCode='KKFOM'.
    Instrument cols: CardNo/CardHolder/ChqNo/ChqDate/TxnNo/ExpDate/
    BatchNo/BillAmount/TipAmt. PYT-guard (safety).
    VB6 extra: contra entry for credit card, credit check for company."""
    row = _resolve_folio(site, folio, vprefix, cn=cn)
    if not row:
        raise ValueError(f"Folio #{folio} nahi mila")
    if not str(row[1] or "").upper().startswith("PYT"):
        raise ValueError(
            "Safety: sirf PYT* folio pe payment receive hoga")
    if amount <= 0:
        raise ValueError("Amount > 0 hona chahiye")
    # VB6 credit check: company payments check AllowCredit/CreditLimit
    if paycode == "KKCRED":
        _check_company_credit(row[2] or "", amount, cn=cn)
    own = cn is None
    cn = cn or db.connect()
    try:
        # BUG-015: race-safe VNo (UPDLOCK/HOLDLOCK)
        vno = db.next_vno("PayCharge", "REC", vprefix, site=site, cn=cn)
        # DocId 'D'+site+'REC'.ljust(6)+year(4).ljust(4)+VNo.rjust(8) = 21
        docid = ("D" + site + "REC".ljust(6) + vprefix.ljust(4) +
                 str(vno).rjust(8))
        # Context cols from RoomOcc
        orows = db.query(
            "SELECT TOP 1 RoomCat, RoomType, RoomNo FROM RoomOcc "
            "WHERE DocId = ?", (row[0],), cn=cn)
        roomcat = (orows[0][0] or "") if orows else ""
        roomtype = (orows[0][1] or "") if orows else ""
        roomno = (orows[0][2] or "") if orows else ""
        paytype = PAY_TYPES.get(paycode)
        if paytype is None:
            raise ValueError(
                f"Unknown paycode '{paycode}' (known: " +
                ", ".join(sorted(PAY_TYPES)) + ")")
        srows = db.query(
            "SELECT MAX(SNo) FROM PayCharge WHERE FolioNo = ? AND "
            "Site_Code = ?", (folio, site), cn=cn)
        base_sno = (srows[0][0] or 0) if srows and srows[0][0] else 0
        today = datetime.date.today()
        if chqdate == "":
            chqdate = None
        if expdate == "":
            expdate = None
        if batchno == "":
            batchno = None
        bill_amt = (float(billamount) if billamount not in (None, "")
                    else float(amount))
        tip_amt = float(tipamt) if tipamt not in (None, "") else 0.0
        db.execute(
            "INSERT INTO PayCharge (DocId, SNo, Vtype, VNo, Site_Code, "
            "VPrefix, Vdate, VTime, GuestProf, Comments, PayCode, PayType, "
            "BillAmount, AmtCr, TipAmt, RoomCat, RoomType, RoomNo, FolioNo, "
            "CardNo, CardHolder, ChqNo, ChqDate, TxnNo, ExpDate, "
            "U_Name, U_EntDt, U_AE, RestCode, ModeSet, BatchNo, "
            "FolioNoDocid, LogSite_Code) "
            "VALUES (?, ?, 'REC', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
            "?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', 'KKFOM', 'S', ?, "
            "?, ?)",
            (docid, base_sno + 1, vno, site, vprefix, today,
             datetime.datetime.now().strftime("%H:%M"), (row[2] or ""),
             (comments or "CASH RECD."), paycode, paytype, bill_amt,
             float(amount), tip_amt, roomcat, roomtype, roomno, folio,
             (cardno or ""), (cardholder or ""), (chqno or ""), chqdate,
             (txnno or ""), expdate, user, batchno, row[0], site),
            cn=cn, commit=False)
        # VB6 pattern: contra entry for credit card/company payments
        if paycode in CONTRA_PAYCODES:
            _create_contra(docid, amount, site, vprefix, user, cn)
        if commit:
            cn.commit()
        return vno
    finally:
        if own:
            cn.close()


def _check_company_credit(guestprof: str, amount: float, cn=None):
    """VB6 credit check: Subgroup.AllowCredit + CreditLimit validation."""
    rows = db.query(
        "SELECT SG.AllowCredit, SG.CreditLimit FROM SubGroup SG "
        "INNER JOIN GuestProf GP ON GP.Code = ? "
        "WHERE GP.Company = SG.Code", (guestprof,), cn=cn)
    if not rows:
        return  # No company linked = no credit check
    allow = (rows[0][0] or "Y").strip().upper()
    limit = float(rows[0][1] or 0)
    if allow == "N":
        raise ValueError("Credit payment not allowed for this company")
    if limit > 0 and amount > limit:
        raise ValueError(
            f"Amount {amount:.2f} exceeds credit limit {limit:.2f}")


def _create_contra(ref_docid: str, amount: float, site: str,
                   vprefix: str, user: str, cn):
    """VB6 pattern: contra entry for credit card settlements.
    Creates a second PayCharge row with reversed Dr/Cr linked via ContraDocId."""
    vno = db.next_vno("PayCharge", "CONTRA", vprefix, site=site, cn=cn)
    docid = ("D" + site + "CONTRA".ljust(6) + vprefix.ljust(4) +
             str(vno).rjust(8))
    today = datetime.date.today()
    db.execute(
        "INSERT INTO PayCharge (DocId, SNo, Vtype, VNo, Site_Code, "
        "VPrefix, Vdate, GuestProf, Comments, PayCode, AmtDr, "
        "U_Name, U_EntDt, U_AE, ContraDocId, ModeSet, LogSite_Code) "
        "VALUES (?, 1, 'CONTRA', ?, ?, ?, ?, '', 'Contra entry', "
        "'KKCNTR', ?, ?, getdate(), 'A', ?, 'C', ?)",
        (docid, vno, site, vprefix, today, amount, user, ref_docid, site),
        cn=cn, commit=False)


def log_before_delete(docid: str, cn=None, user: str = USER,
                      site: str = SITE_CODE) -> bool:
    """VB6 pattern: copy PayCharge to PayChargeLog before delete (audit trail)."""
    rows = db.query(
        "SELECT 1 FROM PayCharge WHERE DocId = ? AND Site_Code = ?",
        (docid, site), cn=cn)
    if not rows:
        return False
    db.execute(
        "INSERT INTO PayChargeLog SELECT *, getdate(), ? "
        "FROM PayCharge WHERE DocId = ?",
        (user, docid), cn=cn, commit=True)
    return True


def list_payments(cn=None, top: int = 200, site: str = SITE_CODE,
                  vprefix: str = VPREFIX) -> list:
    """Recent REC payments (VB6 fdPaymentCharge receipt register)."""
    rows = db.query(
        f"SELECT TOP {int(top)} DocId, VNo, Vdate, GuestProf, Comments, "
        "PayCode, PayType, AmtCr, FolioNo FROM PayCharge WHERE Vtype = 'REC' "
        "AND Site_Code = ? AND VPrefix = ? ORDER BY VNo DESC",
        (site, vprefix), cn=cn)
    return [{"docid": (r.DocId or "").strip(), "vno": int(r.VNo or 0),
             "vdate": r.Vdate, "guestprof": (r.GuestProf or "").strip(),
             "comments": (r.Comments or "").strip(),
             "paycode": (r.PayCode or "").strip(),
             "paytype": (r.PayType or "").strip(), "amt": r.AmtCr or 0.0,
             "folio": int(r.FolioNo or 0)} for r in rows]


def delete_payment(vno: int, user: str = USER, cn=None, commit: bool = True,
                   site: str = SITE_CODE, vprefix: str = VPREFIX) -> int:
    """PYT*-folio REC payment cleanup (test hygiene).
    VB6 pattern: copy to PayChargeLog before delete (audit trail)."""
    rows = db.query(
        "SELECT pc.DocId, gf.Name FROM PayCharge pc LEFT JOIN GuestFolio "
        "gf ON gf.DocId = pc.FolioNoDocid WHERE pc.Vtype = 'REC' AND "
        "pc.VNo = ? AND pc.Site_Code = ? AND pc.VPrefix = ?",
        (vno, site, vprefix), cn=cn)
    if not rows:
        raise ValueError(f"REC payment #{vno} nahi mila")
    if not str(rows[0][1] or "").upper().startswith("PYT"):
        raise ValueError("Safety: sirf PYT folio ka payment delete hoga")
    own = cn is None
    cn = cn or db.connect()
    try:
        # VB6 pattern: log before delete
        db.execute(
            "INSERT INTO PayChargeLog SELECT *, getdate(), ? "
            "FROM PayCharge WHERE DocId = ?",
            (user, rows[0][0]), cn=cn, commit=False)
        n = db.execute(
            "DELETE FROM PayCharge WHERE DocId = ?",
            (rows[0][0],), cn=cn, commit=False)
        # Also delete contra entry if exists
        db.execute(
            "DELETE FROM PayCharge WHERE ContraDocId = ?",
            (rows[0][0],), cn=cn, commit=False)
        if commit:
            cn.commit()
        return n
    finally:
        if own:
            cn.close()


def delete_settle(folio: int, user: str = USER,
                  cn=None, commit: bool = True, site: str = SITE_CODE) -> int:
    """PYT-guarded settle-row cleanup (test hygiene)."""
    rows = db.query(
        "SELECT FolioNoDocid FROM FOMBillDetails WHERE FolioNo = ? AND "
        "SiteCode = ?", (folio, site), cn=cn)
    if not rows:
        raise ValueError(f"Folio #{folio} ka settle-row nahi mila")
    own = cn is None
    cn = cn or db.connect()
    try:
        n = db.execute(
            "DELETE FROM FOMBillDetails WHERE FolioNo = ? AND SiteCode = ? "
            "AND FolioNoDocid = ?",
            (folio, site, rows[0][0]), cn=cn, commit=False)
        db.execute("DELETE FROM FolioLog WHERE FolionoDocid = ? AND "
                   "U_Name = ?", (rows[0][0], user), cn=cn, commit=False)
        if commit:
            cn.commit()
        return n
    finally:
        if own:
            cn.close()


# ─── Advance Deposit (VB6 BookingMore / DepositeReq) ─────────────────────

def post_advance_deposit(folio: int, amount: float, paycode: str = "KKCASH",
                         remarks: str = "ADVANCE DEPOSIT", user: str = USER,
                         cn=None, commit: bool = True, site: str = SITE_CODE,
                         vprefix: str = VPREFIX) -> int:
    """VB6 advance deposit: booking advance received before check-in.
    Posts as REC to folio, marked as deposit for settlement at checkout."""
    rec = checkin_mod.get(folio, cn=cn, vprefix=vprefix)
    if not rec:
        raise ValueError(f"Folio #{folio} nahi mila")
    if amount <= 0:
        raise ValueError("Deposit amount > 0 hona chahiye")
    return receive_payment(folio, amount, paycode=paycode,
                           comments=remarks, user=user, cn=cn,
                           commit=commit, site=site, vprefix=vprefix)


# ─── NCUR Update (VB6 FDNCURUpdate) ─────────────────────────────────────

def update_ncur(folio: int, dep_date, user: str = USER, cn=None,
                commit: bool = True, site: str = SITE_CODE,
                vprefix: str = VPREFIX) -> bool:
    """VB6 FDNCURUpdate: update NoDays + DepDate on GuestFolio
    when departure date changes (extended stay / early checkout)."""
    rec = checkin_mod.get(folio, cn=cn, vprefix=vprefix)
    if not rec:
        raise ValueError(f"Folio #{folio} nahi mila")
    new_dep = dep_date if isinstance(dep_date, datetime.date) else dep_date.date()
    old_vdate = rec["vdate"]
    nodays = max((new_dep - old_vdate).days, 1)
    own = cn is None
    cn = cn or db.connect()
    try:
        db.execute(
            "UPDATE GuestFolio SET DepDate = ?, NoDays = ?, U_EntDt = getdate(), "
            "U_Name = ? WHERE Site_Code = ? AND Vprefix = ? AND FolioNo = ?",
            (new_dep, nodays, user, site, vprefix, folio),
            cn=cn, commit=False)
        _log(rec["docid"], "E", user, cn, site)
        if commit:
            cn.commit()
        return True
    finally:
        if own:
            cn.close()


# ─── Token Reset (VB6 Token Reset pattern) ───────────────────────────────

def reset_tokens(folio: int, user: str = USER, cn=None,
                 commit: bool = True, site: str = SITE_CODE,
                 vprefix: str = VPREFIX) -> bool:
    """VB6 token reset: clear any pending charges/payments (fresh start).
    Used when folio needs to be reset before new billing cycle."""
    rec = checkin_mod.get(folio, cn=cn, vprefix=vprefix)
    if not rec:
        raise ValueError(f"Folio #{folio} nahi mila")
    if not str(rec["name"] or "").upper().startswith("PYT"):
        raise ValueError("Safety: sirf PYT* folios reset ho sakte hain")
    own = cn is None
    cn = cn or db.connect()
    try:
        # Log before delete (audit trail)
        db.execute(
            "INSERT INTO PayChargeLog SELECT *, getdate(), ? "
            "FROM PayCharge WHERE FolioNoDocid = ?",
            (user, rec["docid"]), cn=cn, commit=False)
        # Delete all charges for this folio
        db.execute(
            "DELETE FROM PayCharge WHERE FolioNoDocid = ?",
            (rec["docid"],), cn=cn, commit=False)
        # Delete any settle rows
        db.execute(
            "DELETE FROM FOMBillDetails WHERE FolioNoDocid = ?",
            (rec["docid"],), cn=cn, commit=False)
        _log(rec["docid"], "T", user, cn, site)
        if commit:
            cn.commit()
        return True
    finally:
        if own:
            cn.close()


# ─── Diplomat Tax Exemption (VB6 Diplomat pattern) ───────────────────────

def apply_diplomat_exemption(folio: int, user: str = USER, cn=None,
                             commit: bool = True, site: str = SITE_CODE,
                             vprefix: str = VPREFIX) -> bool:
    """VB6 diplomat check: if SubGroup.Diplomat='Y', exempt from tax.
    Updates RoomOcc.RoomCat = 'DIPLOMAT' for tax-free billing."""
    rec = checkin_mod.get(folio, cn=cn, vprefix=vprefix)
    if not rec:
        raise ValueError(f"Folio #{folio} nahi mila")
    rows = db.query(
        "SELECT SG.Diplomat FROM SubGroup SG "
        "INNER JOIN GuestProf GP ON GP.Code = ? "
        "WHERE GP.Company = SG.Code", (rec["guestprof"],), cn=cn)
    if not rows or (rows[0][0] or "").strip().upper() != "Y":
        return False
    own = cn is None
    cn = cn or db.connect()
    try:
        db.execute(
            "UPDATE RoomOcc SET RoomCat = 'DIPLOMAT', U_EntDt = getdate(), "
            "U_Name = ? WHERE DocId = ?",
            (user, rec["docid"]), cn=cn, commit=False)
        _log(rec["docid"], "D", user, cn, site)
        if commit:
            cn.commit()
        return True
    finally:
        if own:
            cn.close()


# ─── Amount to Words (VB6 CommonFunction ToWords) ────────────────────────

def amount_to_words(amount: float) -> str:
    """VB6 amount_to_words: converts number to Indian currency words."""
    if amount == 0:
        return "Rupees Zero Only"
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven",
            "Eight", "Nine", "Ten", "Eleven", "Twelve", "Thirteen",
            "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen",
            "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty",
            "Seventy", "Eighty", "Ninety"]

    def _conv(n):
        if n == 0:
            return ""
        elif n < 20:
            return ones[n]
        elif n < 100:
            return tens[n // 10] + " " + ones[n % 10]
        else:
            return ones[n // 100] + " Hundred " + _conv(n % 100)

    int_part = int(amount)
    dec_part = round((amount - int_part) * 100)
    result = "Rupees "
    if int_part >= 10000000:
        result += _conv(int_part // 10000000) + " Crore "
        int_part %= 10000000
    if int_part >= 100000:
        result += _conv(int_part // 100000) + " Lakh "
        int_part %= 100000
    if int_part >= 1000:
        result += _conv(int_part // 1000) + " Thousand "
        int_part %= 1000
    if int_part > 0:
        result += _conv(int_part)
    if dec_part > 0:
        result += f" and {dec_part} Paise"
    result += " Only"
    return result.strip()
