"""Scheme/HappyHours/TDS round-trip (rollback-safe live proof).

Run: C:/Python314/python.exe HMS_py/tests/database/test_scheme_tds.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from HMS_py.core import db, scheme as sch, tdscat as td

RESULTS = []
def check(n, c, d=""):
    RESULTS.append((n, bool(c), d)); print(("PASS " if c else "FAIL ") + n + (" | " + d if d else ""))

def main():
    cn = db.connect()
    code = "TSTSCH"
    try:
        sch.scheme_delete(code, cn=cn); td.delete("TSTTDS", cn=cn)
        # S1: scheme insert + get
        sch.scheme_insert({"code": code, "name": "Test Scheme",
                           "startdate": "2026-10-01", "enddate": "2026-10-31",
                           "fromtime": "18:00", "totime": "21:00",
                           "days": "15", "active": "Y"}, cn=cn)
        g = sch.scheme_get(code, cn=cn)
        check("S1 scheme insert/get", g and g["name"] == "Test Scheme"
              and g["fromtime"] == "18:00")
        # S2: dup reject
        try:
            sch.scheme_insert({"code": code, "name": "Dup"}, cn=cn)
            check("S2 scheme dup reject", False)
        except ValueError as e:
            check("S2 scheme dup reject", "Already Exists" in str(e))
        # S3: invalid time reject
        try:
            sch.scheme_insert({"code": "TST2", "name": "Bad",
                               "fromtime": "99:99"}, cn=cn)
            check("S3 invalid time reject", False)
        except ValueError as e:
            check("S3 invalid time reject", "invalid time" in str(e))
        # S4: update
        sch.scheme_update(code, {"name": "Renamed Scheme",
                                 "active": "N"}, cn=cn)
        check("S4 scheme update", sch.scheme_get(code, cn=cn)["name"]
              == "Renamed Scheme")
        # S5: happy hours insert + list by scheme
        sch.happyhours_insert({"schemecode": code, "itemcode": "TSTITEM",
                               "discounttype": "PERCENT",
                               "discountvalue": 10, "fromtime": "18:00"},
                              cn=cn)
        hh = sch.happyhours_list(cn=cn, schemecode=code)
        check("S5 happyhours insert/list", len(hh) == 1
              and hh[0]["itemcode"] == "TSTITEM"
              and hh[0]["discountvalue"] == 10.0)
        sch.happyhours_delete(code, cn=cn)
        # T1: TDS insert/get
        td.insert({"code": "TSTTDS", "name": "Test TDS",
                   "tdslimit": 30000, "tdsper": 10}, cn=cn)
        g2 = td.get("TSTTDS", cn=cn)
        check("T1 tds insert/get", g2 and g2["tdsper"] == 10.0)
        # T2: tds dup reject
        try:
            td.insert({"code": "TSTTDS", "name": "Dup"}, cn=cn)
            check("T2 tds dup reject", False)
        except ValueError as e:
            check("T2 tds dup reject", "Already Exists" in str(e))
        # T3: tds update + delete
        td.update("TSTTDS", {"code": "TSTTDS", "name": "TDS Renamed", "tdsper": 5}, cn=cn)
        check("T3 tds update", td.get("TSTTDS", cn=cn)["tdsper"] == 5.0)
        td.delete("TSTTDS", cn=cn)
        check("T4 tds delete", td.get("TSTTDS", cn=cn) is None)
    finally:
        sch.happyhours_delete(code, cn=cn)
        sch.happyhead_delete(code, cn=cn)
        sch.scheme_delete(code, cn=cn)
        td.delete("TSTTDS", cn=cn)
        cn.close()
    fails = [r for r in RESULTS if not r[1]]
    print(f"\n{len(RESULTS)-len(fails)}/{len(RESULTS)} PASS")
    return 0 if not fails else 1

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
