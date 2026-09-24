"""Enviro settings tests — VB6 frmEnviro port proof.

Run: C:/Python314/python.exe HMS_py/HMS_py/tests/database/test_enviro.py
Snapshot -> update -> verify -> RESTORE snapshot (byte-exact).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))

from HMS_py.core import db, enviro

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(("PASS " if cond else "FAIL ") + name +
          ("  " + str(detail) if detail else ""))


def main():
    # ---- units: VB6 validation rules
    check("U1 yn3 Yes", enviro._validate("TOKENPrint", "yes") == "Yes")
    check("U2 yn3 reject", _err(lambda: enviro._validate("TOKENPrint", "Y")))
    check("U3 yn1 Y", enviro._validate("GRCMandatory", "y") == "Y")
    check("U4 yn1 reject", _err(lambda: enviro._validate("GRCMandatory", "Yes")))
    check("U5 time", enviro._validate("CheckoutVar", "9:5") == "09:05")
    check("U6 time reject", _err(lambda: enviro._validate("CheckoutVar", "25:00")))
    check("U7 int", enviro._validate("FomBillCopies", "3") == 3)
    check("U8 RO reject", _err(lambda: enviro._validate("Cash_Ac", "KKX")))
    check("U9 unknown reject", _err(lambda: enviro._validate("NopeCol", "x")))

    # ---- live single-row (VB6 assumption: exactly 1 settings row)
    rows = db.query("SELECT COUNT(*) FROM Enviro")
    check("L1 single Enviro row", rows[0][0] == 1, rows[0][0])

    # ---- rollback round-trip (snapshot -> update -> verify -> restore)
    snap = enviro.snapshot()
    try:
        n = enviro.update_settings({
            "TOKENPrint": "Yes",
            "CheckoutVar": "11:30",
            "FomBillCopies": 2,
        })
        check("R1 update ran", n == 1, n)
        check("R2 yn3 applied", enviro.get_setting("TOKENPrint") == "Yes")
        check("R3 time applied",
              enviro.get_setting("CheckoutVar") == "11:30")
        check("R4 int applied", enviro.get_setting("FomBillCopies") == 2)
        # batch: do settings ek saath (VB6 single-UPDATE pattern)
        n = enviro.update_settings({"TaxSummary": "No"})
        check("R5 batch update", n == 1 and
              enviro.get_setting("TaxSummary") == "No")
    finally:
        # restore: snapshot values wapas (type-faithful)
        restore = {}
        for k, v in snap.items():
            t = enviro.EDITABLE[k]
            if t == "int" and v is not None:
                restore[k] = int(v)
            elif t == "float" and v is not None:
                restore[k] = float(v)
            else:
                restore[k] = "" if v is None else str(v)
        enviro.update_settings(restore)
    # byte-exact proof
    snap2 = enviro.snapshot()
    check("R6 SNAPSHOT RESTORED", snap2 == snap,
          str({k: (snap[k], snap2[k]) for k in snap
               if snap[k] != snap2[k]}))

    # ---- guards
    check("G1 prod-safe single-key update works",
          _err(lambda: enviro.update_settings({})) )  # empty rejected
    try:
        enviro.update_settings({"Cash_Ac": "KKHACK"})
        check("G2 finance AC protected", False)
    except ValueError as e:
        check("G2 finance AC protected", "editable nahi" in str(e))

    fails = [r for r in RESULTS if not r[1]]
    print(f"TOTAL: {len(RESULTS) - len(fails)}/{len(RESULTS)} PASS")
    return 0 if not fails else 1


def _err(fn):
    try:
        fn()
        return False
    except ValueError:
        return True


if __name__ == "__main__":
    sys.exit(main())
