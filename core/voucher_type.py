"""Voucher Type Master CRUD (VB6: General Setup -> Voucher Environment).
Schema evidence (live HMS DB): Voucher_Type table - 37 columns.
Key cols: V_Type varchar(5) PK, Category varchar(10), NCat varchar(5),
Description varchar(30), Number_Method varchar(9), Start_No int,
Site_Code varchar(2), U_NAME varchar(15), U_EntDt datetime, U_AE varchar(1).
VB6: Voucher_Type table drives DocId generation (Number_Method='Automatic').
Audit pattern VB6 jaisa: U_NAME + U_EntDt(getdate()) + U_AE ('A'/'E')."""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")  # Analysis.ini key 7
USER = db.get_user()
# Column limits (schema evidence): Code varchar(5), Name varchar(25),
# Plan_Package varchar(7), U_Name varchar(10), ActiveYN varchar(3)
LIMITS = {
    "vtype": 5, "category": 10, "ncat": 5, "contratype": 5,
    "desc": 30, "desc_help": 30, "desc_bilang": 30,
    "short": 10, "short_bilang": 10, "rptidx": 3,
    "method": 9, "form": 25, "narr": 150,
    "print_vno": 1, "header": 80, "terms": 150, "footer": 150,
    "exclude": 100, "serial_tbl": 50, "rest": 6,
    "defaultcr": 8, "defaultdr": 8, "firstdrcr": 2,
    "alias": 6, "uname": 15,
}
SELECT_COLS = (
    "V_Type, Category, NCat, Contratype, Description, Description_Help, "
    "Description_BiLang, Short_Name, Short_Name_BiLang, Report_Index, "
    "Number_Method, Start_No, Last_Ent_Date, Form_Name, Separate_Narr, "
    "Common_Narr, Narration, Print_VNo, Header_Desc, Terms_Desc, "
    "Footer_Desc, Exclude_Ac_Grp, SerialNo_From_Table, U_NAME, U_EntDt, "
    "U_AE, ChqNo, ChqDt, ClgDt, SortNo, RestCode, Site_Code, "
    "DefaultCrAc, DefaultDrAc, FirstDrCr, LogSite_Code, Alias"
)


def _map(r) -> dict:
    try:
        return {
            "vtype": r.V_Type or "", "category": r.Category or "",
            "ncat": r.NCat or "", "contratype": r.Contratype or "",
            "desc": (r.Description or "").strip(),
            "desc_help": (r.Description_Help or "").strip(),
            "desc_bilang": (r.Description_BiLang or "").strip(),
            "short": (r.Short_Name or "").strip(),
            "short_bilang": (r.Short_Name_BiLang or "").strip(),
            "rptidx": r.Report_Index or "",
            "method": r.Number_Method or "",
            "startno": r.Start_No or 1,
            "last_ent": r.Last_Ent_Date,
            "form": r.Form_Name or "",
            "sep_narr": r.Separate_Narr or "N",
            "com_narr": r.Common_Narr or "N",
            "narr": (r.Narration or "").strip(),
            "print_vno": r.Print_VNo or "N",
            "header": (r.Header_Desc or "").strip(),
            "terms": (r.Terms_Desc or "").strip(),
            "footer": (r.Footer_Desc or "").strip(),
            "exclude": (r.Exclude_Ac_Grp or "").strip(),
            "serial_tbl": (r.SerialNo_From_Table or "").strip(),
            "uname": r.U_NAME or "",
            "u_ae": r.U_AE or "",
            "chqno": r.ChqNo or "N",
            "chqdt": r.ChqDt or "N",
            "clgdt": r.ClgDt or "N",
            "sortno": r.SortNo or 0,
            "rest": r.RestCode or "",
            "site": r.Site_Code or "",
            "defaultcr": r.DefaultCrAc or "",
            "defaultdr": r.DefaultDrAc or "",
            "firstdrcr": r.FirstDrCr or "",
            "logsite": r.LogSite_Code or "",
            "alias": r.Alias or "",
        }
    except AttributeError:
        (vt, cat, ncat, ctype, desc, dhlp, dbil, sh, sbi, rid, mth, sno,
         led, frm, snar, cnar, narr, pvno, hdr, trm, ftr, excl, stbl,
         un, _, uae, chqno, chqdt, clgdt, sno2, rest, site, dcr, ddr,
         fdcr, lgs, alias) = r
        return {
            "vtype": vt or "", "category": cat or "", "ncat": ncat or "",
            "contratype": ctype or "", "desc": (desc or "").strip(),
            "desc_help": (dhlp or "").strip(), "desc_bilang": (dbil or "").strip(),
            "short": (sh or "").strip(), "short_bilang": (sbi or "").strip(),
            "rptidx": rid or "", "method": mth or "", "startno": sno or 1,
            "last_ent": led,
            "form": frm or "", "sep_narr": snar or "N", "com_narr": cnar or "N",
            "narr": (narr or "").strip(), "print_vno": pvno or "N",
            "header": (hdr or "").strip(), "terms": (trm or "").strip(),
            "footer": (ftr or "").strip(), "exclude": (excl or "").strip(),
            "serial_tbl": (stbl or "").strip(),
            "uname": un or "", "u_ae": uae or "",
            "chqno": chqno or "N", "chqdt": chqdt or "N", "clgdt": clgdt or "N",
            "sortno": sno2 or 0, "rest": rest or "", "site": site or "",
            "defaultcr": dcr or "", "defaultdr": ddr or "", "firstdrcr": fdcr or "",
            "logsite": lgs or "", "alias": alias or "",
        }


def _validate(rec: dict):
    if not rec.get("vtype", "").strip():
        raise ValueError("V_Type zaroori hai")
    if len(rec["vtype"]) > LIMITS["vtype"]:
        raise ValueError(f"V_Type max {LIMITS['vtype']} chars")
    if not rec.get("category", "").strip():
        raise ValueError("Category zaroori hai")
    if len(rec[ "category"]) > LIMITS["category"]:
        raise ValueError(f"Category max {LIMITS['category']} chars")
    for k, lim in LIMITS.items():
        if k in rec and len(str(rec.get(k, ""))) > lim:
            raise ValueError(f"{k} max {lim} chars")


def list_all(cn=None) -> list[dict]:
    rows = db.query(f"SELECT {SELECT_COLS} FROM Voucher_Type ORDER BY Category, V_Type", cn=cn)
    return [_map(r) for r in rows]


def get(vtype: str, cn=None) -> dict | None:
    rows = db.query(f"SELECT {SELECT_COLS} FROM Voucher_Type WHERE V_Type = ?", (vtype,), cn=cn)
    return _map(rows[0]) if rows else None


def exists(vtype: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM Voucher_Type WHERE V_Type = ?", (vtype,), cn=cn))


def insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    db.require_absent("Voucher_Type", "V_Type", rec["vtype"], "Voucher Type")
    return db.execute(
        "INSERT INTO Voucher_Type (V_Type, Category, NCat, Contratype, Description, "
        "Description_Help, Description_BiLang, Short_Name, Short_Name_BiLang, "
        "Report_Index, Number_Method, Start_No, Last_Ent_Date, Form_Name, Separate_Narr, "
        "Common_Narr, Narration, Print_VNo, Header_Desc, Terms_Desc, "
        "Footer_Desc, Exclude_Ac_Grp, SerialNo_From_Table, U_NAME, U_EntDt, "
        "U_AE, ChqNo, ChqDt, ClgDt, SortNo, RestCode, Site_Code, "
        "DefaultCrAc, DefaultDrAc, FirstDrCr, LogSite_Code, Alias) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
        "getdate(), 'A', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (rec["vtype"], rec.get("category", ""), rec.get("ncat", ""),
         rec.get("contratype", ""), rec.get("desc", ""), rec.get("desc_help", ""),
         rec.get("desc_bilang", ""), rec.get("short", ""), rec.get("short_bilang", ""),
         rec.get("rptidx", ""), rec.get("method", ""), rec.get("startno", 1), None,
         rec.get("form", ""), rec.get("sep_narr", "N"), rec.get("com_narr", "N"),
         rec.get("narr", ""), rec.get("print_vno", "N"), rec.get("header", ""),
         rec.get("terms", ""), rec.get("footer", ""), rec.get("exclude", ""),
         rec.get("serial_tbl", ""), USER,
         rec.get("chqno", "N"), rec.get("chqdt", "N"), rec.get("clgdt", "N"),
         rec.get("sortno", 0), rec.get("rest", ""), SITE_CODE,
         rec.get("defaultcr", ""), rec.get("defaultdr", ""),
         rec.get("firstdrcr", ""), SITE_CODE, rec.get("alias", "")),
        cn=cn, commit=commit)


def update(vtype: str, rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    return db.execute(
        "UPDATE Voucher_Type SET Category = ?, NCat = ?, Contratype = ?, "
        "Description = ?, Description_Help = ?, Description_BiLang = ?, "
        "Short_Name = ?, Short_Name_BiLang = ?, Report_Index = ?, "
        "Number_Method = ?, Start_No = ?, Form_Name = ?, Separate_Narr = ?, "
        "Common_Narr = ?, Narration = ?, Print_VNo = ?, Header_Desc = ?, "
        "Terms_Desc = ?, Footer_Desc = ?, Exclude_Ac_Grp = ?, "
        "SerialNo_From_Table = ?, U_NAME = ?, U_EntDt = getdate(), "
        "U_AE = 'E', ChqNo = ?, ChqDt = ?, ClgDt = ?, SortNo = ?, "
        "RestCode = ?, DefaultCrAc = ?, DefaultDrAc = ?, FirstDrCr = ?, "
        "LogSite_Code = ?, Alias = ? WHERE V_Type = ?",
        (rec.get("category", ""), rec.get("ncat", ""), rec.get("contratype", ""),
         rec.get("desc", ""), rec.get("desc_help", ""), rec.get("desc_bilang", ""),
         rec.get("short", ""), rec.get("short_bilang", ""), rec.get("rptidx", ""),
         rec.get("method", ""), rec.get("startno", 1), rec.get("form", ""),
         rec.get("sep_narr", "N"), rec.get("com_narr", "N"), rec.get("narr", ""),
         rec.get("print_vno", "N"), rec.get("header", ""), rec.get("terms", ""),
         rec.get("footer", ""), rec.get("exclude", ""), rec.get("serial_tbl", ""),
         USER, rec.get("chqno", "N"), rec.get("chqdt", "N"), rec.get("clgdt", "N"),
         rec.get("sortno", 0), rec.get("rest", ""), rec.get("defaultcr", ""),
         rec.get("defaultdr", ""), rec.get("firstdrcr", ""), SITE_CODE,
         rec.get("alias", ""), vtype),
        cn=cn, commit=commit)


def delete(vtype: str, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM Voucher_Type WHERE V_Type = ?", (vtype,),
        cn=cn, commit=commit)


def get_categories(cn=None) -> list[dict]:
    """Get unique categories from VoucherCat table."""
    rows = db.query(
        "SELECT Category, NCat FROM VoucherCat ORDER BY Category", cn=cn)
    return [{"category": r[0], "ncat": r[1]} for r in rows]


def get_ncat(vtype: str, cn=None) -> str:
    """FA-6: NCat for a V_Type (VB6 FaVoucher Proc_7 SELECT NCAT)."""
    rows = db.query(
        "SELECT NCat FROM Voucher_Type WHERE V_Type = ?", (vtype,), cn=cn)
    return ((rows[0][0] if rows else "") or "").strip()


def list_entry_types(cn=None) -> list[dict]:
    """FA entry Voucher_Type rows (Category='FA' + legacy HPOST/F_AO)."""
    rows = db.query(
        "SELECT V_Type, NCat, Category, Description, SortNo "
        "FROM Voucher_Type "
        "WHERE Category = 'FA' OR V_Type IN ('HPOST', 'F_AO') "
        "ORDER BY SortNo, V_Type", cn=cn)
    return [{"vtype": (r[0] or "").strip(),
             "ncat": ((r[1] or "").strip()),
             "category": ((r[2] or "").strip()),
             "desc": (r[3] or "").strip(),
             "sortno": r[4] or 0} for r in rows]