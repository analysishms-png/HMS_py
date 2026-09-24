"""POS_SBill - multi-outlet split linkage (VB6 RsSaleBillSplit).

Table verified in moondata.sql: POS_SBill (DocId, OutletDocId, OutletCode) PK (DocId, OutletDocId).
VB6 writes POS_SBill for each outlet slice during split settlement.
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()
USER = db.get_user()

def _logsite(cn=None) -> str:
    try:
        return db.get_logsite_code(cn=cn)
    except Exception:
        return SITE_CODE


def pos_sbill_list(docid: str, cn=None) -> list[dict]:
    rows = db.query("SELECT DocId, OutletDocId, OutletCode FROM POS_SBill WHERE DocId=? ORDER BY OutletDocId", (docid,), cn=cn)
    out = []
    for r in rows:
        if isinstance(r, (list,tuple)):
            out.append({"docid": r[0] or "", "outlet_docid": r[1] or "", "outlet_code": r[2] or ""})
        else:
            out.append({"docid": getattr(r, "DocId", "") or "", "outlet_docid": getattr(r, "OutletDocId", "") or "", "outlet_code": getattr(r, "OutletCode", "") or ""})
    return out


def pos_sbill_insert(rec: dict, cn=None, commit: bool = True) -> int:
    if not rec.get("docid", "").strip():
        raise ValueError("DocId zaroori hai")
    if not rec.get("outlet_docid", rec.get("outletdocid","")).strip():
        raise ValueError("OutletDocId zaroori hai")
    outlet_docid = rec.get("outlet_docid", rec.get("outletdocid","")).strip()
    return db.execute(
        "INSERT INTO POS_SBill (DocId, OutletDocId, OutletCode) VALUES (?, ?, ?)",
        (rec["docid"], outlet_docid, rec.get("outlet_code", rec.get("outletcode","")) or rec.get("OutletCode","")),
        cn=cn, commit=commit)


def pos_sbill_delete(docid: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM POS_SBill WHERE DocId=?", (docid,), cn=cn, commit=commit)


class _POSSBillAPI:
    @staticmethod
    def list_by_doc(docid, cn=None): return pos_sbill_list(docid, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return pos_sbill_insert(rec, cn, commit)
    @staticmethod
    def delete(docid, cn=None, commit=True): return pos_sbill_delete(docid, cn, commit)

POSSBillAPI = _POSSBillAPI()
