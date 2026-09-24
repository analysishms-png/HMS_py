"""EPABX Operations (VB6: EPABX In/Out/CDR Data).

Tables:
- EPABX_Data: CDR data (call detail records, 16 cols)
- TelCallControl, EPABX_IN, EPABX_OUT, COUNTER: NOT FOUND in DB

Note: TelCallControl/EPABX_IN/EPABX_OUT/COUNTER tables do not exist in
KailashData2526. Only EPABX_Data is present and operational.

Schema: verified from live KailashData2526 DB.
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()


# ============================================================
# EPABX_Data - CDR (Call Detail Records)
# PK: ID (identity)
# ============================================================
def _map_epabxdata(r) -> dict:
    try:
        return {
            "id": r.ID, "vtype": r.V_TYPE or "",
            "pnt_no": r.PNT_NO or "",
            "extension": r.Extension or 0,
            "roomno": r.RoomNo or "", "shopno": r.ShopNo or "",
            "depcode": r.DepCode or "",
            "call_start_date": r.CALL_START_DATE,
            "call_start_time": r.CALL_START_TIME or "",
            "call_duration": r.CALL_DURATION or "",
            "dialed_no": r.DIALED_NO or "",
            "call_info": r.CALL_INFO or "",
            "call_rate": float(r.CALL_RATE or 0),
            "call_amt": float(r.CALL_AMT or 0),
        }
    except AttributeError:
        i, vt, pnt, ext, rm, sh, dp, csd, cst, cd, dn, ci, cr, ca, site, lgs = r
        return {
            "id": i, "vtype": vt or "",
            "pnt_no": pnt or "",
            "extension": ext or 0,
            "roomno": rm or "", "shopno": sh or "",
            "depcode": dp or "",
            "call_start_date": csd,
            "call_start_time": cst or "",
            "call_duration": cd or "",
            "dialed_no": dn or "",
            "call_info": ci or "",
            "call_rate": float(cr or 0),
            "call_amt": float(ca or 0),
        }


def epabxdata_list(cn=None, limit: int = 500) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} ID, V_TYPE, PNT_NO, Extension, RoomNo, "
        "ShopNo, DepCode, CALL_START_DATE, CALL_START_TIME, "
        "CALL_DURATION, DIALED_NO, CALL_INFO, CALL_RATE, CALL_AMT, "
        "Site_Code, LogSite_Code "
        "FROM EPABX_Data ORDER BY ID DESC", cn=cn)
    return [_map_epabxdata(r) for r in rows]


def epabxdata_get(id: int, cn=None) -> dict | None:
    rows = db.query(
        "SELECT ID, V_TYPE, PNT_NO, Extension, RoomNo, ShopNo, DepCode, "
        "CALL_START_DATE, CALL_START_TIME, CALL_DURATION, DIALED_NO, "
        "CALL_INFO, CALL_RATE, CALL_AMT, Site_Code, LogSite_Code "
        "FROM EPABX_Data WHERE ID = ?", (id,), cn=cn)
    return _map_epabxdata(rows[0]) if rows else None


def epabxdata_search(extension: int = None, roomno: str = None,
                     dialed_no: str = None, cn=None,
                     limit: int = 200) -> list[dict]:
    """Search CDR by extension, room, or dialed number."""
    sql = f"SELECT TOP {int(limit)} ID, V_TYPE, PNT_NO, Extension, RoomNo, " \
          "ShopNo, DepCode, CALL_START_DATE, CALL_START_TIME, " \
          "CALL_DURATION, DIALED_NO, CALL_INFO, CALL_RATE, CALL_AMT, " \
          "Site_Code, LogSite_Code FROM EPABX_Data WHERE 1=1 "
    params: list = []
    if extension is not None:
        sql += "AND Extension = ? "
        params.append(extension)
    if roomno:
        sql += "AND RoomNo = ? "
        params.append(roomno)
    if dialed_no:
        sql += "AND DIALED_NO LIKE ? "
        params.append(f"%{dialed_no}%")
    sql += "ORDER BY ID DESC"
    rows = db.query(sql, tuple(params), cn=cn)
    return [_map_epabxdata(r) for r in rows]


def epabxdata_insert(rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "INSERT INTO EPABX_Data (V_TYPE, PNT_NO, Extension, RoomNo, "
        "ShopNo, DepCode, CALL_START_DATE, CALL_START_TIME, "
        "CALL_DURATION, DIALED_NO, CALL_INFO, CALL_RATE, CALL_AMT, "
        "Site_Code, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (rec.get("vtype", ""), rec.get("pnt_no", ""),
         rec.get("extension", 0), rec.get("roomno", ""),
         rec.get("shopno", ""), rec.get("depcode", ""),
         rec.get("call_start_date"), rec.get("call_start_time", ""),
         rec.get("call_duration", ""), rec.get("dialed_no", ""),
         rec.get("call_info", ""),
         float(rec.get("call_rate") or 0),
         float(rec.get("call_amt") or 0),
         SITE_CODE, SITE_CODE),
        cn=cn, commit=commit)


def epabxdata_delete(id: int, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM EPABX_Data WHERE ID = ?", (id,),
        cn=cn, commit=commit)


class _EPABXDataAPI:
    @staticmethod
    def list_all(cn=None, limit=500): return epabxdata_list(cn, limit)
    @staticmethod
    def get(id, cn=None): return epabxdata_get(id, cn)
    @staticmethod
    def search(extension=None, roomno=None, dialed_no=None, cn=None, limit=200):
        return epabxdata_search(extension, roomno, dialed_no, cn, limit)
    @staticmethod
    def insert(rec, cn=None, commit=True): return epabxdata_insert(rec, cn, commit)
    @staticmethod
    def delete(id, cn=None, commit=True): return epabxdata_delete(id, cn, commit)

EPABXDataAPI = _EPABXDataAPI()
