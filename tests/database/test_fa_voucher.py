"""FA voucher engine live proof (rollback-safe): post->TB->chq->cleanup.

Run: C:/Python314/python.exe HMS_py/tests/database/test_fa_voucher.py
"""
import os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from HMS_py.core import db, fa_voucher as fv

RESULTS = []
def check(n, c, d=""):
    RESULTS.append((n, bool(c), d)); print(("PASS " if c else "FAIL ") + n + (" | " + d if d else ""))

def main():
    cn = db.connect()
    today = datetime.date.today()
    try:
        # basline counts
        nM0 = db.query("SELECT COUNT(*) FROM LedgerM")[0][0]
        cash = db.query("SELECT TOP 1 SubCode FROM Subgroup WHERE Name LIKE '%CASH IN HAND%'")[0][0]
        bank = db.query("SELECT TOP 1 SubCode FROM Subgroup WHERE Name LIKE '%ICIC%'")[0][0]
        # V1: unbalanced reject
        try:
            fv.post_voucher([
                {"subcode": cash, "amt_dr": 100},
                {"subcode": bank, "amt_cr": 90}], today, cn=cn)
            check("V1 unbalanced reject", False)
        except ValueError as e:
            check("V1 unbalanced reject", "!= Credit" in str(e) or "Debit" in str(e))
        # V2: bad subcode reject
        try:
            fv.post_voucher([
                {"subcode": "NOPE01", "amt_dr": 100},
                {"subcode": bank, "amt_cr": 100}], today, cn=cn)
            check("V2 bad subcode reject", False)
        except ValueError as e:
            check("V2 bad subcode reject", "live Subgroup" in str(e))
        # V3: post balanced voucher with cheque
        res = fv.post_voucher([
            {"subcode": bank, "amt_dr": 5000},
            {"subcode": cash, "amt_cr": 5000, "narration": "cash dep"}],
            today, narration="PYT test voucher", vtype="JV",
            chq_no="TSTCHQ001", cn=cn)
        check("V3 post", res["dr"] == 5000.0 and res["cr"] == 5000.0,
              f"docid={res['docid']}")
        # V4: header+lines written
        nM1 = db.query("SELECT COUNT(*) FROM LedgerM")[0][0]
        nL1 = db.query("SELECT COUNT(*) FROM Ledger WHERE DocId = ?",
                       (res["docid"],))[0][0]
        check("V4 header+lines", nM1 == nM0 + 1 and nL1 == 2,
              f"dM={nM1-nM0} lines={nL1}")
        # V5: pending cheque list me dikha
        pend = [p for p in fv.cheque_pending(cn=cn)
                if p["docid"] == res["docid"]]
        # chq_no voucher-level hai -> dono lines (bank+cash) pending list me
        check("V5 pending me aaya", len(pend) == 2 and
              all(p["chq_no"] == "TSTCHQ001" for p in pend),
              f"rows={len(pend)}")
        # V6: mark cleared
        fv.cheque_mark_cleared(res["docid"], 1, today, cn=cn)
        clr = [c for c in fv.cheque_cleared(cn=cn)
               if c["docid"] == res["docid"]]
        check("V6 cleared", len(clr) == 1)
        # V7: TB balance ab bhi DR==CR
        tb = fv.trial_balance(cn=cn)
        check("V7 TB balanced", abs(sum(g['dr'] for g in tb) -
              sum(g['cr'] for g in tb)) < 0.01)
        # V8: delete voucher (cleanup + proof)
        fv.delete_voucher(res["docid"], cn=cn)
        nM2 = db.query("SELECT COUNT(*) FROM LedgerM")[0][0]
        check("V8 delete", nM2 == nM0, f"M {nM1}->{nM2}")
        # V9: journal book me count aya tha (read-only proof)
        jb = fv.journal_book(today.isoformat(), today.isoformat(), cn=cn)
        check("V9 journal_book works", isinstance(jb, list))
    finally:
        # safety cleanup (agar beech me fail hua)
        try:
            db.execute("DELETE FROM Ledger WHERE Narration = 'PYT test voucher'",
                       cn=cn, commit=False)
            db.execute("DELETE FROM LedgerM WHERE Narration = 'PYT test voucher'",
                       cn=cn)
        except Exception:
            pass
        cn.close()
    fails = [r for r in RESULTS if not r[1]]
    print(f"\n{len(RESULTS)-len(fails)}/{len(RESULTS)} PASS")
    return 0 if not fails else 1

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
