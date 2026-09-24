"""REC payment tests — VB6 fdPaymentCharge.frm:3356 pattern.

Run: C:/Python314/python.exe HMS_py/tests/database/test_receive_payment.py
Every write is rolled back / deleted: DB restored exactly.
Preflight: pichhle crashed-run ke PYT* orphans saaf karta hai (sirf
U_Name='PYADMIN' / Name PYT* rows — production data untouched).
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))

from HMS_py.core import db, checkin, guestprof, folio

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(("PASS " if cond else "FAIL ") + name +
          ("  " + str(detail) if detail else ""))


def _count(t):
    return db.query(f"SELECT COUNT(*) FROM {t}")[0][0]


def _preflight_cleanup():
    """Crashed-run orphans (sirf hamare PYT*/PYADMIN rows)."""
    # 1) orphan charges: jinka folio ab exist nahi karta
    db.execute(
        "DELETE FROM PayCharge WHERE Site_Code = 'KK' AND "
        "U_Name = 'PYADMIN' AND VPrefix = '2026' AND NOT EXISTS ("
        "SELECT 1 FROM GuestFolio gf WHERE gf.Site_Code = 'KK' AND "
        "gf.Vprefix = '2026' AND gf.FolioNo = PayCharge.FolioNo)")
    # 2) orphan PYT folios (crash ke baad bache check-ins) + unka RoomOcc/
    #    FolioLog/PayCharge
    orphans = db.query(
        "SELECT DocId, FolioNo FROM GuestFolio WHERE Site_Code = 'KK' AND "
        "Vprefix = '2026' AND RTRIM(Name) LIKE 'PYT%' AND U_Name = 'PYADMIN'")
    for r in orphans:
        db.execute("DELETE FROM PayCharge WHERE Site_Code='KK' AND FolioNo=?",
                   (r[1],))
        db.execute("DELETE FROM RoomOcc WHERE DocId = ?", (r[0],))
        db.execute("DELETE FROM FolioLog WHERE FolionoDocid = ?", (r[0],))
        db.execute("DELETE FROM GuestFolio WHERE DocId = ?", (r[0],))
    # 3) orphan guest profiles (PYT*)
    db.execute(
        "DELETE FROM GuestProf WHERE Code LIKE 'KK%' AND Name LIKE 'PYT%' "
        "AND U_Name = 'PYADMIN'")


def main():
    _preflight_cleanup()
    base = {"PayCharge": _count("PayCharge"),
            "GuestFolio": _count("GuestFolio"),
            "FolioLog": _count("FolioLog"),
            "GuestProf": _count("GuestProf")}

    # ---- T1: PYT guest + checkin (guest name PYT-prefixed = safety guard)
    gcode = guestprof.next_code()
    guestprof.insert({"code": gcode, "name": "PYT PAY GUEST", "add1": "TEST",
                      "type": "India"})
    today = datetime.date.today()
    folio_no = checkin.create_checkin(gcode, "PYT PAY GUEST", today, today)
    docid = checkin.make_docid(folio.SITE_CODE, folio.VPREFIX, folio_no)
    gf = db.query("SELECT RTRIM(Name), DocId FROM GuestFolio WHERE DocId=?",
                  (docid,))
    check("T1 create PYT checkin", gf and
          str(gf[0][0]).upper().startswith("PYT"), docid)

    try:
        # ---- T2: payment 5000 receive (live default: KKCASH CASH RECD.)
        vno = folio.receive_payment(folio_no, 5000.0)
        pays = [p for p in folio.list_payments(top=500) if p["vno"] == vno]
        check("T2 payment insert", len(pays) == 1, f"vno={vno}")
        p = pays[0]
        check("T3 docid byte-exact 21ch 'DKKREC'",
              len(p["docid"]) == 21 and p["docid"].startswith("DKKREC"),
              p["docid"])
        check("T4 paycode/type", p["paycode"] == "KKCASH" and
              p["paytype"].upper() == "CASH", f"{p['paycode']}/{p['paytype']}")
        check("T5 folio link", p["folio"] == folio_no and
              p["guestprof"] == gcode)

        bal = folio.folio_balance(folio_no)
        check("T6 balance credit", abs(bal - (-5000.0)) < 0.01, f"bal={bal}")

        # ---- T7: guards
        try:
            folio.receive_payment(463, 100.0)  # production folio
            check("T7a prod-folio reject", False)
        except ValueError as e:
            check("T7a prod-folio reject", "Safety" in str(e), str(e)[:60])
        try:
            folio.receive_payment(folio_no, 0)
            check("T7b zero reject", False)
        except ValueError:
            check("T7b zero reject", True)
        try:
            folio.receive_payment(folio_no, 50.0, paycode="NOPE")
            check("T7c unknown paycode reject", False)
        except ValueError:
            check("T7c unknown paycode reject", True)

        # ---- T8: room charge bhi post karke payment ke saath balance dekho
        folio.post_room_charge(folio_no, 1000.0)
        bal = folio.folio_balance(folio_no)
        check("T8 charge+payment balance",
              abs(bal - (1000.0 * 1.10 - 5000.0)) < 0.01, f"bal={bal}")

        # ---- T9: delete_payment (PYT-guarded test hygiene)
        folio.delete_payment(vno)
        pays2 = [p for p in folio.list_payments(top=500) if p["vno"] == vno]
        check("T9 payment deleted", len(pays2) == 0)
    finally:
        # Cleanup: settle-row -> folio-linked charges -> checkin -> guest
        try:
            folio.delete_settle(folio_no)
        except Exception:
            pass
        try:
            db.execute(
                "DELETE FROM PayCharge WHERE Site_Code = ? AND FolioNo = ? "
                "AND U_Name = ?", (folio.SITE_CODE, folio_no, folio.USER))
        except Exception as e:
            print("charge-cleanup warn:", e)
        try:
            checkin.delete_checkin(folio_no)
        except Exception as e:
            print("checkin-cleanup warn:", e)
        try:
            guestprof.delete(gcode)
        except Exception as e:
            print("guest-cleanup warn:", e)
        after = {"PayCharge": _count("PayCharge"),
                 "GuestFolio": _count("GuestFolio"),
                 "FolioLog": _count("FolioLog"),
                 "GuestProf": _count("GuestProf")}
        check("T10 DB restored", after == base, f"{after} vs {base}")

    fails = [r for r in RESULTS if not r[1]]
    print(f"TOTAL: {len(RESULTS) - len(fails)}/{len(RESULTS)} PASS")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
