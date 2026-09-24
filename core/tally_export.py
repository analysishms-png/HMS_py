"""Tally XML export (VB6 frmTallyExport.frm ka port) - READ-ONLY DB.

EVIDENCE (decompiled frmTallyExport.frm):
- btnStart_Click: 2 XML files banti hain App.Path me:
    LedgerMaster.xml : Acgroup (groups) + Subgroup (ledgers) masters
    Ledger.xml       : Ledger vouchers (date-range, V_Type filter)
- Envelope: TALLYREQUEST 'Import Data', REPORTNAME 'Vouchers'.
- Group row  (Proc_331_6_F94D78): <GROUP NAME=.. RESERVEDNAME=..><PARENT>..
- Ledger row (Proc_331_7_11B6A94): <LEDGER NAME=..><ADDRESS..><PARENT>..
    PARENT = UnderGroupName (VB6 special-case renames:
    DIRECT EXPENSE->DIRECT EXPENSES, INDIRECT INCOME->INDIRECT INCOMES,
    SUSPENCE A/C->SUSPENSE A/C, PROFIT & LOSS A/C->SUSPENSE A/C)
- Voucher rows (btnStart 2nd half): VouchType mapping by V_Type prefix:
    MT/PV->Payment, CT/RV->Receipt, NT->Contra, N*->Credit/Debit Note,
    BPB/RPB/BPC/RPC->Purchase, else Journal
    mDate = yyyymmdd; REMOTEID/GUID = running 8-digit counter.
- Ledger entry (Proc_331_8_104FBE4): <ALLLEDGERENTRIES.LIST>
    ISDEEMEDPOSITIVE Yes iff DR; AMOUNT = -amt (DR) / amt (CR), 0.00 fmt.
- V_Type filter: L.v_type Not like '_ao' (F_AO skip) + subcode-not-null
    logic (party rows).
- READ-ONLY: yahan file-writes hi export hain, DB me sirf SELECT.
"""
from __future__ import annotations

import datetime
import os

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")

# VB6 PARENT renames (frmTallyExport btnStart_Click If-chain)
GROUP_RENAME = {
    "DIRECT EXPENSE": "DIRECT EXPENSES",
    "INDIRECT INCOME": "INDIRECT INCOMES",
    "SUSPENCE A/C": "SUSPENSE A/C",
    "PROFIT & LOSS A/C": "SUSPENSE A/C",
}

# VB6 voucher-type mapping (btnStart_Click Case-when SQL)
VTYPE_MAP_RULES = [  # (prefix, Tally voucher type)
    ("MT", "Payment"), ("PV", "Payment"),
    ("CT", "Receipt"), ("RV", "Receipt"),
    ("NT", "Contra"),
    ("BPB", "Purchase"), ("RPB", "Purchase"),
    ("BPC", "Purchase"), ("RPC", "Purchase"),
]


def esc(s) -> str:
    """VB6 Replace(x, '&', '&amp;') + tag-safety."""
    return (str(s or "").strip().replace("&", "&amp;")
            .replace("<", "&lt;").replace(">", "&gt;"))


def voucher_type(vtype: str) -> str:
    vt = (vtype or "").strip().upper()
    for prefix, name in VTYPE_MAP_RULES:
        if vt.startswith(prefix):
            return name
    if vt.startswith("N"):  # VB6: 'N then Credit Note / Debit Note (order)
        return "Credit Note"
    return "Journal"


def mdate(d) -> str:
    """VB6: yyyymmdd string (len<=1 -> '0'+)."""
    if hasattr(d, "strftime"):
        return d.strftime("%Y%m%d")
    return str(d or "")


def fetch_groups(cn=None) -> list:
    """VB6: Select Distinct Grp.GroupName, Grp1.GroupName As
    UnderGroupName ... Order By Cast(Grp.MainGrCode As Numeric)."""
    return db.query(
        "SELECT DISTINCT Grp.GroupName, Grp1.GroupName AS UnderGroupName, "
        "CAST(CASE WHEN ISNUMERIC(Grp.MainGrCode) = 1 AND LEN(Grp.MainGrCode) > 0 "
        "THEN Grp.MainGrCode ELSE '999999' END AS NUMERIC) AS nMainGrCode "
        "FROM Acgroup Grp LEFT JOIN AcGroup Grp1 ON "
        "Grp1.MainGrCode = CASE WHEN LEN(Grp.MainGrCode) > 3 "
        "THEN SUBSTRING(Grp.MainGrCode, 1, LEN(Grp.MainGrCode) - 3) "
        "ELSE '' END "
        "WHERE (Grp.LOGSITE_CODE = ? OR Grp.LOGSITE_CODE = 'HO') "
        "ORDER BY CAST(CASE WHEN ISNUMERIC(Grp.MainGrCode) = 1 AND LEN(Grp.MainGrCode) > 0 "
        "THEN Grp.MainGrCode ELSE '999999' END AS NUMERIC)",
        (SITE_CODE,), cn=cn)


def fetch_ledgers(cn=None) -> list:
    """VB6: Subgroup M + AcGroup G + City C + State S join."""
    return db.query(
        "SELECT M.*, G.GroupName AS UnderGroupName, S.Name AS Statename, "
        "G.Sysgroup FROM Subgroup M LEFT JOIN AcGroup G ON "
        "M.GroupCode = G.GroupCode LEFT JOIN City C ON "
        "M.Citycode = C.Citycode LEFT JOIN State S ON C.Statecode = S.code "
        "WHERE (M.LOGSITE_CODE = ? OR M.LOGSITE_CODE = 'HO')",
        (SITE_CODE,), cn=cn)


def fetch_vouchers(date_from, date_to, cn=None) -> list:
    """VB6 voucher cursor: date-range, '_ao' skip, party = first
    Subgroup-name on Docid."""
    return db.query(
        "SELECT DISTINCT L.Docid, CAST(LTRIM(L.V_No) AS INTEGER) AS V_No, "
        "LM.Narration, L.V_Date, "
        "CASE "
        " WHEN L.V_Type LIKE 'MT%' THEN 'Payment' "
        " WHEN L.V_Type LIKE 'PV%' THEN 'Payment' "
        " WHEN L.V_Type LIKE 'CT%' THEN 'Receipt' "
        " WHEN L.V_Type LIKE 'RV%' THEN 'Receipt' "
        " WHEN L.V_Type LIKE 'NT%' THEN 'Contra' "
        " WHEN L.V_Type LIKE 'N%'  THEN 'Credit Note' "
        " WHEN L.V_Type LIKE 'BPB%' OR L.V_Type LIKE 'RPB%' OR "
        "      L.V_Type LIKE 'BPC%' OR L.V_Type LIKE 'RPC%' "
        "  THEN 'Purchase' "
        " ELSE 'Journal' END AS VouchType, "
        "CAST(YEAR(L.V_Date) AS VARCHAR) + "
        " RIGHT('0' + CAST(MONTH(L.V_Date) AS VARCHAR), 2) + "
        " RIGHT('0' + CAST(DAY(L.V_Date) AS VARCHAR), 2) AS mDate, "
        "(SELECT TOP 1 M.name FROM Subgroup M LEFT JOIN Ledger L1 ON "
        " L1.Subcode = M.Subcode WHERE L1.Docid = L.Docid) AS Party "
        "FROM Ledger L LEFT JOIN LedgerM LM ON L.Docid = LM.Docid "
        "LEFT JOIN Acgroup Grp ON L.groupcode = Grp.groupcode "
        "WHERE L.V_Date BETWEEN ? AND ? "
        "AND L.v_type NOT LIKE '_ao' "
        "ORDER BY L.V_Date, V_No",
        (date_from, date_to), cn=cn)


def fetch_voucher_lines(docid: str, cn=None) -> list:
    """VB6: Docid ki Dr(Lvl1 Cr>0?) / Cr(Lvl2 Dr>0) entries — actually
    2-pass union: Cr rows pehle, fir Dr (Lvl order) — hum L.V_SNo order
    me saare rows dete hain, side writer decide karta hai."""
    return db.query(
        "SELECT L.*, M.Name, LM.Narration AS NarrationNew "
        "FROM Ledger L LEFT JOIN Subgroup M ON L.Subcode = M.Subcode "
        "LEFT JOIN LedgerM LM ON L.Docid = LM.Docid "
        "WHERE L.Docid = ? AND L.LogSite_Code IN (?, 'HO') "
        "ORDER BY L.V_SNo",
        (docid, SITE_CODE), cn=cn)


# ---------------------------------------------------------------- writers
def group_xml(name: str, parent: str) -> str:
    """VB6 Proc_331_6_F94D78 — exact tag sequence."""
    return (
        f'<GROUP NAME="{esc(name)}" RESERVEDNAME="{esc(name)}">\n'
        f"<PARENT>{esc(parent)}</PARENT>\n"
        "<GRPDEBITPARENT></GRPDEBITPARENT>\n"
        "<GRPCREDITPARENT></GRPCREDITPARENT>\n"
        "<ISBILLWISEON>No</ISBILLWISEON>\n"
        "<ISCOSTCENTRESON>No</ISCOSTCENTRESON>\n"
        "<ISADDABLE>No</ISADDABLE>\n"
        "<ISSUBLEDGER>No</ISSUBLEDGER>\n"
        "<ISREVENUE>No</ISREVENUE>\n"
        "<AFFECTSGROSSPROFIT>No</AFFECTSGROSSPROFIT>\n"
        "<ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>\n"
        "<TRACKNEGATIVEBALANCES>No</TRACKNEGATIVEBALANCES>\n"
        "<ISCONDENSED>No</ISCONDENSED>\n"
        "<AFFECTSSTOCK>No</AFFECTSSTOCK>\n"
        "<ISGROUPFORLOANRCPT>No</ISGROUPFORLOANRCPT>\n"
        "<ISGROUPFORLOANPYMNT>No</ISGROUPFORLOANPYMNT>\n"
        "<SORTPOSITION>No</SORTPOSITION>\n"
        '<LANGUAGENAME.LIST>\n<NAME.LIST TYPE="SString">\n'
        f"<NAME>{esc(name)}</NAME>\n"
        "</NAME.LIST>\n<LANGUAGEID>1033</LANGUAGEID>\n"
        "</LANGUAGENAME.LIST>\n</GROUP>")


def ledger_xml(name: str, add1: str, add2: str, statename: str,
               parent: str) -> str:
    """VB6 Proc_331_7_11B6A94 — ADDRESS 'No' jab blank (IIf logic)."""
    return (
        f'<LEDGER NAME="{esc(name)}" RESERVEDNAME="">\n'
        '<ADDRESS.LIST TYPE="String">\n'
        f"<ADDRESS>{esc(add1) if str(add1 or '').strip() else 'No'}</ADDRESS>\n"
        f"<ADDRESS>{esc(add2) if str(add2 or '').strip() else 'No'}</ADDRESS>\n"
        "</ADDRESS.LIST>\n"
        '<MAILINGNAME.LIST TYPE="String">\n'
        f"<MAILINGNAME>{esc(name)}</MAILINGNAME>\n"
        "</MAILINGNAME.LIST>\n"
        f"<STATENAME>{esc(statename)}</STATENAME>\n"
        "<SALESTAXNUMBER>05002007343</SALESTAXNUMBER>\n"
        "<PRICELEVEL>PL</PRICELEVEL>\n"
        f"<PARENT>{esc(parent)}</PARENT>\n"
        "<TAXCLASSIFICATIONNAME></TAXCLASSIFICATIONNAME>\n"
        "<TAXTYPE>Others</TAXTYPE>\n"
        "<BILLCREDITPERIOD>5 Days</BILLCREDITPERIOD>\n"
        "<GSTTYPE></GSTTYPE>\n"
        "<ISBILLWISEON>Yes</ISBILLWISEON>\n"
        "<ISCOSTCENTRESON>No</ISCOSTCENTRESON>\n"
        "<ISINTERESTON>No</ISINTERESTON>\n"
        "<ALLOWINMOBILE>No</ALLOWINMOBILE>\n"
        "<ISCOSTTRACKINGON>No</ISCOSTTRACKINGON>\n"
        "<ISCONDENSED>No</ISCONDENSED>\n"
        "</LEDGER>")


def entry_xml(ledger_name: str, narration: str, side: str,
              amount: float) -> str:
    """VB6 Proc_331_8_104FBE4 — DR => negative AMOUNT."""
    amt = -round(float(amount), 2) if side == "DR" else round(float(amount), 2)
    return (
        "<ALLLEDGERENTRIES.LIST>\n"
        f"<NARRATION>{esc(narration)}</NARRATION>\n"
        f"<LEDGERNAME>{esc(ledger_name)}</LEDGERNAME>\n"
        "<GSTCLASS />\n"
        f"<ISDEEMEDPOSITIVE>{'Yes' if side == 'DR' else 'No'}"
        "</ISDEEMEDPOSITIVE>\n"
        "<REMOVEZEROENTRIES>No</REMOVEZEROENTRIES>\n"
        "<ISPARTYLEDGER>Yes</ISPARTYLEDGER>\n"
        f"<ISLASTDEEMEDPOSITIVE>{'Yes' if side == 'DR' else 'No'}"
        "</ISLASTDEEMEDPOSITIVE>\n"
        f"<AMOUNT>{amt:.2f}</AMOUNT>\n"
        "<BANKALLOCATIONS.LIST />\n"
        "<BILLALLOCATIONS.LIST />\n"
        "<INTERESTCOLLECTION.LIST />\n"
        "<AUDITENTRIES.LIST />\n"
        "<INVENTORYALLOCATIONS.LIST>\n"
        "</INVENTORYALLOCATIONS.LIST>\n"
        "<TAXBILLALLOCATIONS.LIST />\n"
        "<TAXOBJECTALLOCATIONS.LIST />\n"
        "<TDSEXPENSEALLOCATIONS.LIST />\n"
        "<VATSTATUTORYDETAILS.LIST />\n"
        "</ALLLEDGERENTRIES.LIST>")


def build_master_xml() -> str:
    """LedgerMaster.xml ka poora content (groups + ledgers)."""
    out = ["<ENVELOPE>", "<HEADER>",
           "<TALLYREQUEST>Import Data</TALLYREQUEST>",
           "</HEADER>", "<BODY>", "<IMPORTDATA>",
           "<REQUESTDESC>", "<REPORTNAME>Vouchers</REPORTNAME>",
           "<STATICVARIABLES>", "</STATICVARIABLES>",
           "</REQUESTDESC>", "<REQUESTDATA>",
           '<TALLYMESSAGE xmlns:UDF="TallyUDF">']
    for g in fetch_groups():
        gname = (g.GroupName or "").strip() if not isinstance(g, (list, tuple)) \
            else str(g[0] or "").strip()
        under = (g.UnderGroupName or "").strip() if not isinstance(g, (list, tuple)) \
            else str(g[1] or "").strip()
        # VB6 If-chain: special PARENT renames
        parent = GROUP_RENAME.get(under.upper(), under) or gname
        out.append(group_xml(gname, parent))
    rows = fetch_ledgers()
    for m in rows:
        def f(name, idx):
            try:
                v = m[idx]
            except Exception:
                v = getattr(m, name, "")
            return "" if v is None else str(v).strip()
        name = f("Name", 2)
        add1 = f("Add1", 12)
        add2 = f("Add2", 13)
        state = f("Statename", -1)
        parent = GROUP_RENAME.get(f("UnderGroupName", -2).upper(),
                                  f("UnderGroupName", -2)) or "SUSPENSE A/C"
        out.append(ledger_xml(name, add1, add2, state, parent))
    out += ["</TALLYMESSAGE>", "</REQUESTDATA>", "</IMPORTDATA>",
            "</BODY>", "</ENVELOPE>"]
    return "\n".join(out)


def build_voucher_xml(date_from, date_to) -> str:
    """Ledger.xml ka poora content (vouchers + entries)."""
    out = ["<ENVELOPE>", "<HEADER>",
           "<TALLYREQUEST>Import Data</TALLYREQUEST>",
           "</HEADER>", "<BODY>", "<IMPORTDATA>",
           "<REQUESTDESC>", "<REPORTNAME>Vouchers</REPORTNAME>",
           "<STATICVARIABLES>", "</STATICVARIABLES>",
           "</REQUESTDESC>", "<REQUESTDATA>"]
    counter = 0
    vrows = fetch_vouchers(date_from, date_to)
    for v in vrows:
        def f(name, idx):
            try:
                val = v[idx]
            except Exception:
                val = getattr(v, name, "")
            return "" if val is None else str(val).strip()
        docid = f("Docid", 0)
        counter += 1
        rid = f"{counter:08d}"
        vouchtype = f("VouchType", 4)
        out.append('<TALLYMESSAGE xmlns:UDF="TallyUDF">')
        out.append(
            f'<VOUCHER REMOTEID="{rid}" VCHKEY="" '
            f'VCHTYPE="{esc(vouchtype)}" ACTION="Create" '
            'OBJVIEW="Accounting Voucher View">')
        out.append(f"<DATE>{esc(f('mDate', 5))}</DATE>")
        out.append(f"<GUID>{rid}</GUID>")
        narr = f("Narration", 2)
        out.append(f"<NARRATION>{esc(narr)}</NARRATION>")
        out.append(f"<VOUCHERTYPENAME>{esc(vouchtype)}</VOUCHERTYPENAME>")
        out.append(f"<VOUCHERNUMBER>{esc(f('V_No', 1))}</VOUCHERNUMBER>")
        out.append(f"<PARTYLEDGERNAME>{esc(f('Party', 6))}</PARTYLEDGERNAME>")
        out.append("<FBTPAYMENTTYPE>Default</FBTPAYMENTTYPE>")
        out.append("<PERSISTEDVIEW>Accounting Voucher View</PERSISTEDVIEW>")
        for tag in ("AUDITED", "ISOPTIONAL", "ISCANCELLED", "HASCASHFLOW",
                    "ISPOSTDATED", "ISINVOICE", "ISCOSTCENTRE", "ISDELETED",
                    "ASORIGINAL", "VCHISFROMSYNC"):
            out.append(f"<{tag}>No</{tag}>")
        out.append("<EFFECTIVEDATE>" + esc(f("mDate", 5)) + "</EFFECTIVEDATE>")
        out.append("<ALTERID></ALTERID>")
        out.append("<MASTERID></MASTERID>")
        out.append("<VOUCHERKEY></VOUCHERKEY>")
        out.append("<AUDITENTRIES.LIST></AUDITENTRIES.LIST>")

        # --- entries: Cr>0 rows pehle (Lvl1), fir Dr>0 (Lvl2) — VB6
        # union order; side/amount net-computation Prog_6_39 pattern:
        # running total -> last diff. Hum simple faithful version:
        # har row ka side uske AmtCr/AmtDr se.
        lrows = fetch_voucher_lines(docid)
        for l in lrows:
            def fl(name, idx):
                try:
                    val = l[idx]
                except Exception:
                    val = getattr(l, name, "")
                return "" if val is None else str(val).strip()
            dr = float(l.AmtDr or 0) if not isinstance(l, (list, tuple)) \
                else float(l[9] or 0)
            cr = float(l.AmtCr or 0) if not isinstance(l, (list, tuple)) \
                else float(l[8] or 0)
            if dr <= 0 and cr <= 0:
                continue
            side = "DR" if dr > 0 else "CR"
            amt = dr if dr > 0 else cr
            out.append(entry_xml(fl("Name", -3), fl("NarrationNew", -2),
                                 side, amt))
        out.append("<ATTDRECORDS.LIST></ATTDRECORDS.LIST>")
        out.append("<LEDGERENTRIESRECORDS.LIST></LEDGERENTRIESRECORDS.LIST>")
        out.append("<LEDGERCSTENTRIESRECORDS.LIST>"
                   "</LEDGERCSTENTRIESRECORDS.LIST>")
        out.append("</VOUCHER>")
        out.append("</TALLYMESSAGE>")
    out += ["</REQUESTDATA>", "</IMPORTDATA>", "</BODY>", "</ENVELOPE>"]
    return "\n".join(out)


def export_all(out_dir: str, date_from=None, date_to=None) -> dict:
    """VB6 btnStart_Click: dono XML files App.Path me — yahan out_dir me.
    READ-ONLY DB; sirf files banti hain. Returns paths + counts."""
    if date_to is None:
        date_to = datetime.date.today()
    if date_from is None:
        # TImp_Dt (last-import marker) blank hai is DB me -> default: is FY
        date_from = datetime.date(date_to.year, 4, 1)
        if date_from > date_to:
            date_from = datetime.date(date_to.year - 1, 4, 1)
    os.makedirs(out_dir, exist_ok=True)
    master_path = os.path.join(out_dir, "LedgerMaster.xml")
    voucher_path = os.path.join(out_dir, "Ledger.xml")
    master_xml = build_master_xml()
    with open(master_path, "w", encoding="utf-8") as fh:
        fh.write(master_xml)
    voucher_xml = build_voucher_xml(date_from, date_to)
    with open(voucher_path, "w", encoding="utf-8") as fh:
        fh.write(voucher_xml)
    return {
        "master_xml": master_path,
        "voucher_xml": voucher_path,
        "groups": master_xml.count("<GROUP "),
        "ledgers": master_xml.count("<LEDGER "),
        "vouchers": voucher_xml.count("<VOUCHER "),
        "entries": voucher_xml.count("<ALLLEDGERENTRIES.LIST>"),
        "from": str(date_from), "to": str(date_to),
    }
