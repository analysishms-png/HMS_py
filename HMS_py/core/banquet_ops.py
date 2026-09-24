"""Banquet Operations Core (P8): Booking, Billing, Estimate, Advance/Deposit.

EVIDENCE (live DB + VB6 decompiled):
- HallBook: Banquet booking header - EXISTS (0 rows in live)
  DocId, Vtype, VNo, VTime, Site_Code, Vprefix, Vdate, PartyName,
  Add1, Add2, City, PinCode, PANNO, ContactNo_Res, ContactNo_Off,
  MobileNo, Func_Name, BookingStatus, RestCode, FrBookDate, FrBookTime,
  ToBookDate, ToBookTime, HouseKeep, FrontOff, Engg, Security, Chef,
  Board, MenuSpl1-7, Advance, RectNo, rectDate, CrCardNo, CrCardHolder,
  Total, DiscPer, DiscAmt, NonTaxable, Taxable, Tax, ServiceCharge,
  AddAmt, DedAmt, RoundOff, ExpAtt, GuarAtt, CoverRate, U_Name, U_EntDt,
  U_AE, HallRent, Remarks, MenuCatalog, Amount, MarketSeg, BussSource,
  CompanyCode, TotalCoverRate, NetAmount, InquiryCode, ContactNo,
  TaxPer, ServiceTaxPer, OtherChrg, LogSite_Code, Remark, BookingAgent

- HallBook1: Booking detail lines (items) - EXISTS (0 rows)
  DocId, Sno, Vtype, VNo, Site_Code, Vprefix, Vdate, PartyCode,
  RestCode, RoomCat, RoomType, RoomNo, ContraDocId, ContraSno, Item,
  QtyIss, QtyRec, Unit, Rate, Amount, TaxPer, TaxAmt, DiscPer, DiscAmt,
  VoidYN, Remarks, KOTDocId, KOTSno, VTime, U_Name, U_EntDt, U_AE,
  Total, DiscApp, RoundOff, PartyName, LogSite_Code

- HallSale1: Banquet bill header - EXISTS (0 rows)
  DocId, Vtype, VNo, VTime, Site_Code, Vprefix, Vdate, RestCode, Party,
  Total, DiscPer, DiscAmt, NonTaxable, Taxable, Tax, ServiceCharge,
  AddAmt, DedAmt, RoundOff, NetAmt, FrBookDate, FrBookTime, U_Name,
  U_EntDt, U_AE, ToBookDate, ToBookTime, HallRent, Remarks, NoOfPax,
  RatePerPax, TotalPerCover, Amount, Advance, RectNo, rectDate,
  CrCardNo, CrCardHolder, BookDocId, DelFlag, Narration, LogSite_Code,
  Narration1, CGST, SGST, IGST

- HallSale2: Bill tax/detail lines - EXISTS (0 rows)
  DocId, Sno, SNo1, Vtype, VNo, Site_Code, Vprefix, Vdate, RestCode,
  TaxCode, BaseValue, TaxPer, TaxAmt, U_Name, U_EntDt, U_AE, DelFlag,
  LOGSITE_CODE

- VenueOcc: Venue occupancy (linked to booking) - EXISTS (0 rows)
  FPDocid, VenuCode, FromDate, ToDate, FromTime, ToTime, Site_Code,
  U_Name, U_EntDt, U_AE, LogSite_Code

- BookingDetail: Additional booking info - EXISTS (0 rows)
  Code, VenueCode, FuncDate, ToDate, FuncTime, ToTime, Site_Code,
  U_EntDt, U_AE, LogSite_Code

VB6 patterns: HallBooking.frm (TopCtrl), HallBill.frm, CateringBooking.frm,
HallAdvanceDepDialog, HallEstimate.frm, HallBillEstimate.frm

Document numbering: HallBook uses 'HBK' Vtype series (IBOOK/OBOOK)
HallSale1 uses 'HSL' Vtype series (IDC=Indoor, ODC=Outdoor)
VNo from Voucher_Type + Voucher_Prefix per RestCode
"""
from __future__ import annotations

import datetime
from typing import Optional

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
VPREFIX = "2026"

# Vtypes
VTYPE_IBOOK = "IBOOK"
VTYPE_OBOOK = "OBOOK"
VTYPE_HSL_IDC = "IDC"  # Indoor bill
VTYPE_HSL_ODC = "ODC"  # Outdoor bill

# Pay codes for hall charges
PAY_CODE_HALL = "KKHALL"
CGST_CODE = "KKCGSS"
SGST_CODE = "KKSGSS"
GST_RATE = 0.05  # 5% CGST + 5% SGST


# ============================================================
# Helpers
# ============================================================

def _make_hall_docid(vtype: str, vprefix: str, vno: int) -> str:
    """'D'+site(2)+vtype.ljust(6)+vprefix(4)+VNo.rjust(8) = 21 char"""
    return "D" + SITE_CODE + vtype.ljust(6) + vprefix.ljust(4) + str(vno).rjust(8)


def _next_vno(vtype: str, vprefix: str, cn=None) -> int:
    """Next VNo for a VType/VPrefix from Voucher_Type.

    BUG-015: race-safe (UPDLOCK/HOLDLOCK) - concurrent bookings ko same
    number nahi milega. NOTE: Voucher_Type me Site_Code filter nahi hai
    (VB6 pattern), isliye raw lock query yahin rakhi hai.
    """
    rows = db.query(
        "SELECT MAX(VNo) FROM Voucher_Type WITH (UPDLOCK, HOLDLOCK) "
        "WHERE V_Type = ? AND VPrefix = ?",
        (vtype, vprefix), cn=cn)
    return (rows[0][0] or 0) + 1 if rows and rows[0][0] else 1


def _next_sno(docid: str, cn=None) -> int:
    """Next SNo for HallBook1 lines."""
    rows = db.query(
        "SELECT MAX(Sno) FROM HallBook1 WHERE DocId = ?", (docid,), cn=cn)
    return (rows[0][0] or 0) + 1 if rows and rows[0][0] else 1


# ============================================================
# HallBook (Booking Header)
# ============================================================

HALLBOOK_COLS = (
    "DocId, Vtype, VNo, VTime, Site_Code, Vprefix, Vdate, PartyName, "
    "Add1, Add2, City, PinCode, PANNO, ContactNo_Res, ContactNo_Off, "
    "MobileNo, Func_Name, BookingStatus, RestCode, FrBookDate, FrBookTime, "
    "ToBookDate, ToBookTime, HouseKeep, FrontOff, Engg, Security, Chef, "
    "Board, MenuSpl1, MenuSpl2, MenuSpl3, MenuSpl4, MenuSpl5, MenuSpl6, "
    "MenuSpl7, Advance, RectNo, rectDate, CrCardNo, CrCardHolder, Total, "
    "DiscPer, DiscAmt, NonTaxable, Taxable, Tax, ServiceCharge, AddAmt, "
    "DedAmt, RoundOff, ExpAtt, GuarAtt, CoverRate, U_Name, U_EntDt, U_AE, "
    "HallRent, Remarks, MenuCatalog, Amount, MarketSeg, BussSource, "
    "CompanyCode, TotalCoverRate, NetAmount, InquiryCode, ContactNo, "
    "TaxPer, ServiceTaxPer, OtherChrg, LogSite_Code, Remark, BookingAgent"
)


def _map_hallbook(r) -> dict:
    try:
        return {
            "docid": r.DocId, "vtype": r.Vtype or "", "vno": r.VNo,
            "vtime": r.VTime, "vprefix": r.Vprefix or "", "vdate": r.Vdate,
            "party": (r.PartyName or "").strip(),
            "add1": (r.Add1 or "").strip(), "add2": (r.Add2 or "").strip(),
            "city": r.City or "", "pin": r.PinCode or "", "pan": r.PANNO or "",
            "phone_res": r.ContactNo_Res or "", "phone_off": r.ContactNo_Off or "",
            "mobile": r.MobileNo or "", "func_name": r.Func_Name or "",
            "booking_status": r.BookingStatus or "",
            "rest": r.RestCode or "",
            "frdate": r.FrBookDate, "frtime": r.FrBookTime,
            "todate": r.ToBookDate, "totime": r.ToBookTime,
            "housekeep": r.HouseKeep or "", "frontoff": r.FrontOff or "",
            "engg": r.Engg or "", "security": r.Security or "",
            "chef": r.Chef or "", "board": r.Board or "",
            "menu1": r.MenuSpl1 or "", "menu2": r.MenuSpl2 or "",
            "menu3": r.MenuSpl3 or "", "menu4": r.MenuSpl4 or "",
            "menu5": r.MenuSpl5 or "", "menu6": r.MenuSpl6 or "",
            "menu7": r.MenuSpl7 or "",
            "advance": float(r.Advance or 0),
            "rectno": r.RectNo or "", "rectdate": r.rectDate,
            "cardno": r.CrCardNo or "", "cardholder": r.CrCardHolder or "",
            "total": float(r.Total or 0), "discper": float(r.DiscPer or 0),
            "discamt": float(r.DiscAmt or 0),
            "nontaxable": float(r.NonTaxable or 0), "taxable": float(r.Taxable or 0),
            "tax": float(r.Tax or 0), "service": float(r.ServiceCharge or 0),
            "addamt": float(r.AddAmt or 0), "dedamt": float(r.DedAmt or 0),
            "roundoff": float(r.RoundOff or 0), "expatt": r.ExpAtt or "",
            "guaratt": int(r.GuarAtt or 0), "cover_rate": float(r.CoverRate or 0),
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
            "hallrent": float(r.HallRent or 0),
            "remarks": (r.Remarks or "").strip(),
            "menucat": r.MenuCatalog or "", "amount": float(r.Amount or 0),
            "mktseg": r.MarketSeg or "", "bussrc": r.BussSource or "",
            "company": r.CompanyCode or "", "totalcover": float(r.TotalCoverRate or 0),
            "netamt": float(r.NetAmount or 0), "inquiry": r.InquiryCode or "",
            "contact": r.ContactNo or "", "taxper": float(r.TaxPer or 0),
            "servtaxper": float(r.ServiceTaxPer or 0), "otherchrg": float(r.OtherChrg or 0),
            "remark": (r.Remark or "").strip(), "agent": r.BookingAgent or "",
        }
    except AttributeError:
        # Fallback for tuple - just return basic fields
        return {
            "docid": str(r[0]), "vtype": str(r[1] or ""), "vno": r[2],
            "party": str(r[7] or "").strip(), "add1": str(r[8] or "").strip(),
            "add2": str(r[9] or "").strip(), "city": str(r[10] or ""),
            "rest": str(r[18] or ""), "mktseg": str(r[58] or ""),
            "bussrc": str(r[59] or ""), "company": str(r[60] or ""),
            "inquiry": str(r[65] or ""), "agent": str(r[67] or ""),
            "remark": str(r[66] or "").strip(),
            "u_name": str(r[48] or ""), "u_ae": str(r[50] or ""),
        }


def hallbook_list(cn=None, top: int = 300) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(top)} {HALLBOOK_COLS} FROM HallBook ORDER BY DocId DESC",
        cn=cn)
    return [_map_hallbook(r) for r in rows]


def hallbook_get(docid: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {HALLBOOK_COLS} FROM HallBook WHERE DocId = ?", (docid,), cn=cn)
    return _map_hallbook(rows[0]) if rows else None


def hallbook_exists(docid: str, cn=None) -> bool:
    return bool(db.query(
        "SELECT 1 FROM HallBook WHERE DocId = ?", (docid,), cn=cn))


def hallbook_insert(rec: dict, cn=None, commit: bool = True) -> int:
    """Insert a new banquet booking."""
    vtype = rec.get("vtype", VTYPE_IBOOK).strip().upper()
    if vtype not in (VTYPE_IBOOK, VTYPE_OBOOK):
        raise ValueError("Vtype must be IBOOK or OBOOK")

    if not rec.get("party", "").strip():
        raise ValueError("PartyName zaroori hai")

    # Get next VNo
    vno = _next_vno(vtype, VPREFIX, cn=cn)
    docid = _make_hall_docid(vtype, VPREFIX, vno)
    now = datetime.datetime.now()

    # Minimal insert with required columns
    cols = [
        "DocId", "Vtype", "VNo", "VTime", "Site_Code", "Vprefix", "Vdate",
        "PartyName", "Add1", "Add2", "City", "PinCode", "PANNO",
        "ContactNo_Res", "ContactNo_Off", "MobileNo", "Func_Name",
        "BookingStatus", "RestCode", "FrBookDate", "FrBookTime",
        "ToBookDate", "ToBookTime", "Total", "DiscPer", "DiscAmt",
        "NonTaxable", "Taxable", "Tax", "ServiceCharge", "AddAmt",
        "DedAmt", "RoundOff", "ExpAtt", "GuarAtt", "CoverRate",
        "U_Name", "U_EntDt", "U_AE", "HallRent", "Remarks",
        "MenuCatalog", "Amount", "MarketSeg", "BussSource", "CompanyCode",
        "TotalCoverRate", "NetAmount", "InquiryCode", "ContactNo",
        "TaxPer", "ServiceTaxPer", "OtherChrg", "LogSite_Code", "Remark",
        "BookingAgent"
    ]

    vals = [
        docid, vtype, vno, now.strftime("%H:%M"), SITE_CODE, VPREFIX,
        now.date(), rec["party"], rec.get("add1", ""), rec.get("add2", ""),
        rec.get("city", ""), rec.get("pin", ""), rec.get("pan", ""),
        rec.get("phone_res", ""), rec.get("phone_off", ""),
        rec.get("mobile", ""), rec.get("func_name", ""),
        rec.get("booking_status", "Confirmed"), rec.get("rest", ""),
        rec.get("frdate", now.date()), rec.get("frtime", "00:00"),
        rec.get("todate", now.date() + datetime.timedelta(days=1)),
        rec.get("totime", "23:59"), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, "", int(rec.get("guaratt", 0)),
        float(rec.get("cover_rate", 0)), USER, now, "A",
        float(rec.get("hallrent", 0)), rec.get("remark", ""),
        rec.get("menucat", ""), 0.0, rec.get("mktseg", ""),
        rec.get("bussrc", ""), rec.get("company", ""), 0.0, 0.0,
        rec.get("inquiry", ""), rec.get("contact", ""), 0.0, 0.0, 0.0,
        SITE_CODE, rec.get("remark", ""), rec.get("agent", "")
    ]

    placeholders = ", ".join(["?"] * len(vals))
    sql = f"INSERT INTO HallBook ({', '.join(cols)}) VALUES ({placeholders})"
    return db.execute(sql, tuple(vals), cn=cn, commit=commit)


def hallbook_update(docid: str, rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "UPDATE HallBook SET PartyName = ?, Add1 = ?, Add2 = ?, City = ?, "
        "PinCode = ?, PANNO = ?, ContactNo_Res = ?, ContactNo_Off = ?, "
        "MobileNo = ?, Func_Name = ?, BookingStatus = ?, RestCode = ?, "
        "Total = ?, DiscPer = ?, DiscAmt = ?, NonTaxable = ?, Taxable = ?, "
        "Tax = ?, ServiceCharge = ?, AddAmt = ?, DedAmt = ?, RoundOff = ?, "
        "ExpAtt = ?, GuarAtt = ?, CoverRate = ?, U_Name = ?, U_EntDt = getdate(), "
        "U_AE = 'E', HallRent = ?, Remarks = ?, MenuCatalog = ?, Amount = ?, "
        "MarketSeg = ?, BussSource = ?, CompanyCode = ?, TotalCoverRate = ?, "
        "NetAmount = ?, InquiryCode = ?, ContactNo = ?, TaxPer = ?, "
        "ServiceTaxPer = ?, OtherChrg = ?, Remark = ?, BookingAgent = ? "
        "WHERE DocId = ?",
        (rec.get("party", ""), rec.get("add1", ""), rec.get("add2", ""),
         rec.get("city", ""), rec.get("pin", ""), rec.get("pan", ""),
         rec.get("phone_res", ""), rec.get("phone_off", ""),
         rec.get("mobile", ""), rec.get("func_name", ""),
         rec.get("booking_status", "Confirmed"), rec.get("rest", ""),
         float(rec.get("total", 0)), float(rec.get("discper", 0)),
         float(rec.get("discamt", 0)), float(rec.get("nontaxable", 0)),
         float(rec.get("taxable", 0)), float(rec.get("tax", 0)),
         float(rec.get("service", 0)), float(rec.get("addamt", 0)),
         float(rec.get("dedamt", 0)), float(rec.get("roundoff", 0)),
         rec.get("expatt", ""), int(rec.get("guaratt", 0)),
         float(rec.get("cover_rate", 0)), USER,
         float(rec.get("hallrent", 0)), rec.get("remarks", ""),
         rec.get("menucat", ""), float(rec.get("amount", 0)),
         rec.get("mktseg", ""), rec.get("bussrc", ""), rec.get("company", ""),
         float(rec.get("totalcover", 0)), float(rec.get("netamt", 0)),
         rec.get("inquiry", ""), rec.get("contact", ""),
         float(rec.get("taxper", 0)), float(rec.get("servtaxper", 0)),
         float(rec.get("otherchrg", 0)), rec.get("remark", ""),
         rec.get("agent", ""), docid),
        cn=cn, commit=commit)


def hallbook_delete(docid: str, cn=None, commit: bool = True) -> int:
    if not docid.upper().startswith("PYT"):
        raise ValueError("Safety: sirf PYT* bookings delete hote hain")
    return db.execute(
        "DELETE FROM HallBook WHERE DocId = ?", (docid,), cn=cn, commit=commit)


# ============================================================
# HallBook1 (Booking Detail Lines)
# ============================================================

HALLBOOK1_COLS = (
    "DocId, Sno, Vtype, VNo, Site_Code, Vprefix, Vdate, PartyCode, "
    "RestCode, RoomCat, RoomType, RoomNo, ContraDocId, ContraSno, Item, "
    "QtyIss, QtyRec, Unit, Rate, Amount, TaxPer, TaxAmt, DiscPer, DiscAmt, "
    "VoidYN, Remarks, KOTDocId, KOTSno, VTime, U_Name, U_EntDt, U_AE, "
    "Total, DiscApp, RoundOff, PartyName, LogSite_Code"
)


def _map_hallbook1(r) -> dict:
    try:
        return {
            "docid": r.DocId, "sno": r.Sno, "vtype": r.Vtype or "",
            "vno": r.VNo, "vprefix": r.Vprefix or "", "vdate": r.Vdate,
            "partycode": r.PartyCode or "", "rest": r.RestCode or "",
            "roomcat": r.RoomCat or "", "roomtype": r.RoomType or "",
            "roomno": r.RoomNo or "", "contradocid": r.ContraDocId or "",
            "contrasno": r.ContraSno or 0, "item": r.Item or "",
            "qtyiss": float(r.QtyIss or 0), "qtyrec": float(r.QtyRec or 0),
            "unit": r.Unit or "", "rate": float(r.Rate or 0),
            "amount": float(r.Amount or 0), "taxper": float(r.TaxPer or 0),
            "taxamt": float(r.TaxAmt or 0), "discper": float(r.DiscPer or 0),
            "discamt": float(r.DiscAmt or 0), "voidyn": r.VoidYN or "N",
            "remarks": (r.Remarks or "").strip(),
            "kotdocid": r.KOTDocId or "", "kotsno": r.KOTSno or 0,
            "vtime": r.VTime, "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
            "total": float(r.Total or 0), "discapp": r.DiscApp or "N",
            "roundoff": float(r.RoundOff or 0), "partyname": (r.PartyName or "").strip(),
        }
    except AttributeError:
        d, sn, vt, vn, sc, vp, vd, pc, rc, rcat, rtype, rno, cd, cs, it, qi, qr, un, rt, am, tp, ta, dp, da, vy, rm, kd, ks, vt2, un2, _, uae, tot, da2, ro, pn, ls = r
        return {
            "docid": d, "sno": sn, "vtype": vt or "", "vno": vn,
            "item": it or "", "qtyiss": float(qi or 0), "rate": float(rt or 0),
            "amount": float(am or 0), "taxper": float(tp or 0),
            "taxamt": float(ta or 0), "discper": float(dp or 0),
            "discamt": float(da or 0), "remarks": (rm or "").strip(),
            "u_name": un2 or "", "u_ae": uae or "",
        }


def hallbook1_lines(docid: str, cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {HALLBOOK1_COLS} FROM HallBook1 WHERE DocId = ? ORDER BY Sno",
        (docid,), cn=cn)
    return [_map_hallbook1(r) for r in rows]


def hallbook1_insert(docid: str, line: dict, cn=None, commit: bool = True) -> int:
    sno = _next_sno(docid, cn=cn)
    now = datetime.datetime.now()

    cols = [
        "DocId", "Sno", "Vtype", "VNo", "Site_Code", "Vprefix", "Vdate",
        "PartyCode", "RestCode", "RoomCat", "RoomType", "RoomNo",
        "ContraDocId", "ContraSno", "Item", "QtyIss", "QtyRec", "Unit",
        "Rate", "Amount", "TaxPer", "TaxAmt", "DiscPer", "DiscAmt",
        "VoidYN", "Remarks", "KOTDocId", "KOTSno", "VTime", "U_Name",
        "U_EntDt", "U_AE", "Total", "DiscApp", "RoundOff", "PartyName",
        "LogSite_Code"
    ]

    vals = [
        docid, sno, line.get("vtype", ""), line.get("vno", 0),
        SITE_CODE, VPREFIX, now.date(),
        line.get("partycode", ""), line.get("rest", ""),
        line.get("roomcat", ""), line.get("roomtype", ""),
        line.get("roomno", ""), line.get("contradocid", ""),
        line.get("contrasno", 0), line.get("item", ""),
        float(line.get("qtyiss", 0)), float(line.get("qtyrec", 0)),
        line.get("unit", ""), float(line.get("rate", 0)),
        float(line.get("amount", 0)), float(line.get("taxper", 0)),
        float(line.get("taxamt", 0)), float(line.get("discper", 0)),
        float(line.get("discamt", 0)), line.get("voidyn", "N"),
        line.get("remarks", ""), line.get("kotdocid", ""),
        line.get("kotsno", 0), now.strftime("%H:%M"), USER,
        now, "A", float(line.get("total", 0)), line.get("discapp", "N"),
        float(line.get("roundoff", 0)), line.get("partyname", ""),
        SITE_CODE
    ]

    placeholders = ", ".join(["?"] * len(vals))
    sql = f"INSERT INTO HallBook1 ({', '.join(cols)}) VALUES ({placeholders})"
    return db.execute(sql, tuple(vals), cn=cn, commit=commit)


def hallbook1_delete(docid: str, sno: int, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM HallBook1 WHERE DocId = ? AND Sno = ?",
        (docid, sno), cn=cn, commit=commit)


# ============================================================
# HallSale1 (Banquet Bill Header)
# ============================================================

HALLSALE1_COLS = (
    "DocId, Vtype, VNo, VTime, Site_Code, Vprefix, Vdate, RestCode, Party, "
    "Total, DiscPer, DiscAmt, NonTaxable, Taxable, Tax, ServiceCharge, "
    "AddAmt, DedAmt, RoundOff, NetAmt, FrBookDate, FrBookTime, U_Name, "
    "U_EntDt, U_AE, ToBookDate, ToBookTime, HallRent, Remarks, NoOfPax, "
    "RatePerPax, TotalPerCover, Amount, Advance, RectNo, rectDate, "
    "CrCardNo, CrCardHolder, BookDocId, DelFlag, Narration, LogSite_Code, "
    "Narration1, CGST, SGST, IGST"
)


def _map_hallsale1(r) -> dict:
    try:
        return {
            "docid": r.DocId, "vtype": r.Vtype or "", "vno": r.VNo,
            "vtime": r.VTime, "vprefix": r.Vprefix or "", "vdate": r.Vdate,
            "rest": r.RestCode or "", "party": (r.Party or "").strip(),
            "total": float(r.Total or 0), "discper": float(r.DiscPer or 0),
            "discamt": float(r.DiscAmt or 0),
            "nontaxable": float(r.NonTaxable or 0), "taxable": float(r.Taxable or 0),
            "tax": float(r.Tax or 0), "service": float(r.ServiceCharge or 0),
            "addamt": float(r.AddAmt or 0), "dedamt": float(r.DedAmt or 0),
            "roundoff": float(r.RoundOff or 0), "netamt": float(r.NetAmt or 0),
            "frdate": r.FrBookDate, "frtime": r.FrBookTime,
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
            "todate": r.ToBookDate, "totime": r.ToBookTime,
            "hallrent": float(r.HallRent or 0),
            "remarks": (r.Remarks or "").strip(),
            "pax": int(r.NoOfPax or 0), "rateper": float(r.RatePerPax or 0),
            "totalper": float(r.TotalPerCover or 0), "amount": float(r.Amount or 0),
            "advance": float(r.Advance or 0), "rectno": r.RectNo or "",
            "rectdate": r.rectDate, "cardno": r.CrCardNo or "",
            "cardholder": r.CrCardHolder or "", "bookdocid": r.BookDocId or "",
            "delflag": r.DelFlag or "N", "narration": (r.Narration or "").strip(),
            "narration1": (r.Narration1 or "").strip(),
            "cgst": float(r.CGST or 0), "sgst": float(r.SGST or 0),
            "igst": float(r.IGST or 0),
        }
    except AttributeError:
        d, vt, vn, vt2, sc, vp, vd, rc, pa, tot, dp, da, nt, tx, tx2, sv, aa, dd, ro, na, fd, ft, un, _, uae, td, tt, hr, rm, np, rp, tp, am, ad, rn, rd, cn, ch, bd, df, nar, ls, nar1, cg, sg, ig = r
        return {
            "docid": d, "vtype": vt or "", "vno": vn, "vprefix": vp or "",
            "vdate": vd, "rest": rc or "", "party": (pa or "").strip(),
            "total": float(tot or 0), "discper": float(dp or 0),
            "discamt": float(da or 0), "nontaxable": float(nt or 0),
            "taxable": float(tx or 0), "tax": float(tx2 or 0),
            "service": float(sv or 0), "addamt": float(aa or 0),
            "dedamt": float(dd or 0), "roundoff": float(ro or 0),
            "netamt": float(na or 0), "frdate": fd, "frtime": ft,
            "u_name": un or "", "u_ae": uae or "", "todate": td, "totime": tt,
            "hallrent": float(hr or 0), "remarks": (rm or "").strip(),
            "pax": int(np or 0), "rateper": float(rp or 0),
            "totalper": float(tp or 0), "amount": float(am or 0),
            "advance": float(ad or 0), "rectno": rn or "", "rectdate": rd,
            "cardno": cn or "", "cardholder": ch or "", "bookdocid": bd or "",
            "delflag": df or "N", "narration": (nar or "").strip(),
            "narration1": (nar1 or "").strip(), "cgst": float(cg or 0),
            "sgst": float(sg or 0), "igst": float(ig or 0),
        }


def hallsale1_list(cn=None, top: int = 300) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(top)} {HALLSALE1_COLS} FROM HallSale1 ORDER BY DocId DESC",
        cn=cn)
    return [_map_hallsale1(r) for r in rows]


def hallsale1_get(docid: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {HALLSALE1_COLS} FROM HallSale1 WHERE DocId = ?", (docid,), cn=cn)
    return _map_hallsale1(rows[0]) if rows else None


def hallsale1_get_by_booking(bookdocid: str, cn=None) -> list[dict]:
    """Get all bills for a booking."""
    rows = db.query(
        f"SELECT {HALLSALE1_COLS} FROM HallSale1 WHERE BookDocId = ? ORDER BY VNo",
        (bookdocid,), cn=cn)
    return [_map_hallsale1(r) for r in rows]


def _calc_bill_amounts(lines: list[dict]) -> dict:
    """Calculate bill totals from lines."""
    total = sum(float(l.get("amount", 0)) for l in lines)
    disc_per = 0.0
    disc_amt = sum(float(l.get("discamt", 0)) for l in lines)
    taxable = sum(float(l.get("amount", 0)) for l in lines if float(l.get("taxper", 0)) > 0)
    nontaxable = sum(float(l.get("amount", 0)) for l in lines if float(l.get("taxper", 0)) == 0)
    tax = sum(float(l.get("taxamt", 0)) for l in lines)
    cgst = sum(float(l.get("taxamt", 0)) for l in lines if float(l.get("taxper", 0)) > 0 and "CGST" in str(l.get("taxcode", "")))
    sgst = sum(float(l.get("taxamt", 0)) for l in lines if float(l.get("taxper", 0)) > 0 and "SGST" in str(l.get("taxcode", "")))
    igst = sum(float(l.get("taxamt", 0)) for l in lines if float(l.get("taxper", 0)) > 0 and "IGST" in str(l.get("taxcode", "")))
    service = sum(float(l.get("amount", 0)) for l in lines if "SERVICE" in str(l.get("item", "")).upper())
    netamt = total - disc_amt + tax + service
    return {
        "total": total, "discper": disc_per, "discamt": disc_amt,
        "nontaxable": nontaxable, "taxable": taxable, "tax": tax,
        "cgst": cgst, "sgst": sgst, "igst": igst, "service": service,
        "netamt": netamt
    }


def hallsale1_create_from_booking(
    bookdocid: str, vtype: str, restcode: str, user: str = USER,
    cn=None, commit: bool = True
) -> str:
    """Create a banquet bill from a booking.
    vtype: 'IDC' (indoor) or 'ODC' (outdoor)
    """
    # Get booking
    booking = hallbook_get(bookdocid, cn=cn)
    if not booking:
        raise ValueError(f"Booking {bookdocid} nahi mila")

    # Get lines
    lines = hallbook1_lines(bookdocid, cn=cn)
    if not lines:
        raise ValueError("Booking me koi items nahi hain")

    # Get next VNo
    vno = _next_vno(vtype, VPREFIX, cn=cn)
    docid = _make_hall_docid(vtype, VPREFIX, vno)

    # Calculate amounts
    amounts = _calc_bill_amounts(lines)

    # Insert HallSale1 header
    now = datetime.datetime.now()
    cols = [
        "DocId", "Vtype", "VNo", "VTime", "Site_Code", "Vprefix", "Vdate",
        "RestCode", "Party", "Total", "DiscPer", "DiscAmt", "NonTaxable",
        "Taxable", "Tax", "ServiceCharge", "AddAmt", "DedAmt", "RoundOff",
        "NetAmt", "FrBookDate", "FrBookTime", "U_Name", "U_EntDt", "U_AE",
        "ToBookDate", "ToBookTime", "HallRent", "Remarks", "NoOfPax",
        "RatePerPax", "TotalPerCover", "Amount", "Advance", "RectNo",
        "rectDate", "CrCardNo", "CrCardHolder", "BookDocId", "DelFlag",
        "Narration", "LogSite_Code", "Narration1", "CGST", "SGST", "IGST"
    ]

    vals = [
        docid, vtype, vno, now.strftime("%H:%M"), SITE_CODE, VPREFIX,
        now.date(), restcode, booking["party"],
        amounts["total"], amounts["discper"], amounts["discamt"],
        amounts["nontaxable"], amounts["taxable"], amounts["tax"],
        amounts["service"], 0.0, 0.0, amounts["netamt"],
        booking.get("frdate", now.date()), booking.get("frtime", "00:00"),
        USER, now, "A",
        booking.get("todate", now.date() + datetime.timedelta(days=1)),
        booking.get("totime", "23:59"),
        float(booking.get("hallrent", 0)), "",
        int(booking.get("guaratt", 0)), float(booking.get("cover_rate", 0)),
        float(booking.get("totalcover", 0)), 0.0, 0.0, "", now.date(),
        "", "", "", bookdocid, "N", "", SITE_CODE, "", amounts["cgst"],
        amounts["sgst"], amounts["igst"]
    ]

    placeholders = ", ".join(["?"] * len(vals))
    sql = f"INSERT INTO HallSale1 ({', '.join(cols)}) VALUES ({placeholders})"
    db.execute(sql, tuple(vals), cn=cn, commit=False)

    # Insert HallSale2 lines
    for i, line in enumerate(lines, 1):
        _insert_hallsale2_line(docid, i, line, vno, VPREFIX, restcode, cn=cn)

    if commit:
        cn.commit()
    return docid


def _insert_hallsale2_line(
    docid: str, sno: int, line: dict, vno: int, vprefix: str,
    restcode: str, cn=None
) -> int:
    taxcode = line.get("taxcode", "")
    taxper = float(line.get("taxper", 0))
    taxamt = float(line.get("taxamt", 0))
    base = float(line.get("amount", 0)) - float(line.get("discamt", 0))

    return db.execute(
        "INSERT INTO HallSale2 (DocId, Sno, SNo1, Vtype, VNo, Site_Code, "
        "Vprefix, Vdate, RestCode, TaxCode, BaseValue, TaxPer, TaxAmt, "
        "U_Name, U_EntDt, U_AE, DelFlag, LOGSITE_CODE) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', 'N', ?)",
        (docid, sno, line.get("sno1", 0), line.get("vtype", ""),
         vno, SITE_CODE, vprefix, line.get("vdate", None),
         restcode, taxcode, base, taxper, taxamt,
         USER, SITE_CODE),
        cn=cn, commit=False)


# ============================================================
# HallSale2 (Bill Tax/Detail Lines)
# ============================================================

HALLSALE2_COLS = (
    "DocId, Sno, SNo1, Vtype, VNo, Site_Code, Vprefix, Vdate, "
    "RestCode, TaxCode, BaseValue, TaxPer, TaxAmt, U_Name, U_EntDt, "
    "U_AE, DelFlag, LOGSITE_CODE"
)


def _map_hallsale2(r) -> dict:
    try:
        return {
            "docid": r.DocId, "sno": r.Sno, "sno1": r.SNo1,
            "vtype": r.Vtype or "", "vno": r.VNo,
            "vprefix": r.Vprefix or "", "vdate": r.Vdate,
            "rest": r.RestCode or "", "taxcode": r.TaxCode or "",
            "base": float(r.BaseValue or 0), "taxper": float(r.TaxPer or 0),
            "taxamt": float(r.TaxAmt or 0), "u_name": r.U_Name or "",
            "u_ae": r.U_AE or "", "delflag": r.DelFlag or "N",
        }
    except AttributeError:
        d, sn, sn1, vt, vn, sc, vp, vd, rc, tc, bv, tp, ta, un, _, uae, df, ls = r
        return {
            "docid": d, "sno": sn, "sno1": sn1, "vtype": vt or "",
            "vno": vn, "vprefix": vp or "", "vdate": vd,
            "rest": rc or "", "taxcode": tc or "", "base": float(bv or 0),
            "taxper": float(tp or 0), "taxamt": float(ta or 0),
            "u_name": un or "", "u_ae": uae or "", "delflag": df or "N",
        }


def hallsale2_lines(docid: str, cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {HALLSALE2_COLS} FROM HallSale2 WHERE DocId = ? ORDER BY Sno",
        (docid,), cn=cn)
    return [_map_hallsale2(r) for r in rows]


# ============================================================
# VenueOcc (Venue Occupancy)
# ============================================================

VENUEOCC_COLS = (
    "FPDocid, VenuCode, FromDate, ToDate, FromTime, ToTime, "
    "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code"
)


def _map_venueocc(r) -> dict:
    try:
        return {
            "fpdocid": r.FPDocid, "venue": r.VenuCode or "",
            "fromdate": r.FromDate, "todate": r.ToDate,
            "fromtime": r.FromTime, "totime": r.ToTime,
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        fp, vc, fd, td, ft, tt, sc, un, _, uae, ls = r
        return {
            "fpdocid": fp, "venue": vc or "", "fromdate": fd, "todate": td,
            "fromtime": ft, "totime": tt, "u_name": un or "", "u_ae": uae or "",
        }


def venueocc_list(cn=None, venue: str = "") -> list[dict]:
    if venue:
        rows = db.query(
            f"SELECT {VENUEOCC_COLS} FROM VenueOcc WHERE VenuCode = ? ORDER BY FromDate",
            (venue,), cn=cn)
    else:
        rows = db.query(
            f"SELECT {VENUEOCC_COLS} FROM VenueOcc ORDER BY FromDate", cn=cn)
    return [_map_venueocc(r) for r in rows]


def venueocc_get_by_booking(fpdocid: str, cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {VENUEOCC_COLS} FROM VenueOcc WHERE FPDocid = ? ORDER BY FromDate",
        (fpdocid,), cn=cn)
    return [_map_venueocc(r) for r in rows]


def venueocc_insert(rec: dict, cn=None, commit: bool = True) -> int:
    if not rec.get("fpdocid", "").strip():
        raise ValueError("FPDocid zaroori hai")
    if not rec.get("venue", "").strip():
        raise ValueError("VenuCode zaroori hai")

    return db.execute(
        "INSERT INTO VenueOcc (FPDocid, VenuCode, FromDate, ToDate, "
        "FromTime, ToTime, Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["fpdocid"], rec["venue"],
         rec.get("fromdate"), rec.get("todate"),
         rec.get("fromtime"), rec.get("totime"),
         SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def venueocc_delete(fpdocid: str, venue: str, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM VenueOcc WHERE FPDocid = ? AND VenuCode = ?",
        (fpdocid, venue), cn=cn, commit=commit)


# ============================================================
# Advance/Deposit Handling
# ============================================================

def hall_advance_get(bookdocid: str, cn=None) -> list[dict]:
    """Get advance payments for a booking from PayChargeH."""
    rows = db.query(
        "SELECT DocId, SNo, Vtype, VNo, VDate, PayCode, AmtCr, AmtDr, "
        "Comments, ContraDocId FROM PayChargeH "
        "WHERE VType IN ('AD','AR') AND ContraDocId = ? AND Site_Code = ?",
        (bookdocid, SITE_CODE), cn=cn)
    return [{
        "docid": r.DocId, "sno": r.SNo, "vtype": r.Vtype or "",
        "vno": r.VNo, "vdate": r.VDate, "paycode": r.PayCode or "",
        "amtcr": float(r.AmtCr or 0), "amtdr": float(r.AmtDr or 0),
        "comments": (r.Comments or "").strip(),
        "contradocid": r.ContraDocId or "",
    } for r in rows]


def hall_advance_total(bookdocid: str, cn=None) -> float:
    """Total advance received (AmtCr - AmtDr) for AD/AR vouchers."""
    rows = db.query(
        "SELECT SUM(AmtCr - AmtDr) FROM PayChargeH "
        "WHERE VType IN ('AD','AR') AND ContraDocId = ? AND Site_Code = ?",
        (bookdocid, SITE_CODE), cn=cn)
    return float(rows[0][0] or 0.0)


# ============================================================
# HallBill Estimate (Preview)
# ============================================================

def hall_estimate_preview(bookdocid: str, cn=None) -> dict:
    """Generate estimate preview for a booking (read-only)."""
    booking = hallbook_get(bookdocid, cn=cn)
    if not booking:
        raise ValueError(f"Booking {bookdocid} nahi mila")

    lines = hallbook1_lines(bookdocid, cn=cn)
    amounts = _calc_bill_amounts(lines)

    # Check existing advances
    advance = hall_advance_total(bookdocid, cn=cn)

    # Check existing bills
    existing_bills = hallsale1_get_by_booking(bookdocid, cn=cn)
    billed = sum(float(b.get("netamt", 0)) for b in existing_bills)

    return {
        "booking": booking,
        "lines": lines,
        "amounts": amounts,
        "advance_received": advance,
        "billed_so_far": billed,
        "balance_due": amounts["netamt"] - advance - billed,
    }


# ============================================================
# Booking Inquiry Link
# ============================================================

def bookinginquiry_list(cn=None) -> list[dict]:
    """Get active booking inquiries (BookingInquiry table)."""
    rows = db.query(
        "SELECT Code, CatType, PartyName, Add1, Add2, City, PhoneR, PhoneO, "
        "MobileNo, FaxNo, ConPerson, BookedBy, FuncType, FuncDate, HandledBy, "
        "BussSource, Status, MarketSeg, Pax, GurrPax, RatePax, VenueCode, "
        "Site_Code, U_Name, U_EntDt, U_AE, Capacity, CapacityType, "
        "LogSite_Code, Remark "
        "FROM BookingInquiry WHERE Status = 'Active' ORDER BY Code", cn=cn)
    return [{
        "code": r.Code, "cattype": r.CatType or "",
        "party": (r.PartyName or "").strip(),
        "add1": (r.Add1 or "").strip(), "add2": (r.Add2 or "").strip(),
        "city": r.City or "", "phone_r": r.PhoneR or "",
        "phone_o": r.PhoneO or "", "mobile": r.MobileNo or "",
        "fax": r.FaxNo or "", "conperson": r.ConPerson or "",
        "bookedby": r.BookedBy or "", "functype": r.FuncType or "",
        "funcdate": r.FuncDate, "handledby": r.HandledBy or "",
        "bussrc": r.BussSource or "", "status": r.Status or "",
        "mktseg": r.MarketSeg or "", "pax": int(r.Pax or 0),
        "gurrpax": int(r.GurrPax or 0), "ratepax": float(r.RatePax or 0),
        "venue": r.VenueCode or "", "site": r.Site_Code or "",
        "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        "capacity": int(r.Capacity or 0), "capacitytype": r.CapacityType or "",
        "remark": (r.Remark or "").strip(),
    } for r in rows]


def bookinginquiry_get(code: str, cn=None) -> dict | None:
    rows = db.query(
        "SELECT Code, CatType, PartyName, Add1, Add2, City, PhoneR, PhoneO, "
        "MobileNo, FaxNo, ConPerson, BookedBy, FuncType, FuncDate, HandledBy, "
        "BussSource, Status, MarketSeg, Pax, GurrPax, RatePax, VenueCode, "
        "Site_Code, U_Name, U_EntDt, U_AE, Capacity, CapacityType, "
        "LogSite_Code, Remark "
        "FROM BookingInquiry WHERE Code = ?", (code,), cn=cn)
    if not rows:
        return None
    r = rows[0]
    return {
        "code": r.Code, "cattype": r.CatType or "",
        "party": (r.PartyName or "").strip(),
        "add1": (r.Add1 or "").strip(), "add2": (r.Add2 or "").strip(),
        "city": r.City or "", "phone_r": r.PhoneR or "",
        "phone_o": r.PhoneO or "", "mobile": r.MobileNo or "",
        "fax": r.FaxNo or "", "conperson": r.ConPerson or "",
        "bookedby": r.BookedBy or "", "functype": r.FuncType or "",
        "funcdate": r.FuncDate, "handledby": r.HandledBy or "",
        "bussrc": r.BussSource or "", "status": r.Status or "",
        "mktseg": r.MarketSeg or "", "pax": int(r.Pax or 0),
        "gurrpax": int(r.GurrPax or 0), "ratepax": float(r.RatePax or 0),
        "venue": r.VenueCode or "", "site": r.Site_Code or "",
        "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        "capacity": int(r.Capacity or 0), "capacitytype": r.CapacityType or "",
        "remark": (r.Remark or "").strip(),
    }


# ============================================================
# Catering Booking (separate from hall booking)
# ============================================================

CATERING_COLS = (
    "DocId, Vtype, VNo, VTime, Site_Code, PartyName, Add1, Add2, City, "
    "Func_Date, Func_Time, CoverRate, RestCode, "
    "MarketSeg, BussSource, CompanyCode, BookingAgent, InquiryCode, "
    "Remark, U_Name, U_EntDt, U_AE, LogSite_Code"
)


def _catering_missing_table_err() -> ValueError:
    return ValueError(
        "CateringBooking table not present in this DB. "
        "Feature is disabled for schema compatibility."
    )


def _catering_query_safe(sql: str, params=(), cn=None):
    try:
        return db.query(sql, params, cn=cn)
    except Exception as exc:
        msg = str(exc)
        if "Invalid object name 'CateringBooking'" in msg or "CateringBooking" in msg and "does not exist" in msg:
            return []
        raise


def catering_list(cn=None, top: int = 300) -> list[dict]:
    rows = _catering_query_safe(
        f"SELECT TOP {int(top)} {CATERING_COLS} FROM CateringBooking ORDER BY DocId DESC",
        cn=cn)
    return [{
        "docid": r.DocId, "vtype": r.Vtype or "", "vno": r.VNo,
        "vtime": r.VTime, "party": (r.PartyName or "").strip(),
        "add1": (r.Add1 or "").strip(), "add2": (r.Add2 or "").strip(),
        "city": r.City or "", "func_date": r.Func_Date,
        "func_time": r.Func_Time, "cover_rate": float(r.CoverRate or 0),
        "rest": r.RestCode or "", "mktseg": r.MarketSeg or "",
        "bussrc": r.BussSource or "", "company": r.CompanyCode or "",
        "agent": r.BookingAgent or "", "inquiry": r.InquiryCode or "",
        "remark": (r.Remark or "").strip(),
        "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
    } for r in rows]


def catering_get(docid: str, cn=None) -> dict | None:
    rows = _catering_query_safe(
        f"SELECT {CATERING_COLS} FROM CateringBooking WHERE DocId = ?", (docid,), cn=cn)
    if not rows:
        return None
    r = rows[0]
    return {
        "docid": r.DocId, "vtype": r.Vtype or "", "vno": r.VNo,
        "vtime": r.VTime, "party": (r.PartyName or "").strip(),
        "add1": (r.Add1 or "").strip(), "add2": (r.Add2 or "").strip(),
        "city": r.City or "", "func_date": r.Func_Date,
        "func_time": r.Func_Time, "cover_rate": float(r.CoverRate or 0),
        "rest": r.RestCode or "", "mktseg": r.MarketSeg or "",
        "bussrc": r.BussSource or "", "company": r.CompanyCode or "",
        "agent": r.BookingAgent or "", "inquiry": r.InquiryCode or "",
        "remark": (r.Remark or "").strip(),
        "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
    }


class _CateringAPI:
    @staticmethod
    def list_all(cn=None): return catering_list(cn)
    @staticmethod
    def get(docid, cn=None): return catering_get(docid, cn)

CateringAPI = _CateringAPI()


# ============================================================
# Exportable API classes for UI
# ============================================================

class _HallBookAPI:
    @staticmethod
    def list_all(cn=None): return hallbook_list(cn)
    @staticmethod
    def get(docid, cn=None): return hallbook_get(docid, cn)
    @staticmethod
    def exists(docid, cn=None): return hallbook_exists(docid, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return hallbook_insert(rec, cn, commit)
    @staticmethod
    def update(docid, rec, cn=None, commit=True): return hallbook_update(docid, rec, cn, commit)
    @staticmethod
    def delete(docid, cn=None, commit=True): return hallbook_delete(docid, cn, commit)

HallBookAPI = _HallBookAPI()


class _HallSale1API:
    @staticmethod
    def list_all(cn=None): return hallsale1_list(cn)
    @staticmethod
    def get(docid, cn=None): return hallsale1_get(docid, cn)
    @staticmethod
    def get_by_booking(bookdocid, cn=None): return hallsale1_get_by_booking(bookdocid, cn)
    @staticmethod
    def create_from_booking(bookdocid, vtype, restcode, user=USER, cn=None, commit=True):
        return hallsale1_create_from_booking(bookdocid, vtype, restcode, user, cn, commit)

HallSale1API = _HallSale1API()


class _VenueOccAPI:
    @staticmethod
    def list_all(cn=None, venue=""): return venueocc_list(cn, venue)
    @staticmethod
    def get_by_booking(fpdocid, cn=None): return venueocc_get_by_booking(fpdocid, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return venueocc_insert(rec, cn, commit)
    @staticmethod
    def delete(fpdocid, venue, cn=None, commit=True): return venueocc_delete(fpdocid, venue, cn, commit)

VenueOccAPI = _VenueOccAPI()


class _BookingInquiryAPI:
    @staticmethod
    def list_all(cn=None): return bookinginquiry_list(cn)
    @staticmethod
    def get(code, cn=None): return bookinginquiry_get(code, cn)

BookingInquiryAPI = _BookingInquiryAPI()