"""Inventory register tests (P6-3) - read-only, live DB.

Run: python HMS_py/tests/database/test_inventory_registers.py

Evidence: StkRegStore.ttx (Item/VDate/VType/VNo/RecQty/IssQty/BalQty),
Stock live = 13253 rows, all Vprefix='2025', all QtyRec=0 (issue-only DB),
GIN/POrder empty (purchase register legitimately 0 rows).
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))

from HMS_py.core import db, inventory as inv

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(("PASS " if cond else "FAIL ") + name + (f" | {detail}" if detail else ""))


def main():
    cn = db.connect()
    before = db.query("SELECT COUNT(*) FROM Stock", cn=cn)[0][0]

    # T1: default (no prefix pin) returns live rows
    sr = inv.stock_register(cn=cn, top=20)
    check("T1 stock_register returns live rows", len(sr) > 0, f"{len(sr)} rows")

    # T2: fields match StkRegStore.ttx evidence
    need = {"docid", "vtype", "vno", "vdate", "item", "godown",
            "qty_iss", "qty_rec", "rate", "amount"}
    check("T2 register fields (ttx cols)", need.issubset(set(sr[0])) if sr else False,
          str(sorted(sr[0]) if sr else "no rows"))

    # T3: date-window filter (VB6 register is date-based)
    lo, hi = datetime.date(2026, 1, 1), datetime.date(2026, 1, 25)
    w = inv.stock_register(cn=cn, top=100, vdate_from=lo, vdate_to=hi)
    inwin = all(lo <= r["vdate"].date() <= hi for r in w)
    check("T3 date window respected", len(w) > 0 and inwin, f"{len(w)} rows")

    # T4: godown filter
    g = inv.stock_register(cn=cn, top=50, godown="KKMK")
    check("T4 godown filter", len(g) > 0 and all(r["godown"] == "KKMK" for r in g),
          f"{len(g)} KKMJ rows")

    # T5: vprefix filter still available (explicit)
    check("T5 vprefix='9999' -> 0", inv.stock_register(cn=cn, top=10,
          vprefix="9999") == [])
    check("T5b vprefix='2025' -> rows", len(inv.stock_register(
        cn=cn, top=5, vprefix="2025")) > 0)

    # T6: purchase_register graceful on empty GIN/POrder (live reality)
    pr = inv.purchase_register(cn=cn, top=10)
    check("T6 purchase_register graceful", isinstance(pr, list) and len(pr) == 0,
          "GIN/POrder empty in this DB")

    # T7: read-only proof
    after = db.query("SELECT COUNT(*) FROM Stock", cn=cn)[0][0]
    check("T7 Stock untouched", before == after, f"{before} -> {after}")

    fails = [r for r in RESULTS if not r[1]]
    print(f"\n{len(RESULTS) - len(fails)}/{len(RESULTS)} PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
