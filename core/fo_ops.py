"""Front Office missing-logic ops — VB6 fdRoomChange / FrmMergeCharge /
FdReSetlement ka faithful port (core writers, schema ZERO change).

Port scope (EXTRAS.text P-code se transcribe kiya):
  room_change   -> fdRoomChange save transaction (RoomOcc new-row +
                   old-row checkout + GuestMessage + Booking.OccRoom +
                   RoomMast RoomStat='D' + PlanDetails + EPABX_IN audit).
  merge_charge  -> FrmMergeCharge/BtnroomMerge: source folio ke sabhi
                   PayCharge lines target folio pe re-home + GuestFolio
                   mFolioNo linkage.
  re_settlement -> FdReSetlement core: last REC settlement receipt reverse
                   (delete) + nayi receipt lines re-post, sum barabar
                   validate karke.

Saare SQL param-bound hain (kabhi string-concat nahi). Tables verified
against KailashData2526 schema via codebase SELECT_COLS / VB6 sources.
"""
from __future__ import annotations

import datetime

from HMS_py.core import db
from HMS_py.core.folio import PAY_TYPES as _PAY_TYPES
from HMS_py.core.room_occ import SELECT_COLS as _ROOM_OCC_COLS

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven
USER = db.get_user()


# ------------------------------------------------------------
# Folio / room lookup helpers
# ------------------------------------------------------------
def open_folio_by_room(room: str, site: str = SITE_CODE, cn=None):
    """Open GuestFolio jiski RoomOcc row room number se match karti hai
    (ChkOutDate NULL = in-house). Merge/Resettle/Change forms isi par
    resolve karti hain."""
    rows = db.query(
        "SELECT TOP 1 gf.DocId, gf.FolioNo, gf.GuestProf, gf.Name, "
        "gf.BookingDocId, gf.Vprefix, gf.Vdate "
        "FROM RoomOcc ro INNER JOIN GuestFolio gf ON gf.DocId = ro.DocId "
        "WHERE RTRIM(ro.RoomNo) = ? AND ro.ChkOutDate IS NULL "
        "AND ro.Site_Code = ? ORDER BY ro.ChkInDate DESC",
        (room, site), cn=cn)
    if not rows:
        return None
    r = rows[0]
    return {"docid": (r.DocId or "").strip(), "folio": int(r.FolioNo or 0),
            "guestprof": (r.GuestProf or "").strip(),
            "name": (r.Name or "").strip(),
            "bookingdocid": (r.BookingDocId or "").strip(),
            "vprefix": (r.Vprefix or "").strip(),
            "vdate": r.Vdate}


def open_folio_by_docid(docid: str, site: str = SITE_CODE, cn=None):
    rows = db.query(
        "SELECT FolioNo, GuestProf, Name, BookingDocId, Vprefix, Vdate "
        "FROM GuestFolio WHERE DocId = ?", (docid,), cn=cn)
    if not rows:
        return None
    r = rows[0]
    return {"docid": docid.strip(), "folio": int(r.FolioNo or 0),
            "guestprof": (r.GuestProf or "").strip(),
            "name": (r.Name or "").strip(),
            "bookingdocid": (r.BookingDocId or "").strip(),
            "vprefix": (r.Vprefix or "").strip(),
            "vdate": r.Vdate}


def free_rooms(site: str = SITE_CODE, cn=None) -> list[str]:
    """Saare free 'RO' rooms (kisi open RoomOcc me nahi). Room Change form
    ke 'New Room' combo ke liye."""
    rows = db.query(
        "SELECT RTRIM(Code) FROM RoomMast rm "
        "WHERE RTRIM(rm.Type) = 'RO' AND (rm.LogSite_Code = ? OR "
        "rm.LogSite_Code = 'HO') AND rm.Code NOT IN "
        "(SELECT RTRIM(ro.RoomNo) FROM RoomOcc ro WHERE ro.ChkOutDate IS "
        "NULL AND ro.Site_Code = ?) ORDER BY rm.Code", (site, site), cn=cn)
    return [r[0] for r in rows]


# ------------------------------------------------------------
# Room Change (VB6 fdRoomChange.frm save transaction)
# ------------------------------------------------------------
def room_change(docid: str, new_room: str, reason: str = "",
                change_date=None, change_time: str = "",
                user: str = USER, site: str = SITE_CODE, cn=None,
                commit: bool = True) -> dict:
    """In-house guest ko dusre room me shift karo.

    VB6 fdRoomChange save (EXTRAS.text loc_18AE13D.. loc_18AEBA5):
      1. New RoomOcc row INSERT (RoomNo=new, ChkInDate=ChngDate, SNo=max+1)
      2. Nayi row par PlanCode/PlanAmt/PlanDisc UPDATE (SNo=new)
      3. Old RoomOcc row checkout: CHKOUTDATE/TIME, Type='C', NewRoomNo,
         Reason, U_AE='E'
      4. GuestMessage RoomNo/RoomCat update (FolioNo match)
      5. Booking.OccRoom = new (BookingDocId link)
      6. RoomMast RoomStat='D' (old room ko dirty mark)
      7. PlanDetails delete + nayi RoomNo ke saath re-insert
      8. EPABX_IN audit inserts ('CHKOT'/'CHKIN')

    Returns dict(affected, new_sno, new_room, old_room, folio)."""
    docid = (docid or "").strip()
    new_room = (new_room or "").strip()
    if not docid:
        raise ValueError("Check-in DocId zaroori hai")
    if not new_room:
        raise ValueError("New Room zaroori hai")
    chng_date = change_date or datetime.date.today()
    chng_time = change_time or datetime.datetime.now().strftime("%H:%M")
    own = cn is None
    cn = cn or db.connect()
    try:
        rows = db.query(
            f"SELECT {_ROOM_OCC_COLS} FROM RoomOcc WHERE DocId = ? AND "
            "ChkOutDate IS NULL AND Site_Code = ?", (docid, site), cn=cn)
        if not rows:
            raise ValueError("Is folio ki koi open RoomOcc row nahi mili")
        r = rows[0]
        old_room = (r.RoomNo or "").strip()
        if old_room == new_room:
            raise ValueError("New room aur current room same hai")
        # naya room valid + free hona chahiye
        rm = db.query(
            "SELECT TOP 1 RoomCat FROM RoomMast WHERE RTRIM(Code) = ? AND "
            "(LogSite_Code = ? OR LogSite_Code = 'HO')",
            (new_room, site), cn=cn)
        if not rm:
            raise ValueError(f"Room {new_room} RoomMast me nahi mila")
        new_cat = (rm[0].RoomCat or "").strip()
        busy = db.query(
            "SELECT COUNT(*) FROM RoomOcc WHERE RTRIM(RoomNo) = ? AND "
            "ChkOutDate IS NULL AND Site_Code = ? AND DocId <> ?",
            (new_room, site, docid), cn=cn)
        if busy and busy[0][0]:
            raise ValueError(f"Room {new_room} pehle se occupied hai")
        gf = db.query(
            "SELECT TOP 1 FolioNo, Name, BookingDocId FROM GuestFolio "
            "WHERE DocId = ?", (docid,), cn=cn)
        folio = int(gf[0].FolioNo or 0) if gf else 0
        guest_name = (gf[0].Name or "").strip() if gf else ""
        bookingdocid = (gf[0].BookingDocId or "").strip() if gf else ""
        old_sno = int(r.SNo or 0)
        mx = db.query("SELECT MAX(SNo) FROM RoomOcc WHERE DocId = ?",
                      (docid,), cn=cn)
        new_sno = int((mx[0][0] or 0) if mx else old_sno) + 1
        raised_dates = (chng_date, chng_time)
        # --- 1. nayi RoomOcc row (VB6 30-col INSERT pattern) ---
        db.execute(
            "INSERT INTO RoomOcc (DocId, SNo, FolioNo, Vtype, Site_Code, "
            "Vprefix, GuestProf, RoomCat, RoomType, RoomNo, RateCode, "
            "RoomRate, ChkInDate, ChkInTime, Adult, Children, DepDate, "
            "DepTime, Type, U_Name, U_EntDt, U_AE, LogSite_Code, "
            "RRTaxInc, RRServiceChrg, ChngDate, ExtraBed, RoomTarrif, "
            "RackRate, RoomTaxStru) "
            "VALUES (?, ?, ?, 'CHK', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
            "?, ?, 'I', ?, getdate(), 'A', ?, ?, ?, ?, ?, ?, ?, ?)",
            (docid, new_sno, r.FolioNo, site, r.Vprefix or "", r.GuestProf,
             r.RoomCat or "", r.RoomType or "", new_room, r.RateCode or "",
             r.RoomRate or 0, raised_dates[0], raised_dates[1],
             int(r.Adult or 1), int(r.Children or 0), r.DepDate, r.DepTime,
             user, site, r.RRTaxInc or "", r.RRServiceChrg or "",
             raised_dates[0], r.ExtraBed or "", r.RoomTarrif or 0,
             r.RackRate or 0, r.RoomTaxStru or ""), cn=cn, commit=False)
        # --- 2. nayi row par plan fields ---
        db.execute(
            "UPDATE RoomOcc SET PlanCode = ?, PlanAmt = ?, IncInRate = ?, "
            "PlanDisc = ?, PlanDiscAmt = ?, U_AE = 'E' "
            "WHERE SNo = ? AND DocId = ? AND Site_Code = ? AND "
            "RTRIM(RoomNo) = ?",
            (r.PlanCode or "", r.PlanAmt or 0, r.IncInRate or "",
             r.PlanDisc or 0, r.PlanDiscAmt or 0, new_sno, docid, site,
             new_room), cn=cn, commit=False)
        # --- 3. old row checkout ---
        db.execute(
            "UPDATE RoomOcc SET ChkOutDate = ?, ChkOutTime = ?, "
            "Type = 'C', NewRoomNo = ?, Reason = ?, U_Name = ?, "
            "U_EntDt = getdate(), U_AE = 'E' "
            "WHERE SNo = ? AND DocId = ? AND Site_Code = ? AND "
            "RTRIM(RoomNo) = ?",
            (raised_dates[0], raised_dates[1], new_room,
             (reason or "").strip()[:100], user, old_sno, docid, site,
             old_room), cn=cn, commit=False)
        # --- 4. GuestMessage room move ---
        if folio:
            db.execute(
                "UPDATE GuestMessage SET RoomNo = ?, RoomCat = ? "
                "WHERE FolioNo = ? AND LogSite_Code = ? AND "
                "RTRIM(RoomNo) = ?",
                (new_room, new_cat, folio, site, old_room), cn=cn,
                commit=False)
        # --- 5. Booking.OccRoom link ---
        if bookingdocid:
            db.execute("UPDATE Booking SET OccRoom = ? WHERE DocId = ?",
                       (new_room, bookingdocid), cn=cn, commit=False)
        # --- 6. old room dirty ---
        db.execute(
            "UPDATE RoomMast SET RoomStat = 'D', U_Name = ?, "
            "U_EntDt = getdate(), U_AE = 'E' "
            "WHERE RTRIM(Type) = 'RO' AND RTRIM(Code) = ? AND "
            "(LogSite_Code = ? OR LogSite_Code = 'HO')",
            (user, old_room, site), cn=cn, commit=False)
        # --- 7. PlanDetails: delete + re-insert (nayi RoomNo) ---
        db.execute(
            "DELETE FROM PlanDetails WHERE DocId = ? AND Site_Code = ?",
            (docid, site), cn=cn, commit=False)
        for pl in db.query(
                "SELECT FolioNo, RevCode, Chrgcode, TaxInc, TaxStru, "
                "PrintOption, PostingMethod, ChargeType, FlatRate, Adult, "
                "Child, ExtraAdult, ExtraChild, NoOfDays, PlanPer, "
                "App_Date, FixRate, Amount, PlanCode, NetPackageAmount, "
                "Logsite_Code, DiscAmt, PlanAppDate "
                "FROM PlanDetails WHERE DocId = ?", (docid,), cn=cn):
            db.execute(
                "INSERT INTO PlanDetails (FolioNo, RoomNo, RevCode, "
                "Chrgcode, TaxInc, TaxStru, PrintOption, PostingMethod, "
                "ChargeType, FlatRate, Adult, Child, ExtraAdult, "
                "ExtraChild, NoOfDays, PlanPer, App_Date, FixRate, "
                "Site_Code, U_Name, U_EntDt, U_AE, Amount, PlanCode, "
                "Docid, NetPackageAmount, Logsite_Code, DiscAmt, "
                "PlanAppDate) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
                "?, ?, ?, ?, getdate(), 'A', ?, ?, ?, ?, ?, ?, ?)",
                (pl.FolioNo, new_room, pl.RevCode, pl.Chrgcode, pl.TaxInc,
                 pl.TaxStru, pl.PrintOption, pl.PostingMethod,
                 pl.ChargeType, pl.FlatRate, pl.Adult, pl.Child,
                 pl.ExtraAdult, pl.ExtraChild, pl.NoOfDays, pl.PlanPer,
                 pl.App_Date, pl.FixRate, site, user, pl.Amount,
                 pl.PlanCode, docid, pl.NetPackageAmount, pl.Logsite_Code,
                 pl.DiscAmt, pl.PlanAppDate), cn=cn, commit=False)
        # --- 8. EPABX_IN audit (VB6 loc_18AD546 pattern) ---
        # OPTIONAL (live DB me EPABX_IN nahi hai - epabx_ops.py docs).
        # Feature-detect: MAX(ID) query 208 (Invalid object name) pe
        # audit skip; room_change ke 7 core steps phir bhi commit.
        epabx_n = 0
        try:
            eid = db.query("SELECT COALESCE(MAX(ID), 0) + 1 FROM EPABX_IN",
                           cn=cn)
            id1 = int((eid[0][0] or 1) if eid else 1)
            db.execute(
                "INSERT INTO EPABX_IN (ID, V_TYPE, ROOM_NO, ROOM_NO_NEW, "
                "GUEST_NAME) VALUES (?, 'CHKOT', ?, ?, ?)",
                (id1, old_room, new_room, guest_name), cn=cn, commit=False)
            eid2 = db.query("SELECT COALESCE(MAX(ID), 0) + 1 FROM EPABX_IN",
                            cn=cn)
            id2 = int((eid2[0][0] or 1) if eid2 else 1)
            db.execute(
                "INSERT INTO EPABX_IN (ID, V_TYPE, ROOM_NO, ROOM_NO_NEW, "
                "GUEST_NAME) VALUES (?, 'CHKIN', ?, ?, ?)",
                (id2, new_room, old_room, guest_name), cn=cn, commit=False)
            epabx_n = 2
        except db.pyodbc.Error as e:
            msg = str(e)
            if "208" in msg or "Invalid object name" in msg:
                epabx_n = 0
            else:
                raise
        if commit:
            cn.commit()
        return {"new_sno": new_sno, "folio": folio, "old_room": old_room,
                "new_room": new_room, "affected": 7 + epabx_n,
                "epabx_audited": bool(epabx_n)}
    finally:
        if own:
            cn.close()


# ------------------------------------------------------------
# Merge Charge (VB6 FrmMergeCharge)
# ------------------------------------------------------------
def merge_charge(from_room: str, to_room: str, user: str = USER,
                 site: str = SITE_CODE, cn=None, commit: bool = True) -> dict:
    """Source room ke folio ke saare PayCharge lines target room ke folio
    pe shift karo (VB6 FrmMergeCharge/cmdTransferCharge transaction):

      1. GuestFolio: source folio ko mFolioNo/mFolioNoDocId me target link
      2. PayCharge: source ki 'clean' rows (ContraDocID NULL/'') ko
         target ka RelatedFolio mark
      3. PayCharge: source ki saari rows ko FolioNoDocid/FolioNo=target aur
         RelatedFolioNo/RelatedFolioNoDocId=source bana do

    Returns dict(rows_moved, folio_from, folio_to)."""
    from_room = (from_room or "").strip()
    to_room = (to_room or "").strip()
    if not from_room or not to_room:
        raise ValueError("Dono room numbers zaroori hain")
    src = open_folio_by_room(from_room, site, cn=cn)
    tgt = open_folio_by_room(to_room, site, cn=cn)
    if not src:
        raise ValueError(f"Source room {from_room} pe koi in-house guest nahi")
    if not tgt:
        raise ValueError(f"Target room {to_room} pe koi in-house guest nahi")
    if src["docid"] == tgt["docid"]:
        raise ValueError("Dono rooms ka folio same hai (pehle se merged)")
    own = cn is None
    cn = cn or db.connect()
    try:
        n1 = db.execute(
            "UPDATE GuestFolio SET mFolioNoDocid = ?, mFolioNo = ?, "
            "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE DocId = ?",
            (tgt["docid"], tgt["folio"], user, src["docid"]), cn=cn,
            commit=False)
        n2 = db.execute(
            "UPDATE PayCharge SET RelatedFolioNo = ?, RelatedFolioNoDocId = ? "
            "WHERE FolioNoDocid = ? AND (ContraDocID IS NULL OR "
            "ContraDocID = '')",
            (tgt["folio"], tgt["docid"], src["docid"]), cn=cn, commit=False)
        n3 = db.execute(
            "UPDATE PayCharge SET FolioNoDocid = ?, FolioNo = ?, "
            "RelatedFolioNo = ?, RelatedFolioNoDocId = ?, U_Name = ?, "
            "U_EntDt = getdate(), U_AE = 'E' WHERE FolioNoDocid = ?",
            (tgt["docid"], tgt["folio"], src["folio"], src["docid"], user,
             src["docid"]), cn=cn, commit=False)
        if commit:
            cn.commit()
        return {"rows_moved": n1 + n2 + n3, "folio_from": src["folio"],
                "folio_to": tgt["folio"]}
    finally:
        if own:
            cn.close()


# ------------------------------------------------------------
# Re-Settlement (VB6 FdReSetlement)
# ------------------------------------------------------------
def list_settlements(docid: str, site: str = SITE_CODE, cn=None) -> list[dict]:
    """Folio ke settlement receipts (ModeSet='S', ROFF contra nahi)."""
    rows = db.query(
        "SELECT DocId, VNo, Vdate, VTime, PayCode, PayType, AmtCr, Comments, "
        "ModeSet FROM PayCharge WHERE FolioNoDocid = ? AND ModeSet = 'S' "
        "AND PayCode <> ? ORDER BY Vdate DESC, VNo, U_EntDt",
        (docid, site + "ROFF"), cn=cn)
    return [{"docid": (r.DocId or "").strip(), "vno": int(r.VNo or 0),
             "vdate": r.Vdate, "vtime": r.VTime or "",
             "paycode": (r.PayCode or "").strip(),
             "paytype": (r.PayType or "").strip(),
             "amount": float(r.AmtCr or 0),
             "comments": (r.Comments or "").strip(),
             "modeset": (r.ModeSet or "").strip()} for r in rows]


def re_settlement(docid: str, lines: list[dict], user: str = USER,
                  site: str = SITE_CODE, cn=None,
                  commit: bool = True) -> dict:
    """FdReSetlement core: pichhla REC settlement receipt reverse karke
    nayi payment lines re-post karo.

    lines = [{"paycode": "KKCASH", "amount": 500.0, "comments": "BY CASH"}]
    Sum(lines.amount) purane receipt ke AmtCr ke barabar hona zaroori hai
    (VB6 ka 'sum match' guard). Nayi lines Vtype='REC', ModeSet='S'.

    Returns dict(old_receipt, new_vnos, total)."""
    docid = (docid or "").strip()
    if not docid:
        raise ValueError("Folio DocId zaroori hai")
    if not lines:
        raise ValueError("Koi nayi settlement line nahi di")
    own = cn is None
    cn = cn or db.connect()
    try:
        gf = db.query(
            "SELECT FolioNo, GuestProf, Vprefix FROM GuestFolio "
            "WHERE DocId = ?", (docid,), cn=cn)
        if not gf:
            raise ValueError("GuestFolio nahi mila (DocId galt hai?)")
        folio = int(gf[0].FolioNo or 0)
        guestprof = (gf[0].GuestProf or "").strip()
        vprefix = (gf[0].Vprefix or "2026").strip()
        rc = db.query("SELECT TOP 1 RoomCat, RoomType, RoomNo FROM RoomOcc "
                      "WHERE DocId = ?", (docid,), cn=cn)
        roomcat = (rc[0].RoomCat or "") if rc else ""
        roomtype = (rc[0].RoomType or "") if rc else ""
        roomno = (rc[0].RoomNo or "") if rc else ""
        last = db.query(
            "SELECT TOP 1 DocId, AmtCr FROM PayCharge WHERE FolioNoDocid = ? "
            "AND ModeSet = 'S' AND PayCode <> ? ORDER BY VNo DESC",
            (docid, site + "ROFF"), cn=cn)
        if not last:
            raise ValueError("Pichhla settlement receipt nahi mila "
                             "(re-settle possible nahi)")
        old_docid = (last[0].DocId or "").strip()
        old_amt = float(last[0].AmtCr or 0)
        new_amt = sum(float(l.get("amount") or 0) for l in lines)
        if abs(new_amt - old_amt) > 0.005:
            raise ValueError(
                f"Nayi settlement sum {new_amt:.2f} purane receipt "
                f"{old_amt:.2f} se match nahi karta")
        # reverse + delete old receipt (VB6: Delete From PayCharge
        # Where DocId=<receipt> And FolioNoDocid=<docid>)
        db.execute(
            "DELETE FROM PayCharge WHERE DocId = ? AND FolioNoDocid = ? "
            "AND Site_Code = ? AND ModeSet = 'S'",
            (old_docid, docid, site), cn=cn, commit=False)
        # nayi receipt lines re-post
        new_vnos = []
        for line in lines:
            paycode = (line.get("paycode") or "KKCASH").strip()
            paytype = _PAY_TYPES.get(paycode)
            if paytype is None:
                raise ValueError(
                    f"Unknown paycode '{paycode}' (known: " +
                    ", ".join(sorted(_PAY_TYPES)) + ")")
            vno = db.next_vno("PayCharge", "REC", vprefix, site=site, cn=cn)
            ndocid = ("D" + site + "REC".ljust(6) + vprefix.ljust(4) +
                      str(vno).rjust(8))
            db.execute(
                "INSERT INTO PayCharge (DocId, SNo, Vtype, VNo, Site_Code, "
                "VPrefix, Vdate, VTime, GuestProf, Comments, PayCode, "
                "PayType, AmtCr, TipAmt, RoomCat, RoomType, RoomNo, "
                "FolioNo, U_Name, U_EntDt, U_AE, RestCode, ModeSet, "
                "FolioNoDocid, LogSite_Code) "
                "VALUES (?, 1, 'REC', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0.0, ?, "
                "?, ?, ?, ?, getdate(), 'A', 'KKFOM', 'S', ?, ?)",
                (ndocid, vno, site, vprefix, datetime.date.today(),
                 datetime.datetime.now().strftime("%H:%M"), guestprof,
                 (line.get("comments") or "RE-SETTLEMENT").strip(),
                 paycode, paytype, float(line.get("amount") or 0),
                 roomcat, roomtype, roomno, folio, user, docid, site),
                cn=cn, commit=False)
            new_vnos.append(vno)
        if commit:
            cn.commit()
        return {"old_receipt": old_docid, "new_vnos": new_vnos,
                "total": new_amt}
    finally:
        if own:
            cn.close()


# ------------------------------------------------------------
# Folio charge summary (merge/preview ke liye)
# ------------------------------------------------------------
def folio_charge_total(docid: str, site: str = SITE_CODE, cn=None) -> float:
    rows = db.query(
        "SELECT SUM(DrAmt) FROM PayCharge WHERE FolioNoDocid = ? "
        "AND Site_Code = ?", (docid, site), cn=cn)
    return float(rows[0][0] or 0) if rows and rows[0] else 0.0