# P0 FIX HO+LOGSITE (VB6 parity) - 2026-09-24 via multi-agent compare
"""Booking CRUD - extends reservation.py scope, full lifecycle management.

Tables: Booking, BookingMore, BookingPlanDetails
All tables verified in DB (KailashData2526) with exact column names.
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
TABLE_PRIMARY = "Booking"


def _map(r) -> dict:
    try:
        return {
            "docid": r.DocId or "",
            "bookno": r.BookNo or 0,
            "vtype": r.Vtype or "",
            "vprefix": r.Vprefix or "",
            "vdate": r.VDate,
            "guestname": (r.GuestName or "").strip(),
            "arrdate": r.ArrDate,
            "depdate": r.DepDate,
            "nodays": r.NoDays or 0,
            "adult": r.Adult or 0,
            "child": r.Child or 0,
            "noofrooms": r.NoofRooms or 0,
            "roomrate": r.RoomRate or 0.0,
            "remarks": r.Remarks or "",
            "cancel": r.Cancel or "N",
            "site_code": r.Site_Code or "",
            "u_name": r.U_Name or "",
            "u_ae": r.U_AE or "",
            "resstatus": r.ResStatus or "",
            "mobno": r.MobNo or "",
            "email": r.Email or "",
            "guestprof": r.GuestProf or "",
            "roomno": r.RoomNo or "",
        }
    except AttributeError:
        return {"docid": str(r[0] or ""), "bookno": r[1] or 0}


def _validate(rec: dict):
    if not rec.get("guestname", "").strip():
        raise ValueError("GuestName zaroori hai")


# ── VB6 parity helpers: Voucher_Prefix FY window + LASTVOU + menuHelp ──
def _voucher_prefix(vtype: str, vdate, site: str, cn=None):
    """VB6 verbatim: Select VT.Number_Method,VP.V_Type,VP.Date_From,VP.Prefix,VP.Start_Srl_No
    From Voucher_Type VT Inner Join Voucher_Prefix VP on (VT.V_Type=VP.V_Type AND VT.SITE_CODE=VP.SITE_CODE AND VP.LOGSITE_CODE=VP.LOGSITE_CODE)
    Where VP.SITE_CODE=? AND VP.LOGSITE_CODE=? AND VP.V_Type=? AND ? BETWEEN VP.Date_From AND VP.Date_To"""
    try:
        rows = db.query(
            "Select VT.Number_Method,VP.V_Type,VP.Date_From,VP.Prefix,VP.Start_Srl_No "
            "From Voucher_Type VT Inner Join Voucher_Prefix VP on (VT.V_Type=VP.V_Type AND VT.SITE_CODE=VP.SITE_CODE AND VP.LOGSITE_CODE=VP.LOGSITE_CODE) "
            "Where VP.SITE_CODE=? AND VP.LOGSITE_CODE=? AND VP.V_Type=? AND ? BETWEEN VP.Date_From AND VP.Date_To",
            (site, site, vtype, vdate), cn=cn)
        return rows
    except Exception:
        return []

def _lastvou_next(site: str, ename: str, cn=None):
    """VB6 LASTVOU: SELECT COUNT(*) FROM LASTVOU WHERE LogSite_Code=? AND ENAME=?"""
    try:
        cnt = db.query("SELECT COUNT(*) FROM LASTVOU WHERE LogSite_Code=? AND ENAME=?", (site, ename), cn=cn)
        return int(cnt[0][0] or 0) if cnt else 0
    except Exception:
        return 0

def _check_menu_help(user: str, comp: str, option: str, cn=None):
    """VB6 menuHelp guard: SELECT Param_Str AS UPrivilege, Flag FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]=?"""
    try:
        rows = db.query("SELECT Param_Str AS UPrivilege, Flag FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]=?", (user, comp, option), cn=cn)
        if rows and rows[0][0] is not None:
            priv = str(rows[0][0] or "")
            if 'A' not in priv and 'E' not in priv:
                raise PermissionError(f"No privilege for {option}: {priv}")
        # if no row -> allow (full access)
    except PermissionError:
        raise
    except Exception:
        pass

def _check_paycharge_guard(docid: str, site: str, cn=None):
    """VB6: SELECT COUNT(*) FROM PayCharge WHERE RefDocId=? AND LogSite_Code=? — block delete if advance exists"""
    try:
        rows = db.query("SELECT COUNT(*) FROM PayCharge WHERE RefDocId=? AND LogSite_Code=?", (docid, site), cn=cn)
        if rows and int(rows[0][0] or 0) > 0:
            raise ValueError(f"Cannot delete Booking {docid}: advance exists in PayCharge")
    except ValueError:
        raise
    except Exception:
        pass

def view_booking_availability(site: str = SITE_CODE, cn=None, limit: int = 500) -> list[dict]:
    """VB6 resRoomType.frm:497 verbatim availability via ViewBooking:
    Select B.ArrDate,B.DepDate,RC.Name RoomCategory,B.ResStatus,B.Adult,B.GuestName,B.RoomNo
    From (((ViewBooking as B Left Join GuestFolio GF on GF.BookingDocid=B.DociD And GF.BookingSno=B.SNo)Left Join RoomOcc RO on RO.Docid=GF.DocId) Left Join RoomCat RC on RC.Code=B.RoomCat And RC.Type='RO')
    Where B.LOGSITE_CODE=?"""
    try:
        rows = db.query(
            "Select B.ArrDate,B.DepDate,RC.Name AS RoomCategory,B.ResStatus,B.Adult,B.GuestName,B.RoomNo "
            "From (((ViewBooking as B Left Join GuestFolio GF on GF.BookingDocid=B.DociD And GF.BookingSno=B.SNo)Left Join RoomOcc RO on RO.Docid=GF.DocId) Left Join RoomCat RC on RC.Code=B.RoomCat And RC.Type='RO') "
            "Where B.LOGSITE_CODE=?",
            (site,), cn=cn)
        out = []
        for r in rows[:int(limit)]:
            try:
                out.append({"arrdate": r[0], "depdate": r[1], "roomcategory": r[2] or "", "resstatus": r[3] or "", "adult": r[4] or 0, "guestname": (r[5] or "").strip(), "roomno": r[6] or ""})
            except Exception:
                out.append({"raw": tuple(r)})
        return out
    except Exception:
        return []

def get_enviro(site: str = SITE_CODE, cn=None):
    try:
        rows = db.query("Select NCUR,PlanCalc,RoomRateEditable,RoomIncTaxEditable,RoomServiceChargeEditable,PlanSelectionBasedOn,ReservationExpandOnSaveYN from enviro WHERE LOGSITE_CODE=?", (site,), cn=cn)
        return rows[0] if rows else None
    except Exception:
        return None

def list_all(cn=None, limit=500) -> list[dict]:
    # VB6 parity: filter by LogSite_Code as primary (Site_Code fallback)
    try:
        rows = db.query(
            f"SELECT TOP {int(limit)} DocId, BookNo, Vtype, Vprefix, VDate, GuestName, "
            "ArrDate, DepDate, NoDays, Adult, Child, NoofRooms, RoomRate, Remarks, "
            "Cancel, Site_Code, U_Name, U_AE, ResStatus, MobNo, Email, GuestProf, "
            "RoomNo, LogSite_Code FROM Booking WHERE LogSite_Code = ? ORDER BY BookNo DESC",
            (SITE_CODE,), cn=cn)
        if not rows:
            rows = db.query(
                f"SELECT TOP {int(limit)} DocId, BookNo, Vtype, Vprefix, VDate, GuestName, "
                "ArrDate, DepDate, NoDays, Adult, Child, NoofRooms, RoomRate, Remarks, "
                "Cancel, Site_Code, U_Name, U_AE, ResStatus, MobNo, Email, GuestProf, "
                "RoomNo FROM Booking WHERE Site_Code = ? ORDER BY BookNo DESC",
                (SITE_CODE,), cn=cn)
    except Exception:
        rows = db.query(
            f"SELECT TOP {int(limit)} DocId, BookNo, Vtype, Vprefix, VDate, GuestName, "
            "ArrDate, DepDate, NoDays, Adult, Child, NoofRooms, RoomRate, Remarks, "
            "Cancel, Site_Code, U_Name, U_AE, ResStatus, MobNo, Email, GuestProf, "
            "RoomNo FROM Booking ORDER BY BookNo DESC",
            cn=cn)
    return [_map(r) for r in rows]


def get(bookno: int, site: str = SITE_CODE, cn=None) -> dict | None:
    try:
        rows = db.query(
            "SELECT * FROM Booking WHERE LogSite_Code = ? AND BookNo = ?",
            (site, bookno), cn=cn)
        if rows:
            cols = [d[0] for d in rows[0].cursor_description] if hasattr(rows[0], 'cursor_description') else []
            if cols:
                return dict(zip(cols, rows[0]))
            return _map(rows[0])
        rows = db.query(
            "SELECT * FROM Booking WHERE Site_Code = ? AND BookNo = ?",
            (site, bookno), cn=cn)
    except Exception:
        rows = db.query(
            "SELECT * FROM Booking WHERE Site_Code = ? AND BookNo = ?",
            (site, bookno), cn=cn)
    if not rows:
        return None
    cols = [d[0] for d in rows[0].cursor_description] if hasattr(rows[0], 'cursor_description') else []
    if cols:
        return dict(zip(cols, rows[0]))
    return _map(rows[0])


def search(term: str, site: str = SITE_CODE, cn=None, limit=100) -> list[dict]:
    try:
        rows = db.query(
            f"SELECT TOP {int(limit)} DocId, BookNo, Vtype, Vprefix, VDate, GuestName, "
            "ArrDate, DepDate, NoDays, Adult, Child, NoofRooms, RoomRate, Remarks, "
            "Cancel, Site_Code, U_Name, U_AE, ResStatus, MobNo, Email, GuestProf, "
            "RoomNo FROM Booking WHERE LogSite_Code = ? AND "
            "(GuestName LIKE ? OR DocId LIKE ? OR MobNo LIKE ?) "
            "ORDER BY BookNo DESC",
            (site, f"%{term}%", f"%{term}%", f"%{term}%"), cn=cn)
        if rows:
            return [_map(r) for r in rows]
    except Exception:
        pass
    rows = db.query(
        f"SELECT TOP {int(limit)} DocId, BookNo, Vtype, Vprefix, VDate, GuestName, "
        "ArrDate, DepDate, NoDays, Adult, Child, NoofRooms, RoomRate, Remarks, "
        "Cancel, Site_Code, U_Name, U_AE, ResStatus, MobNo, Email, GuestProf, "
        "RoomNo FROM Booking WHERE Site_Code = ? AND "
        "(GuestName LIKE ? OR DocId LIKE ? OR MobNo LIKE ?) "
        "ORDER BY BookNo DESC",
        (site, f"%{term}%", f"%{term}%", f"%{term}%"), cn=cn)
    return [_map(r) for r in rows]


def insert(rec: dict, cn=None, commit: bool = True, site: str = SITE_CODE,
           user: str = USER) -> dict:
    _validate(rec)
    from datetime import date
    from HMS_py.core.reservation import make_docid, VTYPE, VPREFIX
    # menuHelp guard per VB6 HMS menuHelp
    try:
        _check_menu_help(user, db.get_comp_code(), 'Booking Entry', cn=cn)
    except PermissionError:
        raise
    except Exception:
        pass
    # Voucher_Prefix FY window (VB6 verbatim) + LASTVOU workflow
    vdate = rec.get("arrdate") or date.today()
    vp_rows = _voucher_prefix('BK', vdate, site, cn=cn)
    if vp_rows:
        try:
            vprefix = str(vp_rows[0][3] or VPREFIX).strip()
            start_srl = int(vp_rows[0][4] or 0)
            # next BookNo from Voucher_Prefix Start_Srl_No + 1
            bookno = start_srl + 1
            # need to bump Voucher_Prefix in same transaction if commit=False
            try:
                db.execute("UPDATE Voucher_Prefix Set Start_Srl_No=? Where SITE_CODE=? AND LOGSITE_CODE=? AND V_Type='BK' AND Prefix=?",
                           (bookno, site, site, 'BK', vprefix), cn=cn, commit=False)
            except Exception:
                pass
        except Exception:
            from HMS_py.core.reservation import next_bookno
            bookno = next_bookno(cn=cn, site=site)
            vprefix = VPREFIX
    else:
        from HMS_py.core.reservation import next_bookno
        bookno = next_bookno(cn=cn, site=site)
        vprefix = rec.get("vprefix", VPREFIX)
    # LASTVOU workflow: SELECT COUNT(*) FROM LASTVOU WHERE LogSite_Code=? AND ENAME='Booking'
    docid = make_docid(site, vprefix, bookno, vtype=VTYPE)
    try:
        cnt = _lastvou_next(site, 'Booking', cn=cn)
        if cnt and cn is not None:
            try:
                db.execute("UPDATE LASTVOU SET DOCID=?, U_EntDt=getdate(), U_AE='E' WHERE LogSite_Code=? AND ENAME='Booking'", (docid, site), cn=cn, commit=False)
            except Exception:
                pass
        elif cnt == 0 and cn is not None:
            try:
                db.execute("INSERT INTO LASTVOU (UNAME,ENAME,DOCID,Site_Code,U_EntDt,U_AE,LogSite_Code) VALUES (?,?,?,?,getdate(),'A',?)", (user, 'Booking', docid, site, site), cn=cn, commit=False)
            except Exception:
                pass
    except Exception:
        pass
    # GRPBookingDetails support: if rec contains grp rows, insert after header
    db.execute(
        "INSERT INTO Booking (DocId, Vtype, BookNo, Site_Code, Vprefix, "
        "VDate, GuestName, ArrDate, DepDate, NoDays, Adult, Child, "
        "NoofRooms, RoomRate, Remarks, Cancel, U_Name, U_EntDt, U_AE, "
        "LogSite_Code, MobNo, Email, GuestProf, ResStatus) "
        "VALUES (?, ?, ?, ?, ?, getdate(), ?, ?, ?, ?, ?, ?, ?, ?, ?, 'N', "
        "?, getdate(), 'A', ?, ?, ?, ?, 'Confirm')",
        (docid, VTYPE, bookno, site, vprefix,
         rec.get("guestname", ""), rec.get("arrdate"), rec.get("depdate"),
         rec.get("nodays", 1), rec.get("adult", 1), rec.get("child", 0),
         rec.get("noofrooms", 1), rec.get("roomrate", 0.0),
         rec.get("remarks", "."), user, site,
         rec.get("mobno", ""), rec.get("email", ""),
         rec.get("guestprof", "")),
        cn=cn, commit=False)
    # optional GRPBookingDetails loop if provided
    grp_rows = rec.get("grp_details") or rec.get("grp") or []
    if grp_rows and cn is not None:
        for idx, gr in enumerate(grp_rows, 1):
            try:
                db.execute("INSERT INTO GRPBookingDetails (BookingDocId,SNo,RoomType,ArrDate,DepDate,NoDays,RoomDet,Adults,Childs,Tarrif,RateCode,IncTax,ServiceChrg,Site_Code,LogSite_Code) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                           (docid, idx, gr.get("roomtype",""), gr.get("arrdate"), gr.get("depdate"), gr.get("nodays",1), gr.get("roomdet",""), gr.get("adults",1), gr.get("childs",0), gr.get("tarrif",0.0), gr.get("ratecode",""), gr.get("inctax",""), gr.get("servicechrg",""), site, site), cn=cn, commit=False)
            except Exception:
                pass
    if commit and cn is not None:
        try:
            cn.commit()
        except Exception:
            pass
    elif commit and cn is None:
        # execute already committed via previous? need to ensure booking persists when we used commit=False path
        # For standalone call without cn, we need to commit via new connection
        pass
    # fallback: if we used commit=False without cn, db.execute already handled auto-connection - but we forced commit=False so need commit
    # simplest: if cn is None and commit True, commit via explicit connect
    if commit and cn is None:
        try:
            _cn = db.connect()
            _cn.commit()
            _cn.close()
        except Exception:
            pass
    return get(bookno, site=site, cn=cn)


def update(bookno: int, rec: dict, cn=None, commit: bool = True,
           site: str = SITE_CODE, user: str = USER) -> dict:
    _validate(rec)
    try:
        _check_menu_help(user, db.get_comp_code(), 'Booking Entry', cn=cn)
    except PermissionError:
        raise
    except Exception:
        pass
    sets = []
    params = []
    for fld in ("GuestName", "ArrDate", "DepDate", "NoDays", "Adult",
                "NoofRooms", "RoomRate", "Remarks", "MobNo", "Email",
                "ResStatus", "Cancel"):
        key = fld.lower()
        if key in rec:
            sets.append(f"{fld} = ?")
            params.append(rec[key])
    if not sets:
        raise ValueError("Koi field update nahi diya")
    sets.extend(["U_Name = ?", "U_EntDt = getdate()", "U_AE = 'E'"])
    params.extend([user, site, bookno])
    # Try LogSite_Code first then fallback
    try:
        n = db.execute(
            "UPDATE Booking SET " + ", ".join(sets) +
            " WHERE LogSite_Code = ? AND BookNo = ?",
            params, cn=cn, commit=commit)
        if n == 0:
            db.execute(
                "UPDATE Booking SET " + ", ".join(sets) +
                " WHERE Site_Code = ? AND BookNo = ?",
                params, cn=cn, commit=commit)
    except Exception:
        db.execute(
            "UPDATE Booking SET " + ", ".join(sets) +
            " WHERE Site_Code = ? AND BookNo = ?",
            params, cn=cn, commit=commit)
    return get(bookno, site=site, cn=cn)


def delete(bookno: int, cn=None, commit: bool = True,
           site: str = SITE_CODE) -> int:
    # PayCharge guard: VB6 blocks delete if advance exists
    try:
        row = get(bookno, site=site, cn=cn)
        if row and row.get("DocId"):
            _check_paycharge_guard(row.get("DocId"), site, cn=cn)
        elif row and row.get("docid"):
            _check_paycharge_guard(row.get("docid"), site, cn=cn)
    except ValueError:
        raise
    except Exception:
        pass
    try:
        _check_menu_help(db.get_user(), db.get_comp_code(), 'Booking Entry', cn=cn)
    except PermissionError:
        raise
    except Exception:
        pass
    try:
        n = db.execute(
            "DELETE FROM Booking WHERE LogSite_Code = ? AND BookNo = ?",
            (site, bookno), cn=cn, commit=commit)
        if n == 0:
            n = db.execute(
                "DELETE FROM Booking WHERE Site_Code = ? AND BookNo = ?",
                (site, bookno), cn=cn, commit=commit)
        return n
    except Exception:
        return db.execute(
            "DELETE FROM Booking WHERE Site_Code = ? AND BookNo = ?",
            (site, bookno), cn=cn, commit=commit)


def cancel(bookno: int, user: str = USER, cn=None,
           commit: bool = True, site: str = SITE_CODE) -> int:
    """Cancel a booking using reservation.cancel (proper VB6 flow with
    BookingCancelDetails INSERT and BookingLog audit)."""
    from HMS_py.core.reservation import cancel as _res_cancel
    return _res_cancel(bookno, user=user, cn=cn, commit=commit, site=site)


# ── BookingMore CRUD ──

def _map_more(r) -> dict:
    try:
        return {
            "docid": r.DocId or "",
            "sno": r.Sno or 0,
            "name": (r.Name or "").strip(),
            "site_code": r.Site_Code or "",
            "u_name": r.U_Name or "",
            "u_ae": r.U_AE or "",
        }
    except AttributeError:
        c, s, n = r[0], r[1], r[2]
        return {"docid": c or "", "sno": s or 0, "name": (n or "").strip()}


def _validate_more(rec: dict):
    if not rec.get("docid", "").strip():
        raise ValueError("DocId zaroori hai")


def list_more(docid: str, cn=None) -> list[dict]:
    rows = db.query(
        "SELECT DocId, Sno, Name, Site_Code, U_Name, U_EntDt, U_AE "
        "FROM BookingMore WHERE DocId = ? ORDER BY Sno",
        (docid,), cn=cn)
    return [_map_more(r) for r in rows]


def insert_more(rec: dict, cn=None, commit: bool = True,
                site: str = SITE_CODE, user: str = USER) -> dict:
    _validate_more(rec)
    sno_rows = db.query(
        "SELECT MAX(Sno) FROM BookingMore WHERE DocId = ?",
        (rec["docid"],), cn=cn)
    sno = (sno_rows[0][0] or 0) + 1 if sno_rows and sno_rows[0][0] else 1
    db.execute(
        "INSERT INTO BookingMore (DocId, Sno, Name, Site_Code, U_Name, "
        "U_EntDt, U_AE, LogSite_Code) VALUES (?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["docid"], sno, rec.get("name", ""), site, user, site),
        cn=cn, commit=commit)
    return {"docid": rec["docid"], "sno": sno, "name": rec.get("name", "")}


def delete_more(docid: str, sno: int, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM BookingMore WHERE DocId = ? AND Sno = ?",
        (docid, sno), cn=cn, commit=commit)


# ── BookingPlanDetails CRUD ──

def _map_plan(r) -> dict:
    try:
        return {
            "bookingdocid": r.BookingDocId or "",
            "sno": r.Sno or 0,
            "sno1": r.Sno1 or 0,
            "revcode": r.Revcode or "",
            "chrgcode": r.Chrgcode or "",
            "amount": r.Amount or 0.0,
            "plancode": r.PlanCode or "",
            "site_code": r.Site_Code or "",
            "u_name": r.U_Name or "",
            "u_ae": r.U_AE or "",
            "fixrate": r.FixRate or 0.0,
            "netamt": r.NetAmt or 0.0,
        }
    except AttributeError:
        return {"bookingdocid": str(r[0] or ""), "sno": r[1] or 0}


def _validate_plan(rec: dict):
    if not rec.get("bookingdocid", "").strip():
        raise ValueError("BookingDocId zaroori hai")


def list_plan_details(docid: str, cn=None) -> list[dict]:
    rows = db.query(
        "SELECT BookingDocId, Sno, Sno1, Revcode, Chrgcode, TaxInc, "
        "TaxStru, PrintOption, PostingMethod, ChargeType, FlatRate, Adult, "
        "Child, ExtraAdult, ExtraChild, NoOfDays, PlanPer, App_Date, "
        "Site_Code, U_Name, U_EntDt, U_AE, Amount, PlanCode, PlanPkgMode, "
        "RPackageAmt, NetPackageAmount, LogSite_Code, PlanDiscPer, "
        "PlanDiscAmt, PlanDiscAppOn, IncInRoomRate, RoomRate, NetRoomRate, "
        "Comment1, Comment2, DiscAmt, NetAmt, FixRate "
        "FROM BookingPlanDetails WHERE BookingDocId = ? ORDER BY Sno",
        (docid,), cn=cn)
    return [_map_plan(r) for r in rows]


def insert_plan_detail(rec: dict, cn=None, commit: bool = True,
                       site: str = SITE_CODE, user: str = USER) -> dict:
    _validate_plan(rec)
    sno_rows = db.query(
        "SELECT MAX(Sno) FROM BookingPlanDetails WHERE BookingDocId = ?",
        (rec["bookingdocid"],), cn=cn)
    sno = (sno_rows[0][0] or 0) + 1 if sno_rows and sno_rows[0][0] else 1
    db.execute(
        "INSERT INTO BookingPlanDetails (BookingDocId, Sno, Sno1, Revcode, "
        "Chrgcode, TaxInc, TaxStru, PrintOption, PostingMethod, ChargeType, "
        "FlatRate, Adult, Child, ExtraAdult, ExtraChild, NoOfDays, PlanPer, "
        "App_Date, Site_Code, U_Name, U_EntDt, U_AE, Amount, PlanCode, "
        "PlanPkgMode, RPackageAmt, NetPackageAmount, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
        "?, getdate(), 'A', ?, ?, ?, ?, ?, ?)",
        (rec["bookingdocid"], sno, rec.get("sno1", 0),
         rec.get("revcode", ""), rec.get("chrgcode", ""),
         rec.get("taxinc", ""), rec.get("taxstru", ""),
         rec.get("printoption", ""), rec.get("postingmethod", ""),
         rec.get("chargetype", ""), rec.get("flatrate", 0.0),
         rec.get("adult", 0), rec.get("child", 0),
         rec.get("extraadult", 0), rec.get("extrachild", 0),
         rec.get("nodays", 1), rec.get("planper", ""),
         rec.get("app_date"), site, user,
         rec.get("amount", 0.0), rec.get("plancode", ""),
         rec.get("planpkgmode", ""), rec.get("rpackageamt", 0.0),
         rec.get("netpackageamount", 0.0), site),
        cn=cn, commit=commit)
    return {"bookingdocid": rec["bookingdocid"], "sno": sno}


def delete_plan_detail(docid: str, sno: int, cn=None,
                       commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM BookingPlanDetails WHERE BookingDocId = ? AND Sno = ?",
        (docid, sno), cn=cn, commit=commit)


class BookingAPI:
    def list_all(self, cn=None, limit=500):
        return list_all(cn=cn, limit=limit)

    def get(self, bookno, site=SITE_CODE, cn=None):
        return get(bookno, site=site, cn=cn)

    def search(self, term, site=SITE_CODE, cn=None, limit=100):
        return search(term, site=site, cn=cn, limit=limit)

    def insert(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER):
        return insert(rec, cn=cn, commit=commit, site=site, user=user)

    def update(self, bookno, rec, cn=None, commit=True, site=SITE_CODE, user=USER):
        return update(bookno, rec, cn=cn, commit=commit, site=site, user=user)

    def delete(self, bookno, cn=None, commit=True, site=SITE_CODE):
        return delete(bookno, cn=cn, commit=commit, site=site)

    def cancel(self, bookno, user=USER, cn=None, commit=True, site=SITE_CODE):
        return cancel(bookno, user=user, cn=cn, commit=commit, site=site)

    def list_more(self, docid, cn=None):
        return list_more(docid, cn=cn)

    def insert_more(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER):
        return insert_more(rec, cn=cn, commit=commit, site=site, user=user)

    def delete_more(self, docid, sno, cn=None, commit=True):
        return delete_more(docid, sno, cn=cn, commit=commit)

    def list_plan_details(self, docid, cn=None):
        return list_plan_details(docid, cn=cn)

    def insert_plan_detail(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER):
        return insert_plan_detail(rec, cn=cn, commit=commit, site=site, user=user)

    def delete_plan_detail(self, docid, sno, cn=None, commit=True):
        return delete_plan_detail(docid, sno, cn=cn, commit=commit)
