"""POS Stock module - Stock CRUD (StockTrans not in DB).

Tables verified in DB KailashData2526:
  Stock - POS stock transactions (DocId+Sno, Item, QtyIss, QtyRec, Rate, Amount)
  StockTrans - DOES NOT EXIST in this DB
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()


def _f(v, default: float = 0.0) -> float:
    try:
        if v in (None, ""):
            return default
        return float(v)
    except (TypeError, ValueError):
        return default


def _i(v, default: int = 0) -> int:
    try:
        if v in (None, ""):
            return default
        return int(float(v))
    except (TypeError, ValueError):
        return default


# ============================================================
# Stock - POS Stock Transactions
# ============================================================
_STOCK_COLS = (
    "DocId, Sno, Vtype, VNo, Site_Code, Vprefix, Vdate, PartyCode, "
    "RestCode, RoomCat, RoomType, RoomNo, ContraDocId, ContraSno, "
    "Item, QtyIss, QtyRec, Unit, Rate, Amount, TaxPer, TaxAmt, "
    "DiscPer, DiscAmt, VoidYN, Remarks, KOTDocId, KOTSno, VTime, "
    "U_Name, U_EntDt, U_AE, Total, DiscApp, RoundOff, DepartCode, "
    "GodownCode, DelFlag, LogSite_Code, FreeSno, SchemeCode, SeqNo, "
    "ShiftCode, RefDocId"
)


def _map_stock(r) -> dict:
    try:
        return {
            "docid": r.DocId or "", "sno": _i(r.Sno),
            "vtype": r.Vtype or "", "vno": _i(r.VNo),
            "site_code": r.Site_Code or "", "vprefix": r.Vprefix or "",
            "vdate": r.Vdate, "partycode": r.PartyCode or "",
            "restcode": r.RestCode or "",
            "roomcat": r.RoomCat or "", "roomtype": r.RoomType or "",
            "roomno": r.RoomNo or "",
            "contradocid": r.ContraDocId or "",
            "contrasno": _i(r.ContraSno),
            "item": r.Item or "", "qtyiss": _f(r.QtyIss),
            "qtyrec": _f(r.QtyRec), "unit": r.Unit or "",
            "rate": _f(r.Rate), "amount": _f(r.Amount),
            "taxper": _f(r.TaxPer), "taxamt": _f(r.TaxAmt),
            "discper": _f(r.DiscPer), "discamt": _f(r.DiscAmt),
            "voidyn": r.VoidYN or "", "remarks": r.Remarks or "",
            "vtime": r.VTime or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
            "total": _f(r.Total), "roundoff": _f(r.RoundOff),
            "departcode": r.DepartCode or "", "godowncode": r.GodownCode or "",
            "delflag": r.DelFlag or "",
            "shiftcode": r.ShiftCode or "", "refdocid": r.RefDocId or "",
        }
    except AttributeError:
        vals = list(r)
        return {
            "docid": vals[0] or "", "sno": _i(vals[1]),
            "vtype": vals[2] or "", "vno": _i(vals[3]),
            "site_code": vals[4] or "", "vprefix": vals[5] or "",
            "vdate": vals[6], "partycode": vals[7] or "",
            "restcode": vals[8] or "",
            "roomcat": vals[9] or "", "roomtype": vals[10] or "",
            "roomno": vals[11] or "",
            "contradocid": vals[12] or "",
            "contrasno": _i(vals[13]),
            "item": vals[14] or "", "qtyiss": _f(vals[15]),
            "qtyrec": _f(vals[16]), "unit": vals[17] or "",
            "rate": _f(vals[18]), "amount": _f(vals[19]),
            "taxper": _f(vals[20]), "taxamt": _f(vals[21]),
            "discper": _f(vals[22]), "discamt": _f(vals[23]),
            "voidyn": vals[24] or "", "remarks": vals[25] or "",
            "vtime": vals[28] or "",
            "u_name": vals[29] or "", "u_ae": vals[31] or "",
            "total": _f(vals[32]), "roundoff": _f(vals[34]),
            "departcode": vals[35] or "", "godowncode": vals[36] or "",
            "delflag": vals[37] if len(vals) > 37 else "",
            "shiftcode": vals[42] if len(vals) > 42 else "",
            "refdocid": vals[43] if len(vals) > 43 else "",
            "freesno": _i(vals[39], 0) if len(vals) > 39 else 0,
            "schemecode": vals[40] if len(vals) > 40 else "",
            "seqno": _i(vals[41], 0) if len(vals) > 41 else 0,
            "logsitcode": vals[38] if len(vals) > 38 else "",
        }


def _validate_stock(rec: dict):
    if not rec.get("docid", "").strip():
        raise ValueError("DocId zaroori hai")
    if not rec.get("item", "").strip():
        raise ValueError("Item zaroori hai")


def stock_list(cn=None, limit: int = 500) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} {_STOCK_COLS} FROM Stock ORDER BY U_EntDt DESC",
        cn=cn)
    return [_map_stock(r) for r in rows]


def stock_list_by_doc(docid: str, cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {_STOCK_COLS} FROM Stock WHERE DocId = ? ORDER BY Sno",
        (docid,), cn=cn)
    return [_map_stock(r) for r in rows]


def stock_get(docid: str, sno: int, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {_STOCK_COLS} FROM Stock WHERE DocId = ? AND Sno = ?",
        (docid, sno), cn=cn)
    return _map_stock(rows[0]) if rows else None


def stock_search(item_part: str, cn=None, limit: int = 100) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} {_STOCK_COLS} FROM Stock "
        "WHERE Item LIKE ? ORDER BY U_EntDt DESC",
        (f"%{item_part}%",), cn=cn)
    return [_map_stock(r) for r in rows]


def stock_insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate_stock(rec)
    return db.execute(
        "INSERT INTO Stock (DocId, Sno, Vtype, VNo, Site_Code, Vprefix, "
        "Vdate, PartyCode, RestCode, RoomCat, RoomType, RoomNo, "
        "ContraDocId, ContraSno, Item, QtyIss, QtyRec, Unit, Rate, Amount, "
        "TaxPer, TaxAmt, DiscPer, DiscAmt, VoidYN, Remarks, VTime, "
        "U_Name, U_EntDt, U_AE, Total, RoundOff, DepartCode, GodownCode, "
        "DelFlag, LogSite_Code, FreeSno, SchemeCode, SeqNo, ShiftCode, "
        "RefDocId) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
        "?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?, ?, ?, ?, 'N', ?, "
        "?, ?, ?, ?, ?)",
        (rec["docid"], int(rec.get("sno") or 0), rec.get("vtype", ""),
         int(rec.get("vno") or 0), SITE_CODE, rec.get("vprefix", ""),
         rec.get("vdate"), rec.get("partycode", ""),
         rec.get("restcode", ""), rec.get("roomcat", ""),
         rec.get("roomtype", ""), rec.get("roomno", ""),
         rec.get("contradocid", ""), int(rec.get("contrasno") or 0),
         rec.get("item", ""), float(rec.get("qtyiss") or 0),
         float(rec.get("qtyrec") or 0), rec.get("unit", ""),
         float(rec.get("rate") or 0), float(rec.get("amount") or 0),
         float(rec.get("taxper") or 0), float(rec.get("taxamt") or 0),
         float(rec.get("discper") or 0), float(rec.get("discamt") or 0),
         rec.get("voidyn", ""), rec.get("remarks", ""),
         rec.get("vtime", ""),
         USER, float(rec.get("total") or 0), float(rec.get("roundoff") or 0),
         rec.get("departcode", ""), rec.get("godowncode", ""),
         SITE_CODE, int(rec.get("freesno") or 0),
         rec.get("schemecode", ""), int(rec.get("seqno") or 0),
         rec.get("shiftcode", ""), rec.get("refdocid", "")),
        cn=cn, commit=commit)


def stock_update(docid: str, sno: int, rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "UPDATE Stock SET QtyIss = ?, QtyRec = ?, Rate = ?, Amount = ?, "
        "TaxPer = ?, TaxAmt = ?, DiscPer = ?, DiscAmt = ?, VoidYN = ?, "
        "Remarks = ?, Total = ?, RoundOff = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' "
        "WHERE DocId = ? AND Sno = ?",
        (float(rec.get("qtyiss") or 0), float(rec.get("qtyrec") or 0),
         float(rec.get("rate") or 0), float(rec.get("amount") or 0),
         float(rec.get("taxper") or 0), float(rec.get("taxamt") or 0),
         float(rec.get("discper") or 0), float(rec.get("discamt") or 0),
         rec.get("voidyn", ""), rec.get("remarks", ""),
         float(rec.get("total") or 0), float(rec.get("roundoff") or 0),
         USER, docid, sno),
        cn=cn, commit=commit)


def stock_delete(docid: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM Stock WHERE DocId = ?", (docid,),
                      cn=cn, commit=commit)


class _StockAPI:
    LIMITS = {"docid": 30, "vtype": 5, "item": 10, "unit": 6}
    @staticmethod
    def list_all(cn=None, limit=500): return stock_list(cn, limit)
    @staticmethod
    def list_by_doc(docid, cn=None): return stock_list_by_doc(docid, cn)
    @staticmethod
    def get(docid, sno, cn=None): return stock_get(docid, sno, cn)
    @staticmethod
    def search(item_part, cn=None, limit=100): return stock_search(item_part, cn, limit)
    @staticmethod
    def insert(rec, cn=None, commit=True): return stock_insert(rec, cn, commit)
    @staticmethod
    def update(docid, sno, rec, cn=None, commit=True): return stock_update(docid, sno, rec, cn, commit)
    @staticmethod
    def delete(docid, cn=None, commit=True): return stock_delete(docid, cn, commit)

StockAPI = _StockAPI()
