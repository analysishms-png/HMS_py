"""POS Hall/Banquet sales module - HallStock/HallStockEst/HallSale1Est/SunTranEst/SunTranHEst/HallPreCosting CRUD.

Tables verified in DB KailashData2526:
  HallStock      - hall stock items (DocId+Sno, Item, QtyIss, Rate, Amount)
  HallStockEst   - estimate stock (DocId+Sno, Item, QtyIss, Rate, Amount)
  HallSale1Est   - estimate sale header (DocId, NetAmt, NoOfPax, RatePerPax)
  SunTranEst     - estimate sundry (DocId+Sno, SunCode, Amount)
  SunTranHEst    - hall estimate sundry (DocId+Sno, SunCode, Amount)
  HallPreCosting - chef pre-costing (Docid+Sno, Item, Qty, Rate, Amount)
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()


# ============================================================
# HallStock - Hall Stock Items
# ============================================================
_HALLSTOCK_COLS = (
    "DocId, Sno, Vtype, VNo, Site_Code, Vprefix, Vdate, Party, RestCode, "
    "ContraDocId, ContraSno, Item, QtyIss, Unit, Rate, Amount, TaxPer, "
    "TaxAmt, DiscPer, DiscAmt, VoidYN, Remarks, U_Name, U_EntDt, U_AE, "
    "Total, DiscApp, RoundOff, DepartCode, GodCode, DelFlag, LogSite_Code, "
    "SChrgApp, SChrgPer, SChrgAmt"
)


def _map_hallstock(r) -> dict:
    try:
        return {
            "docid": r.DocId or "", "sno": int(r.Sno or 0),
            "vtype": r.Vtype or "", "vno": int(r.VNo or 0),
            "site_code": r.Site_Code or "", "vprefix": r.Vprefix or "",
            "vdate": r.Vdate, "party": r.Party or "",
            "restcode": r.RestCode or "",
            "contradocid": r.ContraDocId or "",
            "contrasno": int(r.ContraSno or 0),
            "item": r.Item or "", "qtyiss": float(r.QtyIss or 0),
            "unit": r.Unit or "", "rate": float(r.Rate or 0),
            "amount": float(r.Amount or 0),
            "taxper": float(r.TaxPer or 0), "taxamt": float(r.TaxAmt or 0),
            "discper": float(r.DiscPer or 0), "discamt": float(r.DiscAmt or 0),
            "voidyn": r.VoidYN or "", "remarks": r.Remarks or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
            "total": float(r.Total or 0), "roundoff": float(r.RoundOff or 0),
            "departcode": r.DepartCode or "", "godcode": r.GodCode or "",
            "delflag": r.DelFlag or "",
        }
    except AttributeError:
        vals = list(r)
        return {
            "docid": vals[0] or "", "sno": int(vals[1] or 0),
            "vtype": vals[2] or "", "vno": int(vals[3] or 0),
            "site_code": vals[4] or "", "vprefix": vals[5] or "",
            "vdate": vals[6], "party": vals[7] or "",
            "restcode": vals[8] or "",
            "contradocid": vals[9] or "",
            "contrasno": int(vals[10] or 0),
            "item": vals[11] or "", "qtyiss": float(vals[12] or 0),
            "unit": vals[13] or "", "rate": float(vals[14] or 0),
            "amount": float(vals[15] or 0),
            "taxper": float(vals[16] or 0), "taxamt": float(vals[17] or 0),
            "discper": float(vals[18] or 0), "discamt": float(vals[19] or 0),
            "voidyn": vals[20] or "", "remarks": vals[21] or "",
            "u_name": vals[22] or "", "u_ae": vals[24] or "",
            "total": float(vals[25] or 0), "roundoff": float(vals[27] or 0),
            "departcode": vals[28] or "", "godcode": vals[29] or "",
            "delflag": vals[30] or "",
        }


def hallstock_list(cn=None, limit: int = 500) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} {_HALLSTOCK_COLS} FROM HallStock ORDER BY U_EntDt DESC",
        cn=cn)
    return [_map_hallstock(r) for r in rows]


def hallstock_list_by_doc(docid: str, cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {_HALLSTOCK_COLS} FROM HallStock WHERE DocId = ? ORDER BY Sno",
        (docid,), cn=cn)
    return [_map_hallstock(r) for r in rows]


def hallstock_get(docid: str, sno: int, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {_HALLSTOCK_COLS} FROM HallStock WHERE DocId = ? AND Sno = ?",
        (docid, sno), cn=cn)
    return _map_hallstock(rows[0]) if rows else None


def hallstock_insert(rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "INSERT INTO HallStock (DocId, Sno, Vtype, VNo, Site_Code, Vprefix, "
        "Vdate, Party, RestCode, ContraDocId, ContraSno, Item, QtyIss, Unit, "
        "Rate, Amount, TaxPer, TaxAmt, DiscPer, DiscAmt, VoidYN, Remarks, "
        "U_Name, U_EntDt, U_AE, Total, RoundOff, DepartCode, GodCode, "
        "DelFlag, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
        "?, ?, ?, ?, getdate(), 'A', ?, ?, ?, ?, 'N', ?)",
        (rec["docid"], int(rec.get("sno") or 0), rec.get("vtype", ""),
         int(rec.get("vno") or 0), SITE_CODE, rec.get("vprefix", ""),
         rec.get("vdate"), rec.get("party", ""), rec.get("restcode", ""),
         rec.get("contradocid", ""), int(rec.get("contrasno") or 0),
         rec.get("item", ""), float(rec.get("qtyiss") or 0),
         rec.get("unit", ""), float(rec.get("rate") or 0),
         float(rec.get("amount") or 0), float(rec.get("taxper") or 0),
         float(rec.get("taxamt") or 0), float(rec.get("discper") or 0),
         float(rec.get("discamt") or 0), rec.get("voidyn", ""),
         rec.get("remarks", ""), USER,
         float(rec.get("total") or 0), float(rec.get("roundoff") or 0),
         rec.get("departcode", ""), rec.get("godcode", ""),
         SITE_CODE),
        cn=cn, commit=commit)


def hallstock_delete(docid: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM HallStock WHERE DocId = ?", (docid,),
                      cn=cn, commit=commit)


class _HallStockAPI:
    LIMITS = {"docid": 30, "vtype": 5, "item": 10, "unit": 6}
    @staticmethod
    def list_all(cn=None, limit=500): return hallstock_list(cn, limit)
    @staticmethod
    def list_by_doc(docid, cn=None): return hallstock_list_by_doc(docid, cn)
    @staticmethod
    def get(docid, sno, cn=None): return hallstock_get(docid, sno, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return hallstock_insert(rec, cn, commit)
    @staticmethod
    def delete(docid, cn=None, commit=True): return hallstock_delete(docid, cn, commit)

HallStockAPI = _HallStockAPI()


# ============================================================
# HallStockEst - Estimate Stock (same schema as HallStock)
# ============================================================
def _map_hallstockest(r) -> dict:
    try:
        return {
            "docid": r.DocId or "", "sno": int(r.Sno or 0),
            "vtype": r.Vtype or "", "vno": int(r.VNo or 0),
            "site_code": r.Site_Code or "", "vprefix": r.Vprefix or "",
            "vdate": r.Vdate, "party": r.Party or "",
            "restcode": r.RestCode or "",
            "contradocid": r.ContraDocId or "",
            "contrasno": int(r.ContraSno or 0),
            "item": r.Item or "", "qtyiss": float(r.QtyIss or 0),
            "unit": r.Unit or "", "rate": float(r.Rate or 0),
            "amount": float(r.Amount or 0),
            "taxper": float(r.TaxPer or 0), "taxamt": float(r.TaxAmt or 0),
            "discper": float(r.DiscPer or 0), "discamt": float(r.DiscAmt or 0),
            "voidyn": r.VoidYN or "", "remarks": r.Remarks or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
            "total": float(r.Total or 0), "roundoff": float(r.RoundOff or 0),
            "departcode": r.DepartCode or "", "godcode": r.GodCode or "",
            "delflag": r.DelFlag or "",
        }
    except AttributeError:
        vals = list(r)
        return {
            "docid": vals[0] or "", "sno": int(vals[1] or 0),
            "vtype": vals[2] or "", "vno": int(vals[3] or 0),
            "site_code": vals[4] or "", "vprefix": vals[5] or "",
            "vdate": vals[6], "party": vals[7] or "",
            "restcode": vals[8] or "",
            "contradocid": vals[9] or "",
            "contrasno": int(vals[10] or 0),
            "item": vals[11] or "", "qtyiss": float(vals[12] or 0),
            "unit": vals[13] or "", "rate": float(vals[14] or 0),
            "amount": float(vals[15] or 0),
            "taxper": float(vals[16] or 0), "taxamt": float(vals[17] or 0),
            "discper": float(vals[18] or 0), "discamt": float(vals[19] or 0),
            "voidyn": vals[20] or "", "remarks": vals[21] or "",
            "u_name": vals[22] or "", "u_ae": vals[24] or "",
            "total": float(vals[25] or 0), "roundoff": float(vals[27] or 0),
            "departcode": vals[28] or "", "godcode": vals[29] or "",
            "delflag": vals[30] or "",
        }


def hallstockest_list(cn=None, limit: int = 500) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} {_HALLSTOCK_COLS} FROM HallStockEst ORDER BY U_EntDt DESC",
        cn=cn)
    return [_map_hallstockest(r) for r in rows]


def hallstockest_list_by_doc(docid: str, cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {_HALLSTOCK_COLS} FROM HallStockEst WHERE DocId = ? ORDER BY Sno",
        (docid,), cn=cn)
    return [_map_hallstockest(r) for r in rows]


def hallstockest_get(docid: str, sno: int, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {_HALLSTOCK_COLS} FROM HallStockEst WHERE DocId = ? AND Sno = ?",
        (docid, sno), cn=cn)
    return _map_hallstockest(rows[0]) if rows else None


def hallstockest_insert(rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "INSERT INTO HallStockEst (DocId, Sno, Vtype, VNo, Site_Code, Vprefix, "
        "Vdate, Party, RestCode, ContraDocId, ContraSno, Item, QtyIss, Unit, "
        "Rate, Amount, TaxPer, TaxAmt, DiscPer, DiscAmt, VoidYN, Remarks, "
        "U_Name, U_EntDt, U_AE, Total, RoundOff, DepartCode, GodCode, "
        "DelFlag, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
        "?, ?, ?, ?, getdate(), 'A', ?, ?, ?, ?, 'N', ?)",
        (rec["docid"], int(rec.get("sno") or 0), rec.get("vtype", ""),
         int(rec.get("vno") or 0), SITE_CODE, rec.get("vprefix", ""),
         rec.get("vdate"), rec.get("party", ""), rec.get("restcode", ""),
         rec.get("contradocid", ""), int(rec.get("contrasno") or 0),
         rec.get("item", ""), float(rec.get("qtyiss") or 0),
         rec.get("unit", ""), float(rec.get("rate") or 0),
         float(rec.get("amount") or 0), float(rec.get("taxper") or 0),
         float(rec.get("taxamt") or 0), float(rec.get("discper") or 0),
         float(rec.get("discamt") or 0), rec.get("voidyn", ""),
         rec.get("remarks", ""), USER,
         float(rec.get("total") or 0), float(rec.get("roundoff") or 0),
         rec.get("departcode", ""), rec.get("godcode", ""),
         SITE_CODE),
        cn=cn, commit=commit)


def hallstockest_delete(docid: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM HallStockEst WHERE DocId = ?", (docid,),
                      cn=cn, commit=commit)


class _HallStockEstAPI:
    @staticmethod
    def list_all(cn=None, limit=500): return hallstockest_list(cn, limit)
    @staticmethod
    def list_by_doc(docid, cn=None): return hallstockest_list_by_doc(docid, cn)
    @staticmethod
    def get(docid, sno, cn=None): return hallstockest_get(docid, sno, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return hallstockest_insert(rec, cn, commit)
    @staticmethod
    def delete(docid, cn=None, commit=True): return hallstockest_delete(docid, cn, commit)

HallStockEstAPI = _HallStockEstAPI()


# ============================================================
# HallSale1Est - Estimate Sale Header
# ============================================================
_HALLSALE1EST_COLS = (
    "DocId, Vtype, VNo, VTime, Site_Code, Vprefix, Vdate, RestCode, Party, "
    "Total, DiscPer, DiscAmt, NonTaxable, Taxable, Tax, ServiceCharge, "
    "AddAmt, DedAmt, RoundOff, NetAmt, FrBookDate, FrBookTime, "
    "U_Name, U_EntDt, U_AE, ToBookDate, ToBookTime, HallRent, Remarks, "
    "NoOfPax, RatePerPax, TotalPerCover, Amount, Advance, RectNo, "
    "rectDate, CrCardNo, CrCardHolder, BookDocId, DelFlag, Narration, "
    "LogSite_Code"
)


def _map_hallsale1est(r) -> dict:
    try:
        return {
            "docid": r.DocId or "", "vtype": r.Vtype or "",
            "vno": int(r.VNo or 0), "vtime": r.VTime or "",
            "site_code": r.Site_Code or "", "vprefix": r.Vprefix or "",
            "vdate": r.Vdate, "restcode": r.RestCode or "",
            "party": r.Party or "", "total": float(r.Total or 0),
            "discper": float(r.DiscPer or 0), "discamt": float(r.DiscAmt or 0),
            "nontaxable": float(r.NonTaxable or 0),
            "taxable": float(r.Taxable or 0), "tax": float(r.Tax or 0),
            "servicecharge": float(r.ServiceCharge or 0),
            "addamt": float(r.AddAmt or 0), "dedamt": float(r.DedAmt or 0),
            "roundoff": float(r.RoundOff or 0), "netamt": float(r.NetAmt or 0),
            "hallrent": float(r.HallRent or 0), "remarks": r.Remarks or "",
            "noofpax": int(r.NoOfPax or 0),
            "rateperpax": float(r.RatePerPax or 0),
            "totalpercover": float(r.TotalPerCover or 0),
            "amount": float(r.Amount or 0), "advance": float(r.Advance or 0),
            "narration": r.Narration or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
            "delflag": r.DelFlag or "",
        }
    except AttributeError:
        vals = list(r)
        return {
            "docid": vals[0] or "", "vtype": vals[1] or "",
            "vno": int(vals[2] or 0), "vtime": vals[3] or "",
            "site_code": vals[4] or "", "vprefix": vals[5] or "",
            "vdate": vals[6], "restcode": vals[7] or "",
            "party": vals[8] or "", "total": float(vals[9] or 0),
            "discper": float(vals[10] or 0), "discamt": float(vals[11] or 0),
            "nontaxable": float(vals[12] or 0),
            "taxable": float(vals[13] or 0), "tax": float(vals[14] or 0),
            "servicecharge": float(vals[15] or 0),
            "addamt": float(vals[16] or 0), "dedamt": float(vals[17] or 0),
            "roundoff": float(vals[18] or 0), "netamt": float(vals[19] or 0),
            "hallrent": float(vals[27] or 0), "remarks": vals[28] or "",
            "noofpax": int(vals[29] if len(vals) > 29 else 0),
            "rateperpax": float(vals[30] if len(vals) > 30 else 0),
            "totalpercover": float(vals[31] if len(vals) > 31 else 0),
            "amount": float(vals[32] if len(vals) > 32 else 0),
            "advance": float(vals[33] if len(vals) > 33 else 0),
            "narration": vals[40] if len(vals) > 40 else "",
            "u_name": vals[22] or "", "u_ae": vals[24] or "",
            "delflag": vals[39] if len(vals) > 39 else "",
        }


def hallsale1est_list(cn=None, limit: int = 500) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} {_HALLSALE1EST_COLS} FROM HallSale1Est ORDER BY U_EntDt DESC",
        cn=cn)
    return [_map_hallsale1est(r) for r in rows]


def hallsale1est_get(docid: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {_HALLSALE1EST_COLS} FROM HallSale1Est WHERE DocId = ?",
        (docid,), cn=cn)
    return _map_hallsale1est(rows[0]) if rows else None


def hallsale1est_insert(rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "INSERT INTO HallSale1Est (DocId, Vtype, VNo, VTime, Site_Code, "
        "Vprefix, Vdate, RestCode, Party, Total, DiscPer, DiscAmt, "
        "NonTaxable, Taxable, Tax, ServiceCharge, AddAmt, DedAmt, RoundOff, "
        "NetAmt, FrBookDate, FrBookTime, U_Name, U_EntDt, U_AE, "
        "ToBookDate, ToBookTime, HallRent, Remarks, NoOfPax, RatePerPax, "
        "TotalPerCover, Amount, Advance, Narration, DelFlag, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
        "?, ?, ?, ?, getdate(), 'A', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'N', ?)",
        (rec["docid"], rec.get("vtype", ""), int(rec.get("vno") or 0),
         rec.get("vtime", ""), SITE_CODE, rec.get("vprefix", ""),
         rec.get("vdate"), rec.get("restcode", ""),
         rec.get("party", ""), float(rec.get("total") or 0),
         float(rec.get("discper") or 0), float(rec.get("discamt") or 0),
         float(rec.get("nontaxable") or 0), float(rec.get("taxable") or 0),
         float(rec.get("tax") or 0), float(rec.get("servicecharge") or 0),
         float(rec.get("addamt") or 0), float(rec.get("dedamt") or 0),
         float(rec.get("roundoff") or 0), float(rec.get("netamt") or 0),
         rec.get("frbookdate"), rec.get("frbooktime", ""),
         USER, rec.get("tobookdate"), rec.get("tobooktime", ""),
         float(rec.get("hallrent") or 0), rec.get("remarks", ""),
         int(rec.get("noofpax") or 0), float(rec.get("rateperpax") or 0),
         float(rec.get("totalpercover") or 0), float(rec.get("amount") or 0),
         float(rec.get("advance") or 0), rec.get("narration", ""),
         SITE_CODE),
        cn=cn, commit=commit)


def hallsale1est_delete(docid: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM HallSale1Est WHERE DocId = ?", (docid,),
                      cn=cn, commit=commit)


class _HallSale1EstAPI:
    LIMITS = {"docid": 30, "vtype": 5, "party": 30}
    @staticmethod
    def list_all(cn=None, limit=500): return hallsale1est_list(cn, limit)
    @staticmethod
    def get(docid, cn=None): return hallsale1est_get(docid, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return hallsale1est_insert(rec, cn, commit)
    @staticmethod
    def delete(docid, cn=None, commit=True): return hallsale1est_delete(docid, cn, commit)

HallSale1EstAPI = _HallSale1EstAPI()


# ============================================================
# SunTranEst - Estimate Sundry Transactions
# ============================================================
_SUNTRANEST_COLS = (
    "DocId, Sno, Vtype, VNo, Vdate, PartyCode, SunCode, Limit, "
    "DispName, ROff, CalcFormula, SValue, Amount, BaseAmount, "
    "U_Name, U_EntDt, U_AE, SunAppDate, RevCode, RestCode, "
    "DelFlag, SiteCode, LogSite_Code"
)


def _map_suntranest(r) -> dict:
    try:
        return {
            "docid": r.DocId or "", "sno": int(r.Sno or 0),
            "vtype": r.Vtype or "", "vno": int(r.VNo or 0),
            "vdate": r.Vdate, "partycode": r.PartyCode or "",
            "suncode": r.SunCode or "", "limit": float(r.Limit or 0),
            "dispname": r.DispName or "", "roff": float(r.ROff or 0),
            "calcformula": r.CalcFormula or "",
            "svalue": float(r.SValue or 0),
            "amount": float(r.Amount or 0),
            "baseamount": float(r.BaseAmount or 0),
            "sunappdate": r.SunAppDate, "revcode": r.RevCode or "",
            "restcode": r.RestCode or "",
            "delflag": r.DelFlag or "", "sitecode": r.SiteCode or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        vals = list(r)
        return {
            "docid": vals[0] or "", "sno": int(vals[1] or 0),
            "vtype": vals[2] or "", "vno": int(vals[3] or 0),
            "vdate": vals[4], "partycode": vals[5] or "",
            "suncode": vals[6] or "", "limit": float(vals[7] or 0),
            "dispname": vals[8] or "", "roff": float(vals[9] or 0),
            "calcformula": vals[10] or "",
            "svalue": float(vals[11] or 0),
            "amount": float(vals[12] or 0),
            "baseamount": float(vals[13] or 0),
            "sunappdate": vals[17], "revcode": vals[18] or "",
            "restcode": vals[19] or "",
            "delflag": vals[20] or "", "sitecode": vals[21] or "",
            "u_name": vals[14] or "", "u_ae": vals[16] or "",
        }


def suntranest_list_by_doc(docid: str, cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {_SUNTRANEST_COLS} FROM SunTranEst WHERE DocId = ? ORDER BY Sno",
        (docid,), cn=cn)
    return [_map_suntranest(r) for r in rows]


def suntranest_get(docid: str, sno: int, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {_SUNTRANEST_COLS} FROM SunTranEst WHERE DocId = ? AND Sno = ?",
        (docid, sno), cn=cn)
    return _map_suntranest(rows[0]) if rows else None


def suntranest_insert(rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "INSERT INTO SunTranEst (DocId, Sno, Vtype, VNo, Vdate, PartyCode, "
        "SunCode, Limit, DispName, ROff, CalcFormula, SValue, Amount, "
        "BaseAmount, U_Name, U_EntDt, U_AE, SunAppDate, RevCode, RestCode, "
        "DelFlag, SiteCode, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', "
        "getdate(), ?, ?, 'N', ?, ?)",
        (rec["docid"], int(rec.get("sno") or 0), rec.get("vtype", ""),
         int(rec.get("vno") or 0), rec.get("vdate"),
         rec.get("partycode", ""), rec.get("suncode", ""),
         float(rec.get("limit") or 0), rec.get("dispname", ""),
         float(rec.get("roff") or 0), rec.get("calcformula", ""),
         float(rec.get("svalue") or 0), float(rec.get("amount") or 0),
         float(rec.get("baseamount") or 0), USER,
         rec.get("revcode", ""), rec.get("restcode", ""),
         SITE_CODE, SITE_CODE),
        cn=cn, commit=commit)


def suntranest_delete(docid: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM SunTranEst WHERE DocId = ?", (docid,),
                      cn=cn, commit=commit)


class _SunTranEstAPI:
    @staticmethod
    def list_by_doc(docid, cn=None): return suntranest_list_by_doc(docid, cn)
    @staticmethod
    def get(docid, sno, cn=None): return suntranest_get(docid, sno, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return suntranest_insert(rec, cn, commit)
    @staticmethod
    def delete(docid, cn=None, commit=True): return suntranest_delete(docid, cn, commit)

SunTranEstAPI = _SunTranEstAPI()


# ============================================================
# SunTranHEst - Hall Estimate Sundry (same schema as SunTranEst)
# ============================================================
def suntranhest_list_by_doc(docid: str, cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {_SUNTRANEST_COLS} FROM SunTranHEst WHERE DocId = ? ORDER BY Sno",
        (docid,), cn=cn)
    return [_map_suntranest(r) for r in rows]


def suntranhest_get(docid: str, sno: int, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {_SUNTRANEST_COLS} FROM SunTranHEst WHERE DocId = ? AND Sno = ?",
        (docid, sno), cn=cn)
    return _map_suntranest(rows[0]) if rows else None


def suntranhest_insert(rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "INSERT INTO SunTranHEst (DocId, Sno, Vtype, VNo, Vdate, PartyCode, "
        "SunCode, Limit, DispName, ROff, CalcFormula, SValue, Amount, "
        "BaseAmount, U_Name, U_EntDt, U_AE, SunAppDate, RevCode, RestCode, "
        "DelFlag, SiteCode, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', "
        "getdate(), ?, ?, 'N', ?, ?)",
        (rec["docid"], int(rec.get("sno") or 0), rec.get("vtype", ""),
         int(rec.get("vno") or 0), rec.get("vdate"),
         rec.get("partycode", ""), rec.get("suncode", ""),
         float(rec.get("limit") or 0), rec.get("dispname", ""),
         float(rec.get("roff") or 0), rec.get("calcformula", ""),
         float(rec.get("svalue") or 0), float(rec.get("amount") or 0),
         float(rec.get("baseamount") or 0), USER,
         rec.get("revcode", ""), rec.get("restcode", ""),
         SITE_CODE, SITE_CODE),
        cn=cn, commit=commit)


def suntranhest_delete(docid: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM SunTranHEst WHERE DocId = ?", (docid,),
                      cn=cn, commit=commit)


class _SunTranHEstAPI:
    @staticmethod
    def list_by_doc(docid, cn=None): return suntranhest_list_by_doc(docid, cn)
    @staticmethod
    def get(docid, sno, cn=None): return suntranhest_get(docid, sno, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return suntranhest_insert(rec, cn, commit)
    @staticmethod
    def delete(docid, cn=None, commit=True): return suntranhest_delete(docid, cn, commit)

SunTranHEstAPI = _SunTranHEstAPI()


# ============================================================
# HallPreCosting - Chef Pre-Costing
# ============================================================
_HALLPRECOSTING_COLS = (
    "Docid, Sno, Vtype, Vtime, Vno, Site_Code, Vprefix, Vdate, RestCode, "
    "Item, Qty, Rate, Amount, VoidYN, Waiter, Pending, KOTType, "
    "U_Name, U_EntDt, U_AE, DelFlag, NCKOT, ContraDocId, ContraSno, "
    "DepartCode, Reasons, LogSite_Code"
)


def _map_precosting(r) -> dict:
    try:
        return {
            "docid": r.Docid or "", "sno": int(r.Sno or 0),
            "vtype": r.Vtype or "", "vtime": r.Vtime or "",
            "vno": int(r.Vno or 0), "site_code": r.Site_Code or "",
            "vprefix": r.Vprefix or "", "vdate": r.Vdate,
            "restcode": r.RestCode or "",
            "item": r.Item or "", "qty": float(r.Qty or 0),
            "rate": float(r.Rate or 0), "amount": float(r.Amount or 0),
            "voidyn": r.VoidYN or "", "waiter": r.Waiter or "",
            "pending": r.Pending or "", "kottype": r.KOTType or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
            "delflag": r.DelFlag or "", "nckot": r.NCKOT or "",
            "contradocid": r.ContraDocId or "",
            "contrasno": int(r.ContraSno or 0),
            "departcode": r.DepartCode or "", "reasons": r.Reasons or "",
        }
    except AttributeError:
        vals = list(r)
        return {
            "docid": vals[0] or "", "sno": int(vals[1] or 0),
            "vtype": vals[2] or "", "vtime": vals[3] or "",
            "vno": int(vals[4] or 0), "site_code": vals[5] or "",
            "vprefix": vals[6] or "", "vdate": vals[7],
            "restcode": vals[8] or "",
            "item": vals[9] or "", "qty": float(vals[10] or 0),
            "rate": float(vals[11] or 0), "amount": float(vals[12] or 0),
            "voidyn": vals[13] or "", "waiter": vals[14] or "",
            "pending": vals[15] or "", "kottype": vals[16] or "",
            "u_name": vals[17] or "", "u_ae": vals[19] or "",
            "delflag": vals[20] or "", "nckot": vals[21] or "",
            "contradocid": vals[22] or "",
            "contrasno": int(vals[23] or 0),
            "departcode": vals[24] or "", "reasons": vals[25] or "",
        }


def precosting_list(cn=None, limit: int = 500) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} {_HALLPRECOSTING_COLS} FROM HallPreCosting ORDER BY U_EntDt DESC",
        cn=cn)
    return [_map_precosting(r) for r in rows]


def precosting_list_by_doc(docid: str, cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {_HALLPRECOSTING_COLS} FROM HallPreCosting WHERE Docid = ? ORDER BY Sno",
        (docid,), cn=cn)
    return [_map_precosting(r) for r in rows]


def precosting_get(docid: str, sno: int, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {_HALLPRECOSTING_COLS} FROM HallPreCosting WHERE Docid = ? AND Sno = ?",
        (docid, sno), cn=cn)
    return _map_precosting(rows[0]) if rows else None


def precosting_insert(rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "INSERT INTO HallPreCosting (Docid, Sno, Vtype, Vtime, Vno, "
        "Site_Code, Vprefix, Vdate, RestCode, Item, Qty, Rate, Amount, "
        "VoidYN, Waiter, Pending, KOTType, U_Name, U_EntDt, U_AE, "
        "DelFlag, NCKOT, ContraDocId, ContraSno, DepartCode, Reasons, "
        "LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
        "getdate(), 'A', 'N', ?, ?, ?, ?, ?, ?)",
        (rec["docid"], int(rec.get("sno") or 0), rec.get("vtype", ""),
         rec.get("vtime", ""), int(rec.get("vno") or 0), SITE_CODE,
         rec.get("vprefix", ""), rec.get("vdate"), rec.get("restcode", ""),
         rec.get("item", ""), float(rec.get("qty") or 0),
         float(rec.get("rate") or 0), float(rec.get("amount") or 0),
         rec.get("voidyn", ""), rec.get("waiter", ""),
         rec.get("pending", ""), rec.get("kottype", ""),
         USER, rec.get("nckot", ""), rec.get("contradocid", ""),
         int(rec.get("contrasno") or 0), rec.get("departcode", ""),
         rec.get("reasons", ""), SITE_CODE),
        cn=cn, commit=commit)


def precosting_delete(docid: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM HallPreCosting WHERE Docid = ?", (docid,),
                      cn=cn, commit=commit)


class _HallPreCostingAPI:
    LIMITS = {"docid": 30, "vtype": 5, "item": 10}
    @staticmethod
    def list_all(cn=None, limit=500): return precosting_list(cn, limit)
    @staticmethod
    def list_by_doc(docid, cn=None): return precosting_list_by_doc(docid, cn)
    @staticmethod
    def get(docid, sno, cn=None): return precosting_get(docid, sno, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return precosting_insert(rec, cn, commit)
    @staticmethod
    def delete(docid, cn=None, commit=True): return precosting_delete(docid, cn, commit)

HallPreCostingAPI = _HallPreCostingAPI()
