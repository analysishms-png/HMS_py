"""Expense / Folio Charge entry (VB6: Front Office -> Expense Entry).

EVIDENCE (live HMS DB + VB6 RsFolioEntry.frm):
- PayCharge table: all folio transactions (Dr=charges, Cr=payments/receipts).
  Columns: DocId(21) varchar, Vtype varchar(10), VNo int, VPrefix varchar(4),
  Site_Code varchar(2), FolioDocId varchar(21) FK->GuestFolio.DocId,
  FolioNo int, PayCode varchar(6) FK->FixedCharge/PayTypeMast,
  Amount float, AmtDr float, AmtCr float,
  Remarks varchar(100), Narration varchar(100),
  TaxCode varchar(6), TaxAmt float, TaxPer float,
  U_Name varchar(10), U_EntDt datetime, U_AE varchar(1),
  LogSite_Code varchar(2).
- Vtype='EXP' for manual expense entries.
- DocId = 'D'+site(2)+'EXP'.ljust(6)+vprefix(4)+VNo.rjust(8).
- VNo = MAX(VNo)+1 within (Site_Code, Vprefix, Vtype='EXP').
- AmtDr=Amount (charge to guest); AmtCr=0 for expense.
- Receipts: Vtype='REC', AmtCr=Amount, AmtDr=0.

PYT-guard: sirf PYT* guest folios pe write (production = VB6 EXE).
"""
from __future__ import annotations

from HMS_py.core import db, checkin

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
VTYPE_EXP = "EXP"
VTYPE_REC = "REC"


def _next_vno(vtype: str, vprefix: str, cn=None,
              site: str = SITE_CODE) -> int:
    # BUG-015: race-safe VNo (UPDLOCK/HOLDLOCK) - db.py central helper.
    return db.next_vno("PayCharge", vtype, vprefix, site=site, cn=cn)


def _make_docid(vtype: str, vprefix: str, vno: int,
                site: str = SITE_CODE) -> str:
    return ("D" + site.ljust(2) + vtype.ljust(6) +
            vprefix.ljust(4) + str(vno).rjust(8))[:21]


def list_folio_charges(folio, cn=None,
                       vprefix: str = "2026") -> list[dict]:
    """Ek folio ke sab charges/payments (RsFolioEntry grid jaisa)."""
    try:
        folio = int(folio)
    except (TypeError, ValueError):
        return []
    rec = checkin.get(folio, cn=cn, vprefix=vprefix)
    if not rec:
        return []
    rows = db.query(
        "SELECT DocId, Vtype, VNo, PayCode, Amount, AmtDr, AmtCr, "
        "Remarks, TaxAmt, U_Name, U_EntDt, U_AE "
        "FROM PayCharge WHERE FolioNoDocid = ? AND Site_Code = ? "
        "ORDER BY VNo",
        (rec["docid"], SITE_CODE), cn=cn)
    out = []
    for r in rows:
        try:
            out.append({
                "docid": r.DocId, "vtype": r.Vtype, "vno": r.VNo,
                "paycode": r.PayCode or "",
                "amount": float(r.Amount or 0),
                "amt_dr": float(r.AmtDr or 0),
                "amt_cr": float(r.AmtCr or 0),
                "remarks": (r.Remarks or "").strip(),
                "taxamt": float(r.TaxAmt or 0),
                "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
            })
        except AttributeError:
            did, vt, vn, pc, amt, adr, acr, rem, tax, un, _, uae = r
            out.append({
                "docid": did, "vtype": vt, "vno": vn,
                "paycode": pc or "", "amount": float(amt or 0),
                "amt_dr": float(adr or 0), "amt_cr": float(acr or 0),
                "remarks": (rem or "").strip(), "taxamt": float(tax or 0),
                "u_name": un or "", "u_ae": uae or "",
            })
    return out


def post_expense(folio: int, paycode: str, amount: float,
                 remarks: str = "", taxamt: float = 0.0,
                 user: str = USER, cn=None, commit: bool = True,
                 vprefix: str = "2026", site: str = SITE_CODE) -> int:
    """Expense charge folio pe post karo (AmtDr = charge to guest).
    PYT-guard: production charges VB6 se; sirf PYT* folios test pe.
    Returns VNo."""
    rec = checkin.get(folio, cn=cn, vprefix=vprefix)
    if not rec:
        raise ValueError(f"Folio #{folio} nahi mila")
    if not str(rec["name"]).upper().startswith("PYT"):
        raise ValueError(
            "Safety: sirf PYT* test folios pe expense post ho sakti hai")
    amount = float(amount)
    if amount <= 0:
        raise ValueError("Amount positive hona chahiye")

    own = cn is None
    cn_use = cn or db.connect()
    try:
        vno = _next_vno(VTYPE_EXP, vprefix, cn=cn_use, site=site)
        docid = _make_docid(VTYPE_EXP, vprefix, vno, site)
        db.execute(
            "INSERT INTO PayCharge (DocId, Vtype, VNo, VPrefix, Site_Code, "
            "FolioNoDocid, FolioNo, PayCode, Amount, AmtDr, AmtCr, "
            "Remarks, TaxAmt, TaxPer, U_Name, U_EntDt, U_AE, "
            "LogSite_Code) VALUES "
            "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, 0, ?, "
            "getdate(), 'A', ?)",
            (docid, VTYPE_EXP, vno, vprefix, site,
             rec["docid"], folio, paycode, amount, amount,
             remarks or ".", taxamt, user, site),
            cn=cn_use, commit=False)
        if commit:
            cn_use.commit()
        return vno
    finally:
        if own:
            cn_use.close()


def post_receipt(folio: int, paycode: str, amount: float,
                 remarks: str = "", user: str = USER, cn=None,
                 commit: bool = True, vprefix: str = "2026",
                 site: str = SITE_CODE) -> int:
    """Payment/Receipt folio pe post karo (AmtCr = payment received).
    PYT-guard same as post_expense."""
    rec = checkin.get(folio, cn=cn, vprefix=vprefix)
    if not rec:
        raise ValueError(f"Folio #{folio} nahi mila")
    if not str(rec["name"]).upper().startswith("PYT"):
        raise ValueError(
            "Safety: sirf PYT* test folios pe receipt post ho sakti hai")
    amount = float(amount)
    if amount <= 0:
        raise ValueError("Amount positive hona chahiye")

    own = cn is None
    cn_use = cn or db.connect()
    try:
        vno = _next_vno(VTYPE_REC, vprefix, cn=cn_use, site=site)
        docid = _make_docid(VTYPE_REC, vprefix, vno, site)
        db.execute(
            "INSERT INTO PayCharge (DocId, Vtype, VNo, VPrefix, Site_Code, "
            "FolioNoDocid, FolioNo, PayCode, Amount, AmtDr, AmtCr, "
            "Remarks, TaxAmt, TaxPer, U_Name, U_EntDt, U_AE, "
            "LogSite_Code) VALUES "
            "(?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, 0, 0, ?, "
            "getdate(), 'A', ?)",
            (docid, VTYPE_REC, vno, vprefix, site,
             rec["docid"], folio, paycode, amount, amount,
             remarks or ".", user, site),
            cn=cn_use, commit=False)
        if commit:
            cn_use.commit()
        return vno
    finally:
        if own:
            cn_use.close()


def delete_charge(docid: str, cn=None, commit: bool = True,
                  site: str = SITE_CODE) -> int:
    """Test-only: sirf PYT* folio charges delete hoti hain.
    VB6 pattern: PayChargeLog me copy before delete (audit trail)."""
    rows = db.query(
        "SELECT gf.Name FROM PayCharge pc "
        "JOIN GuestFolio gf ON gf.DocId = pc.FolioNoDocid "
        "WHERE pc.DocId = ? AND pc.Site_Code = ?",
        (docid, site), cn=cn)
    if not rows:
        raise ValueError(f"Charge {docid} nahi mila")
    if not str(rows[0][0] or "").upper().startswith("PYT"):
        raise ValueError("Safety: sirf PYT* folio charges delete ho sakti hain")
    own = cn is None
    cn_use = cn or db.connect()
    try:
        # VB6 pattern: copy to PayChargeLog before delete (audit trail)
        db.execute(
            "INSERT INTO PayChargeLog SELECT *, getdate(), ? "
            "FROM PayCharge WHERE DocId = ?",
            (USER, docid), cn=cn_use, commit=False)
        n = db.execute(
            "DELETE FROM PayCharge WHERE DocId = ?", (docid,),
            cn=cn_use, commit=False)
        if commit:
            cn_use.commit()
        return n
    finally:
        if own:
            cn_use.close()
