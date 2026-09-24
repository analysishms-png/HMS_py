# P0 FIX HO+LOGSITE (VB6 parity) - 2026-09-24 via multi-agent compare
"""Room Occupancy tracking - RoomOcc CRUD.

Table: RoomOcc (verified in DB - 42 columns)
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
TABLE_PRIMARY = "RoomOcc"

SELECT_COLS = (
    "DocId, SNo, FolioNo, Vtype, Site_Code, Vprefix, GuestProf, RoomCat, "
    "RoomType, RoomNo, RateCode, RoomRate, ChkInDate, ChkInTime, Adult, "
    "Children, DepDate, DepTime, ChkOutDate, ChkOutTime, Type, U_Name, "
    "U_EntDt, U_AE, UserchkoutDate, ChkoutUser, NewRoomNo, Reason, "
    "PlanCode, PlanAmt, IncInRate, LogSite_Code, PlanDisc, PlanDiscAmt, "
    "PlanDiscAppon, RRTaxInc, RRServiceChrg, ChngDate, ExtraBed, "
    "RoomTarrif, RoomTaxStru, RackRate"
)


def _map(r) -> dict:
    try:
        return {
            "docid": r.DocId or "",
            "sno": r.SNo or 0,
            "folio": r.FolioNo or 0,
            "vtype": r.Vtype or "",
            "site_code": r.Site_Code or "",
            "vprefix": r.Vprefix or "",
            "guestprof": r.GuestProf or "",
            "roomcat": r.RoomCat or "",
            "roomtype": r.RoomType or "",
            "roomno": r.RoomNo or "",
            "ratecode": r.RateCode or "",
            "roomrate": r.RoomRate or 0.0,
            "chkindate": r.ChkInDate,
            "chkinime": r.ChkInTime or "",
            "adult": r.Adult or 0,
            "children": r.Children or 0,
            "depdate": r.DepDate,
            "deptime": r.DepTime or "",
            "chkoutdate": r.ChkOutDate,
            "chkouttime": r.ChkOutTime or "",
            "u_name": r.U_Name or "",
            "u_ae": r.U_AE or "",
            "reason": r.Reason or "",
            "plancode": r.PlanCode or "",
            "extrabed": r.ExtraBed or "",
            "rackrate": r.RackRate or 0.0,
        }
    except AttributeError:
        docid, sno = r[0], r[1]
        return {"docid": docid or "", "sno": sno or 0, "roomno": str(r[9] or "")}


def _validate(rec: dict):
    if not rec.get("roomno", "").strip():
        raise ValueError("RoomNo zaroori hai")


def list_all(cn=None, limit=500) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} {SELECT_COLS} FROM RoomOcc "
        "WHERE Site_Code = ? AND (LogSite_Code = ? OR LogSite_Code = 'HO' OR ISNULL(LogSite_Code,'')='') AND ChkOutDate IS NULL "
        "ORDER BY RoomNo",
        (SITE_CODE, SITE_CODE), cn=cn)
    return [_map(r) for r in rows]


def get_by_docid(docid: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM RoomOcc WHERE DocId = ?",
        (docid,), cn=cn)
    return _map(rows[0]) if rows else None


def get_by_room(roomno: str, site: str = SITE_CODE,
                cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM RoomOcc WHERE RTRIM(RoomNo) = ? AND "
        "ChkOutDate IS NULL AND Site_Code = ? AND (LogSite_Code = ? OR LogSite_Code = 'HO' OR ISNULL(LogSite_Code,'')='')",
        (roomno, site, site), cn=cn)
    return _map(rows[0]) if rows else None


def list_occupied(site: str = SITE_CODE, cn=None,
                  limit=500) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} {SELECT_COLS} FROM RoomOcc "
        "WHERE Site_Code = ? AND (LogSite_Code = ? OR LogSite_Code = 'HO' OR ISNULL(LogSite_Code,'')='') AND ChkOutDate IS NULL "
        "ORDER BY RoomNo",
        (site, site), cn=cn)
    return [_map(r) for r in rows]


def search(term: str, site: str = SITE_CODE, cn=None,
           limit=100) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} {SELECT_COLS} FROM RoomOcc "
        "WHERE Site_Code = ? AND (LogSite_Code = ? OR LogSite_Code = 'HO' OR ISNULL(LogSite_Code,'')='') AND (RoomNo LIKE ? OR GuestProf LIKE ? OR "
        "DocId LIKE ?) ORDER BY RoomNo",
        (site, site, f"%{term}%", f"%{term}%", f"%{term}%"), cn=cn)
    return [_map(r) for r in rows]


def insert(rec: dict, cn=None, commit: bool = True,
           site: str = SITE_CODE, user: str = USER) -> dict:
    _validate(rec)
    sno_rows = db.query(
        "SELECT MAX(SNo) FROM RoomOcc WHERE DocId = ?",
        (rec.get("docid", ""),), cn=cn)
    sno = (sno_rows[0][0] or 0) + 1 if sno_rows and sno_rows[0][0] else 1
    db.execute(
        "INSERT INTO RoomOcc (DocId, SNo, FolioNo, Vtype, Site_Code, "
        "Vprefix, GuestProf, RoomCat, RoomType, RoomNo, RateCode, "
        "RoomRate, ChkInDate, ChkInTime, Adult, Children, DepDate, "
        "DepTime, ChkOutDate, ChkOutTime, Type, U_Name, U_EntDt, U_AE, "
        "LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
        "NULL, NULL, 'I', ?, getdate(), 'A', ?)",
        (rec.get("docid", ""), sno, rec.get("folio", 0),
         rec.get("vtype", "CHK"), site, rec.get("vprefix", "2026"),
         rec.get("guestprof", ""), rec.get("roomcat", ""),
         rec.get("roomtype", ""), rec.get("roomno", ""),
         rec.get("ratecode", ""), rec.get("roomrate", 0.0),
         rec.get("chkindate"), rec.get("chkinime", "10:00"),
         rec.get("adult", 1), rec.get("children", 0),
         rec.get("depdate"), rec.get("deptime", "10:00"),
         user, site),
        cn=cn, commit=commit)
    return get_by_docid(rec.get("docid", ""), cn=cn)


def checkout(docid: str, user: str = USER, cn=None,
             commit: bool = True, site: str = SITE_CODE) -> dict:
    from datetime import datetime
    db.execute(
        "UPDATE RoomOcc SET ChkOutDate = ?, ChkOutTime = ?, "
        "Type = 'O', U_Name = ?, U_EntDt = getdate(), U_AE = 'E', "
        "UserchkoutDate = getdate(), ChkoutUser = ? "
        "WHERE DocId = ? AND (LogSite_Code = ? OR LogSite_Code = 'HO' OR ISNULL(LogSite_Code,'')='')",
        (datetime.now().date(), datetime.now().strftime("%H:%M"),
         user, user, docid, site), cn=cn, commit=commit)
    return get_by_docid(docid, cn=cn)


def update(docid: str, sno: int, rec: dict, cn=None, commit: bool = True,
           site: str = SITE_CODE, user: str = USER) -> dict:
    sets = []
    params = []
    for fld in ("RoomNo", "RoomCat", "RoomType", "RoomRate", "RateCode",
                "Adult", "Children", "DepDate", "DepTime", "GuestProf",
                "PlanCode", "ExtraBed", "Reason"):
        key = fld.lower()
        if key in rec:
            sets.append(f"{fld} = ?")
            params.append(rec[key])
    if not sets:
        raise ValueError("Koi field update nahi diya")
    sets.extend(["U_Name = ?", "U_EntDt = getdate()", "U_AE = 'E'"])
    params.extend([user, docid, sno])
    db.execute(
        "UPDATE RoomOcc SET " + ", ".join(sets) +
        " WHERE DocId = ? AND SNo = ?",
        params, cn=cn, commit=commit)
    return get_by_docid(docid, cn=cn)


def delete(docid: str, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM RoomOcc WHERE DocId = ?", (docid,), cn=cn, commit=commit)


class RoomOccAPI:
    def list_all(self, cn=None, limit=500):
        return list_all(cn=cn, limit=limit)

    def get_by_docid(self, docid, cn=None):
        return get_by_docid(docid, cn=cn)

    def get_by_room(self, roomno, site=SITE_CODE, cn=None):
        return get_by_room(roomno, site=site, cn=cn)

    def list_occupied(self, site=SITE_CODE, cn=None, limit=500):
        return list_occupied(site=site, cn=cn, limit=limit)

    def search(self, term, site=SITE_CODE, cn=None, limit=100):
        return search(term, site=site, cn=cn, limit=limit)

    def insert(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER):
        return insert(rec, cn=cn, commit=commit, site=site, user=user)

    def checkout(self, docid, user=USER, cn=None, commit=True, site=SITE_CODE):
        return checkout(docid, user=user, cn=cn, commit=commit, site=site)

    def update(self, docid, sno, rec, cn=None, commit=True, site=SITE_CODE, user=USER):
        return update(docid, sno, rec, cn=cn, commit=commit, site=site, user=user)

    def delete(self, docid, cn=None, commit=True):
        return delete(docid, cn=cn, commit=commit)



# ============================================================
# Phase B: REAL availability - Booking (Confirm/cancel aware) +
# RoomOcc (in-house) + RoomMast.RoomStat (D=dirty, M=blocked) +
# RoomBLockOut. Koi hardcoded "sab available" nahi.
# ============================================================
def room_availability(date_from, date_to=None, cn=None,
                      site: str = SITE_CODE) -> dict:
    """Real availability - Booking (Confirm/cancel aware) + RoomOcc (in-house)
    + RoomMast.RoomStat (D=dirty, M=blocked) + RoomBLockOut.
    Koi hardcoded "sab available" nahi.
    """
    from datetime import datetime
    # Validate date range
    if isinstance(date_from, str):
        date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
    if isinstance(date_to, str):
        date_to = datetime.strptime(date_to, "%Y-%m-%d").date()
    if date_to is None:
        date_to = date_from
    if date_from > date_to:
        date_from, date_to = date_to, date_from
    
    rooms = db.query(
        "SELECT RTRIM(Code) AS Code, RTRIM(Name) AS Name, RTRIM(RoomCat) "
        "AS RoomCat, RTRIM(RoomStat) AS RoomStat FROM RoomMast "
        "WHERE RTRIM(ISNULL(Type, 'RO')) = 'RO' AND (LogSite_Code = ? OR LogSite_Code = 'HO' OR ISNULL(LogSite_Code,'')='') AND RTRIM(ISNULL(InclCount,'Y'))='Y'",
        (site,), cn=cn)
    
    if not rooms:
        return {"date": str(date_from), "total_rooms": 0,
                "available": [], "occupied": [], "dirty": [],
                "blocked": [], "reserved": [], "per_category": {}}
    
    occupied = {str(r[0]) for r in db.query(
        "SELECT DISTINCT RTRIM(RoomNo) FROM RoomOcc WHERE Site_Code = ? AND (LogSite_Code = ? OR LogSite_Code = 'HO' OR ISNULL(LogSite_Code,'')='') "
        "AND ChkOutDate IS NULL AND RoomNo IS NOT NULL", (site, site), cn=cn)}
    booked = {str(r[0]) for r in db.query(
        "SELECT DISTINCT RTRIM(b.RoomNo) FROM Booking b "
        "WHERE b.Site_Code = ? AND (b.LogSite_Code = ? OR b.LogSite_Code = 'HO' OR ISNULL(b.LogSite_Code,'')='') AND ISNULL(b.Cancel, 'N') <> 'Y' "
        "AND ISNULL(b.RoomNo, '') <> '' AND b.DepDate > ? AND ? >= b.ArrDate",
        (site, site, date_from, date_to), cn=cn)}
    # RoomBLockOut: sirf VALID dated blocks (NULL ToDate wali 50 legacy
    # rows block nahi karti — live data: 9 dated (sab expired), 50 NULL).
    blocked = {str(r[0]) for r in db.query(
        "SELECT DISTINCT RTRIM(b.RoomCode) FROM RoomBLockOut b "
        "WHERE b.RoomCode IS NOT NULL AND b.FromDate IS NOT NULL "
        "AND b.ToDate IS NOT NULL AND b.FromDate <= b.ToDate "
        "AND b.ToDate >= ? AND b.FromDate <= ?",
        (date_from, date_to), cn=cn)}
    available, occ_list, dirty, blocked_list = [], [], [], []
    for r in rooms:
        code = str(r.Code or "").strip()
        stat = str(r.RoomStat or "").strip().upper()
        if code in occupied:
            occ_list.append(code)
        elif code in blocked:
            blocked_list.append(code)
        elif code in booked:
            continue  # reserved -> available pool me nahi
        elif stat == "D":
            dirty.append(code)
        else:
            available.append(code)
    cats = {}
    for r in rooms:
        cats.setdefault(str(r.RoomCat or ""), 0)
    for r in rooms:
        code = str(r.Code or "").strip()
        if code in available:
            cats[str(r.RoomCat or "")] = cats.get(str(r.RoomCat or ""), 0) + 1
    return {"date": str(date_from), "total_rooms": len(rooms),
            "available": available, "occupied": occ_list, "dirty": dirty,
            "blocked": blocked_list, "reserved": sorted(booked),
            "per_category": cats}
def tariff_matrix(room_cat: str, cn=None) -> list[dict]:
    """VB6 SRate tariff matrix 9510 - RoomCat tariff slabs"""
    return db.query("SELECT RateCode, RoomRate, PlanCode, PlanAmt FROM RoomCatTariff WHERE RoomCat=? AND (LOGSITE_CODE=? OR LOGSITE_CODE='HO') ORDER BY RateCode", (room_cat, db.get_site_code()), cn=cn)

