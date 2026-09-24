"""Night Audit core (P5): NA log + occupancy + revenue summary + POSTING.

EVIDENCE (live + VB6 decompiled):
- NightAuditLog: Id, DateChngFrom, DateChngTo, StartNightAudit, EndNightAudit,
  Site_Code, U_AE, U_Name, U_EntDt, LogSite_Code.
- HMS.bas:90-115 (NightAuditoR_Click): Enviro KOTAtNightAudit/POSBillAtNightAudit flags
- Proc_96_46_10187AC: Check pending KOTs (KOT table, NC='N', VOID='N', Pending='Y', KOTAtNightAudit<>'No')
- Proc_96_45_11033E4: Check unsettled bills (Sale1/POS + HallSale1/Banquet, unpaid)
- Proc_96_14_1F70BE8: Daily bill-wise posting (room charges + POS revenue)
- Proc_96_16_1F369E4: Summary posting (similar but aggregated)
- fdNDAcPostChrg.TopCtrl1_UnknownEvent_16: PostingType from Enviro drives mode
- Room charges: PayCharge Vtype='RC', PayCode='KKRMCH' + CGST/SGST tax
- POS revenue: PayCharge Vtype='PPOS', grouped by RevCode/RestCode
- Voucher numbering: Voucher_Type + Voucher_Prefix for Vtype='PPOS'
- RoomChrgPostingType in Enviro: 'Daily' = per room, else summary
- RoomChrgDueAc in Enviro: GL account for room charge posting

PYT-guard: Production NA runs from VB6 EXE; Python implements logic for testing/automation."""
from __future__ import annotations

import datetime
from typing import Optional

from HMS_py.core import db
from HMS_py.core import folio as folio_mod
from datetime import datetime as _dt

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
VYEAR = str(_dt.now().year)
VTYPE_RC = "RC"
VTYPE_PPOS = "PPOS"
PAY_CODE_RC = "KKRMCH"
CGST_CODE = "KKCGSS"
SGST_CODE = "KKSGSS"
GST_RATE = 0.05  # Live evidence: 5% CGST + 5% SGST


# ============================================================
# Pre-checks (VB6 Proc_96_46, Proc_96_45)
# ============================================================

def get_night_audit_flags(cn=None) -> dict:
    """Read Enviro flags for NA behavior.
    Returns: {'kot_at_na': 'Yes'/'No', 'pos_bill_at_na': 'Yes'/'No',
              'posting_type': 'Daily Bill wise Posting'/'Summary',
              'room_chrg_type': 'Daily'/'Monthly', 'room_chrg_due_ac': ac_code}
    """
    rows = db.query(
        "SELECT KOTAtNightAudit, POSBillAtNightAudit, PostingType, "
        "RoomChrgPostingType, RoomChrgDueAc FROM Enviro WHERE LogSite_Code = ?",
        (SITE_CODE,), cn=cn)
    if not rows:
        return {"kot_at_na": "No", "pos_bill_at_na": "No",
                "posting_type": "Summary", "room_chrg_type": "Daily",
                "room_chrg_due_ac": ""}
    r = rows[0]
    return {
        "kot_at_na": r[0] or "No",
        "pos_bill_at_na": r[1] or "No",
        "posting_type": r[2] or "Summary",
        "room_chrg_type": r[3] or "Daily",
        "room_chrg_due_ac": r[4] or "",
    }


def check_pending_kots(vdate, cn=None) -> tuple[bool, list[str]]:
    """VB6 Proc_96_46_10187AC: Check pending KOTs for a date.
    Returns (has_pending, list_of_outlets_with_pending).
    KOT criteria: NCKOT<>'Y', VOIDYN<>'Y', VDate=date, NCAT='RSKOT',
    Pending='Y', DELFLAG NOT IN('Y'), Depart.KOTAtNightAudit<>'No'
    """
    rows = db.query(
        "SELECT DISTINCT D.Name FROM KOT K "
        "INNER JOIN Depart D ON K.RestCode = D.Code "
        "WHERE K.NCKOT <> 'Y' AND K.VOIDYN <> 'Y' AND K.VDate = ? "
        "AND K.Vtype = 'BMM' AND K.Pending = 'Y' AND K.DELFLAG NOT IN ('Y') "
        "AND D.KOTAtNightAudit <> 'No' AND D.LogSite_Code = ?",
        (vdate, SITE_CODE), cn=cn)
    outlets = [r[0] for r in rows]
    return len(outlets) > 0, outlets


def check_unsettled_bills(vdate, cn=None) -> tuple[bool, list[str]]:
    """VB6 Proc_96_45_11033E4: Check unsettled POS + Banquet bills.
    Returns (has_unsettled, list_of_outlets_with_unsettled).
    POS: Sale1 with PayCharge AmtCr < NetAmt
    Banquet: HallSale1 with PayChargeH AmtCr < NetAmt-Advance
    """
    outlets = []

    # POS unsettled bills (Sale1)
    rows = db.query(
        "SELECT DISTINCT D.Name FROM Sale1 S "
        "LEFT JOIN PayCharge P ON S.DocId = P.DocId "
        "INNER JOIN Depart D ON S.RestCode = D.Code "
        "WHERE S.VDate = ? AND S.Vtype = 'BMM' AND D.RestType <> 'Production' "
        "AND S.LogSite_Code = ? AND (P.DocId IS NULL OR S.NetAmt > ISNULL(P.AmtCr, 0)) "
        "AND (S.DelFlag = '' OR S.DelFlag = 'N')",
        (vdate, SITE_CODE), cn=cn)
    outlets.extend([r[0] for r in rows])

    # Banquet unsettled bills (HallSale1)
    rows = db.query(
        "SELECT DISTINCT D.Name FROM HallSale1 H "
        "LEFT JOIN (SELECT DocId, SUM(AmtCr) AS AmtCr FROM PayChargeH GROUP BY DocId) PH "
        "ON H.DocId = PH.DocId "
        "INNER JOIN Depart D ON H.RestCode = D.Code "
        "WHERE H.VDate = ? AND H.LogSite_Code = ? "
        "AND (ISNULL(H.NetAmt, 0) - ISNULL(H.Advance, 0)) <> ISNULL(PH.AmtCr, 0)",
        (vdate, SITE_CODE), cn=cn)
    outlets.extend([r[0] for r in rows])

    return len(outlets) > 0, list(set(outlets))


# ============================================================
# Posting Helpers
# ============================================================

def _next_vno(vtype: str, vprefix: str, cn=None) -> int:
    # BUG-015: race-safe VNo (UPDLOCK/HOLDLOCK) - db.py central helper.
    return db.next_vno("PayCharge", vtype, vprefix, site=SITE_CODE, cn=cn)


def _next_sno(foliono: int, cn=None) -> int:
    rows = db.query(
        "SELECT MAX(SNo) FROM PayCharge WHERE FolioNo = ? AND Site_Code = ?",
        (foliono, SITE_CODE), cn=cn)
    return (rows[0][0] or 0) + 1 if rows and rows[0][0] else 1


def _make_rc_docid(vprefix: str, vno: int) -> str:
    """'D' + site(2) + 'RC'.ljust(6) + vprefix(4) + VNo.rjust(8) = 21 char"""
    return "D" + SITE_CODE + "RC".ljust(6) + vprefix.ljust(4) + str(vno).rjust(8)


def _make_ppos_docid(vprefix: str, vno: int) -> str:
    return "D" + SITE_CODE + "PPOS".ljust(6) + vprefix.ljust(4) + str(vno).rjust(8)


def _log_night_audit(date_from, date_to, start_dt, end_dt, user, cn=None, commit=True) -> int:
    """Insert NightAuditLog entry (like BookingLog pattern)."""
    return db.execute(
        "INSERT INTO NightAuditLog (DateChngFrom, DateChngTo, StartNightAudit, "
        "EndNightAudit, Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (date_from, date_to, start_dt, end_dt, SITE_CODE, user, SITE_CODE),
        cn=cn, commit=commit)


# ============================================================
# Room Charge Posting (VB6 Proc_96_14 daily bill-wise)
# ============================================================

def get_inhouse_rooms(vdate, vprefix: str = VYEAR, cn=None) -> list[dict]:
    """Get occupied rooms for a date (RoomOcc ChkOutDate IS NULL, ChkInDate <= date).
    Returns list of {folio, docid, roomno, roomrate, guest_name, comp_flag, mfolio}
    """
    rows = db.query(
        "SELECT RO.DocId, RO.FolioNo, RO.RoomNo, RO.RoomRate, GF.Name, "
        "ISNULL(GF.MFOlioNO, 0) AS MFOlioNO "
        "FROM RoomOcc RO LEFT JOIN GuestFolio GF ON GF.DocId = RO.DocId "
        "WHERE RO.ChkOutDate IS NULL AND RO.Site_Code = ? AND RO.Vprefix = ? "
        "AND RO.ChkInDate <= ? AND RO.ChkInDate IS NOT NULL",
        (SITE_CODE, vprefix, vdate), cn=cn)
    out = []
    for r in rows:
        out.append({
            "docid": r[0] or "",
            "folio": r[1] or 0,
            "roomno": (r[2] or "").strip(),
            "roomrate": float(r[3] or 0),
            "guest": (r[4] or "").strip(),
            "mfolio": r[5] or 0,
        })
    return out


def post_room_charges_for_date(vdate, vprefix: str = VYEAR,
                                user: str = USER, cn=None, commit: bool = True) -> dict:
    """Post room charges for all in-house guests on a date.
    VB6 Proc_96_14 pattern: For each in-house room, if not already posted
    (PayCharge Vtype='RC' for that folio/date), insert RC charge + tax.
    Returns: {'posted': count, 'skipped': count, 'errors': list}
    """
    rooms = get_inhouse_rooms(vdate, vprefix, cn=cn)
    posted = 0
    skipped = 0
    errors = []

    # Get next VNo for RC series
    vno = _next_vno(VTYPE_RC, vprefix, cn=cn)

    # Pre-compute max sno per folio to avoid N+1 queries
    folios = [r["folio"] for r in rooms]
    sno_map = {}
    if folios:
        placeholders = ",".join("?" for _ in folios)
        rows = db.query(
            f"SELECT FolioNo, MAX(SNo) FROM PayCharge WHERE FolioNo IN ({placeholders}) AND Site_Code = ? AND VPrefix = ? GROUP BY FolioNo",
            tuple(folios + [SITE_CODE, vprefix]), cn=cn)
        for r in rows:
            sno_map[r[0]] = r[1] or 0

    own = cn is None
    cn = cn or db.connect()
    try:
        for room in rooms:
            # Check if RC already posted for this folio/date
            existing = db.query(
                "SELECT 1 FROM PayCharge WHERE Vtype = ? AND Vdate = ? AND FolioNo = ? "
                "AND Site_Code = ? AND VPrefix = ?",
                (VTYPE_RC, vdate, room["folio"], SITE_CODE, vprefix), cn=cn)
            if existing:
                skipped += 1
                continue

            # Post room charge
            amount = room["roomrate"]
            if amount <= 0:
                skipped += 1
                continue

            docid = _make_rc_docid(vprefix, vno)
            sno = sno_map.get(room["folio"], 0) + 1
            sno_map[room["folio"]] = sno

            # Room charge row (Dr)
            db.execute(
                "INSERT INTO PayCharge (DocId, SNo, Vtype, VNo, Site_Code, VPrefix, Vdate, "
                "GuestProf, Comments, PayCode, FolioNo, RoomNo, AmtDr, U_Name, U_EntDt, U_AE, LogSite_Code) "
                "VALUES (?, ?, 'RC', ?, ?, ?, ?, '', '', ?, ?, ?, ?, ?, getdate(), 'A', ?)",
                (docid, sno, vno, SITE_CODE, vprefix, vdate, PAY_CODE_RC,
                 room["folio"], room["roomno"] or "", amount, user, SITE_CODE),
                cn=cn, commit=False)

            # CGST row
            cgst = round(amount * GST_RATE, 2)
            if cgst > 0:
                sno += 1
                db.execute(
                    "INSERT INTO PayCharge (DocId, SNo, Vtype, VNo, Site_Code, VPrefix, Vdate, "
                    "GuestProf, Comments, PayCode, FolioNo, RoomNo, AmtDr, U_Name, U_EntDt, U_AE, LogSite_Code) "
                    "VALUES (?, ?, 'RC', ?, ?, ?, ?, '', '', ?, ?, ?, ?, ?, getdate(), 'A', ?)",
                    (docid, sno, vno, SITE_CODE, vprefix, vdate, CGST_CODE,
                     room["folio"], room["roomno"] or "", cgst, user, SITE_CODE),
                    cn=cn, commit=False)

            # SGST row
            sgst = round(amount * GST_RATE, 2)
            if sgst > 0:
                sno += 1
                db.execute(
                    "INSERT INTO PayCharge (DocId, SNo, Vtype, VNo, Site_Code, VPrefix, Vdate, "
                    "GuestProf, Comments, PayCode, FolioNo, RoomNo, AmtDr, U_Name, U_EntDt, U_AE, LogSite_Code) "
                    "VALUES (?, ?, 'RC', ?, ?, ?, ?, '', '', ?, ?, ?, ?, ?, getdate(), 'A', ?)",
                    (docid, sno, vno, SITE_CODE, vprefix, vdate, SGST_CODE,
                     room["folio"], room["roomno"] or "", sgst, user, SITE_CODE),
                    cn=cn, commit=False)

            # FolioLog for room charge post (use GuestFolio DocId, not PayCharge DocId)
            folio_mod._log(room["docid"], "P", user, cn, SITE_CODE)

            posted += 1
            vno += 1

        if commit:
            cn.commit()
        return {"posted": posted, "skipped": skipped, "errors": errors}
    finally:
        if own:
            cn.close()


# ============================================================
# POS Revenue Posting (VB6 Proc_96_14/16 - PPOS)
# ============================================================

def get_pos_revenue(vdate, cn=None) -> list[dict]:
    """Get POS revenue for a date (VB6 SunTran aggregation).
    Returns: list of {revcode, restcode, revname, outlet, dshortname, amount, sundrycode}
    """
    rows = db.query(
        "SELECT SUM(SunTran.Amount) AS RevAmt, SunTran.RevCode, SunTran.RestCode, "
        "SunTran.Vdate, MAX(Depart.Name) AS Outlet, MAX(Depart.ShortName) AS DShortName, "
        "MAX(RevMast.Name) AS RevenueName, MAX(SunTran.SunCode) AS SundryCode "
        "FROM SunTran LEFT JOIN RevMast ON SunTran.RevCode = RevMast.Code "
        "LEFT JOIN Depart ON SunTran.RestCode = Depart.Code "
        "WHERE SunTran.Vdate = ? AND SunTran.RevCode IS NOT NULL AND SunTran.RevCode <> '' "
        "AND SunTran.SunCode <> 'SNET' AND SunTran.LogSite_Code = ? "
        "AND Depart.RestType IN ('Outlet', 'Room Service') AND SunTran.DelFlag <> 'D' "
        "GROUP BY SunTran.RestCode, SunTran.RevCode, SunTran.Vdate ORDER BY SunTran.RestCode",
        (vdate, SITE_CODE), cn=cn)
    out = []
    for r in rows:
        amt = float(r[0] or 0)
        if amt != 0:
            out.append({
                "revcode": r[1] or "",
                "restcode": r[2] or "",
                "vdate": r[3],
                "outlet": (r[4] or "").strip(),
                "dshortname": (r[5] or "").strip(),
                "revname": (r[6] or "").strip(),
                "sundrycode": r[7] or "",
                "amount": amt,
            })
    return out


def _get_voucher_prefix(vtype: str, vdate, cn=None) -> tuple[str, int]:
    """Get voucher prefix and start serial for a Vtype/date.
    Returns (vprefix, start_srl)"""
    rows = db.query(
        "SELECT VP.Prefix, VP.Start_Srl_No FROM Voucher_Type VT "
        "INNER JOIN Voucher_Prefix VP ON VT.V_Type = VP.V_Type "
        "AND VT.Site_Code = VP.Site_Code AND VT.LogSite_Code = VP.LogSite_Code "
        "WHERE VT.Site_Code = ? AND VP.V_Type = ? "
        "AND VP.Date_From <= ? ORDER BY VP.Date_From DESC",
        (SITE_CODE, vtype, vdate), cn=cn)
    if not rows:
        return str(vdate.year), 1
    return rows[0][0] or str(vdate.year), int(rows[0][1] or 1)


def post_pos_revenue_for_date(vdate, vprefix: str = VYEAR,
                               user: str = USER, cn=None, commit: bool = True) -> dict:
    """Post POS revenue (SunTran) to PayCharge as Vtype='PPOS'.
    VB6 Proc_96_14: Groups by RevCode/RestCode, creates PPOS entries.
    Returns: {'posted': count, 'skipped': count}
    """
    revenues = get_pos_revenue(vdate, cn=cn)
    if not revenues:
        return {"posted": 0, "skipped": 0}

    vno = _next_vno(VTYPE_PPOS, vprefix, cn=cn)
    pp, start_srl = _get_voucher_prefix(VTYPE_PPOS, vdate, cn=cn)

    posted = 0
    skipped = 0
    own = cn is None
    cn = cn or db.connect()
    try:
        for rev in revenues:
            # Check if already posted
            existing = db.query(
                "SELECT 1 FROM PayCharge WHERE Vtype = ? AND Vdate = ? AND RestCode = ? "
                "AND RevCode = ? AND Site_Code = ? AND VPrefix = ?",
                (VTYPE_PPOS, vdate, rev["restcode"], rev["revcode"], SITE_CODE, vprefix), cn=cn)
            if existing:
                skipped += 1
                continue

            amount = rev["amount"]
            if amount == 0:
                skipped += 1
                continue

            docid = _make_ppos_docid(vprefix, vno)
            # For PPOS, FolioNo=0 (not linked to specific folio)

            db.execute(
                "INSERT INTO PayCharge (DocId, SNo, Vtype, VNo, Site_Code, VPrefix, Vdate, "
                "GuestProf, Comments, PayCode, FolioNo, RoomNo, AmtDr, U_Name, U_EntDt, U_AE, LogSite_Code) "
                "VALUES (?, ?, 'PPOS', ?, ?, ?, ?, '', '', ?, 0, '', ?, ?, getdate(), 'A', ?)",
                (docid, 1, vno, SITE_CODE, vprefix, vdate, rev["revcode"],
                 amount, user, SITE_CODE),
                cn=cn, commit=False)

            posted += 1
            vno += 1

        if commit:
            cn.commit()
        return {"posted": posted, "skipped": skipped}
    finally:
        if own:
            cn.close()


# ============================================================
# Main Night Audit Process
# ============================================================

def run_night_audit(date_from, date_to=None, user: str = USER,
                    cn=None, commit: bool = True,
                    vprefix: str = VYEAR) -> dict:
    """Run full Night Audit for a date range (VB6 fdNDAcPostChrg pattern).
    
    Steps:
    1. Check Enviro flags (KOTAtNightAudit, POSBillAtNightAudit)
    2. For each date in range:
       a. If KOT flag -> check_pending_kots()
       b. If POS flag -> check_unsettled_bills()
       c. If both clear -> post_room_charges + post_pos_revenue
       d. Log NightAuditLog entry
    Returns summary dict.
    """
    if date_to is None:
        date_to = date_from

    start_time = datetime.datetime.now()
    total_posted = 0
    total_skipped = 0
    rc_posted = 0
    pos_posted = 0
    errors = []
    dates_processed = []

    own = cn is None
    cn = cn or db.connect()
    try:
        current = date_from
        while current <= date_to:
            # Pre-checks
            flags = get_night_audit_flags(cn=cn)
            
            # Check pending KOTs
            if flags.get("kot_at_na") == "Yes":
                has_pending, outlets = check_pending_kots(current, cn=cn)
                if has_pending:
                    errors.append(f"{current}: Pending KOTs in {', '.join(outlets)}")
                    current += datetime.timedelta(days=1)
                    continue

            # Check unsettled bills
            if flags.get("pos_bill_at_na") == "Yes":
                has_unsettled, outlets = check_unsettled_bills(current, cn=cn)
                if has_unsettled:
                    errors.append(f"{current}: Unsettled bills in {', '.join(outlets)}")
                    current += datetime.timedelta(days=1)
                    continue

            # Post room charges
            rc_result = post_room_charges_for_date(current, vprefix, user, cn=cn, commit=False)
            total_posted += rc_result["posted"]
            total_skipped += rc_result["skipped"]
            rc_posted += rc_result["posted"]

            # Post POS revenue
            pos_result = post_pos_revenue_for_date(current, vprefix, user, cn=cn, commit=False)
            total_posted += pos_result["posted"]
            total_skipped += pos_result["skipped"]
            pos_posted += pos_result["posted"]

            # Log NA entry
            end_time = datetime.datetime.now()
            _log_night_audit(current, current, start_time, end_time, user, cn=cn, commit=False)

            dates_processed.append(current)
            current += datetime.timedelta(days=1)

        if commit:
            cn.commit()

        return {
            "success": len(errors) == 0,
            "date_from": date_from,
            "date_to": date_to,
            "dates_processed": dates_processed,
            "room_charges_posted": rc_posted,
            "pos_revenue_posted": pos_posted,
            "total_skipped": total_skipped,
            "errors": errors,
            "start_time": start_time,
            "end_time": datetime.datetime.now(),
        }
    except Exception as e:
        if own and cn:
            cn.rollback()
        return {
            "success": False,
            "error": str(e),
            "date_from": date_from,
            "date_to": date_to,
        }
    finally:
        if own:
            cn.close()


# ============================================================
# Read-only functions (existing)
# ============================================================

# ============================================================
# Reverse Night Audit (VB6 frmReNightAudit.frm:318-340)
# ============================================================

def reverse_night_audit(user: str = USER, cn=None,
                        commit: bool = True) -> dict:
    """VB6 reverse night audit: sirf Enviro.NCur -1 day.

    Evidence (frmReNightAudit.frm:331-336):
      If Format(NCur, 'dd/MMM') <> '01/Apr' Then
        Update Enviro Set NCur = DateAdd('D', -1, NCur) Where LogSite_Code=...
      Else 'Reverse Night Audit Not Go Beyond F/A Year..'
    PayCharge delete VB6 me NAHI hota - sirf business-date rollback.

    Returns {from_date, to_date}. Raises ValueError on FY-start guard."""
    rows = db.query(
        "SELECT [NCur] FROM Enviro WHERE LogSite_Code = ? OR "
        "LogSite_Code = 'HO'", (SITE_CODE,), cn=cn)
    if not rows:
        raise ValueError("Enviro NCur nahi mila")
    ncur = rows[0][0]
    if ncur is None:
        raise ValueError("Enviro NCur NULL hai (reverse possible nahi)")
    ncur_d = ncur.date() if isinstance(ncur, datetime.datetime) else ncur
    # VB6 guard: 01/Apr = FY start - usse pehle reverse nahi
    if ncur_d.month == 4 and ncur_d.day == 1:
        raise ValueError("Reverse Night Audit Not Go Beyond F/A Year..")
    new_d = ncur_d - datetime.timedelta(days=1)
    own = cn is None
    cn = cn or db.connect()
    try:
        db.execute(
            "UPDATE Enviro SET [NCur] = ?, U_Name = ?, "
            "U_EntDt = getdate(), U_AE = 'E' WHERE LogSite_Code = ?",
            (new_d, user, SITE_CODE), cn=cn, commit=False)
        if commit:
            cn.commit()
        return {"from_date": ncur_d, "to_date": new_d, "user": user}
    finally:
        if own:
            cn.close()


def na_log(cn=None, top: int = 100) -> list:
    rows = db.query(
        f"SELECT TOP {int(top)} Id, DateChngFrom, DateChngTo, "
        "StartNightAudit, EndNightAudit, U_Name, U_AE "
        "FROM NightAuditLog WHERE Site_Code = ? ORDER BY Id DESC",
        (SITE_CODE,), cn=cn)
    return [{"id": int(r.Id), "from": r.DateChngFrom, "to": r.DateChngTo,
             "start": r.StartNightAudit, "end": r.EndNightAudit,
             "user": r.U_Name or "", "ae": r.U_AE or ""} for r in rows]


def occupancy(cn=None, vprefix: str = VYEAR, top: int = 30) -> list:
    rooms = db.query(
        "SELECT COUNT(*) FROM RoomMast WHERE Site_Code = ?", (SITE_CODE,), cn=cn)[0][0]
    rows = db.query(
        f"SELECT TOP {int(top)} Vdate, COUNT(*) AS ChkIns "
        "FROM GuestFolio WHERE Site_Code = ? AND Vprefix = ? AND "
        "Vtype = 'CHK' GROUP BY Vdate ORDER BY Vdate DESC",
        (SITE_CODE, vprefix), cn=cn)
    total = rooms or 1
    return [{"date": r.Vdate, "checkins": r.ChkIns,
             "occ_pct": round((r.ChkIns or 0) * 100.0 / total, 1)}
            for r in rows]


def revenue_summary(cn=None, vprefix: str = VYEAR, top: int = 30) -> list:
    rows = db.query(
        f"SELECT TOP {int(top)} Vdate, "
        "SUM(AmtDr) AS Dr, SUM(AmtCr) AS Cr, COUNT(*) AS Lines "
        "FROM PayCharge WHERE Site_Code = ? AND VPrefix = ? "
        "GROUP BY Vdate ORDER BY Vdate DESC",
        (SITE_CODE, vprefix), cn=cn)
    return [{"date": r.Vdate, "dr": r.Dr or 0.0, "cr": r.Cr or 0.0,
             "lines": r.Lines or 0} for r in rows]


def room_revenue(cn=None, vprefix: str = VYEAR, top: int = 30) -> list:
    rows = db.query(
        f"SELECT TOP {int(top)} Vdate, SUM(AmtDr - AmtCr) AS RoomRev "
        "FROM PayCharge WHERE Site_Code = ? AND VPrefix = ? AND "
        "Vtype = 'RC' GROUP BY Vdate ORDER BY Vdate DESC",
        (SITE_CODE, vprefix), cn=cn)
    return [{"date": r.Vdate, "roomrev": r.RoomRev or 0.0} for r in rows]


def night_audit_rr(index: int, cn=None) -> dict | None:
    """VB6 NightAuditRR_Click logic ported to Python.

    Index mapping (VB6 evidence from HMS.bas:12FF954-12FF952):
      0  -> rFomRepView / DailyReport
      1  -> rFomRepView / DailyReport (Daily Report-II)
      2  -> rFomRepView / RevAnalysis
      3  -> rFomRepView / GuestTrialBalance
      4  -> rFomRepView / NightAuditReportI
      5  -> rFomRepView / OccAnalysis
      6  -> rFomRepView / MarketSegAnalysis
      7  -> rFomRepView / BusinessAnalysis
      8  -> rFomRepView / CompanyAnalysis
      9  -> rFomRepView / TravelAgentAnalysis
      &HA (10) -> rFomRepView / FOCC Report
      &HB (11) -> rFomRepView / FoodCost
      &HC (12) -> rFomRepView / FBCostStatement
      &HE (14) -> FaReports / AgingRepDr
      &HF (15) -> FaReports / AgingRepCr
    """

    reports_data = {
        0: ("rFomRepView", "DailyReport", "Daily Night Audit Report"),
        1: ("rFomRepView", "DailyReport", "Daily Report-II"),
        2: ("rFomRepView", "RevAnalysis", "Revenue Analysis"),
        3: ("rFomRepView", "GuestTrialBalance", "Guest Trial Balance"),
        4: ("rFomRepView", "NightAuditReportI", "Night Audit Report I"),
        5: ("rFomRepView", "OccAnalysis", "Occupancy Analysis"),
        6: ("rFomRepView", "MarketSegAnalysis", "Market Segment Analysis"),
        7: ("rFomRepView", "BusinessAnalysis", "Business Analysis"),
        8: ("rFomRepView", "CompanyAnalysis", "Company Analysis"),
        9: ("rFomRepView", "TravelAgentAnalysis", "Travel Agent Analysis"),
        10: ("rFomRepView", "FOCC Report", "FOCC Report (Front Office CC Analysis)"),
        11: ("rFomRepView", "FoodCost", "Food Cost Analysis"),
        12: ("rFomRepView", "FBCostStatement", "FBCost Statement"),
        13: ("rFomRepView", "GratuityReport", "Gratuity Report"),
        14: ("FaReports", "AgingRepDr", "Aging Report (Debtors)"),
        15: ("FaReports", "AgingRepCr", "Aging Report (Creditors)"),
        16: ("FaReports", "DetailedTrial", "Detailed Trial Balance"),
        17: ("FaReports", "DayBook", "Day Book"),
        18: ("FaReports", "BankBook", "Bank Book"),
        19: ("FaReports", "CashBook", "Cash Book"),
        20: ("FaReports", "JournalBook", "Journal Book"),
        21: ("FaReports", "LedCred", "Ledger (Creditors)"),
        22: ("FaReports", "LedDeb", "Ledger (Debtors)"),
        23: ("FaReports", "LedInt", "Ledger (Internal)"),
        24: ("FaReports", "GratuityReport", "Gratuity Report"),
        25: ("FaReports", "PFStatement", "PF Statement"),
        26: ("FaReports", "LoanAdvSumm", "Loan Advance Summary"),
        27: ("FaReports", "LoanReg", "Loan Register"),
        28: ("FaReports", "LoanLedg", "Loan Ledger"),
        29: ("FaReports", "PayrollReg", "Payroll Register"),
        30: ("FaReports", "PaySlip", "Pay Slip"),
        31: ("FaReports", "AcCheckList", "Account Check List"),
    }

    entry = reports_data.get(index)
    if not entry:
        return {
            "action": "night_audit_rr_unknown",
            "index": index,
            "message": f"NightAuditRR index {index} not in mapping (0-31)",
        }

    form, report_name, description = entry
    return {
        "action": report_name.lower(),
        "form": form,
        "report_name": report_name,
        "description": description,
        "index": index,
    }


# --------------------------------------------------------------------------
# POS Revenue Aggregation (idempotent posting)
# --------------------------------------------------------------------------

def aggregate_pos_revenue(date_from, date_to, cn=None) -> list[dict]:
    """Aggregate POS revenue by RestCode + RevCode for a date window."""
    rows = db.query(
        "SELECT RestCode, RevCode, SUM(NetAmt) AS TotalNet, "
        "SUM(Tax) AS TotalTax, COUNT(*) AS FolioCount "
        "FROM PayCharge WHERE Vdate BETWEEN ? AND ? "
        "AND Vtype = 'PPOS' GROUP BY RestCode, RevCode "
        "ORDER BY RestCode, RevCode",
        (date_from, date_to), cn=cn)
    return [{"restcode": r.RestCode or "", "revcode": r.RevCode or "",
             "total_net": float(r.TotalNet or 0), "total_tax": float(r.TotalTax or 0),
             "folio_count": int(r.FolioCount or 0)} for r in rows]


def is_already_posted(date_from, date_to, restcode, revcode, cn=None) -> bool:
    """Check if POS revenue already posted for this date/outlet/revenue combo."""
    rows = db.query(
        "SELECT 1 FROM PayCharge WHERE Vdate BETWEEN ? AND ? "
        "AND RestCode = ? AND RevCode = ? AND Vtype = 'PPOS' "
        "AND ContraDocId LIKE 'NA_%'",
        (date_from, date_to, restcode, revcode), cn=cn)
    return bool(rows)


def post_pos_revenue(date_from, date_to, user=USER, cn=None) -> int:
    """Idempotent POS revenue posting. Skips already-posted combos.
    Returns count of new records posted."""
    posted = 0
    aggregates = aggregate_pos_revenue(date_from, date_to, cn)
    own = cn is None
    cn = cn or db.connect()
    try:
        for agg in aggregates:
            if is_already_posted(date_from, date_to, agg["restcode"], agg["revcode"], cn):
                continue
            contra_docid = f"NA_{agg['restcode']}_{agg['revcode']}_{date_from}"
            db.execute(
                "INSERT INTO PayCharge (DocId, Vtype, Vdate, RestCode, RevCode, "
                "AmtDr, AmtCr, Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
                "VALUES (?, 'PPOS', ?, ?, ?, ?, 0, ?, ?, getdate(), 'A', ?)",
                (contra_docid, date_to, agg["restcode"], agg["revcode"],
                 agg["total_net"], SITE_CODE, user, SITE_CODE),
                cn=cn, commit=False)
            posted += 1
        if posted:
            cn.commit()
        return posted
    except Exception:
        if own:
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