"""POS Packing/Advance Orders - PackingOrder/PackingOrderDetail CRUD.

Tables verified in DB KailashData2526:
  PackingOrder      - packing/advance order header (Docid, CustName, NetAmt, PhoneNo)
  PackingOrderDetail - packing order detail lines (DocID+SNo, ItemCode, Qty, Rate, Amount)
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()


# ============================================================
# PackingOrder - Packing/Advance Order Header
# ============================================================
_PACKINGORDER_COLS = (
    "Docid, VNo, VPrefix, VType, Site_Code, VDate, VTime, DDate, DTime, "
    "CustName, Total, Discount, Tax, Addition, Deduction, RoundOff, "
    "NetAmt, U_Name, U_EntDt, U_AE, LogSite_Code, RestCode, AdvAmt, "
    "DiscPer, TaxPer, PhoneNo, Addr1, Addr2, TokenNo, NCBOOKING, NCTYPE, "
    "PrintedYN, Remark, OrderType"
)


def _map_packing(r) -> dict:
    try:
        return {
            "docid": r.Docid or "", "vno": int(r.VNo or 0),
            "vprefix": r.VPrefix or "", "vtype": r.VType or "",
            "site_code": r.Site_Code or "",
            "vdate": r.VDate, "vtime": r.VTime or "",
            "ddate": r.DDate, "dtime": r.DTime or "",
            "custname": r.CustName or "", "total": float(r.Total or 0),
            "discount": float(r.Discount or 0), "tax": float(r.Tax or 0),
            "addition": float(r.Addition or 0), "deduction": float(r.Deduction or 0),
            "roundoff": float(r.RoundOff or 0), "netamt": float(r.NetAmt or 0),
            "restcode": r.RestCode or "", "advamt": float(r.AdvAmt or 0),
            "discper": float(r.DiscPer or 0), "taxper": float(r.TaxPer or 0),
            "phoneno": r.PhoneNo or "", "addr1": r.Addr1 or "",
            "addr2": r.Addr2 or "", "tokenno": r.TokenNo or "",
            "ncbooking": r.NCBOOKING or "", "nctype": r.NCTYPE or "",
            "printedy": r.PrintedYN or "", "remark": r.Remark or "",
            "ordertype": r.OrderType or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        vals = list(r)
        return {
            "docid": vals[0] or "", "vno": int(vals[1] or 0),
            "vprefix": vals[2] or "", "vtype": vals[3] or "",
            "site_code": vals[4] or "",
            "vdate": vals[5], "vtime": vals[6] or "",
            "ddate": vals[7], "dtime": vals[8] or "",
            "custname": vals[9] or "", "total": float(vals[10] or 0),
            "discount": float(vals[11] or 0), "tax": float(vals[12] or 0),
            "addition": float(vals[13] or 0), "deduction": float(vals[14] or 0),
            "roundoff": float(vals[15] or 0), "netamt": float(vals[16] or 0),
            "restcode": vals[21] if len(vals) > 21 else "",
            "advamt": float(vals[22] if len(vals) > 22 else 0),
            "discper": float(vals[23] if len(vals) > 23 else 0),
            "taxper": float(vals[24] if len(vals) > 24 else 0),
            "phoneno": vals[25] if len(vals) > 25 else "",
            "addr1": vals[26] if len(vals) > 26 else "",
            "addr2": vals[27] if len(vals) > 27 else "",
            "tokenno": vals[28] if len(vals) > 28 else "",
            "ncbooking": vals[29] if len(vals) > 29 else "",
            "nctype": vals[30] if len(vals) > 30 else "",
            "printedy": vals[31] if len(vals) > 31 else "",
            "remark": vals[32] if len(vals) > 32 else "",
            "ordertype": vals[33] if len(vals) > 33 else "",
            "u_name": vals[17] or "", "u_ae": vals[19] or "",
        }


def _validate_packing(rec: dict):
    if not rec.get("docid", "").strip():
        raise ValueError("Docid zaroori hai")
    if not rec.get("vtype", "").strip():
        raise ValueError("VType zaroori hai")


def packing_list(cn=None, limit: int = 500) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} {_PACKINGORDER_COLS} FROM PackingOrder ORDER BY U_EntDt DESC",
        cn=cn)
    return [_map_packing(r) for r in rows]


def packing_get(docid: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {_PACKINGORDER_COLS} FROM PackingOrder WHERE Docid = ?",
        (docid,), cn=cn)
    if not rows:
        return None
    d = _map_packing(rows[0])
    d["items"] = packing_detail(docid, cn=cn)
    return d


def packing_search(custname: str, cn=None, limit: int = 100) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} {_PACKINGORDER_COLS} FROM PackingOrder "
        "WHERE CustName LIKE ? ORDER BY U_EntDt DESC",
        (f"%{custname}%",), cn=cn)
    return [_map_packing(r) for r in rows]


def packing_insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate_packing(rec)
    items = rec.get("items", [])
    own = cn is None
    cn = cn or db.connect()
    try:
        db.execute(
            "INSERT INTO PackingOrder (Docid, VNo, VPrefix, VType, Site_Code, "
            "VDate, VTime, DDate, DTime, CustName, Total, Discount, Tax, "
            "Addition, Deduction, RoundOff, NetAmt, U_Name, U_EntDt, U_AE, "
            "LogSite_Code, RestCode, AdvAmt, DiscPer, TaxPer, PhoneNo, Addr1, "
            "Addr2, TokenNo, NCBOOKING, NCTYPE, PrintedYN, Remark, OrderType) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
            "getdate(), 'A', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (rec["docid"], int(rec.get("vno") or 0), rec.get("vprefix", ""),
             rec.get("vtype", ""), SITE_CODE,
             rec.get("vdate"), rec.get("vtime", ""),
             rec.get("ddate"), rec.get("dtime", ""),
             rec.get("custname", ""), float(rec.get("total") or 0),
             float(rec.get("discount") or 0), float(rec.get("tax") or 0),
             float(rec.get("addition") or 0), float(rec.get("deduction") or 0),
             float(rec.get("roundoff") or 0), float(rec.get("netamt") or 0),
             USER, SITE_CODE,
             rec.get("restcode", ""), float(rec.get("advamt") or 0),
             float(rec.get("discper") or 0), float(rec.get("taxper") or 0),
             rec.get("phoneno", ""), rec.get("addr1", ""),
             rec.get("addr2", ""), rec.get("tokenno", ""),
             rec.get("ncbooking", ""), rec.get("nctype", ""),
             rec.get("printedy", ""), rec.get("remark", ""),
             rec.get("ordertype", "")),
            cn=cn, commit=False)
        for item in items:
            packing_detail_insert({**item, "docid": rec["docid"]}, cn=cn, commit=False)
        if commit:
            cn.commit()
        return 0
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


def packing_update(docid: str, rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "UPDATE PackingOrder SET CustName = ?, Total = ?, Discount = ?, "
        "Tax = ?, Addition = ?, Deduction = ?, RoundOff = ?, NetAmt = ?, "
        "PhoneNo = ?, Addr1 = ?, Addr2 = ?, Remark = ?, OrderType = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Docid = ?",
        (rec.get("custname", ""), float(rec.get("total") or 0),
         float(rec.get("discount") or 0), float(rec.get("tax") or 0),
         float(rec.get("addition") or 0), float(rec.get("deduction") or 0),
         float(rec.get("roundoff") or 0), float(rec.get("netamt") or 0),
         rec.get("phoneno", ""), rec.get("addr1", ""),
         rec.get("addr2", ""), rec.get("remark", ""),
         rec.get("ordertype", ""), USER, docid),
        cn=cn, commit=commit)


def packing_delete(docid: str, cn=None, commit: bool = True) -> int:
    own = cn is None
    cn = cn or db.connect()
    try:
        db.execute("DELETE FROM PackingOrderDetail WHERE DocID = ?",
                   (docid,), cn=cn, commit=False)
        r = db.execute("DELETE FROM PackingOrder WHERE Docid = ?",
                       (docid,), cn=cn, commit=False)
        if commit:
            cn.commit()
        return r
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


class _PackingOrderAPI:
    LIMITS = {"docid": 30, "vtype": 5, "custname": 40, "phoneno": 15}
    @staticmethod
    def list_all(cn=None, limit=500): return packing_list(cn, limit)
    @staticmethod
    def get(docid, cn=None): return packing_get(docid, cn)
    @staticmethod
    def search(custname, cn=None, limit=100): return packing_search(custname, cn, limit)
    @staticmethod
    def insert(rec, cn=None, commit=True): return packing_insert(rec, cn, commit)
    @staticmethod
    def update(docid, rec, cn=None, commit=True): return packing_update(docid, rec, cn, commit)
    @staticmethod
    def delete(docid, cn=None, commit=True): return packing_delete(docid, cn, commit)

PackingOrderAPI = _PackingOrderAPI()


# ============================================================
# PackingOrderDetail - Packing Order Detail Lines
# ============================================================
_PACKINGDETAIL_COLS = (
    "DocID, SNo, VType, VNo, Site_Code, VPrefix, VDate, ItemCode, Qty, "
    "Rate, Amount, Remark, U_Name, U_EntDt, U_AE, LogSite_Code, "
    "ContraDocID, ContraSNo, RestCode, ItemRate, Unit, RateIncTax, "
    "RateEdit, SChrgApp, DiscApp, TaxCode, TaxROff, DepartCode, "
    "GodownCode, TaxPer, TaxAmt, DiscPer, DiscAmt, Total, VoidYN, "
    "ItemRestCode"
)


def _map_packingdetail(r) -> dict:
    try:
        return {
            "docid": r.DocID or "", "sno": int(r.SNo or 0),
            "vtype": r.VType or "", "vno": int(r.VNo or 0),
            "site_code": r.Site_Code or "", "vprefix": r.VPrefix or "",
            "vdate": r.VDate, "itemcode": r.ItemCode or "",
            "qty": float(r.Qty or 0), "rate": float(r.Rate or 0),
            "amount": float(r.Amount or 0), "remark": r.Remark or "",
            "restcode": r.RestCode or "",
            "itemrate": float(r.ItemRate or 0), "unit": r.Unit or "",
            "taxper": float(r.TaxPer or 0), "taxamt": float(r.TaxAmt or 0),
            "discper": float(r.DiscPer or 0), "discamt": float(r.DiscAmt or 0),
            "total": float(r.Total or 0), "voidyn": r.VoidYN or "",
            "itemrestcode": r.ItemRestCode or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        vals = list(r)
        return {
            "docid": vals[0] or "", "sno": int(vals[1] or 0),
            "vtype": vals[2] or "", "vno": int(vals[3] or 0),
            "site_code": vals[4] or "", "vprefix": vals[5] or "",
            "vdate": vals[6], "itemcode": vals[7] or "",
            "qty": float(vals[8] or 0), "rate": float(vals[9] or 0),
            "amount": float(vals[10] or 0), "remark": vals[11] or "",
            "restcode": vals[18] if len(vals) > 18 else "",
            "itemrate": float(vals[19] if len(vals) > 19 else 0),
            "unit": vals[20] if len(vals) > 20 else "",
            "taxper": float(vals[29] if len(vals) > 29 else 0),
            "taxamt": float(vals[30] if len(vals) > 30 else 0),
            "discper": float(vals[31] if len(vals) > 31 else 0),
            "discamt": float(vals[32] if len(vals) > 32 else 0),
            "total": float(vals[33] if len(vals) > 33 else 0),
            "voidyn": vals[34] if len(vals) > 34 else "",
            "itemrestcode": vals[35] if len(vals) > 35 else "",
            "u_name": vals[12] or "", "u_ae": vals[14] or "",
        }


def packing_detail(docid: str, cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {_PACKINGDETAIL_COLS} FROM PackingOrderDetail WHERE DocID = ? ORDER BY SNo",
        (docid,), cn=cn)
    return [_map_packingdetail(r) for r in rows]


def packing_detail_get(docid: str, sno: int, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {_PACKINGDETAIL_COLS} FROM PackingOrderDetail WHERE DocID = ? AND SNo = ?",
        (docid, sno), cn=cn)
    return _map_packingdetail(rows[0]) if rows else None


def packing_detail_insert(rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "INSERT INTO PackingOrderDetail (DocID, SNo, VType, VNo, Site_Code, "
        "VPrefix, VDate, ItemCode, Qty, Rate, Amount, Remark, U_Name, "
        "U_EntDt, U_AE, LogSite_Code, ContraDocID, ContraSNo, RestCode, "
        "ItemRate, Unit, TaxPer, TaxAmt, DiscPer, DiscAmt, Total, VoidYN, "
        "ItemRestCode) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?, "
        "?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'N', ?)",
        (rec["docid"], int(rec.get("sno") or 0), rec.get("vtype", ""),
         int(rec.get("vno") or 0), SITE_CODE, rec.get("vprefix", ""),
         rec.get("vdate"), rec.get("itemcode", ""),
         float(rec.get("qty") or 0), float(rec.get("rate") or 0),
         float(rec.get("amount") or 0), rec.get("remark", ""),
         USER, SITE_CODE,
         rec.get("contradocid", ""), int(rec.get("contrasno") or 0),
         rec.get("restcode", ""), float(rec.get("itemrate") or 0),
         rec.get("unit", ""), float(rec.get("taxper") or 0),
         float(rec.get("taxamt") or 0), float(rec.get("discper") or 0),
         float(rec.get("discamt") or 0), float(rec.get("total") or 0),
         rec.get("itemrestcode", "")),
        cn=cn, commit=commit)


def packing_detail_delete(docid: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM PackingOrderDetail WHERE DocID = ?",
                      (docid,), cn=cn, commit=commit)


class _PackingDetailAPI:
    @staticmethod
    def list_by_doc(docid, cn=None): return packing_detail(docid, cn)
    @staticmethod
    def get(docid, sno, cn=None): return packing_detail_get(docid, sno, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return packing_detail_insert(rec, cn, commit)
    @staticmethod
    def delete(docid, cn=None, commit=True): return packing_detail_delete(docid, cn, commit)

PackingDetailAPI = _PackingDetailAPI()



# ============================================================
# Phase A (api-mismatch audit): UI pos_packing_ui list_all/get/
# insert/update (docid-keyed) call karta tha. insert() UI-keys
# (PartyName/ItemName/Qty/...) se PackingOrder+detail bhar deta hai.
# ============================================================
def list_all(cn=None, limit: int = 500) -> list:
    return packing_list(cn=cn, limit=limit)


def get(docid: str, cn=None):
    return packing_get(docid, cn=cn)


def insert(rec: dict, cn=None, commit: bool = True) -> int:
    if not str(rec.get("docid", "")).strip():
        vno_rows = db.query(
            "SELECT MAX(VNo) FROM PackingOrder WITH (UPDLOCK, HOLDLOCK)",
            cn=cn)
        vno = (vno_rows[0][0] or 0) + 1 if vno_rows and vno_rows[0][0] else 1
        vtype = str(rec.get("vtype") or "PK")
        rec = {**rec,
               "docid": ("D" + SITE_CODE.ljust(2) + "PK".ljust(6) +
                         str(rec.get("vprefix", "2026")).ljust(4) +
                         str(vno).rjust(8))[:21],
               "vno": vno, "vtype": vtype,
               "custname": str(rec.get("custname") or rec.get("PartyName") or ""),
               "remark": str(rec.get("remark") or rec.get("Remarks") or ""),
               "items": rec.get("items") or [{
                   "sno": 1, "vtype": vtype,
                   "vprefix": rec.get("vprefix", "2026"),
                   "vdate": rec.get("vdate"), "itemcode": "",
                   "qty": rec.get("Qty", 0) or 0, "rate": 0,
                   "amount": 0, "remark": rec.get("ItemName", "")}]}
    return packing_insert(rec, cn=cn, commit=commit)


def update(docid: str, rec: dict, cn=None, commit: bool = True) -> int:
    n = packing_update(docid, rec, cn=cn, commit=commit)
    # UI ka fake "Status" field -> PrintedYN par map (Packed = printed)
    if "status" in rec:
        db.execute(
            "UPDATE PackingOrder SET PrintedYN = ? WHERE Docid = ?",
            ("Y" if str(rec["status"]).lower() == "packed" else "N", docid),
            cn=cn, commit=commit)
    return n
