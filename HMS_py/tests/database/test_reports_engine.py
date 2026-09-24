"""Reports engine verification - ALL reports live DB par read-only run.

Run: C:/Python314/python.exe HMS_py/HMS_py/tests/database/test_reports_engine.py
Window 2016..2027 (poora live data). READ-ONLY proof: table row-counts
before/after unchanged.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))

from HMS_py.core import db, reports

RESULTS = []
F, T = "2016-01-01", "2027-12-31"
GUARD_TABLES = ("RoomOcc", "GuestFolio", "PayCharge", "FOMBillDetails",
                "Sale1", "Sale2", "Ledger", "Stock")


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(("PASS " if cond else "FAIL ") + name + (" | " + detail if detail else ""))


def counts():
    return {t: db.query(f"SELECT COUNT(*) FROM {t}")[0][0]
            for t in GUARD_TABLES}


def main():
    before = counts()

    # Registry consistency
    keys = [r["key"] for r in reports.REPORTS]
    check("T0 registry non-empty", len(keys) >= 25, f"{len(keys)} reports")
    check("T0 unique keys", len(keys) == len(set(keys)))
    caps = reports.menu_caption_map()
    check("T0 menu captions mapped", len(caps) >= 20, f"{len(caps)} captions")

    # Har report ko window 2016..2027 par chalao (spine reports = wide window)
    for r in reports.REPORTS:
        k = r["key"]
        try:
            cols, rows = reports.run(k, F, T, limit=200)
            check(f"T1 {k}", True,
                  f"{len(rows)} rows x {len(cols)} cols")
            # header/row width match
            if rows:
                check(f"T2 {k} width", len(rows[0]) == len(cols))
        except Exception as e:
            check(f"T1 {k}", False, repr(e)[:140])

    # CSV export round-trip (temp file)
    import tempfile
    try:
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "out.csv")
            n = reports.export_csv("fom_sales_register", "2016-01-01",
                                   "2027-12-31", p, limit=50)
            check("T3 export_csv", n > 0, f"{n} rows -> {os.path.basename(p)}")
    except Exception as e:
        check("T3 export_csv", False, repr(e)[:140])

    # Error paths
    try:
        reports.run("fom_sales_register")
        check("T4 missing-dates rejected", False, "no error raised")
    except ValueError:
        check("T4 missing-dates rejected", True)
    try:
        reports.run("NoSuchReport")
        check("T5 unknown-key rejected", False)
    except KeyError:
        check("T5 unknown-key rejected", True)

    # READ-ONLY proof
    after = counts()
    check("T6 DB untouched", before == after,
          "; ".join(f"{t}:{before[t]}->{after[t]}" for t in GUARD_TABLES
                    if before[t] != after[t]) or "all equal")

    fails = [r for r in RESULTS if not r[1]]
    print(f"\n{len(RESULTS) - len(fails)}/{len(RESULTS)} PASS")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
