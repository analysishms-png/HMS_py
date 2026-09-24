# P0 FIX HO+LOGSITE (VB6 parity) - 2026-09-24 via multi-agent compare
"""POS KOT enhancements - KOTLog/TOKEN/SplitBillDetail CRUD.

VB6 references: KOT audit trail, token order management, bill splitting.
Tables verified in DB KailashData2526:
  KOTLog        - KOT audit/change log (DocId+Sno, Item, Qty, Rate, Amount)
  TOKEN         - token order lines (DocId+Sno, Item, Qty, Rate, Amount)
  SplitBillDetail - bill splitting details (DocId+SNo, ItemName, BillQty)
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()

def _logsite(cn=None) -> str:
    try:
        return db.get_logsite_code(cn=cn)
    except Exception:
        return SITE_CODE


# ============================================================
# KOTLog - KOT Audit Trail
# ============================================================
_KOTLOG_COLS = (
    "DocId, Sno, Vtype, Vtime, VNo, Site_Code, Vprefix, Vdate, RestCode, "
    "RoomCat, RoomType, RoomNo, Item, Qty, Rate, Amount, VoidYN, Waiter, "
    "Pending, KOTType, U_Name, U_EntDt, U_AE, U_Name1, U_EntDt1, U_AE1, "
    "DelFlag, NCKOT, ContraDocId, ContraSNo, Reasons, LogSite_Code, "
    "FreeSno, SchemeCode, Party, ItemRestCode, SeqNo, TokenNo, PrintFlag"
)


def _map_kotlog(r) -> dict:
    try:
        return {
            "docid": r.DocId or "", "sno": int(r.Sno or 0),
            "vtype": r.Vtype or "", "vtime": r.Vtime or "",
            "vno": int(r.VNo or 0), "site_code": r.Site_Code or "",
            "vprefix": r.Vprefix or "", "vdate": r.Vdate,
            "restcode": r.RestCode or "",
            "roomcat": r.RoomCat or "", "roomtype": r.RoomType or "",
            "roomno": r.RoomNo or "",
            "item": r.Item or "", "qty": float(r.Qty or 0),
            "rate": float(r.Rate or 0), "amount": float(r.Amount or 0),
            "voidyn": r.VoidYN or "", "waiter": r.Waiter or "",
            "pending": r.Pending or "", "kottype": r.KOTType or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
            "delflag": r.DelFlag or "", "nckot": r.NCKOT or "",
            "contradocid": r.ContraDocId or "",
            "contrasno": int(r.ContraSNo or 0),
            "reasons": r.Reasons or "",
            "freesno": int(r.FreeSno or 0),
            "schemecode": r.SchemeCode or "", "party": r.Party or "",
            "itemrestcode": r.ItemRestCode or "",
            "tokenno": r.TokenNo or "", "printflag": r.PrintFlag or "",
        }
    except AttributeError:
        vals = list(r)
        return {
            "docid": vals[0] or "", "sno": int(vals[1] or 0),
            "vtype": vals[2] or "", "vtime": vals[3] or "",
            "vno": int(vals[4] or 0), "site_code": vals[5] or "",
            "vprefix": vals[6] or "", "vdate": vals[7],
            "restcode": vals[8] or "",
            "roomcat": vals[9] or "", "roomtype": vals[10] or "",
            "roomno": vals[11] or "",
            "item": vals[12] or "", "qty": float(vals[13] or 0),
            "rate": float(vals[14] or 0), "amount": float(vals[15] or 0),
            "voidyn": vals[16] or "", "waiter": vals[17] or "",
            "pending": vals[18] or "", "kottype": vals[19] or "",
            "u_name": vals[20] or "", "u_ae": vals[22] or "",
            "delflag": vals[26] or "", "nckot": vals[27] or "",
            "contradocid": vals[28] or "",
            "contrasno": int(vals[29] or 0),
            "reasons": vals[30] or "",
            "freesno": int(vals[32] if len(vals) > 32 else 0),
            "schemecode": vals[33] if len(vals) > 33 else "",
            "party": vals[34] if len(vals) > 34 else "",
            "itemrestcode": vals[35] if len(vals) > 35 else "",
            "tokenno": vals[37] if len(vals) > 37 else "",
            "printflag": vals[38] if len(vals) > 38 else "",
        }


def _validate_kotlog(rec: dict):
    if not rec.get("docid", "").strip():
        raise ValueError("DocId zaroori hai")


def kotlog_list(cn=None, limit: int = 500) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} {_KOTLOG_COLS} FROM KOTLog ORDER BY U_EntDt DESC",
        cn=cn)
    return [_map_kotlog(r) for r in rows]


def kotlog_list_by_doc(docid: str, cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {_KOTLOG_COLS} FROM KOTLog WHERE DocId = ? ORDER BY Sno",
        (docid,), cn=cn)
    return [_map_kotlog(r) for r in rows]


def kotlog_get(docid: str, sno: int, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {_KOTLOG_COLS} FROM KOTLog WHERE DocId = ? AND Sno = ?",
        (docid, sno), cn=cn)
    return _map_kotlog(rows[0]) if rows else None


def kotlog_insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate_kotlog(rec)
    ls = _logsite(cn)
    return db.execute(
        "INSERT INTO KOTLog (DocId, Sno, Vtype, Vtime, VNo, Site_Code, "
        "Vprefix, Vdate, RestCode, RoomCat, RoomType, RoomNo, Item, Qty, "
        "Rate, Amount, VoidYN, Waiter, Pending, KOTType, U_Name, U_EntDt, "
        "U_AE, DelFlag, NCKOT, ContraDocId, ContraSNo, Reasons, "
        "LogSite_Code, FreeSno, SchemeCode, Party, ItemRestCode, TokenNo, "
        "PrintFlag) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
        "?, ?, getdate(), 'A', 'N', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (rec["docid"], int(rec.get("sno") or 0), rec.get("vtype", ""),
         rec.get("vtime", ""), int(rec.get("vno") or 0), ls,
         rec.get("vprefix", ""), rec.get("vdate"), rec.get("restcode", ""),
         rec.get("roomcat", ""), rec.get("roomtype", ""),
         rec.get("roomno", ""), rec.get("item", ""),
         float(rec.get("qty") or 0), float(rec.get("rate") or 0),
         float(rec.get("amount") or 0), rec.get("voidyn", ""),
         rec.get("waiter", ""), rec.get("pending", ""),
         rec.get("kottype", ""), USER,
         rec.get("nckot", ""), rec.get("contradocid", ""),
         int(rec.get("contrasno") or 0), rec.get("reasons", ""),
         ls, int(rec.get("freesno") or 0),
         rec.get("schemecode", ""), rec.get("party", ""),
         rec.get("itemrestcode", ""), rec.get("tokenno", ""),
         rec.get("printflag", "")),
        cn=cn, commit=commit)


def kotlog_update(docid: str, sno: int, rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "UPDATE KOTLog SET Qty = ?, Rate = ?, Amount = ?, VoidYN = ?, "
        "U_Name1 = ?, U_EntDt1 = getdate(), U_AE1 = 'E' "
        "WHERE DocId = ? AND Sno = ?",
        (float(rec.get("qty") or 0), float(rec.get("rate") or 0),
         float(rec.get("amount") or 0), rec.get("voidyn", ""),
         USER, docid, sno),
        cn=cn, commit=commit)


def kotlog_delete(docid: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM KOTLog WHERE DocId = ?", (docid,),
                      cn=cn, commit=commit)


class _KOTLogAPI:
    LIMITS = {"docid": 30, "vtype": 5, "item": 10}
    @staticmethod
    def list_all(cn=None, limit=500): return kotlog_list(cn, limit)
    @staticmethod
    def list_by_doc(docid, cn=None): return kotlog_list_by_doc(docid, cn)
    @staticmethod
    def get(docid, sno, cn=None): return kotlog_get(docid, sno, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return kotlog_insert(rec, cn, commit)
    @staticmethod
    def update(docid, sno, rec, cn=None, commit=True): return kotlog_update(docid, sno, rec, cn, commit)
    @staticmethod
    def delete(docid, cn=None, commit=True): return kotlog_delete(docid, cn, commit)

KOTLogAPI = _KOTLogAPI()


# ============================================================
# TOKEN - Token Order Lines
# ============================================================
_TOKEN_COLS = (
    "DocId, Sno, Vtype, Vtime, VNo, Site_Code, Vprefix, Vdate, RestCode, "
    "RoomCat, RoomType, RoomNo, Item, Qty, Rate, Amount, VoidYN, Waiter, "
    "Pending, TOKENType, U_Name, U_EntDt, U_AE, U_Name1, U_EntDt1, U_AE1, "
    "DelFlag, NCTOKEN, ContraDocId, ContraSNo, Reasons, Remarks, "
    "LogSite_Code, NCTYPE, FreeSno, Printed, Description, SchemeCode, "
    "Party, TokenNo, CancelYN, ItemRestCode"
)


def _map_token(r) -> dict:
    try:
        return {
            "docid": r.DocId or "", "sno": int(r.Sno or 0),
            "vtype": r.Vtype or "", "vtime": r.Vtime or "",
            "vno": int(r.VNo or 0), "site_code": r.Site_Code or "",
            "vprefix": r.Vprefix or "", "vdate": r.Vdate,
            "restcode": r.RestCode or "",
            "roomcat": r.RoomCat or "", "roomtype": r.RoomType or "",
            "roomno": r.RoomNo or "",
            "item": r.Item or "", "qty": float(r.Qty or 0),
            "rate": float(r.Rate or 0), "amount": float(r.Amount or 0),
            "voidyn": r.VoidYN or "", "waiter": r.Waiter or "",
            "pending": r.Pending or "", "tokentype": r.TOKENType or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
            "delflag": r.DelFlag or "", "nctoken": r.NCTOKEN or "",
            "contradocid": r.ContraDocId or "",
            "contrasno": int(r.ContraSNo or 0),
            "reasons": r.Reasons or "", "remarks": r.Remarks or "",
            "nctype": r.NCTYPE or "",
            "freesno": int(r.FreeSno or 0), "printed": r.Printed or "",
            "description": r.Description or "",
            "schemecode": r.SchemeCode or "", "party": r.Party or "",
            "tokenno": r.TokenNo or "", "cancelyn": r.CancelYN or "",
            "itemrestcode": r.ItemRestCode or "",
        }
    except AttributeError:
        vals = list(r)
        return {
            "docid": vals[0] or "", "sno": int(vals[1] or 0),
            "vtype": vals[2] or "", "vtime": vals[3] or "",
            "vno": int(vals[4] or 0), "site_code": vals[5] or "",
            "vprefix": vals[6] or "", "vdate": vals[7],
            "restcode": vals[8] or "",
            "roomcat": vals[9] or "", "roomtype": vals[10] or "",
            "roomno": vals[11] or "",
            "item": vals[12] or "", "qty": float(vals[13] or 0),
            "rate": float(vals[14] or 0), "amount": float(vals[15] or 0),
            "voidyn": vals[16] or "", "waiter": vals[17] or "",
            "pending": vals[18] or "", "tokentype": vals[19] or "",
            "u_name": vals[20] or "", "u_ae": vals[22] or "",
            "delflag": vals[26] or "", "nctoken": vals[27] or "",
            "contradocid": vals[28] or "",
            "contrasno": int(vals[29] or 0),
            "reasons": vals[30] or "", "remarks": vals[31] or "",
            "nctype": vals[33] if len(vals) > 33 else "",
            "freesno": int(vals[34] if len(vals) > 34 else 0),
            "printed": vals[35] if len(vals) > 35 else "",
            "description": vals[36] if len(vals) > 36 else "",
            "schemecode": vals[37] if len(vals) > 37 else "",
            "party": vals[38] if len(vals) > 38 else "",
            "tokenno": vals[39] if len(vals) > 39 else "",
            "cancelyn": vals[40] if len(vals) > 40 else "",
            "itemrestcode": vals[41] if len(vals) > 41 else "",
        }


def _validate_token(rec: dict):
    if not rec.get("docid", "").strip():
        raise ValueError("DocId zaroori hai")


def token_list(cn=None, limit: int = 500) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} {_TOKEN_COLS} FROM TOKEN ORDER BY U_EntDt DESC",
        cn=cn)
    return [_map_token(r) for r in rows]


def token_list_by_doc(docid: str, cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {_TOKEN_COLS} FROM TOKEN WHERE DocId = ? ORDER BY Sno",
        (docid,), cn=cn)
    return [_map_token(r) for r in rows]


def token_get(docid: str, sno: int, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {_TOKEN_COLS} FROM TOKEN WHERE DocId = ? AND Sno = ?",
        (docid, sno), cn=cn)
    return _map_token(rows[0]) if rows else None


def token_insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate_token(rec)
    ls = _logsite(cn)
    return db.execute(
        "INSERT INTO TOKEN (DocId, Sno, Vtype, Vtime, VNo, Site_Code, "
        "Vprefix, Vdate, RestCode, RoomCat, RoomType, RoomNo, Item, Qty, "
        "Rate, Amount, VoidYN, Waiter, Pending, TOKENType, U_Name, "
        "U_EntDt, U_AE, DelFlag, NCTOKEN, ContraDocId, ContraSNo, "
        "Reasons, Remarks, LogSite_Code, NCTYPE, FreeSno, Printed, "
        "Description, SchemeCode, Party, TokenNo, CancelYN, ItemRestCode) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
        "?, ?, getdate(), 'A', 'N', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
        "?, ?, ?, ?)",
        (rec["docid"], int(rec.get("sno") or 0), rec.get("vtype", ""),
         rec.get("vtime", ""), int(rec.get("vno") or 0), ls,
         rec.get("vprefix", ""), rec.get("vdate"), rec.get("restcode", ""),
         rec.get("roomcat", ""), rec.get("roomtype", ""),
         rec.get("roomno", ""), rec.get("item", ""),
         float(rec.get("qty") or 0), float(rec.get("rate") or 0),
         float(rec.get("amount") or 0), rec.get("voidyn", ""),
         rec.get("waiter", ""), rec.get("pending", ""),
         rec.get("tokentype", ""), USER,
         rec.get("nctoken", ""), rec.get("contradocid", ""),
         int(rec.get("contrasno") or 0), rec.get("reasons", ""),
         rec.get("remarks", ""), ls,
         rec.get("nctype", ""), int(rec.get("freesno") or 0),
         rec.get("printed", ""), rec.get("description", ""),
         rec.get("schemecode", ""), rec.get("party", ""),
         rec.get("tokenno", ""), rec.get("cancelyn", ""),
         rec.get("itemrestcode", "")),
        cn=cn, commit=commit)


def token_update(docid: str, sno: int, rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "UPDATE TOKEN SET Qty = ?, Rate = ?, Amount = ?, VoidYN = ?, "
        "CancelYN = ?, U_Name1 = ?, U_EntDt1 = getdate(), U_AE1 = 'E' "
        "WHERE DocId = ? AND Sno = ?",
        (float(rec.get("qty") or 0), float(rec.get("rate") or 0),
         float(rec.get("amount") or 0), rec.get("voidyn", ""),
         rec.get("cancelyn", ""), USER, docid, sno),
        cn=cn, commit=commit)


def token_delete(docid: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM TOKEN WHERE DocId = ?", (docid,),
                      cn=cn, commit=commit)


class _TokenAPI:
    LIMITS = {"docid": 30, "vtype": 5, "item": 10}
    @staticmethod
    def list_all(cn=None, limit=500): return token_list(cn, limit)
    @staticmethod
    def list_by_doc(docid, cn=None): return token_list_by_doc(docid, cn)
    @staticmethod
    def get(docid, sno, cn=None): return token_get(docid, sno, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return token_insert(rec, cn, commit)
    @staticmethod
    def update(docid, sno, rec, cn=None, commit=True): return token_update(docid, sno, rec, cn, commit)
    @staticmethod
    def delete(docid, cn=None, commit=True): return token_delete(docid, cn, commit)

TokenAPI = _TokenAPI()


# ============================================================
# SplitBillDetail - Bill Splitting
# ============================================================
_SPLITBILL_COLS = (
    "DocId, VNo, VDate, VTime, RestCode, TableNo, SNo, SNo1, "
    "ItemName, OQty, Rate, BillQty, BillCat, Site_Code, "
    "U_Name, U_EntDt, U_AE, DelFlag, LogSite_Code"
)


def _map_splitbill(r) -> dict:
    try:
        return {
            "docid": r.DocId or "", "vno": int(r.VNo or 0),
            "vdate": r.VDate, "vtime": r.VTime or "",
            "restcode": r.RestCode or "", "tableno": r.TableNo or "",
            "sno": int(r.SNo or 0), "sno1": int(r.SNo1 or 0),
            "itemname": r.ItemName or "", "oqty": float(r.OQty or 0),
            "rate": float(r.Rate or 0), "billqty": float(r.BillQty or 0),
            "billcat": r.BillCat or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
            "delflag": r.DelFlag or "",
        }
    except AttributeError:
        vals = list(r)
        return {
            "docid": vals[0] or "", "vno": int(vals[1] or 0),
            "vdate": vals[2], "vtime": vals[3] or "",
            "restcode": vals[4] or "", "tableno": vals[5] or "",
            "sno": int(vals[6] or 0), "sno1": int(vals[7] or 0),
            "itemname": vals[8] or "", "oqty": float(vals[9] or 0),
            "rate": float(vals[10] or 0), "billqty": float(vals[11] or 0),
            "billcat": vals[12] or "",
            "u_name": vals[14] or "", "u_ae": vals[16] or "",
            "delflag": vals[17] or "",
        }


def splitbill_list_by_doc(docid: str, cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {_SPLITBILL_COLS} FROM SplitBillDetail WHERE DocId = ? ORDER BY SNo",
        (docid,), cn=cn)
    return [_map_splitbill(r) for r in rows]


def splitbill_get(docid: str, sno: int, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {_SPLITBILL_COLS} FROM SplitBillDetail WHERE DocId = ? AND SNo = ?",
        (docid, sno), cn=cn)
    return _map_splitbill(rows[0]) if rows else None


def splitbill_insert(rec: dict, cn=None, commit: bool = True) -> int:
    ls = _logsite(cn)
    return db.execute(
        "INSERT INTO SplitBillDetail (DocId, VNo, VDate, VTime, RestCode, "
        "TableNo, SNo, SNo1, ItemName, OQty, Rate, BillQty, BillCat, "
        "Site_Code, U_Name, U_EntDt, U_AE, DelFlag, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', "
        "'N', ?)",
        (rec["docid"], int(rec.get("vno") or 0), rec.get("vdate"),
         rec.get("vtime", ""), rec.get("restcode", ""),
         rec.get("tableno", ""), int(rec.get("sno") or 0),
         int(rec.get("sno1") or 0), rec.get("itemname", ""),
         float(rec.get("oqty") or 0), float(rec.get("rate") or 0),
         float(rec.get("billqty") or 0), rec.get("billcat", ""),
         ls, USER, ls),
        cn=cn, commit=commit)


def splitbill_delete(docid: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM SplitBillDetail WHERE DocId = ?", (docid,),
                      cn=cn, commit=commit)


class _SplitBillAPI:
    @staticmethod
    def list_by_doc(docid, cn=None): return splitbill_list_by_doc(docid, cn)
    @staticmethod
    def get(docid, sno, cn=None): return splitbill_get(docid, sno, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return splitbill_insert(rec, cn, commit)
    @staticmethod
    def delete(docid, cn=None, commit=True): return splitbill_delete(docid, cn, commit)

SplitBillAPI = _SplitBillAPI()


# ============================================================
# Table Change + KOT Transfer (VB6 RsTbChange/RsKOTTransfer)
# ============================================================
_KOT_PENDING = ("Pending = 'Y' AND ISNULL(VoidYN, 'N') <> 'Y' "
                "AND ISNULL(NCKOT, 'N') <> 'Y' "
                "AND ISNULL(DelFlag, '') IN ('', 'N') "
                "AND ISNULL(ContraDocId, '') = ''")


def pending_kot_tables(rest_code: str, site: str = SITE_CODE,
                       cn=None) -> list[dict]:
    """RestCode ke pending KOTs table-wise count (Table Change lists). LOGSITE aware."""
    rows = db.query(
        "SELECT RTRIM(RoomNo) RoomNo, COUNT(*) PendingCnt, MAX(VDate) "
        "LastOrder FROM KOT WHERE RestCode = ? AND " + _KOT_PENDING +
        " AND RoomNo <> '' GROUP BY RoomNo ORDER BY RoomNo",
        (rest_code,), cn=cn)
    return [{"roomno": (r.RoomNo or "").strip(),
             "pending": int(r.PendingCnt or 0), "last_date": r.LastOrder}
            for r in rows]


def vacant_tables(rest_code: str, site: str = SITE_CODE, cn=None) -> list[dict]:
    """VB6 RsTbChange vacancy: RoomMast NOT IN pending KOT RoomNo, with LOGSITE+HO."""
    ls = site or _logsite(cn)
    try:
        rows = db.query(
            "SELECT DISTINCT CODE,code as Name From RoomMast Where type='TB' AND RESTCODE=? And (LOGSITE_CODE=? OR LOGSITE_CODE='HO' OR LOGSITE_CODE IS NULL) And Code Not in(SELECT DISTINCT RoomNo AS CODE FROM KOT WHERE restCode=? and ROOMTYPE='TB' AND (PENDING ='Y' OR PENDING IS NULL) AND (DELFLAG<>'Y' OR DELFLAG IS NULL) and (NCKOT<>'Y' OR NCKOT IS NULL) AND VOIDYN<>'Y') ORDER BY code",
            (rest_code, ls, rest_code), cn=cn)
        return [{"code": (r[0] if isinstance(r, (list,tuple)) else getattr(r, "Code", "") or "").strip(),
                 "name": (r[1] if isinstance(r, (list,tuple)) and len(r)>1 else getattr(r, "Name", getattr(r, "Code", "")) or "").strip()} for r in rows]
    except Exception:
        return []


def pending_kot_list(rest_code: str, table: str = "",
                     site: str = SITE_CODE, cn=None) -> list[dict]:
    """Pending KOT headers for a table (KOT Transfer list)."""
    params = [rest_code]
    where = "RestCode = ? AND " + _KOT_PENDING
    if table:
        where += " AND RTRIM(RoomNo) = ?"
        params.append(table)
    rows = db.query(
        "SELECT DocId, VNo, VDate, VTime, RoomNo, RoomCat, VType, "
        "RestCode FROM KOT WHERE " + where + " ORDER BY VDate DESC, VNo",
        tuple(params), cn=cn)
    return [{"docid": (r.DocId or "").strip(), "vno": int(r.VNo or 0),
             "vdate": r.VDate, "vtime": r.VTime or "",
             "roomno": (r.RoomNo or "").strip(),
             "roomcat": (r.RoomCat or "").strip(),
             "vtype": (r.VType or "").strip(),
             "restcode": (r.RestCode or "").strip()} for r in rows]


def table_change(rest_code: str, from_table: str, to_table: str,
                 user: str = USER, site: str = SITE_CODE, cn=None,
                 commit: bool = True) -> int:
    """Table ke saare pending KOTs doosri table pe shift (VB6 RsTbChange
    loc_...: Update Kot Set ROOMNO=<to>, U_Name1/U_EntDt1/U_AE1='E' Where
    RestCode And Pending='Y' And DelFlag filter And ROOMNO=<from>)."""
    rest_code = (rest_code or "").strip()
    from_table = (from_table or "").strip()
    to_table = (to_table or "").strip()
    if not rest_code:
        raise ValueError("RestCode (outlet) zaroori hai")
    if not from_table or not to_table:
        raise ValueError("From/To table dono zaroori hain")
    if from_table == to_table:
        raise ValueError("From aur To table same hai")
    rows = db.query(
        "SELECT COUNT(*) FROM KOT WHERE RestCode = ? AND " + _KOT_PENDING +
        " AND RTRIM(RoomNo) = ?", (rest_code, from_table), cn=cn)
    if not rows or not rows[0][0]:
        raise ValueError(f"Table {from_table} pe koi pending KOT nahi hai")
    own = cn is None
    cn = cn or db.connect()
    try:
        n = db.execute(
            "UPDATE KOT SET RoomNo = ?, U_Name1 = ?, U_EntDt1 = getdate(), "
            "U_AE1 = 'E' WHERE RestCode = ? AND " + _KOT_PENDING +
            " AND RTRIM(RoomNo) = ?",
            (to_table, user, rest_code, from_table), cn=cn, commit=False)
        if commit:
            cn.commit()
        return n
    finally:
        if own:
            cn.close()


def kot_transfer(rest_code: str, kot_ref: str, to_table: str,
                 room_service: bool = False, user: str = USER,
                 site: str = SITE_CODE, cn=None, commit: bool = True) -> dict:
    """Ek pending KOT ko doosri table/room pe bhejo (VB6 RsKOTTransfer).

    Room Service flow: target room ke open RoomOcc se RoomCat resolve karke
    KOT ka RoomNo + RoomCat dono update; reference = KOT DOCID.
    Normal flow: KOT reference = VNo; RoomCat untouched.

    Returns dict(affected, roomcat_updated)."""
    rest_code = (rest_code or "").strip()
    kot_ref = (kot_ref or "").strip()
    to_table = (to_table or "").strip()
    if not rest_code:
        raise ValueError("RestCode (outlet) zaroori hai")
    if not kot_ref:
        raise ValueError("KOT reference (DocId/VNo) zaroori hai")
    if not to_table:
        raise ValueError("Target table/room zaroori hai")
    own = cn is None
    cn = cn or db.connect()
    try:
        roomcat = ""
        if room_service:
            # VB6: Room Service me target room se ROOMOCC se RoomCat likho
            occ = db.query(
                "SELECT TOP 1 RoomCat FROM RoomOcc WHERE RTRIM(RoomNo) = ? "
                "AND (LogSite_Code = ? OR LogSite_Code = 'HO') AND "
                "ChkOutDate IS NULL", (to_table, site), cn=cn)
            if not occ:
                raise ValueError(f"Room {to_table} pe koi in-house guest "
                                 "nahi (Room Service KOT)")
            roomcat = (occ[0].RoomCat or "").strip()
            n = db.execute(
                "UPDATE KOT SET RoomNo = ?, RoomCat = ?, U_Name1 = ?, "
                "U_EntDt1 = getdate(), U_AE1 = 'E' "
                "WHERE RestCode = ? AND " + _KOT_PENDING + " AND DocId = ?",
                (to_table, roomcat, user, rest_code, kot_ref), cn=cn,
                commit=False)
        else:
            n = db.execute(
                "UPDATE KOT SET RoomNo = ?, U_Name1 = ?, U_EntDt1 = "
                "getdate(), U_AE1 = 'E' WHERE RestCode = ? AND " +
                _KOT_PENDING + " AND VNo = ?",
                (to_table, user, rest_code, kot_ref), cn=cn, commit=False)
        if commit:
            cn.commit()
        return {"affected": n, "roomcat_updated": bool(roomcat)}
    finally:
        if own:
            cn.close()
