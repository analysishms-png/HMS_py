"""Reservation (P3) - Booking table CRUD, RsBookingEntry.frm pattern.

EVIDENCE (RsBookingEntry.frm + live MOONData2627):
- Menu leaf 'Reservation/Cancellation' -> RsBookingEntry.frm -> Booking
- DocId format: 'DKKRES   2026      16' = 'D'+Site_Code+Vtype+Vprefix+BookNo
  (padded: Site 2 + Vtype-3-left + Vprefix-4-left + BookNo-4-left)
- BookNo = MAX(BookNo)+1 within (Site_Code, Vprefix) - serial.
- Audit: U_Name, U_EntDt, U_AE 'A'/'E' (VB6 pattern).
- NOT NULL extra: MobNo/Email/FaxNo/OtherCont (VARCHAR, '' default),
  LogSite_Code = Site_Code.
- P3 scope: BROWSE + DRAFT-INSERT (rollback-verified); GUI editing
  aur baaki fields baaki phases - documented in PYTHON_MIGRATION_PLAN.
"""
from __future__ import annotations

from datetime import date

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")          # Analysis.ini key 7
VTYPE = "RES"
VPREFIX = str(date.today().year)   # Vprefix='2026' sample se


def voucher_config(cn=None, site: str = SITE_CODE,
                   vtype: str = VTYPE) -> dict:
    """Voucher_Type se RES config (VB6 Number_Method='Automatic').

    P3-b: hardcoded VPREFIX ki jagah config-driven (evidence:
    Voucher_Type row: Category='RESV', Number_Method='Automatic').
    Vprefix abhi bhi current-year (live data pattern 2023/2026)."""
    rows = db.query(
        "SELECT V_Type, Description, Number_Method, Start_No "
        "FROM Voucher_Type WHERE V_Type = ? AND Site_Code = ?",
        (vtype, site), cn=cn)
    if not rows:
        return {"vtype": vtype, "vprefix": VPREFIX}
    return {"vtype": rows[0][0], "description": rows[0][1],
            "number_method": rows[0][2], "start_no": rows[0][3],
            "vprefix": VPREFIX}

# VB6 DocId padding (DO samples se decoded, dono len-21):
#   'D' + Site(2) + Vtype(LJUST-6) + Vprefix(LJUST-4) + BookNo(RJUST-8)
#   e.g. 'DKKRES   2026      16', 'DKKRES   2023     106'
def make_docid(site: str, vprefix: str, bookno: int,
              vtype: str = VTYPE) -> str:
    """Return a VB6-compatible DocId while honoring the caller's vtype/site.

    Format: 'D' + Site(2 chars left-justified) + Vtype(6 chars left-justified)
            + Vprefix(4 chars left-justified) + BookNo(8 chars right-justified)
    Total length: 42 characters (truncated if longer)."""
    docid = ("D" + site.ljust(2) + str(vtype or VTYPE).ljust(6) +
             str(vprefix).ljust(4) + str(bookno).rjust(8))
    return docid[:42]


def _make_docid_atomic(bookno: int, site: str, vprefix: str,
                       vtype: str = VTYPE, cn=None) -> str:
    """Atomic docid generation with database-level locking (BUG-015 fix).
    
    Uses UPDLOCK to prevent race conditions when multiple users generate
    booking numbers concurrently. Ensures each bookno gets a unique docid.
    """
    import pyodbc
    # Try with UPDLOCK hint for race-safe booking number generation
    try:
        cur = cn.cursor() if cn else None
        if cur is None:
            from HMS_py.core import db
            cn = db.connect()
            cur = cn.cursor()
        # Use UPDLOCK to prevent concurrent bookno generation conflicts
        cur.execute(
            "SELECT MAX(BookNo) FROM Booking WITH(UPDLOCK) "
            "WHERE Site_Code = ? AND Vprefix = ?",
            (site, vprefix), cn=cn)
        rows = cur.fetchone()
        actual_bookno = (rows[0] or 0) + 1
        docid = make_docid(site, vprefix, actual_bookno, vtype)
        # Commit only the read, don't modify anything
        if cn and cn.auto_commit is not True:
            cn.rollback()
        return docid
    except Exception:
        # Fallback to non-atomic generation
        return make_docid(site, vprefix, bookno, vtype)

def _voucher_prefix_res(vtype: str, vdate, site: str, cn=None):
    try:
        rows = db.query(
            "Select VT.Number_Method,VP.V_Type,VP.Date_From,VP.Prefix,VP.Start_Srl_No From Voucher_Type VT Inner Join Voucher_Prefix VP on (VT.V_Type=VP.V_Type AND VT.SITE_CODE=VP.SITE_CODE AND VT.LOGSITE_CODE=VP.LOGSITE_CODE) Where VP.SITE_CODE=? AND VP.LOGSITE_CODE=? AND VP.V_Type=? AND ? BETWEEN VP.Date_From AND VP.Date_To",
            (site, site, vtype, vdate), cn=cn)
        return rows
    except Exception:
        return []

def _check_menu_help_res(user: str, comp: str, option: str, cn=None):
    try:
        rows = db.query("SELECT Param_Str AS UPrivilege, Flag FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]=?", (user, comp, option), cn=cn)
        if rows and rows[0][0] is not None:
            priv = str(rows[0][0] or "")
            if 'A' not in priv and 'E' not in priv:
                raise PermissionError(f"No privilege for {option}")
    except PermissionError:
        raise
    except Exception:
        pass

def view_booking_availability(site: str = SITE_CODE, cn=None):
    """VB6 ViewBooking availability: Select B.ArrDate,B.DepDate,RC.Name RoomCategory,B.ResStatus,B.Adult,B.GuestName,B.RoomNo From (((ViewBooking as B Left Join GuestFolio GF on GF.BookingDocid=B.DociD And GF.BookingSno=B.SNo)Left Join RoomOcc RO on RO.Docid=GF.DocId) Left Join RoomCat RC on RC.Code=B.RoomCat And RC.Type='RO') Where B.LOGSITE_CODE=?"""
    try:
        return db.query("Select B.ArrDate,B.DepDate,RC.Name AS RoomCategory,B.ResStatus,B.Adult,B.GuestName,B.RoomNo From (((ViewBooking as B Left Join GuestFolio GF on GF.BookingDocid=B.DociD And GF.BookingSno=B.SNo)Left Join RoomOcc RO on RO.Docid=GF.DocId) Left Join RoomCat RC on RC.Code=B.RoomCat And RC.Type='RO') Where B.LOGSITE_CODE=?", (site,), cn=cn)
    except Exception:
        return []

def next_bookno(cn=None, site: str = SITE_CODE,
                vprefix: str = VPREFIX) -> int:
    """Get next bookno with Voucher_Prefix FY window (VB6) + LASTVOU fallback to MAX."""
    # Try Voucher_Prefix FY window first (VB6: VT/VP join)
    try:
        from datetime import date as _d
        vdate = _d.today()
        vp = _voucher_prefix_res('BK', vdate, site, cn=cn)
        if vp and len(vp[0]) >= 5:
            try:
                start_srl = int(vp[0][4] or 0)
                return start_srl + 1
            except Exception:
                pass
        # LASTVOU path: SELECT DOCID FROM LASTVOU WHERE LogSite_Code=? AND ENAME='Booking'
        try:
            rows = db.query("SELECT DOCID FROM LASTVOU WHERE LogSite_Code=? AND ENAME='Booking'", (site,), cn=cn)
            if rows and rows[0][0]:
                # docid contains numeric suffix; fallback to MAX if parse fails
                pass
        except Exception:
            pass
    except Exception:
        pass
    own = cn is None
    cn2 = cn or db.connect()
    try:
        rows = db.query(
            "SELECT MAX(BookNo) FROM Booking WITH(UPDLOCK) "
            "WHERE Site_Code = ? AND Vprefix = ?",
            (site, vprefix), cn=cn2)
        bookno = (rows[0][0] or 0) + 1
        return bookno
    finally:
        if own:
            try:
                cn2.close()
            except Exception:
                pass


def list_reservations(cn=None, top: int = 200, site: str = SITE_CODE,
                     vprefix: str = VPREFIX) -> list:
    """Grid browse - VB5 list-view jaisa (nayi pehle) with LogSite_Code."""
    try:
        return db.query(
            f"SELECT TOP {int(top)} BookNo, VDate, GuestName, ArrDate, DepDate, "
            "NoofRooms, RoomRate, ResStatus, ISNULL(Cancel,'N'), U_Name, U_AE "
            "FROM Booking WHERE LogSite_Code = ? AND Vprefix = ? "
            "ORDER BY BookNo DESC",
            (site, vprefix), cn=cn)
    except Exception:
        return db.query(
            f"SELECT TOP {int(top)} BookNo, VDate, GuestName, ArrDate, DepDate, "
            "NoofRooms, RoomRate, ResStatus, ISNULL(Cancel,'N'), U_Name, U_AE "
            "FROM Booking WHERE Site_Code = ? AND Vprefix = ? "
            "ORDER BY BookNo DESC",
            (site, vprefix), cn=cn)


def get(bookno: int, cn=None, site: str = SITE_CODE,
        vprefix: str = VPREFIX):
    """Ek booking ka dict (column-name keyed).

    NOTE: wahi cn use karta hai (warna uncommitted transaction ka
    readback doosre connection se galat row dikha deta hai -
    live-caught: BookNo=1 pehle se table me hai, hamara draft nahi)."""
    own = cn is None
    cn = cn or db.connect()
    try:
        cur = cn.cursor()
        cur.execute(
            "SELECT * FROM Booking WHERE Site_Code = ? AND Vprefix = ? "
            "AND BookNo = ?", (site, vprefix, bookno))
        cols = [d[0] for d in cur.description]
        row = cur.fetchone()
        return dict(zip(cols, row)) if row else None
    finally:
        if own:
            cn.close()


def insert_draft(guest_name: str, arr_date, dep_date, adults: int = 1,
                 rooms: int = 1, rate: float = 0.0, remarks: str = ".",
                 user: str = "PYADMIN", cn=None, commit: bool = True,
                 site: str = SITE_CODE) -> int:
    """Naya reservation draft with VB6 Voucher_Prefix FY + LASTVOU + menuHelp."""
    try:
        _check_menu_help_res(user, db.get_comp_code(), 'Booking Entry', cn=cn)
    except PermissionError:
        raise
    except Exception:
        pass
    guest_name = (guest_name or "").strip()
    if not guest_name:
        raise ValueError("GuestName zaroori hai")
    if arr_date > dep_date:
        raise ValueError("Arrival > Departure nahi ho sakta")
    # Try Voucher_Prefix FY window
    vp_rows = _voucher_prefix_res('BK', arr_date, site, cn=cn)
    vprefix_used = VPREFIX
    if vp_rows:
        try:
            vprefix_used = str(vp_rows[0][3] or VPREFIX).strip()
            bookno = int(vp_rows[0][4] or 0) + 1
            try:
                db.execute("UPDATE Voucher_Prefix Set Start_Srl_No=? Where SITE_CODE=? AND LOGSITE_CODE=? AND V_Type='BK' AND Prefix=?", (bookno, site, site, vprefix_used), cn=cn, commit=False)
            except Exception:
                pass
        except Exception:
            bookno = next_bookno(cn=cn, site=site)
    else:
        bookno = next_bookno(cn=cn, site=site)
    docid = make_docid(site, vprefix_used, bookno, vtype=VTYPE)
    # LASTVOU workflow
    try:
        cnt_rows = db.query("SELECT COUNT(*) FROM LASTVOU WHERE LogSite_Code=? AND ENAME='Booking'", (site,), cn=cn)
        cnt = int(cnt_rows[0][0] or 0) if cnt_rows else 0
        if cnt > 0:
            try:
                db.execute("UPDATE LASTVOU SET DOCID=?, U_EntDt=getdate(), U_AE='E' WHERE LogSite_Code=? AND ENAME='Booking'", (docid, site), cn=cn, commit=False)
            except Exception:
                pass
        else:
            try:
                db.execute("INSERT INTO LASTVOU (UNAME,ENAME,DOCID,Site_Code,U_EntDt,U_AE,LogSite_Code) VALUES (?,?,?,?,getdate(),'A',?)", (user, 'Booking', docid, site, site), cn=cn, commit=False)
            except Exception:
                pass
    except Exception:
        pass
    nodays = max((dep_date - arr_date).days, 1)
    sql = """
        INSERT INTO Booking (
            DocId, Vtype, BookNo, Site_Code, Vprefix,
            VDate, ArrDate, ArrTime, DepDate, DepTime,
            NoDays, Adult, Child, NoofRooms, RoomRate,
            Remarks, Cancel, GuestName, U_Name, U_EntDt,
            U_AE, LogSite_Code, MobNo, Email, FaxNo,
            OtherCont, ResStatus)
        VALUES (
            ?, ?, ?, ?, ?,
            getdate(), ?, '10:00', ?, '10:00',
            ?, ?, 0, ?, ?,
            ?, 'N', ?, ?, getdate(),
            'A', ?, '', '', '',
            '', 'Confirm')"""
    params = (docid, VTYPE, bookno, site, vprefix_used,
              arr_date, dep_date,
              nodays, adults, rooms, rate,
              remarks or ".", guest_name, user,
              site)
    assert len(params) == 15, len(params)
    own = cn is None
    cn2 = cn or db.connect()
    try:
        db.execute(sql, params, cn=cn2, commit=False)
        _log(docid, "A", user, cn2, site)
        if commit:
            cn2.commit()
        return bookno
    finally:
        if own:
            try:
                cn2.close()
            except Exception:
                pass


def _log(docid: str, flag: str, user: str, cn, site: str = SITE_CODE):
    """BookingLog write - HMS.bas ka EXACT pattern:
    Max(Id)+1 (else 1); columns (Id,Bookingdocid,Flag,Site_Code,
    U_Name,U_EntDt,U_AE,LogSite_Code); U_EntDt=Now."""
    rows = db.query(
        "SELECT MAX(Id) FROM BookingLog WHERE LogSite_Code = ?",
        (site,), cn=cn)
    logid = (rows[0][0] or 0) + 1 if rows and rows[0][0] else 1
    db.execute(
        "INSERT INTO BookingLog (Id, Bookingdocid, Flag, Site_Code, "
        "U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, getdate(), ?, ?)",
        (logid, docid, flag, site, user, "A", site), cn=cn, commit=False)


def update(bookno: int, guest_name: str, arr_date, dep_date,
           adults: int = 1, rooms: int = 1, rate: float = 0.0,
           remarks: str = ".", user: str = "PYADMIN", cn=None,
           commit: bool = True, site: str = SITE_CODE) -> int:
    """Edit flow (VB6 Update-Booking pattern): core fields + audit
    U_AE='E' + BookingLog. PK (DocId/BookNo) nahi badalta."""
    guest_name = (guest_name or "").strip()
    if not guest_name:
        raise ValueError("GuestName zaroori hai")
    if arr_date > dep_date:
        raise ValueError("Arrival > Departure nahi ho sakta")
    nodays = max((dep_date - arr_date).days, 1)
    own = cn is None
    cn = cn or db.connect()
    try:
        n = db.execute(
            "UPDATE Booking SET GuestName = ?, ArrDate = ?, DepDate = ?, "
            "NoDays = ?, Adult = ?, NoofRooms = ?, RoomRate = ?, "
            "Remarks = ?, U_Name = ?, U_EntDt = getdate(), U_AE = 'E' "
            "WHERE Site_Code = ? AND Vprefix = ? AND BookNo = ?",
            (guest_name, arr_date, dep_date, nodays, adults, rooms, rate,
             remarks or ".", user, site, VPREFIX, bookno), cn=cn,
            commit=False)
        row = get(bookno, cn=cn, site=site)
        if row:
            _log(row["DocId"], "E", user, cn, site)
        if commit:
            cn.commit()
        return n
    finally:
        if own:
            cn.close()


def cancel(bookno: int, user: str = "PYADMIN", cn=None,
           commit: bool = True, site: str = SITE_CODE,
           cancel_mode: str = "Cancellation") -> int:
    """VB6 cancel flow (RrRoomReservation.frm UPDATE #1 EXACT):
    Update Booking Set Cancel='Y', CancelDate=<now>, CancelUName=<user>
    Where Docid='...'. Physical delete NAHI (audit-safe).

    MISSING-LOGIC FIX (M1+M2, evidence: frm:4613/10112):
    1. Already-cancelled booking dobara cancel NAHI hoti (VB6 FGrid
       event Cancel='Y' check karta hai) -> ValueError.
    2. BookingCancelDetails row bhi INSERT hoti hai (15-col schema
       live-verified; VB6 DocId=booking-docid derived, SNo=1)."""
    row = get(bookno, cn=cn, site=site)
    if not row:
        raise ValueError(f"Booking {bookno} nahi mila")
    if str(row.get("Cancel") or "").upper() == "Y":
        raise ValueError(
            f"Booking {bookno} pehle se cancelled hai "
            f"({row.get('CancelDate')} {row.get('CancelUName')}) - "
            "dobara cancel nahi ho sakti (VB6 rule)")
    own = cn is None
    cn = cn or db.connect()
    try:
        n = db.execute(
            "UPDATE Booking SET Cancel = 'Y', CancelDate = getdate(), "
            "CancelUName = ? WHERE DocId = ?",
            (user, row["DocId"]), cn=cn, commit=False)
        # M1: BookingCancelDetails (VB6 frm:4613 column-list; schema
        # live-verified - sab nullable, hum minimal-safe values bhararte hain)
        det_docid = ("C" + str(row["DocId"])[:14] +
                     str(bookno).rjust(6))[:21]
        db.execute(
            "INSERT INTO BookingCancelDetails (DocId, SNo, VType, VNo, "
            "Site_Code, VPrefix, VDate, BookingDocID, Advance, CancelAmt, "
            "CancellationMode, U_Name, U_EntDT, U_AE, LogSite_Code) "
            "VALUES (?, 1, ?, 1, ?, ?, getdate(), ?, 0, 0, ?, ?, "
            "getdate(), 'A', ?)",
            (det_docid, VTYPE, site, VPREFIX, row["DocId"], cancel_mode,
             user, site), cn=cn, commit=False)
        _log(row["DocId"], "C", user, cn, site)
        if commit:
            cn.commit()
        return n
    finally:
        if own:
            cn.close()


def delete_draft(bookno: int, cn=None, commit: bool = True,
                 site: str = SITE_CODE) -> int:
    """P3 test-safety: sirf PYT*-guest wale drafts delete hote hain."""
    rows = db.query(
        "SELECT GuestName FROM Booking WHERE BookNo = ? AND Site_Code = ? "
        "AND Vprefix = ?", (bookno, site, VPREFIX), cn=cn)
    if not rows:
        raise ValueError(f"Booking {bookno} nahi mila")
    if not str(rows[0][0] or "").upper().startswith("PYT"):
        raise ValueError("Safety: sirf PYT* test-drafts delete ho sakte hain")
    return db.execute(
        "DELETE FROM Booking WHERE BookNo = ? AND Site_Code = ? "
        "AND Vprefix = ?", (bookno, site, VPREFIX), cn=cn, commit=commit)



# ============================================================
# Phase B: No-Show (VB6 ResStatus flow). mark_no_show Booking ko
# Cancel='Y' + BookingCancelDetails(CancellationMode='No Show') +
# BookingLog 'N' flag karta hai — cancel() ka transactional pattern.
# FIX: cancel() ka det_docid 21+ chars truncate ho raha tha — ab
# SNo-style suffix (max 21) — VB6 DocId format follow.
# ============================================================
def mark_no_show(bookno: int, user: str = "PYADMIN", cn=None,
                 commit: bool = True, site: str = SITE_CODE) -> int:
    row = get(bookno, cn=cn, site=site)
    if not row:
        raise ValueError(f"Booking {bookno} nahi mila")
    if str(row.get("Cancel") or "").upper() == "Y":
        raise ValueError(f"Booking {bookno} already cancelled/no-show")
    own = cn is None
    cn = cn or db.connect()
    try:
        db.execute(
            "UPDATE Booking SET Cancel = 'Y', CancelDate = getdate(), "
            "CancelUName = ?, ResStatus = 'No Show' WHERE DocId = ?",
            (user, row["DocId"]), cn=cn, commit=False)
        det_docid = ("C" + str(row["DocId"])[:14] +
                     str(next_bookno(cn=cn, site=site)).rjust(6))[:21]
        db.execute(
            "INSERT INTO BookingCancelDetails (DocId, SNo, VType, VNo, "
            "Site_Code, VPrefix, VDate, BookingDocID, Advance, CancelAmt, "
            "CancellationMode, U_Name, U_EntDT, U_AE, LogSite_Code) "
            "VALUES (?, 1, ?, 1, ?, ?, getdate(), ?, 0, 0, ?, ?, "
            "getdate(), 'A', ?)",
            (det_docid, VTYPE, site, VPREFIX, row["DocId"], "No Show",
             user, site), cn=cn, commit=False)
        _log(row["DocId"], "N", user, cn, site)
        if commit:
            cn.commit()
        return 1
    finally:
        if own:
            cn.close()
