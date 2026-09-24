"""Tally export tests — VB6 frmTallyExport port proof.

Run: C:/Python314/python.exe HMS_py/HMS_py/tests/database/test_tally_export.py
READ-ONLY: DB me sirf SELECT; XML files temp me.
"""
import os
import sys
import tempfile
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))

from HMS_py.core import db, tally_export as tx

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(("PASS " if cond else "FAIL ") + name +
          ("  " + str(detail) if detail else ""))


def main():
    before = {"Ledger": _count("Ledger"), "Acgroup": _count("Acgroup"),
              "Subgroup": _count("Subgroup")}

    # T1: unit — voucher_type mapping (VB6 case-when)
    check("T1 MT->Payment", tx.voucher_type("MT") == "Payment")
    check("T1b PV->Payment", tx.voucher_type("PV") == "Payment")
    check("T1c RV->Receipt", tx.voucher_type("RV") == "Receipt")
    check("T1d NT->Contra", tx.voucher_type("NT") == "Contra")
    check("T1e NC->Credit Note", tx.voucher_type("NC") == "Credit Note")
    check("T1f BPB->Purchase", tx.voucher_type("BPB") == "Purchase")
    check("T1g XX->Journal", tx.voucher_type("XX") == "Journal")

    # T2: mdate yyyymmdd
    import datetime
    check("T2 mdate", tx.mdate(datetime.date(2026, 5, 4)) == "20260504")

    # T3: group parent rename (VB6 If-chain)
    gx = tx.group_xml("My Group", "SUSPENCE A/C")
    check("T3 group parent kept", "<PARENT>SUSPENCE A/C</PARENT>" in gx)
    # rename exporter-level me hota hai (build_master_xml) — unit yahin:

    # T4: ledger 'No' address IIf
    lx = tx.ledger_xml("Test Ld", "", "ADD2", "UTTAR PRADESH", "PARENT X")
    check("T4 blank addr -> No", "<ADDRESS>No</ADDRESS>" in lx and
          "<ADDRESS>ADD2</ADDRESS>" in lx)

    # T5: entry DR negative / CR positive
    dr = tx.entry_xml("LD", "N", "DR", 100.0)
    cr = tx.entry_xml("LD", "N", "CR", 100.0)
    check("T5 DR -100", "<AMOUNT>-100.00</AMOUNT>" in dr and
          "<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>" in dr)
    check("T5b CR 100", "<AMOUNT>100.00</AMOUNT>" in cr and
          "<ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>" in cr)

    # T6: full export — files + well-formed XML
    # Live-data window: Ledger vouchers end 2026-01-24, so the FY26 default
    # window is empty; export the FY25 window that actually has data (298).
    outdir = tempfile.mkdtemp(prefix="tally_test_")
    out = tx.export_all(outdir, datetime.date(2025, 4, 1),
                        datetime.date(2026, 3, 31))
    check("T6 groups>0", out["groups"] > 0, out["groups"])
    check("T6b ledgers>0", out["ledgers"] > 0, out["ledgers"])
    check("T6c vouchers>0", out["vouchers"] > 0, out["vouchers"])

    mroot = ET.parse(out["master_xml"]).getroot()
    vroot = ET.parse(out["voucher_xml"]).getroot()
    check("T7 master XML well-formed", mroot.tag == "ENVELOPE")
    check("T7b voucher XML well-formed", vroot.tag == "ENVELOPE")

    # T8: groups + ledgers counts match DB
    dbg = len(tx.fetch_groups())
    dbl = len(tx.fetch_ledgers())
    check("T8 group count == DB", out["groups"] == dbg, f"{out['groups']}/{dbg}")
    check("T8b ledger count == DB", out["ledgers"] == dbl,
          f"{out['ledgers']}/{dbl}")

    # T9: voucher count == DB rows (not-_ao)
    dbv = len(tx.fetch_vouchers(out["from"], out["to"]))
    check("T9 voucher count == DB", out["vouchers"] == dbv,
          f"{out['vouchers']}/{dbv}")

    # T10: entries balanced per voucher (sum DR == sum CR net) — sample
    import re
    vxml = open(out["voucher_xml"], encoding="utf-8").read()
    vouchers = re.findall(r"<VOUCHER .*?</VOUCHER>", vxml, re.S)
    sampled = 0
    balanced = 0
    for vb in vouchers[:50]:
        amts = [float(a) for a in
                re.findall(r"<AMOUNT>(-?[\d.]+)</AMOUNT>", vb)]
        if not amts:
            continue
        sampled += 1
        if abs(sum(amts)) < 0.011:
            balanced += 1
    check("T10 vouchers balanced", sampled > 0 and balanced == sampled,
          f"{balanced}/{sampled}")

    # T11: READ-ONLY proof
    after = {"Ledger": _count("Ledger"), "Acgroup": _count("Acgroup"),
             "Subgroup": _count("Subgroup")}
    check("T11 DB untouched", after == before, f"{before} -> {after}")

    fails = [r for r in RESULTS if not r[1]]
    print(f"TOTAL: {len(RESULTS) - len(fails)}/{len(RESULTS)} PASS")
    return 0 if not fails else 1


def _count(t):
    return db.query(f"SELECT COUNT(*) FROM {t}")[0][0]


if __name__ == "__main__":
    sys.exit(main())
