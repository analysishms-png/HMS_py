"""Purchase Chain Operations (VB6: Purch1/Purch2, KClStk, Indent, INDENT1, PORDER1).

Tables:
- Purch1: Purchase header (36 cols)
- Purch2: Purchase detail (53 cols)
- KClStk: Kitchen/Cleaning stock (16 cols)
- Indent: Indent header (17 cols) - already in inventory.py, added here for completeness
- INDENT1: Indent detail (24 cols) - note: uppercase in DB
- PORDER1: Purchase order detail (27 cols) - note: lowercase 'd' in Docid
- DateLock: already in sys_config.py

Schema: verified from live KailashData2526 DB.
"""
from __future__ import annotations

from datetime import date

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()


# ============================================================
# Purch1 - Purchase Header
# PK: DocId
# ============================================================
def _map_purch1(r) -> dict:
    try:
        return {
            "docid": r.DocId or "", "vno": r.VNo or 0,
            "vdate": r.Vdate, "vtype": r.Vtype or "",
            "vprefix": r.Vprefix or "",
            "rest_code": r.RestCode or "",
            "party": r.Party or "",
            "total": float(r.Total or 0),
            "disc_per": float(r.DiscPer or 0),
            "disc_amt": float(r.DiscAmt or 0),
            "non_taxable": float(r.NonTaxable or 0),
            "taxable": float(r.Taxable or 0),
            "tax": float(r.Tax or 0),
            "service_charge": float(r.ServiceCharge or 0),
            "add_amt": float(r.AddAmt or 0),
            "ded_amt": float(r.DedAmt or 0),
            "round_off": float(r.RoundOff or 0),
            "net_amt": float(r.NetAmt or 0),
            "del_flag": r.DelFlag or "",
            "party_bill_no": r.PartyBillNo or "",
            "party_bill_dt": r.PartyBillDt,
            "cash_party": (r.CashParty or "").strip(),
            "tin_no": r.TinNo or "",
            "remark": (r.Remark or "").strip(),
            "invoice_type": r.InvoiceType or "",
            "invoice_no": r.InvoiceNo or 0,
            "cgst": float(r.CGST or 0),
            "sgst": float(r.SGST or 0),
            "igst": float(r.IGST or 0),
            "payable": r.Payable or 0,
            "bill_image": r.BillImagePath or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        d, vn, vd, vt, vp, rc, p, t, dp, da, nt, tx, sc, sc2, \
            aa, da2, ro, na, un, _, uae, df, pbn, pbd, cp, tin, rem, \
            it, inv, cg, sg, ig, py, bi, lgs = r
        return {
            "docid": d or "", "vno": vn or 0,
            "vdate": vd, "vtype": vt or "",
            "vprefix": vp or "",
            "rest_code": rc or "",
            "party": p or "",
            "total": float(t or 0),
            "disc_per": float(dp or 0),
            "disc_amt": float(da or 0),
            "non_taxable": float(nt or 0),
            "taxable": float(tx or 0),
            "tax": float(sc or 0),
            "service_charge": float(sc2 or 0),
            "add_amt": float(aa or 0),
            "ded_amt": float(da2 or 0),
            "round_off": float(ro or 0),
            "net_amt": float(na or 0),
            "del_flag": df or "",
            "party_bill_no": pbn or "",
            "party_bill_dt": pbd,
            "cash_party": (cp or "").strip(),
            "tin_no": tin or "",
            "remark": (rem or "").strip(),
            "invoice_type": it or "",
            "invoice_no": inv or 0,
            "cgst": float(cg or 0),
            "sgst": float(sg or 0),
            "igst": float(ig or 0),
            "payable": py or 0,
            "bill_image": bi or "",
            "u_name": un or "", "u_ae": uae or "",
        }


def _validate_purch1(rec: dict):
    if not rec.get("docid", "").strip():
        raise ValueError("DocId zaroori hai")
    if not rec.get("vtype", "").strip():
        raise ValueError("Vtype zaroori hai")


def purch1_list(cn=None, limit: int = 500) -> list[dict]:
    cols = ("DocId, VNo, Vdate, Vtype, Vprefix, RestCode, Party, "
            "Total, DiscPer, DiscAmt, NonTaxable, Taxable, Tax, "
            "ServiceCharge, AddAmt, DedAmt, RoundOff, NetAmt, "
            "U_Name, U_EntDt, U_AE, DelFlag, PartyBillNo, PartyBillDt, "
            "CashParty, TinNo, Remark, InvoiceType, InvoiceNo, "
            "CGST, SGST, IGST, Payable, BillImagePath, Site_Code")
    rows = db.query(
        f"SELECT TOP {int(limit)} {cols} FROM Purch1 ORDER BY Vdate DESC, DocId",
        cn=cn)
    return [_map_purch1(r) for r in rows]


def purch1_get(docid: str, cn=None) -> dict | None:
    cols = ("DocId, VNo, Vdate, Vtype, Vprefix, RestCode, Party, "
            "Total, DiscPer, DiscAmt, NonTaxable, Taxable, Tax, "
            "ServiceCharge, AddAmt, DedAmt, RoundOff, NetAmt, "
            "U_Name, U_EntDt, U_AE, DelFlag, PartyBillNo, PartyBillDt, "
            "CashParty, TinNo, Remark, InvoiceType, InvoiceNo, "
            "CGST, SGST, IGST, Payable, BillImagePath, Site_Code")
    rows = db.query(
        f"SELECT {cols} FROM Purch1 WHERE DocId = ?", (docid,), cn=cn)
    return _map_purch1(rows[0]) if rows else None


def purch1_insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate_purch1(rec)
    return db.execute(
        "INSERT INTO Purch1 (DocId, VNo, Vdate, Vtype, Vprefix, Site_Code, "
        "RestCode, Party, Total, DiscPer, DiscAmt, NonTaxable, Taxable, "
        "Tax, ServiceCharge, AddAmt, DedAmt, RoundOff, NetAmt, "
        "U_Name, U_EntDt, U_AE, DelFlag, PartyBillNo, PartyBillDt, "
        "CashParty, TinNo, Remark, InvoiceType, InvoiceNo, "
        "CGST, SGST, IGST, Payable, BillImagePath) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
        "?, ?, getdate(), 'A', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (rec["docid"], rec.get("vno", 0), rec.get("vdate", date.today()),
         rec["vtype"], rec.get("vprefix", ""), SITE_CODE,
         rec.get("rest_code", ""), rec.get("party", ""),
         float(rec.get("total") or 0), float(rec.get("disc_per") or 0),
         float(rec.get("disc_amt") or 0), float(rec.get("non_taxable") or 0),
         float(rec.get("taxable") or 0), float(rec.get("tax") or 0),
         float(rec.get("service_charge") or 0),
         float(rec.get("add_amt") or 0), float(rec.get("ded_amt") or 0),
         float(rec.get("round_off") or 0), float(rec.get("net_amt") or 0),
         USER, rec.get("del_flag", "N"), rec.get("party_bill_no", ""),
         rec.get("party_bill_dt"), rec.get("cash_party", ""),
         rec.get("tin_no", ""), rec.get("remark", ""),
         rec.get("invoice_type", ""), rec.get("invoice_no", 0),
         float(rec.get("cgst") or 0), float(rec.get("sgst") or 0),
         float(rec.get("igst") or 0), rec.get("payable", 0),
         rec.get("bill_image", "")),
        cn=cn, commit=commit)


def purch1_update(docid: str, rec: dict, cn=None, commit: bool = True) -> int:
    _validate_purch1(rec)
    return db.execute(
        "UPDATE Purch1 SET VNo = ?, Vdate = ?, Vtype = ?, Vprefix = ?, "
        "RestCode = ?, Party = ?, Total = ?, DiscPer = ?, DiscAmt = ?, "
        "NonTaxable = ?, Taxable = ?, Tax = ?, ServiceCharge = ?, "
        "AddAmt = ?, DedAmt = ?, RoundOff = ?, NetAmt = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E', "
        "DelFlag = ?, PartyBillNo = ?, PartyBillDt = ?, "
        "CashParty = ?, TinNo = ?, Remark = ?, InvoiceType = ?, "
        "InvoiceNo = ?, CGST = ?, SGST = ?, IGST = ?, "
        "Payable = ?, BillImagePath = ? WHERE DocId = ?",
        (rec.get("vno", 0), rec.get("vdate"), rec.get("vtype", ""),
         rec.get("vprefix", ""), rec.get("rest_code", ""),
         rec.get("party", ""), float(rec.get("total") or 0),
         float(rec.get("disc_per") or 0), float(rec.get("disc_amt") or 0),
         float(rec.get("non_taxable") or 0), float(rec.get("taxable") or 0),
         float(rec.get("tax") or 0), float(rec.get("service_charge") or 0),
         float(rec.get("add_amt") or 0), float(rec.get("ded_amt") or 0),
         float(rec.get("round_off") or 0), float(rec.get("net_amt") or 0),
         USER, rec.get("del_flag", "N"), rec.get("party_bill_no", ""),
         rec.get("party_bill_dt"), rec.get("cash_party", ""),
         rec.get("tin_no", ""), rec.get("remark", ""),
         rec.get("invoice_type", ""), rec.get("invoice_no", 0),
         float(rec.get("cgst") or 0), float(rec.get("sgst") or 0),
         float(rec.get("igst") or 0), rec.get("payable", 0),
         rec.get("bill_image", ""), docid),
        cn=cn, commit=commit)


def purch1_delete(docid: str, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM Purch1 WHERE DocId = ?", (docid,),
        cn=cn, commit=commit)


def purchase_bill_create(party_code: str, vdate, lines: list[dict],
                         remark: str = "", vtype: str = "PBPB",
                         vprefix: str = "2026", user: str = USER,
                         cn=None, commit: bool = True) -> dict:
    """Create Purchase Bill (Purch1 header + Purch2 lines) atomically.

    VB6: PurchBill 'Save' (PBR/PBPB credit voucher).
    Returns {"docid", "vno"}.
    """
    if not lines:
        raise ValueError("At least one line required")
    if not (party_code or "").strip():
        raise ValueError("PartyCode zaroori hai")
    vdate = vdate or date.today()
    own = cn is None
    cn = cn or db.connect()
    try:
        from HMS_py.core import taxstru as _ts
        vno = db.next_vno("Purch1", vtype, vprefix, site=SITE_CODE, cn=cn)
        docid = ("D" + SITE_CODE + vtype.ljust(6) + vprefix.ljust(4)
                 + str(vno).rjust(8))[:21]
        # PI-4: TaxStru slab GST (CGST/SGST/IGST) + service + roundoff
        # instead of hard-coded 0. Lines may carry explicit tax_amt;
        # if tax_stru_code present and tax_amt blank, compute from TaxStru.
        header_cgst = header_sgst = header_igst = header_service = 0.0
        total = 0.0
        tax = 0.0
        for i, line in enumerate(lines, 1):
            amt = float(line.get("amount") or 0)
            total += amt
            tax_stru_code = (line.get("tax_stru") or "").strip()
            explicit_tax = float(line.get("tax_amt") or 0)
            if tax_stru_code:
                calc = _ts.calculate(tax_stru_code, amt, cn=cn)
                if not explicit_tax:
                    line["tax_per"] = line.get("tax_per") or (
                        round(calc["total_tax"] / amt * 100, 2) if amt else 0)
                    line["tax_amt"] = calc["total_tax"]
                    explicit_tax = calc["total_tax"]
                tax += explicit_tax
                # Header split always from TaxStru structure
                header_cgst += calc["cgst"]
                header_sgst += calc["sgst"]
                header_igst += calc["igst"]
                header_service += calc["service"]
            else:
                tax += explicit_tax
                header_cgst += explicit_tax / 2
                header_sgst += explicit_tax / 2
        # VB6 PI-7 rule: Taxable = total (gross), NetAmt = total + tax + roundoff
        taxable = total
        net_raw = total + tax
        roundoff = round(net_raw) - net_raw
        roundoff = round(roundoff, 2)
        net = round(net_raw + roundoff, 2)
        db.execute(
            "INSERT INTO Purch1 (DocId, VNo, Vdate, VType, Vprefix, Site_Code, "
            "RestCode, Party, Total, DiscPer, DiscAmt, NonTaxable, Taxable, "
            "Tax, ServiceCharge, AddAmt, DedAmt, RoundOff, NetAmt, "
            "U_Name, U_EntDt, U_AE, DelFlag, PartyBillNo, PartyBillDt, "
            "CashParty, TinNo, Remark, InvoiceType, InvoiceNo, "
            "CGST, SGST, IGST, Payable, BillImagePath) "
            "VALUES (?, ?, ?, ?, ?, ?, '', ?, ?, 0, 0, 0, ?, ?, ?, 0, 0, ?, ?, "
            "?, getdate(), 'A', 'N', '', NULL, '', '', ?, '', ?, ?, ?, ?, '')",
            (docid, vno, vdate, vtype, vprefix, SITE_CODE,
             party_code.strip(), total, taxable, tax,
             float(header_service), roundoff, net, user,
             remark or "", float(header_cgst), float(header_sgst),
             float(header_igst), net),
            cn=cn, commit=False)
        for i, line in enumerate(lines, 1):
            amt = float(line.get("amount") or 0)
            db.execute(
                "INSERT INTO Purch2 (DocId, Sno, Vtype, VNo, Site_Code, "
                "Vprefix, Vdate, PartyCode, Item, QtyIss, QtyRec, Unit, "
                "Rate, Amount, TaxPer, TaxAmt, DiscPer, DiscAmt, VoidYN, "
                "Remarks, ContraDocId, ContraSno, VTime, U_Name, U_EntDt, "
                "U_AE, Total, GodCode, ChalQty, RecdQty, AccQty, RejQty, "
                "Specification, DelFlag, Taxstru, AcCode, LogSite_Code) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?, "
                "?, 'N', ?, '', 0, '00:00', ?, getdate(), 'A', ?, '', 0, 0, "
                "0, 0, '', 'N', ?, '', ?)",
                (docid, i, vtype, vno, SITE_CODE, vprefix, vdate,
                 party_code.strip(), line.get("item", ""),
                 float(line.get("qty") or 0), line.get("unit", ""),
                 float(line.get("rate") or 0), amt,
                 float(line.get("tax_per") or 0),
                 float(line.get("tax_amt") or 0),
                 float(line.get("disc_per") or 0),
                 float(line.get("disc_amt") or 0),
                 line.get("remarks", ""), user, amt,
                 (line.get("tax_stru") or "").strip(), SITE_CODE),
                cn=cn, commit=False)
        # VB6 FaTaxVoucher/pPBill: Stock row per Purch2 line (ContraDocId link)
        for i, line in enumerate(lines, 1):
            qty = float(line.get("qty") or 0)
            amt = float(line.get("amount") or 0)
            rate = float(line.get("rate") or 0)
            godown = line.get("godown", "") or ""
            db.execute(
                "INSERT INTO Stock (DocId, Sno, Vtype, VNo, Site_Code, Vprefix, "
                "VDate, PartyCode, GodownCode, Item, QtyRec, AccQty, Unit, Rate, "
                "Amount, U_Name, U_EntDt, U_AE, ContraDocId, ContraSno, "
                "LogSite_Code, DelFlag) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
                "?, getdate(), 'A', ?, ?, ?, 'N')",
                (docid, i, vtype, vno, SITE_CODE, vprefix, vdate,
                 party_code.strip(), godown, line.get("item", ""),
                 qty, qty, line.get("unit", ""), rate, amt,
                 user, docid, i, SITE_CODE),
                cn=cn, commit=False)
        if commit:
            cn.commit()
        return {"docid": docid, "vno": vno}
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


class _Purch1API:
    @staticmethod
    def list_all(cn=None, limit=500): return purch1_list(cn, limit)
    @staticmethod
    def get(docid, cn=None): return purch1_get(docid, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return purch1_insert(rec, cn, commit)
    @staticmethod
    def update(docid, rec, cn=None, commit=True): return purch1_update(docid, rec, cn, commit)
    @staticmethod
    def delete(docid, cn=None, commit=True): return purch1_delete(docid, cn, commit)

Purch1API = _Purch1API()


# ============================================================
# Purch2 - Purchase Detail
# PK: DocId + Sno
# ============================================================
def _map_purch2(r) -> dict:
    try:
        return {
            "docid": r.DocId or "", "sno": r.Sno or 0,
            "vtype": r.Vtype or "", "vno": r.VNo or 0,
            "vprefix": r.Vprefix or "", "vdate": r.Vdate,
            "party_code": r.PartyCode or "", "rest_code": r.RestCode or "",
            "room_cat": r.RoomCat or "", "room_type": r.RoomType or "",
            "room_no": r.RoomNo or "",
            "contra_docid": r.ContraDocId or "",
            "contra_sno": r.ContraSno or 0,
            "item": r.Item or "",
            "qty_iss": float(r.QtyIss or 0),
            "qty_rec": float(r.QtyRec or 0),
            "unit": r.Unit or "",
            "rate": float(r.Rate or 0),
            "amount": float(r.Amount or 0),
            "tax_per": float(r.TaxPer or 0),
            "tax_amt": float(r.TaxAmt or 0),
            "disc_per": float(r.DiscPer or 0),
            "disc_amt": float(r.DiscAmt or 0),
            "void_yn": r.VoidYN or "",
            "remarks": (r.Remarks or "").strip(),
            "kot_docid": r.KOTDocId or "",
            "kot_sno": r.KOTSno or 0,
            "vtime": r.VTime or "",
            "total": float(r.Total or 0),
            "god_code": r.GodCode or "",
            "chal_qty": float(r.ChalQty or 0),
            "recd_qty": float(r.RecdQty or 0),
            "acc_qty": float(r.AccQty or 0),
            "rej_qty": float(r.RejQty or 0),
            "specification": r.Specification or "",
            "del_flag": r.DelFlag or "",
            "tax_stru": r.Taxstru or "",
            "ac_code": r.AcCode or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        d, s, vt, vn, vp, vd, pc, rc, rc2, rtp, rn, cd, cs, \
            it, qi, qr, u, r2, a, tp, ta, dp, da, vyn, rem, \
            kd, ks, vt2, t, gc, cq, rq, arq, rj, sp, df, ts, \
            ac, un, _, uae, lgs = r[:43]
        return {
            "docid": d or "", "sno": s or 0,
            "vtype": vt or "", "vno": vn or 0,
            "vprefix": vp or "", "vdate": vd,
            "party_code": pc or "", "rest_code": rc or "",
            "room_cat": rc2 or "", "room_type": rtp or "",
            "room_no": rn or "",
            "contra_docid": cd or "", "contra_sno": cs or 0,
            "item": it or "",
            "qty_iss": float(qi or 0), "qty_rec": float(qr or 0),
            "unit": u or "", "rate": float(r2 or 0),
            "amount": float(a or 0),
            "tax_per": float(tp or 0), "tax_amt": float(ta or 0),
            "disc_per": float(dp or 0), "disc_amt": float(da or 0),
            "void_yn": vyn or "",
            "remarks": (rem or "").strip(),
            "kot_docid": kd or "", "kot_sno": ks or 0,
            "vtime": vt2 or "",
            "total": float(t or 0),
            "god_code": gc or "",
            "chal_qty": float(cq or 0), "recd_qty": float(rq or 0),
            "acc_qty": float(arq or 0), "rej_qty": float(rj or 0),
            "specification": sp or "",
            "del_flag": df or "",
            "tax_stru": ts or "",
            "ac_code": ac or "",
            "u_name": un or "", "u_ae": uae or "",
        }


def _validate_purch2(rec: dict):
    if not rec.get("docid", "").strip():
        raise ValueError("DocId zaroori hai")


def purch2_list(cn=None, limit: int = 500) -> list[dict]:
    cols = ("DocId, Sno, Vtype, VNo, Site_Code, Vprefix, Vdate, "
            "PartyCode, RestCode, RoomCat, RoomType, RoomNo, "
            "ContraDocId, ContraSno, Item, QtyIss, QtyRec, Unit, "
            "Rate, Amount, TaxPer, TaxAmt, DiscPer, DiscAmt, "
            "VoidYN, Remarks, KOTDocId, KOTSno, VTime, "
            "U_Name, U_EntDt, U_AE, Total, GodCode, ChalQty, "
            "RecdQty, AccQty, RejQty, Specification, DelFlag, "
            "Taxstru, AcCode, LogSite_Code")
    rows = db.query(
        f"SELECT TOP {int(limit)} {cols} FROM Purch2 ORDER BY DocId, Sno",
        cn=cn)
    return [_map_purch2(r) for r in rows]


def purch2_get(docid: str, sno: int, cn=None) -> dict | None:
    cols = ("DocId, Sno, Vtype, VNo, Site_Code, Vprefix, Vdate, "
            "PartyCode, RestCode, RoomCat, RoomType, RoomNo, "
            "ContraDocId, ContraSno, Item, QtyIss, QtyRec, Unit, "
            "Rate, Amount, TaxPer, TaxAmt, DiscPer, DiscAmt, "
            "VoidYN, Remarks, KOTDocId, KOTSno, VTime, "
            "U_Name, U_EntDt, U_AE, Total, GodCode, ChalQty, "
            "RecdQty, AccQty, RejQty, Specification, DelFlag, "
            "Taxstru, AcCode, LogSite_Code")
    rows = db.query(
        f"SELECT {cols} FROM Purch2 WHERE DocId = ? AND Sno = ?",
        (docid, sno), cn=cn)
    return _map_purch2(rows[0]) if rows else None


def purch2_lines(docid: str, cn=None) -> list[dict]:
    """Get all detail lines for a purchase document."""
    cols = ("DocId, Sno, Vtype, VNo, Site_Code, Vprefix, Vdate, "
            "PartyCode, RestCode, RoomCat, RoomType, RoomNo, "
            "ContraDocId, ContraSno, Item, QtyIss, QtyRec, Unit, "
            "Rate, Amount, TaxPer, TaxAmt, DiscPer, DiscAmt, "
            "VoidYN, Remarks, KOTDocId, KOTSno, VTime, "
            "U_Name, U_EntDt, U_AE, Total, GodCode, ChalQty, "
            "RecdQty, AccQty, RejQty, Specification, DelFlag, "
            "Taxstru, AcCode, LogSite_Code")
    rows = db.query(
        f"SELECT {cols} FROM Purch2 WHERE DocId = ? ORDER BY Sno",
        (docid,), cn=cn)
    return [_map_purch2(r) for r in rows]


def purch2_insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate_purch2(rec)
    return db.execute(
        "INSERT INTO Purch2 (DocId, Sno, Vtype, VNo, Site_Code, Vprefix, "
        "Vdate, PartyCode, RestCode, RoomCat, RoomType, RoomNo, "
        "ContraDocId, ContraSno, Item, QtyIss, QtyRec, Unit, Rate, "
        "Amount, TaxPer, TaxAmt, DiscPer, DiscAmt, VoidYN, Remarks, "
        "KOTDocId, KOTSno, VTime, U_Name, U_EntDt, U_AE, Total, "
        "GodCode, ChalQty, RecdQty, AccQty, RejQty, Specification, "
        "DelFlag, Taxstru, AcCode, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
        "?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?, ?, "
        "?, ?, ?, ?, ?, ?, ?, ?)",
        (rec["docid"], rec["sno"], rec.get("vtype", ""),
         rec.get("vno", 0), SITE_CODE, rec.get("vprefix", ""),
         rec.get("vdate"), rec.get("party_code", ""),
         rec.get("rest_code", ""), rec.get("room_cat", ""),
         rec.get("room_type", ""), rec.get("room_no", ""),
         rec.get("contra_docid", ""), rec.get("contra_sno", 0),
         rec.get("item", ""),
         float(rec.get("qty_iss") or 0), float(rec.get("qty_rec") or 0),
         rec.get("unit", ""), float(rec.get("rate") or 0),
         float(rec.get("amount") or 0),
         float(rec.get("tax_per") or 0), float(rec.get("tax_amt") or 0),
         float(rec.get("disc_per") or 0), float(rec.get("disc_amt") or 0),
         rec.get("void_yn", "N"), rec.get("remarks", ""),
         rec.get("kot_docid", ""), rec.get("kot_sno", 0),
         rec.get("vtime", "00:00"), USER,
         float(rec.get("total") or 0),
         rec.get("god_code", ""),
         float(rec.get("chal_qty") or 0), float(rec.get("recd_qty") or 0),
         float(rec.get("acc_qty") or 0), float(rec.get("rej_qty") or 0),
         rec.get("specification", ""),
         rec.get("del_flag", "N"), rec.get("tax_stru", ""),
         rec.get("ac_code", ""), SITE_CODE),
        cn=cn, commit=commit)


def purch2_delete(docid: str, sno: int, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM Purch2 WHERE DocId = ? AND Sno = ?",
        (docid, sno), cn=cn, commit=commit)


def purch2_delete_all(docid: str, cn=None, commit: bool = True) -> int:
    """Delete all detail lines for a purchase document."""
    return db.execute(
        "DELETE FROM Purch2 WHERE DocId = ?", (docid,),
        cn=cn, commit=commit)


class _Purch2API:
    @staticmethod
    def list_all(cn=None, limit=500): return purch2_list(cn, limit)
    @staticmethod
    def get(docid, sno, cn=None): return purch2_get(docid, sno, cn)
    @staticmethod
    def lines(docid, cn=None): return purch2_lines(docid, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return purch2_insert(rec, cn, commit)
    @staticmethod
    def delete(docid, sno, cn=None, commit=True): return purch2_delete(docid, sno, cn, commit)
    @staticmethod
    def delete_all(docid, cn=None, commit=True): return purch2_delete_all(docid, cn, commit)

Purch2API = _Purch2API()


# ============================================================
# KClStk - Kitchen/Cleaning Stock
# PK: DocId + Sno
# ============================================================
def _map_kclstk(r) -> dict:
    try:
        return {
            "docid": r.DocId or "", "sno": r.Sno or 0,
            "vtype": r.Vtype or "", "vno": r.VNo or 0,
            "vprefix": r.Vprefix or "", "vdate": r.Vdate,
            "item": r.Item or "",
            "qty": float(r.Qty or 0),
            "unit": r.Unit or "",
            "dept_code": r.DepartCode or "",
            "remarks": (r.Remarks or "").strip(),
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        d, s, vt, vn, vp, vd, it, q, u, dp, rem, un, _, uae, lgs = r
        return {
            "docid": d or "", "sno": s or 0,
            "vtype": vt or "", "vno": vn or 0,
            "vprefix": vp or "", "vdate": vd,
            "item": it or "",
            "qty": float(q or 0), "unit": u or "",
            "dept_code": dp or "",
            "remarks": (rem or "").strip(),
            "u_name": un or "", "u_ae": uae or "",
        }


def _validate_kclstk(rec: dict):
    if not rec.get("docid", "").strip():
        raise ValueError("DocId zaroori hai")
    if not rec.get("item", "").strip():
        raise ValueError("Item zaroori hai")


def kclstk_list(cn=None, limit: int = 500) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} DocId, Sno, Vtype, VNo, Site_Code, Vprefix, "
        "Vdate, Item, Qty, Unit, DepartCode, Remarks, "
        "U_Name, U_EntDt, U_AE, LogSite_Code "
        "FROM KClStk ORDER BY DocId, Sno", cn=cn)
    return [_map_kclstk(r) for r in rows]


def kclstk_get(docid: str, sno: int, cn=None) -> dict | None:
    rows = db.query(
        "SELECT DocId, Sno, Vtype, VNo, Site_Code, Vprefix, Vdate, "
        "Item, Qty, Unit, DepartCode, Remarks, U_Name, U_EntDt, "
        "U_AE, LogSite_Code "
        "FROM KClStk WHERE DocId = ? AND Sno = ?",
        (docid, sno), cn=cn)
    return _map_kclstk(rows[0]) if rows else None


def kclstk_lines(docid: str, cn=None) -> list[dict]:
    """Get all detail lines for a KClStk document."""
    rows = db.query(
        "SELECT DocId, Sno, Vtype, VNo, Site_Code, Vprefix, Vdate, "
        "Item, Qty, Unit, DepartCode, Remarks, U_Name, U_EntDt, "
        "U_AE, LogSite_Code "
        "FROM KClStk WHERE DocId = ? ORDER BY Sno",
        (docid,), cn=cn)
    return [_map_kclstk(r) for r in rows]


def kclstk_insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate_kclstk(rec)
    return db.execute(
        "INSERT INTO KClStk (DocId, Sno, Vtype, VNo, Site_Code, Vprefix, "
        "Vdate, Item, Qty, Unit, DepartCode, Remarks, "
        "U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["docid"], rec["sno"], rec.get("vtype", ""),
         rec.get("vno", 0), SITE_CODE, rec.get("vprefix", ""),
         rec.get("vdate"), rec["item"],
         float(rec.get("qty") or 0), rec.get("unit", ""),
         rec.get("dept_code", ""), rec.get("remarks", ""),
         rec.get("user", USER), SITE_CODE),
        cn=cn, commit=commit)


def kclstk_delete(docid: str, sno: int, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM KClStk WHERE DocId = ? AND Sno = ?",
        (docid, sno), cn=cn, commit=commit)


def kclstk_delete_all(docid: str, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM KClStk WHERE DocId = ?", (docid,),
        cn=cn, commit=commit)


class _KClStkAPI:
    @staticmethod
    def list_all(cn=None, limit=500): return kclstk_list(cn, limit)
    @staticmethod
    def get(docid, sno, cn=None): return kclstk_get(docid, sno, cn)
    @staticmethod
    def lines(docid, cn=None): return kclstk_lines(docid, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return kclstk_insert(rec, cn, commit)
    @staticmethod
    def delete(docid, sno, cn=None, commit=True): return kclstk_delete(docid, sno, cn, commit)
    @staticmethod
    def delete_all(docid, cn=None, commit=True): return kclstk_delete_all(docid, cn, commit)

KClStkAPI = _KClStkAPI()


# ============================================================
# INDENT1 - Indent Detail (uppercase in DB)
# PK: DocId + Sno
# ============================================================
def _map_indent1(r) -> dict:
    try:
        return {
            "docid": r.DocId or "", "sno": r.Sno or 0,
            "vtype": r.Vtype or "", "vno": r.VNo or 0,
            "vdate": r.VDate, "vprefix": r.Vprefix or "",
            "item": r.Item or "",
            "qty": float(r.Qty or 0),
            "unit": r.Unit or "",
            "rate": float(r.Rate or 0),
            "amount": float(r.Amount or 0),
            "specification": r.Specification or "",
            "clear_yn": r.ClearYN or "",
            "conv_factor": float(r.ConvFactor or 0),
            "wt_qty": float(r.WtQty or 0),
            "wt_unit": r.WtUnit or "",
            "tax_stru": r.TaxStru or "",
            "tax_amt": float(r.TaxAmt or 0),
            "total": float(r.Total or 0),
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        d, s, vt, vn, vd, vp, it, q, u, r2, a, sp, cy, cf, \
            wq, wu, ts, ta, t, un, _, uae, lgs = r
        return {
            "docid": d or "", "sno": s or 0,
            "vtype": vt or "", "vno": vn or 0,
            "vdate": vd, "vprefix": vp or "",
            "item": it or "",
            "qty": float(q or 0), "unit": u or "",
            "rate": float(r2 or 0), "amount": float(a or 0),
            "specification": sp or "",
            "clear_yn": cy or "",
            "conv_factor": float(cf or 0),
            "wt_qty": float(wq or 0), "wt_unit": wu or "",
            "tax_stru": ts or "",
            "tax_amt": float(ta or 0), "total": float(t or 0),
            "u_name": un or "", "u_ae": uae or "",
        }


def _validate_indent1(rec: dict):
    if not rec.get("docid", "").strip():
        raise ValueError("DocId zaroori hai")
    if not rec.get("item", "").strip():
        raise ValueError("Item zaroori hai")


def indent1_list(cn=None, limit: int = 500) -> list[dict]:
    cols = ("DocId, Sno, Vtype, VNo, VDate, Site_Code, Vprefix, Item, "
            "Qty, Unit, U_Name, U_EntDt, U_AE, Rate, Amount, "
            "Specification, ClearYN, ConvFactor, WtQty, WtUnit, "
            "LogSite_Code, TaxStru, TaxAmt, Total")
    rows = db.query(
        f"SELECT TOP {int(limit)} {cols} FROM INDENT1 ORDER BY DocId, Sno",
        cn=cn)
    return [_map_indent1(r) for r in rows]


def indent1_get(docid: str, sno: int, cn=None) -> dict | None:
    cols = ("DocId, Sno, Vtype, VNo, VDate, Site_Code, Vprefix, Item, "
            "Qty, Unit, U_Name, U_EntDt, U_AE, Rate, Amount, "
            "Specification, ClearYN, ConvFactor, WtQty, WtUnit, "
            "LogSite_Code, TaxStru, TaxAmt, Total")
    rows = db.query(
        f"SELECT {cols} FROM INDENT1 WHERE DocId = ? AND Sno = ?",
        (docid, sno), cn=cn)
    return _map_indent1(rows[0]) if rows else None


def indent1_lines(docid: str, cn=None) -> list[dict]:
    """Get all detail lines for an indent."""
    cols = ("DocId, Sno, Vtype, VNo, VDate, Site_Code, Vprefix, Item, "
            "Qty, Unit, U_Name, U_EntDt, U_AE, Rate, Amount, "
            "Specification, ClearYN, ConvFactor, WtQty, WtUnit, "
            "LogSite_Code, TaxStru, TaxAmt, Total")
    rows = db.query(
        f"SELECT {cols} FROM INDENT1 WHERE DocId = ? ORDER BY Sno",
        (docid,), cn=cn)
    return [_map_indent1(r) for r in rows]


def indent1_insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate_indent1(rec)
    # 24 columns = 22 params + 2 literals (getdate(), 'A')
    # Note: U_Name position 11 uses USER constant, not from rec
    return db.execute(
        "INSERT INTO INDENT1 (DocId, Sno, Vtype, VNo, VDate, Site_Code, "
        "Vprefix, Item, Qty, Unit, U_Name, U_EntDt, U_AE, Rate, Amount, "
        "Specification, ClearYN, ConvFactor, WtQty, WtUnit, "
        "LogSite_Code, TaxStru, TaxAmt, Total) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?, ?, "
        "?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (rec["docid"], rec["sno"], rec.get("vtype", ""),
         rec.get("vno", 0), rec.get("vdate"), SITE_CODE,
         rec.get("vprefix", ""), rec["item"],
         float(rec.get("qty") or 0), rec.get("unit", ""),
         USER,  # U_Name - was missing, causing parameter shift
         float(rec.get("rate") or 0), float(rec.get("amount") or 0),
         rec.get("specification", ""), rec.get("clear_yn", "N"),
         float(rec.get("conv_factor") or 0),
         float(rec.get("wt_qty") or 0), rec.get("wt_unit", ""),
         SITE_CODE, rec.get("tax_stru", ""),
         float(rec.get("tax_amt") or 0), float(rec.get("total") or 0)),
        cn=cn, commit=commit)


def indent1_delete(docid: str, sno: int, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM INDENT1 WHERE DocId = ? AND Sno = ?",
        (docid, sno), cn=cn, commit=commit)


def indent1_delete_all(docid: str, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM INDENT1 WHERE DocId = ?", (docid,),
        cn=cn, commit=commit)


class _INDENT1API:
    @staticmethod
    def list_all(cn=None, limit=500): return indent1_list(cn, limit)
    @staticmethod
    def get(docid, sno, cn=None): return indent1_get(docid, sno, cn)
    @staticmethod
    def lines(docid, cn=None): return indent1_lines(docid, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return indent1_insert(rec, cn, commit)
    @staticmethod
    def delete(docid, sno, cn=None, commit=True): return indent1_delete(docid, sno, cn, commit)
    @staticmethod
    def delete_all(docid, cn=None, commit=True): return indent1_delete_all(docid, cn, commit)

INDENT1API = _INDENT1API()


# ============================================================
# PORDER1 - Purchase Order Detail
# PK: Docid + Sno (note: lowercase 'd' in Docid)
# ============================================================
def _map_porder1(r) -> dict:
    try:
        return {
            "docid": r.Docid or "", "sno": r.Sno or 0,
            "vno": r.VNo or 0, "vdate": r.VDate,
            "vtype": r.VType or "", "vprefix": r.VPrefix or "",
            "party_code": r.PartyCode or "",
            "item_code": r.ItemCode or "",
            "qty": float(r.Qty or 0),
            "unit": r.Unit or "",
            "rate": float(r.Rate or 0),
            "per_unit": float(r.PerUnit or 0),
            "amount": float(r.Amount or 0),
            "indent_docid": r.IndentDocId or "",
            "indent_sno": r.IndentSno or 0,
            "specification": r.Specification or "",
            "conv_ratio": float(r.ConvRatio or 0),
            "wt_qty": float(r.WtQty or 0),
            "wt_unit": r.WtUnit or "",
            "tax_stru": r.TaxStru or "",
            "tax_amt": float(r.TaxAmt or 0),
            "total": float(r.Total or 0),
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        d, s, vn, vd, vt, vp, pc, ic, q, u, r2, pu, a, \
            idd, isn, sp, cr, wq, wu, ts, ta, t, un, _, uae, lgs = r
        return {
            "docid": d or "", "sno": s or 0,
            "vno": vn or 0, "vdate": vd,
            "vtype": vt or "", "vprefix": vp or "",
            "party_code": pc or "",
            "item_code": ic or "",
            "qty": float(q or 0), "unit": u or "",
            "rate": float(r2 or 0), "per_unit": float(pu or 0),
            "amount": float(a or 0),
            "indent_docid": idd or "", "indent_sno": isn or 0,
            "specification": sp or "",
            "conv_ratio": float(cr or 0),
            "wt_qty": float(wq or 0), "wt_unit": wu or "",
            "tax_stru": ts or "",
            "tax_amt": float(ta or 0), "total": float(t or 0),
            "u_name": un or "", "u_ae": uae or "",
        }


def _validate_porder1(rec: dict):
    if not rec.get("docid", "").strip():
        raise ValueError("Docid zaroori hai")
    if not rec.get("item_code", "").strip():
        raise ValueError("ItemCode zaroori hai")


def porder1_list(cn=None, limit: int = 500) -> list[dict]:
    cols = ("Docid, Sno, VNo, VDate, VType, VPrefix, Site_Code, "
            "PartyCode, ItemCode, Qty, Unit, Rate, PerUnit, Amount, "
            "U_Name, U_EntDt, U_AE, IndentDocId, IndentSno, "
            "Specification, ConvRatio, WtQty, WtUnit, "
            "LogSite_Code, TaxStru, TaxAmt, Total")
    rows = db.query(
        f"SELECT TOP {int(limit)} {cols} FROM PORDER1 ORDER BY Docid, Sno",
        cn=cn)
    return [_map_porder1(r) for r in rows]


def porder1_get(docid: str, sno: int, cn=None) -> dict | None:
    cols = ("Docid, Sno, VNo, VDate, VType, VPrefix, Site_Code, "
            "PartyCode, ItemCode, Qty, Unit, Rate, PerUnit, Amount, "
            "U_Name, U_EntDt, U_AE, IndentDocId, IndentSno, "
            "Specification, ConvRatio, WtQty, WtUnit, "
            "LogSite_Code, TaxStru, TaxAmt, Total")
    rows = db.query(
        f"SELECT {cols} FROM PORDER1 WHERE Docid = ? AND Sno = ?",
        (docid, sno), cn=cn)
    return _map_porder1(rows[0]) if rows else None


def porder1_lines(docid: str, cn=None) -> list[dict]:
    """Get all detail lines for a purchase order."""
    cols = ("Docid, Sno, VNo, VDate, VType, VPrefix, Site_Code, "
            "PartyCode, ItemCode, Qty, Unit, Rate, PerUnit, Amount, "
            "U_Name, U_EntDt, U_AE, IndentDocId, IndentSno, "
            "Specification, ConvRatio, WtQty, WtUnit, "
            "LogSite_Code, TaxStru, TaxAmt, Total")
    rows = db.query(
        f"SELECT {cols} FROM PORDER1 WHERE Docid = ? ORDER BY Sno",
        (docid,), cn=cn)
    return [_map_porder1(r) for r in rows]


def porder1_insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate_porder1(rec)
    # 27 columns = 25 params + 2 literals (getdate(), 'A')
    params = (rec["docid"], rec["sno"], rec.get("vno", 0),
              rec.get("vdate"), rec.get("vtype", ""),
              rec.get("vprefix", ""), SITE_CODE,
              rec.get("party_code", ""), rec["item_code"],
              float(rec.get("qty") or 0), rec.get("unit", ""),
              float(rec.get("rate") or 0), float(rec.get("per_unit") or 0),
              float(rec.get("amount") or 0), USER,
              rec.get("indent_docid", ""), rec.get("indent_sno", 0),
              rec.get("specification", ""),
              float(rec.get("conv_ratio") or 0),
              float(rec.get("wt_qty") or 0), rec.get("wt_unit", ""),
              SITE_CODE, rec.get("tax_stru", ""),
              float(rec.get("tax_amt") or 0), float(rec.get("total") or 0))
    # Verify param count matches placeholders (25 params + 2 literals = 27 cols)
    assert len(params) == 25, f"Expected 25 params, got {len(params)}"
    return db.execute(
        "INSERT INTO PORDER1 (Docid, Sno, VNo, VDate, VType, VPrefix, "
        "Site_Code, PartyCode, ItemCode, Qty, Unit, Rate, PerUnit, "
        "Amount, U_Name, U_EntDt, U_AE, IndentDocId, IndentSno, "
        "Specification, ConvRatio, WtQty, WtUnit, LogSite_Code, "
        "TaxStru, TaxAmt, Total) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
        "getdate(), 'A', ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        params,
        cn=cn, commit=commit)


def porder1_delete(docid: str, sno: int, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM PORDER1 WHERE Docid = ? AND Sno = ?",
        (docid, sno), cn=cn, commit=commit)


def porder1_delete_all(docid: str, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM PORDER1 WHERE Docid = ?", (docid,),
        cn=cn, commit=commit)


class _PORDER1API:
    @staticmethod
    def list_all(cn=None, limit=500): return porder1_list(cn, limit)
    @staticmethod
    def get(docid, sno, cn=None): return porder1_get(docid, sno, cn)
    @staticmethod
    def lines(docid, cn=None): return porder1_lines(docid, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return porder1_insert(rec, cn, commit)
    @staticmethod
    def delete(docid, sno, cn=None, commit=True): return porder1_delete(docid, sno, cn, commit)
    @staticmethod
    def delete_all(docid, cn=None, commit=True): return porder1_delete_all(docid, cn, commit)

PORDER1API = _PORDER1API()
