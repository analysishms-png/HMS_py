"""Guest Folio management - check-in folio CRUD, detail tables.

Tables: GuestFolio, GuestFolioProfDetail
(GuestFolioPlanDetail NOT FOUND in DB - skipped)
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
TABLE_PRIMARY = "GuestFolio"

SELECT_COLS = (
    "DocId, FolioNo, Vtype, Vdate, Site_Code, Vprefix, GuestProf, Name, "
    "Add1, Add2, City, NoDays, SplitFolio, Remarks, Authorisation, Company, "
    "PurVisit, Nationality, ArrFrom, Destination, TravelMode, TclFac, Remark, "
    "RODisc, RSDisc, BookingDocId, U_Name, U_EntDt, U_AE, GroupCode, "
    "BussSource, MarketSeg, DepDate, TravelAgent, MFolioNo, Comp, "
    "MFolioNoDocid, LogSite_Code, RefNo, BookingSno, MyRate, "
    "DoorLock_Card_SN, RefBookNo"
)


def _map(r) -> dict:
    try:
        return {
            "docid": r.DocId or "",
            "folio": r.FolioNo or 0,
            "vtype": r.Vtype or "",
            "vdate": r.Vdate,
            "site_code": r.Site_Code or "",
            "vprefix": r.Vprefix or "",
            "guestprof": r.GuestProf or "",
            "name": (r.Name or "").strip(),
            "add1": r.Add1 or "",
            "add2": r.Add2 or "",
            "city": r.City or "",
            "nodays": r.NoDays or 0,
            "remarks": r.Remarks or "",
            "company": r.Company or "",
            "bookingdocid": r.BookingDocId or "",
            "u_name": r.U_Name or "",
            "u_ae": r.U_AE or "",
            "depdate": r.DepDate,
            "groupcode": r.GroupCode or "",
            "bussource": r.BussSource or "",
            "marketseg": r.MarketSeg or "",
            "refno": r.RefNo or "",
            "refbookno": r.RefBookNo or "",
            "splitfolio": r.SplitFolio or "",
            "nationality": r.Nationality or "",
            "arrfrom": r.ArrFrom or "",
            "destination": r.Destination or "",
            "travelmode": r.TravelMode or "",
            "myrate": r.MyRate or 0.0,
            "doorlock_card_sn": r.DoorLock_Card_SN or "",
        }
    except AttributeError:
        docid, folio = r[0], r[1]
        return {"docid": docid or "", "folio": folio or 0, "name": str(r[7] or "")}


def _validate(rec: dict):
    if not rec.get("name", "").strip():
        raise ValueError("Guest Name zaroori hai")


def list_all(cn=None, limit=500) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} {SELECT_COLS} FROM GuestFolio "
        "WHERE Site_Code = ? ORDER BY FolioNo DESC",
        (SITE_CODE,), cn=cn)
    return [_map(r) for r in rows]


def get(folio: int, site: str = SITE_CODE, cn=None,
        vprefix: str = "2026") -> dict | None:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM GuestFolio WHERE Site_Code = ? AND "
        "Vprefix = ? AND FolioNo = ?", (site, vprefix, folio), cn=cn)
    return _map(rows[0]) if rows else None


def search(term: str, site: str = SITE_CODE, cn=None,
           limit=100) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} {SELECT_COLS} FROM GuestFolio "
        "WHERE Site_Code = ? AND (Name LIKE ? OR DocId LIKE ? OR "
        "GuestProf LIKE ?) ORDER BY FolioNo DESC",
        (site, f"%{term}%", f"%{term}%", f"%{term}%"), cn=cn)
    return [_map(r) for r in rows]


def insert(rec: dict, cn=None, commit: bool = True,
           site: str = SITE_CODE, user: str = USER,
           vprefix: str = "2026") -> dict:
    _validate(rec)
    from HMS_py.core.checkin import next_folio, make_docid, VTYPE
    folio = next_folio(cn=cn, vprefix=vprefix)
    docid = make_docid(site, vprefix, folio)
    nodays = max((rec.get("depdate") - rec.get("vdate")).days, 1) if rec.get("depdate") and rec.get("vdate") else 1
    db.execute(
        "INSERT INTO GuestFolio (DocId, FolioNo, Vtype, Vdate, Site_Code, "
        "Vprefix, GuestProf, Name, Add1, Add2, City, NoDays, SplitFolio, "
        "Remarks, Authorisation, Company, PurVisit, Nationality, ArrFrom, "
        "Destination, TravelMode, TclFac, Remark, RODisc, RSDisc, "
        "BookingDocId, U_Name, U_EntDt, U_AE, GroupCode, BussSource, "
        "MarketSeg, DepDate, TravelAgent, MFolioNo, Comp, MFolioNoDocid, "
        "LogSite_Code, RefNo, BookingSno, MyRate, DoorLock_Card_SN, "
        "RefBookNo) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
        "?, ?, ?, ?, 0, 0, ?, ?, getdate(), 'A', ?, ?, ?, ?, ?, ?, ?, "
        "?, ?, ?, ?, 0, '', ?)",
        (docid, folio, VTYPE, rec.get("vdate"), site, vprefix,
         rec.get("guestprof", ""), rec.get("name", ""),
         rec.get("add1", ""), rec.get("add2", ""),
         rec.get("city", ""), nodays,
         rec.get("splitfolio", ""), rec.get("remarks", ""),
         rec.get("authorisation", ""), rec.get("company", ""),
         rec.get("purvisit", ""), rec.get("nationality", ""),
         rec.get("arrfrom", ""), rec.get("destination", ""),
         rec.get("travelmode", ""), rec.get("tclfac", ""),
         rec.get("remark", ""),
         rec.get("bookingdocid", ""),
         user, rec.get("groupcode", ""), rec.get("bussource", ""),
         rec.get("marketseg", ""), rec.get("depdate"),
         rec.get("travelagent", ""),
         rec.get("mfolio", 0), rec.get("comp", ""),
         rec.get("mfolionodocid", ""),
         site, rec.get("refno", ""),
         rec.get("bookingsno", 0),
         rec.get("refbookno", "")),
        cn=cn, commit=commit)
    return get(folio, site=site, cn=cn, vprefix=vprefix)


def update(folio: int, rec: dict, cn=None, commit: bool = True,
           site: str = SITE_CODE, user: str = USER,
           vprefix: str = "2026") -> dict:
    _validate(rec)
    sets = []
    params = []
    for fld in ("Name", "Add1", "Add2", "City", "NoDays", "Remarks",
                "Company", "DepDate", "GuestProf", "Nationality",
                "ArrFrom", "Destination", "TravelMode", "GroupCode",
                "BussSource", "MarketSeg", "RefNo", "RefBookNo",
                "SplitFolio", "MyRate"):
        key = fld.lower()
        if key in rec:
            sets.append(f"{fld} = ?")
            params.append(rec[key])
    if not sets:
        raise ValueError("Koi field update nahi diya")
    sets.extend(["U_Name = ?", "U_EntDt = getdate()", "U_AE = 'E'"])
    params.extend([user, site, vprefix, folio])
    db.execute(
        "UPDATE GuestFolio SET " + ", ".join(sets) +
        " WHERE Site_Code = ? AND Vprefix = ? AND FolioNo = ?",
        params, cn=cn, commit=commit)
    return get(folio, site=site, cn=cn, vprefix=vprefix)


def delete(folio: int, cn=None, commit: bool = True,
           site: str = SITE_CODE, vprefix: str = "2026") -> int:
    return db.execute(
        "DELETE FROM GuestFolio WHERE Site_Code = ? AND Vprefix = ? "
        "AND FolioNo = ?", (site, vprefix, folio), cn=cn, commit=commit)


# ── GuestFolioProfDetail CRUD ──

def _map_prof(r) -> dict:
    try:
        return {
            "docid": r.Docid or "",
            "guestprof": r.GuestProf or "",
            "mprof": r.mProf or "",
            "u_ae": r.U_AE or "",
            "u_name": r.U_Name or "",
            "site_code": r.Site_Code or "",
        }
    except AttributeError:
        return {"docid": str(r[0] or ""), "guestprof": str(r[1] or ""),
                "mprof": str(r[2] or "")}


def list_prof_details(docid: str, cn=None) -> list[dict]:
    rows = db.query(
        "SELECT Docid, GuestProf, mProf, U_AE, U_Name, U_EntDt, "
        "Site_Code, LogSite_Code FROM GuestFolioProfDetail "
        "WHERE Docid = ? ORDER BY GuestProf", (docid,), cn=cn)
    return [_map_prof(r) for r in rows]


def insert_prof_detail(rec: dict, cn=None, commit: bool = True,
                       site: str = SITE_CODE, user: str = USER) -> dict:
    db.execute(
        "INSERT INTO GuestFolioProfDetail (Docid, GuestProf, mProf, U_AE, "
        "U_Name, U_EntDt, Site_Code, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, getdate(), ?, ?)",
        (rec.get("docid", ""), rec.get("guestprof", ""),
         rec.get("mprof", ""), rec.get("u_ae", "A"), user, site, site),
        cn=cn, commit=commit)
    return rec


def delete_prof_detail(docid: str, guestprof: str, cn=None,
                       commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM GuestFolioProfDetail WHERE Docid = ? AND GuestProf = ?",
        (docid, guestprof), cn=cn, commit=commit)


class GuestFolioAPI:
    def list_all(self, cn=None, limit=500):
        return list_all(cn=cn, limit=limit)

    def get(self, folio, site=SITE_CODE, cn=None, vprefix="2026"):
        return get(folio, site=site, cn=cn, vprefix=vprefix)

    def search(self, term, site=SITE_CODE, cn=None, limit=100):
        return search(term, site=site, cn=cn, limit=limit)

    def insert(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER):
        return insert(rec, cn=cn, commit=commit, site=site, user=user)

    def update(self, folio, rec, cn=None, commit=True, site=SITE_CODE, user=USER):
        return update(folio, rec, cn=cn, commit=commit, site=site, user=user)

    def delete(self, folio, cn=None, commit=True, site=SITE_CODE, vprefix="2026"):
        return delete(folio, cn=cn, commit=commit, site=site, vprefix=vprefix)

    def list_prof(self, docid, cn=None):
        return list_prof_details(docid, cn=cn)

    def insert_prof(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER):
        return insert_prof_detail(rec, cn=cn, commit=commit, site=site, user=user)

    def delete_prof(self, docid, guestprof, cn=None, commit=True):
        return delete_prof_detail(docid, guestprof, cn=cn, commit=commit)
