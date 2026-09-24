"""POS Sales core module - Sale1/Sale2/SunTran/PayCharge CRUD.

VB6 references: RSSaleBill, FrmPOSBillDeletion, Sale entry forms.
Tables verified in DB KailashData2526:
  Sale1   - sale header (DocId PK-like, Vtype, VNo, NetAmt, etc.)
  Sale2   - sale detail lines (DocId+Sno, Item, Qty, Rate, Amount)
  SunTran - sundry transaction posting
  PayCharge - payment/collection entries
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()


# ============================================================
# Sale1 - Sale Header
# ============================================================
_SALE1_COLS = (
    "DocId, Vtype, VNo, Vtime, Site_Code, Vprefix, Vdate, RestCode, "
    "RoomCat, RoomType, RoomNo, FolioNo, Party, Total, DiscPer, DiscAmt, "
    "NonTaxable, Taxable, Tax, ServiceCharge, AddAmt, DedAmt, RoundOff, "
    "NetAmt, Remark, Waiter, FrBookDate, FrBookTime, MenuSpl1, MenuSpl2, "
    "MenuSpl3, MenuSpl4, FuncName, KOTNo, TokenNo, U_Name, U_EntDt, U_AE, "
    "DeliveredYN, PhoneNo, CustName, Addr1, Addr2, CashRecd, BookNo, SeqNo, "
    "CardNo, ServiceTax, CGST, SGST, IGST, EditRemark, PRINTED, DelFlag, "
    "LogSite_Code, RecNo, RecDate, CrCardNo, CrCardHolder, BookDocId, "
    "HallRent, TotalPerCover, Amount, Advance, FolionoDocid"
)


def _map_sale1(r) -> dict:
    try:
        return {
            "docid": r.DocId or "", "vtype": r.Vtype or "",
            "vno": int(r.VNo or 0), "vtime": r.Vtime or "",
            "site_code": r.Site_Code or "", "vprefix": r.Vprefix or "",
            "vdate": r.Vdate, "restcode": r.RestCode or "",
            "roomcat": r.RoomCat or "", "roomtype": r.RoomType or "",
            "roomno": r.RoomNo or "", "foliono": r.FolioNo or "",
            "party": r.Party or "", "total": float(r.Total or 0),
            "discper": float(r.DiscPer or 0), "discamt": float(r.DiscAmt or 0),
            "nontaxable": float(r.NonTaxable or 0), "taxable": float(r.Taxable or 0),
            "tax": float(r.Tax or 0), "servicecharge": float(r.ServiceCharge or 0),
            "addamt": float(r.AddAmt or 0), "dedamt": float(r.DedAmt or 0),
            "roundoff": float(r.RoundOff or 0), "netamt": float(r.NetAmt or 0),
            "remark": r.Remark or "", "waiter": r.Waiter or "",
            "kotno": r.KOTNo or "", "tokenno": r.TokenNo or "",
            "custname": r.CustName or "", "phoneno": r.PhoneNo or "",
            "addr1": r.Addr1 or "", "addr2": r.Addr2 or "",
            "cashrcd": float(r.CashRecd or 0), "printed": r.PRINTED or "",
            "delflag": r.DelFlag or "", "deliveredyn": r.DeliveredYN or "",
            "cgst": float(r.CGST or 0), "sgst": float(r.SGST or 0),
            "igst": float(r.IGST or 0), "hallrent": float(r.HallRent or 0),
            "amount": float(r.Amount or 0), "advance": float(r.Advance or 0),
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        vals = list(r)
        return {
            "docid": vals[0] or "", "vtype": vals[1] or "",
            "vno": int(vals[2] or 0), "vtime": vals[3] or "",
            "site_code": vals[4] or "", "vprefix": vals[5] or "",
            "vdate": vals[6], "restcode": vals[7] or "",
            "roomcat": vals[8] or "", "roomtype": vals[9] or "",
            "roomno": vals[10] or "", "foliono": vals[11] or "",
            "party": vals[12] or "", "total": float(vals[13] or 0),
            "discper": float(vals[14] or 0), "discamt": float(vals[15] or 0),
            "nontaxable": float(vals[16] or 0), "taxable": float(vals[17] or 0),
            "tax": float(vals[18] or 0), "servicecharge": float(vals[19] or 0),
            "addamt": float(vals[20] or 0), "dedamt": float(vals[21] or 0),
            "roundoff": float(vals[22] or 0), "netamt": float(vals[23] or 0),
            "remark": vals[24] or "", "waiter": vals[25] or "",
            "kotno": vals[33] or "", "tokenno": vals[34] or "",
            "custname": vals[40] or "", "phoneno": vals[39] or "",
            "addr1": vals[41] or "", "addr2": vals[42] or "",
            "cashrcd": float(vals[43] or 0), "printed": vals[51] or "",
            "delflag": vals[52] or "", "deliveredyn": vals[38] or "",
            "cgst": float(vals[47] or 0), "sgst": float(vals[48] or 0),
            "igst": float(vals[49] or 0), "hallrent": float(vals[58] or 0),
            "amount": float(vals[60] or 0), "advance": float(vals[61] or 0),
            "u_name": vals[35] or "", "u_ae": vals[37] or "",
        }


def _validate_sale1(rec: dict):
    if not rec.get("docid", "").strip():
        raise ValueError("DocId zaroori hai")
    if not rec.get("vtype", "").strip():
        raise ValueError("Vtype zaroori hai")


def sale1_list(cn=None, limit: int = 500) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} {_SALE1_COLS} FROM Sale1 ORDER BY U_EntDt DESC",
        cn=cn)
    return [_map_sale1(r) for r in rows]


def sale1_search(name_part: str, cn=None, limit: int = 100) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} {_SALE1_COLS} FROM Sale1 "
        "WHERE CustName LIKE ? ORDER BY U_EntDt DESC",
        (f"%{name_part}%",), cn=cn)
    return [_map_sale1(r) for r in rows]


def sale1_get(docid: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {_SALE1_COLS} FROM Sale1 WHERE DocId = ?",
        (docid,), cn=cn)
    return _map_sale1(rows[0]) if rows else None


def sale1_insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate_sale1(rec)
    return db.execute(
        "INSERT INTO Sale1 (DocId, Vtype, VNo, Vtime, Site_Code, Vprefix, "
        "Vdate, RestCode, RoomCat, RoomType, RoomNo, FolioNo, Party, Total, "
        "DiscPer, DiscAmt, NonTaxable, Taxable, Tax, ServiceCharge, AddAmt, "
        "DedAmt, RoundOff, NetAmt, Remark, Waiter, KOTNo, TokenNo, "
        "CustName, PhoneNo, Addr1, Addr2, CashRecd, PRINTED, DelFlag, "
        "DeliveredYN, CGST, SGST, IGST, HallRent, Amount, Advance, "
        "U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
        "?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
        "?, ?, ?, getdate(), 'A', ?)",
        (rec["docid"], rec["vtype"], int(rec.get("vno") or 0),
         rec.get("vtime", ""), SITE_CODE, rec.get("vprefix", ""),
         rec.get("vdate"), rec.get("restcode", ""),
         rec.get("roomcat", ""), rec.get("roomtype", ""),
         rec.get("roomno", ""), rec.get("foliono", ""),
         rec.get("party", ""), float(rec.get("total") or 0),
         float(rec.get("discper") or 0), float(rec.get("discamt") or 0),
         float(rec.get("nontaxable") or 0), float(rec.get("taxable") or 0),
         float(rec.get("tax") or 0), float(rec.get("servicecharge") or 0),
         float(rec.get("addamt") or 0), float(rec.get("dedamt") or 0),
         float(rec.get("roundoff") or 0), float(rec.get("netamt") or 0),
         rec.get("remark", ""), rec.get("waiter", ""),
         rec.get("kotno", ""), rec.get("tokenno", ""),
         rec.get("custname", ""), rec.get("phoneno", ""),
         rec.get("addr1", ""), rec.get("addr2", ""),
         float(rec.get("cashrcd") or 0), rec.get("printed", ""),
         rec.get("delflag", ""), rec.get("deliveredyn", ""),
         float(rec.get("cgst") or 0), float(rec.get("sgst") or 0),
         float(rec.get("igst") or 0), float(rec.get("hallrent") or 0),
         float(rec.get("amount") or 0), float(rec.get("advance") or 0),
         USER, SITE_CODE),
        cn=cn, commit=commit)


def sale1_update(docid: str, rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "UPDATE Sale1 SET CustName = ?, PhoneNo = ?, Addr1 = ?, Addr2 = ?, "
        "Remark = ?, Total = ?, DiscPer = ?, DiscAmt = ?, Tax = ?, "
        "ServiceCharge = ?, AddAmt = ?, DedAmt = ?, RoundOff = ?, NetAmt = ?, "
        "CGST = ?, SGST = ?, IGST = ?, CashRecd = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE DocId = ?",
        (rec.get("custname", ""), rec.get("phoneno", ""),
         rec.get("addr1", ""), rec.get("addr2", ""),
         rec.get("remark", ""), float(rec.get("total") or 0),
         float(rec.get("discper") or 0), float(rec.get("discamt") or 0),
         float(rec.get("tax") or 0), float(rec.get("servicecharge") or 0),
         float(rec.get("addamt") or 0), float(rec.get("dedamt") or 0),
         float(rec.get("roundoff") or 0), float(rec.get("netamt") or 0),
         float(rec.get("cgst") or 0), float(rec.get("sgst") or 0),
         float(rec.get("igst") or 0), float(rec.get("cashrcd") or 0),
         USER, docid),
        cn=cn, commit=commit)


def sale1_delete(docid: str, cn=None, commit: bool = True) -> int:
    own = cn is None
    cn = cn or db.connect()
    try:
        db.execute(
            "UPDATE KOT SET Pending = 'Y', ContraDocId = NULL, ContraSNo = 0 "
            "WHERE ContraDocId = ?",
            (docid,), cn=cn, commit=False)
        db.execute("DELETE FROM Sale2 WHERE DocId = ?", (docid,),
                   cn=cn, commit=False)
        db.execute("DELETE FROM SunTran WHERE DocId = ?", (docid,),
                   cn=cn, commit=False)
        db.execute("DELETE FROM PayCharge WHERE DocId = ?", (docid,),
                   cn=cn, commit=False)
        n = db.execute("DELETE FROM Sale1 WHERE DocId = ?", (docid,),
                       cn=cn, commit=False)
        if commit:
            cn.commit()
        return n
    finally:
        if own:
            cn.close()


class _Sale1API:
    LIMITS = {"docid": 30, "vtype": 5, "custname": 40, "phoneno": 15}
    @staticmethod
    def list_all(cn=None, limit=500): return sale1_list(cn, limit)
    @staticmethod
    def search(name_part, cn=None, limit=100): return sale1_search(name_part, cn, limit)
    @staticmethod
    def get(docid, cn=None): return sale1_get(docid, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return sale1_insert(rec, cn, commit)
    @staticmethod
    def update(docid, rec, cn=None, commit=True): return sale1_update(docid, rec, cn, commit)
    @staticmethod
    def delete(docid, cn=None, commit=True): return sale1_delete(docid, cn, commit)

Sale1API = _Sale1API()


# ============================================================
# Sale2 - Sale Detail Lines
# ============================================================
_SALE2_COLS = (
    "DocId, Sno, SNo1, Vtype, VNo, Site_Code, Vprefix, Vdate, RestCode, "
    "TaxCode, BaseValue, TaxPer, TaxAmt, U_Name, U_EntDt, U_AE, "
    "DelFlag, LogSite_Code, SeqNo"
)


def _map_sale2(r) -> dict:
    try:
        return {
            "docid": r.DocId or "", "sno": int(r.Sno or 0),
            "sno1": int(r.SNo1 or 0), "vtype": r.Vtype or "",
            "vno": int(r.VNo or 0), "site_code": r.Site_Code or "",
            "vprefix": r.Vprefix or "", "vdate": r.Vdate,
            "restcode": r.RestCode or "", "taxcode": r.TaxCode or "",
            "basevalue": float(r.BaseValue or 0), "taxper": float(r.TaxPer or 0),
            "taxamt": float(r.TaxAmt or 0),
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
            "delflag": r.DelFlag or "", "seqno": int(r.SeqNo or 0),
        }
    except AttributeError:
        vals = list(r)
        return {
            "docid": vals[0] or "", "sno": int(vals[1] or 0),
            "sno1": int(vals[2] or 0), "vtype": vals[3] or "",
            "vno": int(vals[4] or 0), "site_code": vals[5] or "",
            "vprefix": vals[6] or "", "vdate": vals[7],
            "restcode": vals[8] or "", "taxcode": vals[9] or "",
            "basevalue": float(vals[10] or 0), "taxper": float(vals[11] or 0),
            "taxamt": float(vals[12] or 0),
            "u_name": vals[13] or "", "u_ae": vals[15] or "",
            "delflag": vals[16] or "", "seqno": int(vals[18] or 0),
        }


def sale2_list_by_doc(docid: str, cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {_SALE2_COLS} FROM Sale2 WHERE DocId = ? ORDER BY Sno",
        (docid,), cn=cn)
    return [_map_sale2(r) for r in rows]


def sale2_get(docid: str, sno: int, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {_SALE2_COLS} FROM Sale2 WHERE DocId = ? AND Sno = ?",
        (docid, sno), cn=cn)
    return _map_sale2(rows[0]) if rows else None


def sale2_insert(rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "INSERT INTO Sale2 (DocId, Sno, SNo1, Vtype, VNo, Site_Code, "
        "Vprefix, Vdate, RestCode, TaxCode, BaseValue, TaxPer, TaxAmt, "
        "U_Name, U_EntDt, U_AE, DelFlag, LogSite_Code, SeqNo) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', "
        "'N', ?, ?)",
        (rec["docid"], int(rec.get("sno") or 0), int(rec.get("sno1") or 0),
         rec.get("vtype", ""), int(rec.get("vno") or 0), SITE_CODE,
         rec.get("vprefix", ""), rec.get("vdate"), rec.get("restcode", ""),
         rec.get("taxcode", ""), float(rec.get("basevalue") or 0),
         float(rec.get("taxper") or 0), float(rec.get("taxamt") or 0),
         USER, SITE_CODE, int(rec.get("seqno") or 0)),
        cn=cn, commit=commit)


def sale2_delete(docid: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM Sale2 WHERE DocId = ?", (docid,),
                      cn=cn, commit=commit)


class _Sale2API:
    @staticmethod
    def list_by_doc(docid, cn=None): return sale2_list_by_doc(docid, cn)
    @staticmethod
    def get(docid, sno, cn=None): return sale2_get(docid, sno, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return sale2_insert(rec, cn, commit)
    @staticmethod
    def delete(docid, cn=None, commit=True): return sale2_delete(docid, cn, commit)

Sale2API = _Sale2API()


# ============================================================
# SunTran - Sundry Transaction Posting
# ============================================================
_SUNTRAN_COLS = (
    "DocId, Sno, Vtype, VNo, Vdate, PartyCode, SunCode, Limit, "
    "DispName, ROff, CalcFormula, SValue, Amount, BaseAmount, "
    "U_Name, U_EntDt, U_AE, SunAppDate, RevCode, RestCode, "
    "DelFlag, SiteCode, LogSite_Code, SeqNo"
)


def _map_suntran(r) -> dict:
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
            "seqno": int(r.SeqNo or 0),
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
            "seqno": int(vals[23] if len(vals) > 23 else 0),
            "u_name": vals[14] or "", "u_ae": vals[16] or "",
        }


def suntran_list_by_doc(docid: str, cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {_SUNTRAN_COLS} FROM SunTran WHERE DocId = ? ORDER BY Sno",
        (docid,), cn=cn)
    return [_map_suntran(r) for r in rows]


def suntran_get(docid: str, sno: int, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {_SUNTRAN_COLS} FROM SunTran WHERE DocId = ? AND Sno = ?",
        (docid, sno), cn=cn)
    return _map_suntran(rows[0]) if rows else None


def suntran_insert(rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "INSERT INTO SunTran (DocId, Sno, Vtype, VNo, Vdate, PartyCode, "
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


def suntran_delete(docid: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM SunTran WHERE DocId = ?", (docid,),
                      cn=cn, commit=commit)


class _SunTranAPI:
    @staticmethod
    def list_by_doc(docid, cn=None): return suntran_list_by_doc(docid, cn)
    @staticmethod
    def get(docid, sno, cn=None): return suntran_get(docid, sno, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return suntran_insert(rec, cn, commit)
    @staticmethod
    def delete(docid, cn=None, commit=True): return suntran_delete(docid, cn, commit)

SunTranAPI = _SunTranAPI()


# ============================================================
# PayCharge - Payment Collection
# ============================================================
_PAYCHARGE_COLS = (
    "DocId, SNo, Vtype, VNo, Site_Code, VPrefix, Vdate, VTime, "
    "GuestProf, EmpCode, CompCode, Comments, PayCode, PayType, "
    "AmtCr, AmtDr, TipAmt, RoomCat, RoomType, RoomNo, FolioNo, "
    "CardNo, CardHolder, ChqNo, ChqDate, ExpDate, BookNo, BookType, "
    "U_Name, U_EntDt, U_AE, RestCode, BillAmount, ContraDocID, "
    "TaxPer, OnAmt, Split, Bill_No, SettleDate, BatchNo, "
    "Remarks, RefNo, PlanCode, SeqNo, RefDocId, "
    "LogSite_Code, AU_Name, AU_EntDt"
)


def _map_paycharge(r) -> dict:
    try:
        return {
            "docid": r.DocId or "", "sno": int(r.SNo or 0),
            "vtype": r.Vtype or "", "vno": int(r.VNo or 0),
            "site_code": r.Site_Code or "", "vprefix": r.VPrefix or "",
            "vdate": r.Vdate, "vtime": r.VTime or "",
            "guestprof": r.GuestProf or "", "empcode": r.EmpCode or "",
            "compcode": r.CompCode or "", "comments": r.Comments or "",
            "paycode": r.PayCode or "", "paytype": r.PayType or "",
            "amtcr": float(r.AmtCr or 0), "amtdr": float(r.AmtDr or 0),
            "tipamt": float(r.TipAmt or 0),
            "roomcat": r.RoomCat or "", "roomtype": r.RoomType or "",
            "roomno": r.RoomNo or "", "foliono": r.FolioNo or "",
            "cardno": r.CardNo or "", "cardholder": r.CardHolder or "",
            "chqno": r.ChqNo or "",
            "restcode": r.RestCode or "", "billamount": float(r.BillAmount or 0),
            "contradocid": r.ContraDocID or "",
            "taxper": float(r.TaxPer or 0), "onamt": float(r.OnAmt or 0),
            "split": r.Split or "", "bill_no": r.Bill_No or "",
            "settledate": r.SettleDate, "batchno": r.BatchNo or "",
            "remarks": r.Remarks or "", "refno": r.RefNo or "",
            "plancode": r.PlanCode or "", "seqno": int(r.SeqNo or 0),
            "refdocid": r.RefDocId or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        vals = list(r)
        return {
            "docid": vals[0] or "", "sno": int(vals[1] or 0),
            "vtype": vals[2] or "", "vno": int(vals[3] or 0),
            "site_code": vals[4] or "", "vprefix": vals[5] or "",
            "vdate": vals[6], "vtime": vals[7] or "",
            "guestprof": vals[8] or "", "empcode": vals[9] or "",
            "compcode": vals[10] or "", "comments": vals[11] or "",
            "paycode": vals[12] or "", "paytype": vals[13] or "",
            "amtcr": float(vals[14] or 0), "amtdr": float(vals[15] or 0),
            "tipamt": float(vals[16] or 0),
            "roomcat": vals[17] or "", "roomtype": vals[18] or "",
            "roomno": vals[19] or "", "foliono": vals[20] or "",
            "cardno": vals[21] or "", "cardholder": vals[22] or "",
            "chqno": vals[23] or "",
            "restcode": vals[31] or "", "billamount": float(vals[32] or 0),
            "contradocid": vals[33] or "",
            "taxper": float(vals[36] or 0), "onamt": float(vals[37] or 0),
            "split": vals[38] or "", "bill_no": vals[39] or "",
            "settledate": vals[41] if len(vals) > 41 else None,
            "batchno": vals[42] if len(vals) > 42 else "",
            "remarks": vals[45] if len(vals) > 45 else "",
            "refno": vals[46] if len(vals) > 46 else "",
            "plancode": vals[48] if len(vals) > 48 else "",
            "seqno": int(vals[49] if len(vals) > 49 else 0),
            "refdocid": vals[44] if len(vals) > 44 else "",
            "u_name": vals[28] or "", "u_ae": vals[30] or "",
        }


def paycharge_list_by_doc(docid: str, cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {_PAYCHARGE_COLS} FROM PayCharge WHERE DocId = ? ORDER BY SNo",
        (docid,), cn=cn)
    return [_map_paycharge(r) for r in rows]


def paycharge_get(docid: str, sno: int, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {_PAYCHARGE_COLS} FROM PayCharge WHERE DocId = ? AND SNo = ?",
        (docid, sno), cn=cn)
    return _map_paycharge(rows[0]) if rows else None


def paycharge_insert(rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "INSERT INTO PayCharge (DocId, SNo, Vtype, VNo, Site_Code, VPrefix, "
        "Vdate, VTime, GuestProf, EmpCode, CompCode, Comments, PayCode, "
        "PayType, AmtCr, AmtDr, TipAmt, RoomCat, RoomType, RoomNo, FolioNo, "
        "CardNo, CardHolder, ChqNo, ChqDate, ExpDate, BookNo, BookType, "
        "U_Name, U_EntDt, U_AE, RestCode, BillAmount, ContraDocID, "
        "TaxPer, OnAmt, Split, Bill_No, SettleDate, BatchNo, Remarks, "
        "RefNo, PlanCode, SeqNo, RefDocId, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
        "?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?, ?, ?, ?, ?, "
        "?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (rec["docid"], int(rec.get("sno") or 0), rec.get("vtype", ""),
         int(rec.get("vno") or 0), SITE_CODE, rec.get("vprefix", ""),
         rec.get("vdate"), rec.get("vtime", ""),
         rec.get("guestprof", ""), rec.get("empcode", ""),
         rec.get("compcode", ""), rec.get("comments", ""),
         rec.get("paycode", ""), rec.get("paytype", ""),
         float(rec.get("amtcr") or 0), float(rec.get("amtdr") or 0),
         float(rec.get("tipamt") or 0),
         rec.get("roomcat", ""), rec.get("roomtype", ""),
         rec.get("roomno", ""), rec.get("foliono", ""),
         rec.get("cardno", ""), rec.get("cardholder", ""),
         rec.get("chqno", ""), rec.get("chqdate"), rec.get("expdate"),
         rec.get("bookno", ""), rec.get("booktype", ""),
         USER, rec.get("restcode", ""),
         float(rec.get("billamount") or 0), rec.get("contradocid", ""),
         float(rec.get("taxper") or 0), float(rec.get("onamt") or 0),
         rec.get("split", ""), rec.get("bill_no", ""),
         rec.get("settledate"), rec.get("batchno", ""),
         rec.get("remarks", ""), rec.get("refno", ""),
         rec.get("plancode", ""), int(rec.get("seqno") or 0),
         rec.get("refdocid", ""), SITE_CODE),
        cn=cn, commit=commit)


def paycharge_delete(docid: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM PayCharge WHERE DocId = ?", (docid,),
                      cn=cn, commit=commit)


class _PayChargeAPI:
    @staticmethod
    def list_by_doc(docid, cn=None): return paycharge_list_by_doc(docid, cn)
    @staticmethod
    def get(docid, sno, cn=None): return paycharge_get(docid, sno, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return paycharge_insert(rec, cn, commit)
    @staticmethod
    def delete(docid, cn=None, commit=True): return paycharge_delete(docid, cn, commit)

PayChargeAPI = _PayChargeAPI()


# ============================================================
# Full sale save (PI-2): Sale1 + Sale2 + SunTran + PayCharge
#                     + Stock QtyIss + KOT close (VB6 RSSaleBill)
# ============================================================
def sale_bill_full_save(header: dict,
                        sale2_lines: list[dict] | None = None,
                        suntran_lines: list[dict] | None = None,
                        paycharge_lines: list[dict] | None = None,
                        stock_lines: list[dict] | None = None,
                        close_kot_docids: list[str] | None = None,
                        cn=None, commit: bool = True) -> dict:
    """Atomic multi-table POS bill save (VB6 RSSaleBill 'Save').

    Writes on ONE shared connection:
      1. Sale1 header
      2. Sale2 tax-lines (DocId+Sno)
      3. SunTran sundry lines
      4. PayCharge payment lines
      5. Stock rows (QtyIss) for item consumption
      6. UPDATE KOT: Pending='N', ContraDocId=<sale DocId> (bill close)

    header keys: docid, vtype, vno, vdate, restcode, custname, total,
    taxable, tax, netamt, cgst, sgst, igst, servicecharge, roundoff, ...
    stock_lines: [{item, qty, rate, amount, unit, godown, sno}]
    close_kot_docids: KOT DocIds to settle against this bill.
    Returns {"docid", "sale2", "suntran", "paycharge", "stock", "kot_closed"}.
    """
    _validate_sale1(header)
    own = cn is None
    cn = cn or db.connect()
    try:
        sale1_insert(header, cn=cn, commit=False)
        docid = header["docid"]
        n_s2 = n_sun = n_pay = n_stk = 0
        for i, rec in enumerate(sale2_lines or [], 1):
            r = dict(rec)
            r.setdefault("docid", docid)
            r.setdefault("sno", i)
            r.setdefault("vtype", header.get("vtype", ""))
            r.setdefault("vno", header.get("vno") or 0)
            r.setdefault("vprefix", header.get("vprefix", ""))
            r.setdefault("vdate", header.get("vdate"))
            r.setdefault("restcode", header.get("restcode", ""))
            sale2_insert(r, cn=cn, commit=False)
            n_s2 += 1
        for i, rec in enumerate(suntran_lines or [], 1):
            r = dict(rec)
            r.setdefault("docid", docid)
            r.setdefault("sno", i)
            r.setdefault("vtype", header.get("vtype", ""))
            r.setdefault("vno", header.get("vno") or 0)
            r.setdefault("vdate", header.get("vdate"))
            r.setdefault("restcode", header.get("restcode", ""))
            suntran_insert(r, cn=cn, commit=False)
            n_sun += 1
        for i, rec in enumerate(paycharge_lines or [], 1):
            r = dict(rec)
            r.setdefault("docid", docid)
            r.setdefault("sno", i)
            r.setdefault("vtype", header.get("vtype", ""))
            r.setdefault("vno", header.get("vno") or 0)
            r.setdefault("vprefix", header.get("vprefix", ""))
            r.setdefault("vdate", header.get("vdate"))
            r.setdefault("restcode", header.get("restcode", ""))
            paycharge_insert(r, cn=cn, commit=False)
            n_pay += 1
        for i, rec in enumerate(stock_lines or [], 1):
            sno = int(rec.get("sno") or i)
            qty = abs(float(rec.get("qty") or 0))
            rate = float(rec.get("rate") or 0)
            amount = float(rec.get("amount") or 0) or qty * rate
            db.execute(
                "INSERT INTO Stock (DocId, Sno, Vtype, VNo, Site_Code, "
                "VPrefix, VDate, VTime, Item, QtyIss, QtyRec, Unit, Rate, "
                "Amount, GodownCode, RestCode, U_Name, U_EntDt, U_AE, "
                "LogSite_Code, DelFlag) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, '00:00', ?, ?, 0, ?, ?, ?, "
                "?, ?, ?, getdate(), 'A', ?, 'N')",
                (docid, sno, header.get("vtype", ""),
                 int(header.get("vno") or 0), SITE_CODE,
                 header.get("vprefix", ""), header.get("vdate"),
                 rec.get("item", ""), qty, rec.get("unit", ""),
                 rate, amount, rec.get("godown", ""),
                 header.get("restcode", ""), USER, SITE_CODE),
                cn=cn, commit=False)
            n_stk += 1
        n_kot = 0
        for kid in (close_kot_docids or []):
            if not kid:
                continue
            n_kot += db.execute(
                "UPDATE KOT SET Pending = 'N', ContraDocId = ?, "
                "U_Name = ?, U_AE = 'E', U_EntDt = getdate() "
                "WHERE DocId = ? AND ISNULL(VoidYN, 'N') <> 'Y'",
                (docid, USER, kid), cn=cn, commit=False)
        if commit:
            cn.commit()
        return {"docid": docid, "sale2": n_s2, "suntran": n_sun,
                "paycharge": n_pay, "stock": n_stk, "kot_closed": n_kot}
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


class _SaleBillAPI:
    @staticmethod
    def full_save(header, sale2_lines=None, suntran_lines=None,
                  paycharge_lines=None, stock_lines=None,
                  close_kot_docids=None, cn=None, commit=True):
        return sale_bill_full_save(
            header, sale2_lines, suntran_lines, paycharge_lines,
            stock_lines, close_kot_docids, cn, commit)

SaleBillAPI = _SaleBillAPI()
