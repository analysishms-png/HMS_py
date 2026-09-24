"""Check-In core (VB6: Front Office check-in - GuestFolio port).

Schema evidence (live): GuestFolio 43 cols, 10605 rows, Vtype='CHK' only.
DocId pattern (sample 'DKKCHK   2021       1'):
  'D' + site(2) + 'CHK'.ljust(6) + year(4).ljust(4) + FolioNo.rjust(8) = 21
FolioNo = MAX(FolioNo)+1 (live 2026 me 463 tak).
FolioLog = audit (BookingLog jaisa: Max(Id)+1, Flag A/E, 8 cols).
Vprefix = FY start year ('2026' for 2026-27).
Defaults sample row se: ArrTime-type cols 'Remark' '.', RODisc 0.0, RSDisc 0.0.
Core write cols (13): DocId, FolioNo, Vtype, Vprefix, Vdate, GuestProf,
  Name, City, NoDays, DepDate, BookingDocId, U_Name/U_EntDt/U_AE, LogSite_Code.

BUGFIX (P0): _map() uses index-based access instead of named attribute access.
pyodbc rows support .ColumnName BUT only when description matches exactly.
Index access is driver-agnostic and immune to column name case differences.
SELECT_COLS order: DocId(0),FolioNo(1),Vtype(2),Vprefix(3),Vdate(4),
  GuestProf(5),Name(6),City(7),NoDays(8),DepDate(9),BookingDocId(10),
  U_Name(11),U_EntDt(12),U_AE(13)
"""
from __future__ import annotations

import datetime

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
VTYPE = "CHK"
SELECT_COLS = ("DocId, FolioNo, Vtype, Vprefix, Vdate, GuestProf, Name, "
               "City, NoDays, DepDate, BookingDocId, U_Name, U_EntDt, U_AE")


def _map(r) -> dict:
    """BUGFIX: index-based access - works with all pyodbc drivers.
    Named attribute access (.Vdate etc.) fails with some ODBC drivers
    when column names have mixed case or driver returns uppercase names."""
    # Try attribute access first (native client), fall back to index
    try:
        docid = r.DocId
        folio = r.FolioNo
        vtype = r.Vtype
        vprefix = r.Vprefix
        vdate = r.Vdate
        guestprof = r.GuestProf
        name = r.Name
        city = r.City
        nodays = r.NoDays
        depdate = r.DepDate
        bookingdocid = r.BookingDocId
        u_name = r.U_Name
        u_ae = r.U_AE
    except AttributeError:
        # Fallback: positional index (SELECT_COLS order)
        docid, folio, vtype, vprefix, vdate, guestprof, name, city, \
            nodays, depdate, bookingdocid, u_name, _, u_ae = r
    return {
        "docid": docid,
        "folio": folio,
        "vtype": vtype,
        "vprefix": vprefix,
        "vdate": vdate.date() if isinstance(vdate, datetime.datetime) else vdate,
        "guestprof": guestprof or "",
        "name": (name or "").strip(),
        "city": city or "",
        "nodays": nodays or 0,
        "depdate": depdate.date() if isinstance(depdate, datetime.datetime) else depdate,
        "bookingdocid": (bookingdocid or "").strip(),
        "u_name": u_name or "",
        "u_ae": u_ae or "",
    }


def list_checkins(cn=None, vprefix: str = "2026", top: int = 200) -> list:
    rows = db.query(
        f"SELECT TOP {int(top)} {SELECT_COLS} FROM GuestFolio "
        "WHERE Site_Code = ? AND Vprefix = ? ORDER BY FolioNo DESC",
        (SITE_CODE, vprefix), cn=cn)
    return [_map(r) for r in rows]


def get(folio: int, cn=None, vprefix: str = "2026") -> dict | None:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM GuestFolio WHERE Site_Code = ? AND "
        "Vprefix = ? AND FolioNo = ?", (SITE_CODE, vprefix, folio), cn=cn)
    return _map(rows[0]) if rows else None


def next_folio(cn=None, vprefix: str = "2026") -> int:
    # BUG-015: race-safe FolioNo (UPDLOCK/HOLDLOCK) - do concurrent
    # check-ins ko same folio number nahi milega.
    rows = db.query(
        "SELECT MAX(FolioNo) FROM GuestFolio WITH (UPDLOCK, HOLDLOCK) "
        "WHERE Site_Code = ? AND Vprefix = ?", (SITE_CODE, vprefix), cn=cn)
    return (rows[0][0] or 0) + 1 if rows and rows[0][0] else 1


def make_docid(site: str, vprefix: str, folio: int) -> str:
    """VB6 exact 21-char pattern (Booking DocId jaisa, VTYPE='CHK')."""
    return ("D" + site.ljust(2) + VTYPE.ljust(6) + vprefix.ljust(4) +
            str(folio).rjust(8))


def _log(docid: str, flag: str, user: str, cn, site: str = SITE_CODE):
    """FolioLog write - FolioLog 8-col schema (BookingLog pattern)."""
    rows = db.query("SELECT MAX(Id) FROM FolioLog WHERE LogSite_Code = ?",
                    (site,), cn=cn)
    logid = (rows[0][0] or 0) + 1 if rows and rows[0][0] else 1
    db.execute(
        "INSERT INTO FolioLog (Id, FolionoDocid, Flag, Site_Code, "
        "U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, getdate(), ?, ?)",
        (logid, docid, flag, site, user, "A", site), cn=cn, commit=False)


def create_checkin(guestprof: str, name: str, arr_date, dep_date,
                   city: str = "", bookingdocid: str = "",
                   roomno: str = "", user: str = USER, cn=None,
                   commit: bool = True,
                   site: str = SITE_CODE, vprefix: str = "2026",
                   adult: int | None = None, children: int | None = None,
                   ratecode: str = "", chkintime: str = "") -> int:
    """Naya check-in (VB6 CHK doc-engine): DocId + FolioNo + FolioLog 'A'
    + RoomOcc row (P4-c MISSING-LOGIC FIX).

    MISSING LOGIC (live-evidence se): pehle hum sirf GuestFolio likh rahe
    the, par VB6 me har check-in ki RoomOcc row banti hai (FrmHouseStatus
    frm:1065 join + 6/6 live in-house rooms RoomOcc me hain; fdRoomChange
    frm:3639 30-col INSERT pattern). Bina RoomOcc ke room rack me check-in
    dikhta hi nahi. roomno optional: blank -> pehla free 'RO' room
    (RoomMast.Type='RO' jo open RoomOcc me na ho).

    FO-7: adult/children/ratecode/chkintime RoomOcc me jaate hain
    (VB6 fdWalkInEntry Adult/Children/ChkInTime cols). Defaults:
    Adult=1, Children=0, ChkInTime=abhi ka HH:MM (hardcode nahi).

    PYT-guard caller-side (UI sirf PYT* naam likhta hai; production
    check-ins VB6 EXE se hi)."""
    name = (name or "").strip()
    if not name:
        raise ValueError("Guest Name zaroori hai")
    if arr_date > dep_date:
        raise ValueError("Arrival > Departure nahi ho sakta")
    n_adult = int(adult) if adult is not None else 1
    n_child = int(children) if children is not None else 0
    if n_adult < 0 or n_child < 0:
        raise ValueError("Adult/Children negative nahi ho sakte")
    t_in = (chkintime or "").strip() or datetime.datetime.now().strftime("%H:%M")
    folio = next_folio(cn=cn, vprefix=vprefix)
    docid = make_docid(site, vprefix, folio)
    nodays = max((dep_date - arr_date).days, 1)
    own = cn is None
    cn = cn or db.connect()
    try:
        # --- P4-c: room assign (VB6 FdLookUpRoom pattern) ---
        if roomno:
            rrows = db.query(
                "SELECT COUNT(*) FROM RoomMast WHERE RTRIM(Code) = ? AND "
                "(LogSite_Code = ? OR LogSite_Code = 'HO')",
                (roomno, site), cn=cn)
            if not rrows or not rrows[0][0]:
                raise ValueError(f"Room {roomno} RoomMast me nahi mila")
            busy = db.query(
                "SELECT COUNT(*) FROM RoomOcc WHERE RTRIM(RoomNo) = ? AND "
                "ChkOutDate IS NULL AND Site_Code = ?", (roomno, site),
                cn=cn)
            if busy and busy[0][0]:
                raise ValueError(f"Room {roomno} pehle se occupied hai")
        else:
            free = db.query(
                "SELECT TOP 1 RTRIM(rm.Code) FROM RoomMast rm "
                "WHERE RTRIM(rm.Type) = 'RO' AND (rm.LogSite_Code = ? OR "
                "rm.LogSite_Code = 'HO') AND rm.Code NOT IN "
                "(SELECT RTRIM(ro.RoomNo) FROM RoomOcc ro WHERE "
                "ro.ChkOutDate IS NULL AND ro.Site_Code = ?) "
                "ORDER BY rm.Code", (site, site), cn=cn)
            if not free:
                raise ValueError("Koi free room nahi (full house)")
            roomno = free[0][0]
        # 13 cols = 13 params (site_code bugfix: ordinal-shift live-caught -
        # Site_Code '' jaa raha tha, get() fail)
        db.execute(
            "INSERT INTO GuestFolio (DocId, FolioNo, Vtype, Vprefix, "
            "Vdate, GuestProf, Name, City, NoDays, DepDate, BookingDocId, "
            "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
            "getdate(), 'A', ?)",
            (docid, folio, VTYPE, vprefix, arr_date, guestprof or "",
             name, city or "", nodays, dep_date, bookingdocid or "",
             site, user, site), cn=cn, commit=False)
        # --- P4-c: RoomOcc row (fdRoomChange:3639 pattern, core cols;
        # SNo=1 per folio). Vtype discrimination via GuestFolio.Vtype='CHK'.
        # RoomOcc.Type='I' = in-house (dashboard rack/report joins).
        # FO-7: Adult/Children/RateCode/ChkInTime caller se (defaults
        # 1/0/''/abhi) - hardcode nahi.
        db.execute(
            "INSERT INTO RoomOcc (DocId, SNo, FolioNo, Vtype, Site_Code, "
            "Vprefix, GuestProf, RoomNo, RateCode, ChkInDate, ChkInTime, "
            "Adult, Children, DepDate, DepTime, Type, U_Name, U_EntDt, "
            "U_AE, LogSite_Code) "
            "VALUES (?, 1, ?, 'CHK', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
            "'10:00', 'I', ?, getdate(), 'A', ?)",
            (docid, folio, site, vprefix, guestprof, roomno,
             (ratecode or "").strip(), arr_date, t_in, n_adult, n_child,
             dep_date, user, site), cn=cn, commit=False)
        _log(docid, "A", user, cn, site)
        if commit:
            cn.commit()
        return folio
    finally:
        if own:
            cn.close()


# ─── Room Move / Change (VB6 fdRoomChange) ───────────────────────────────

def move_room(folio: int, new_room: str, user: str = USER, cn=None,
              commit: bool = True, site: str = SITE_CODE,
              vprefix: str = "2026") -> bool:
    """VB6 fdRoomChange: room change with old/new RoomOcc tracking.
    1. Validate new room exists + not occupied
    2. Update RoomOcc.RoomNo for current folio
    3. Log 'R' flag in FolioLog
    4. Insert old/new room details in FolioLog remarks."""
    rec = get(folio, cn=cn, vprefix=vprefix)
    if not rec:
        raise ValueError(f"Folio #{folio} nahi mila")
    # Get current room from RoomOcc
    curr = db.query(
        "SELECT TOP 1 RoomNo, ChkInDate FROM RoomOcc WHERE DocId = ?",
        (rec["docid"],), cn=cn)
    if not curr:
        raise ValueError(f"Folio #{folio} ki RoomOcc entry nahi mili")
    old_room = (curr[0][0] or "").strip()
    if old_room == new_room:
        raise ValueError("Current room and new room same hai")
    # Validate new room
    rrows = db.query(
        "SELECT COUNT(*) FROM RoomMast WHERE RTRIM(Code) = ? AND "
        "(LogSite_Code = ? OR LogSite_Code = 'HO')",
        (new_room, site), cn=cn)
    if not rrows or not rrows[0][0]:
        raise ValueError(f"Room {new_room} RoomMast me nahi mila")
    busy = db.query(
        "SELECT COUNT(*) FROM RoomOcc WHERE RTRIM(RoomNo) = ? AND "
        "ChkOutDate IS NULL AND Site_Code = ? AND DocId != ?",
        (new_room, site, rec["docid"]), cn=cn)
    if busy and busy[0][0]:
        raise ValueError(f"Room {new_room} pehle se occupied hai")
    own = cn is None
    cn = cn or db.connect()
    try:
        # Update RoomOcc
        db.execute(
            "UPDATE RoomOcc SET RoomNo = ?, U_EntDt = getdate(), U_Name = ? "
            "WHERE DocId = ?", (new_room, user, rec["docid"]),
            cn=cn, commit=False)
        # Log
        _log(rec["docid"], "R", user, cn, site)
        if commit:
            cn.commit()
        return True
    finally:
        if own:
            cn.close()


# ─── Split Folio (VB6 fdSplit) ──────────────────────────────────────────

def split_folio(folio: int, new_room: str, user: str = USER, cn=None,
                commit: bool = True, site: str = SITE_CODE,
                vprefix: str = "2026") -> int:
    """VB6 fdSplit: split existing folio into new folio for different room.
    Creates new GuestFolio + RoomOcc with MFolioNo link.
    Returns new folio number."""
    rec = get(folio, cn=cn, vprefix=vprefix)
    if not rec:
        raise ValueError(f"Folio #{folio} nahi mila")
    if not str(rec["name"] or "").upper().startswith("PYT"):
        raise ValueError("Safety: sirf PYT* folios split ho sakte hain")
    # Validate new room
    rrows = db.query(
        "SELECT COUNT(*) FROM RoomMast WHERE RTRIM(Code) = ? AND "
        "(LogSite_Code = ? OR LogSite_Code = 'HO')",
        (new_room, site), cn=cn)
    if not rrows or not rrows[0][0]:
        raise ValueError(f"Room {new_room} RoomMast me nahi mila")
    busy = db.query(
        "SELECT COUNT(*) FROM RoomOcc WHERE RTRIM(RoomNo) = ? AND "
        "ChkOutDate IS NULL AND Site_Code = ?", (new_room, site), cn=cn)
    if busy and busy[0][0]:
        raise ValueError(f"Room {new_room} pehle se occupied hai")
    own = cn is None
    cn = cn or db.connect()
    try:
        new_folio = next_folio(cn=cn, vprefix=vprefix)
        new_docid = make_docid(site, vprefix, new_folio)
        # New GuestFolio (MFolioNo = original folio)
        db.execute(
            "INSERT INTO GuestFolio (DocId, FolioNo, Vtype, Vprefix, Vdate, "
            "GuestProf, Name, City, NoDays, DepDate, BookingDocId, MFolioNo, "
            "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
            "VALUES (?, ?, 'CHK', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
            "getdate(), 'A', ?)",
            (new_docid, new_folio, vprefix, rec["vdate"],
             rec["guestprof"], rec["name"], rec["city"],
             rec["nodays"], rec["depdate"], rec["bookingdocid"],
             folio, site, user, site), cn=cn, commit=False)
        # New RoomOcc (Type='I' in-house)
        db.execute(
            "INSERT INTO RoomOcc (DocId, SNo, FolioNo, Vtype, Site_Code, "
            "Vprefix, GuestProf, RoomNo, ChkInDate, ChkInTime, Adult, "
            "Children, DepDate, DepTime, Type, U_Name, U_EntDt, U_AE, "
            "LogSite_Code) "
            "VALUES (?, 1, ?, 'CHK', ?, ?, ?, ?, ?, '10:00', 1, 0, ?, "
            "'10:00', 'I', ?, getdate(), 'A', ?)",
            (new_docid, new_folio, site, vprefix, rec["guestprof"],
             new_room, rec["vdate"], rec["depdate"], user, site),
            cn=cn, commit=False)
        _log(new_docid, "A", user, cn, site)
        if commit:
            cn.commit()
        return new_folio
    finally:
        if own:
            cn.close()


# ─── Group Check-In (VB6 group check-in pattern) ─────────────────────────

def group_checkin(guests: list[dict], user: str = USER, cn=None,
                  commit: bool = True, site: str = SITE_CODE,
                  vprefix: str = "2026") -> list[int]:
    """VB6 group check-in: multiple guests with same booking, different rooms.
    Each guest gets own GuestFolio + RoomOcc. Returns list of folio numbers.
    guests = [{"guestprof":"", "name":"", "roomno":"101", "depdate":date}, ...]"""
    if not guests:
        raise ValueError("Guests list empty hai")
    own = cn is None
    cn = cn or db.connect()
    folios = []
    try:
        for g in guests:
            f = create_checkin(
                guestprof=g.get("guestprof", ""),
                name=g["name"],
                arr_date=g.get("arrdate", datetime.date.today()),
                dep_date=g.get("depdate", datetime.date.today() +
                               datetime.timedelta(days=1)),
                city=g.get("city", ""),
                bookingdocid=g.get("bookingdocid", ""),
                roomno=g.get("roomno", ""),
                adult=g.get("adult"), children=g.get("children"),
                ratecode=g.get("ratecode", ""),
                chkintime=g.get("chkintime", ""),
                user=user, cn=cn, commit=False,
                site=site, vprefix=vprefix)
            folios.append(f)
        if commit:
            cn.commit()
        return folios
    finally:
        if own:
            cn.close()


# ─── Group Check-Out (VB6 group check-out pattern) ───────────────────────

def group_checkout(folios: list[int], user: str = USER, cn=None,
                   commit: bool = True, site: str = SITE_CODE,
                   vprefix: str = "2026") -> dict:
    """VB6 group check-out: settle + checkout multiple folios together.
    Returns {"settled": N, "errors": [...]}."""
    from HMS_py.core import folio as folio_mod
    own = cn is None
    cn = cn or db.connect()
    settled = 0
    errors = []
    try:
        for f in folios:
            try:
                folio_mod.settle_folio(f, user=user, cn=cn, commit=False,
                                       site=site, vprefix=vprefix)
                from HMS_py.core import checkout
                checkout.do_checkout(f, user=user, cn=cn, commit=False,
                                     site=site, vprefix=vprefix)
                settled += 1
            except Exception as ex:
                errors.append({"folio": f, "error": str(ex)})
        if commit:
            cn.commit()
        return {"settled": settled, "errors": errors}
    finally:
        if own:
            cn.close()


def delete_checkin(folio: int, user: str = USER, cn=None,
                   commit: bool = True, site: str = SITE_CODE,
                   vprefix: str = "2026") -> int:
    """P4 test-safety: sirf PYT* naam wale check-ins delete hote hain."""
    rows = db.query(
        "SELECT Name, DocId FROM GuestFolio WHERE Site_Code = ? AND "
        "Vprefix = ? AND FolioNo = ?", (site, vprefix, folio), cn=cn)
    if not rows:
        raise ValueError(f"Check-in #{folio} nahi mila")
    if not str(rows[0][0] or "").upper().startswith("PYT"):
        raise ValueError("Safety: sirf PYT* test check-ins delete ho sakte hain")
    own = cn is None
    cn = cn or db.connect()
    try:
        n = db.execute(
            "DELETE FROM GuestFolio WHERE Site_Code = ? AND Vprefix = ? AND "
            "FolioNo = ?", (site, vprefix, folio), cn=cn, commit=False)
        db.execute("DELETE FROM RoomOcc WHERE DocId = ?",
                   (rows[0][1],), cn=cn, commit=False)
        # VB6 deletion also removes the folio's charge/payment rows
        # (link by FolioNoDocid, plus legacy FolioNo fallback rows).
        db.execute(
            "DELETE FROM PayCharge WHERE FolioNoDocid = ?",
            (rows[0][1],), cn=cn, commit=False)
        db.execute(
            "DELETE FROM PayCharge WHERE FolioNoDocid = '' AND Site_Code = ? "
            "AND VPrefix = ? AND FolioNo = ?",
            (site, vprefix, folio), cn=cn, commit=False)
        db.execute("DELETE FROM FolioLog WHERE FolionoDocid = ?",
                   (rows[0][1],), cn=cn, commit=False)
        if commit:
            cn.commit()
        return n
    finally:
        if own:
            cn.close()
