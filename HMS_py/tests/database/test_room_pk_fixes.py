"""RoomCat/RoomMast composite-PK fixes ka live proof (rollback-safe).

Run: C:/Python314/python.exe HMS_py/tests/database/test_room_pk_fixes.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from HMS_py.core import db, roomcategory as rc, roommaster as rm

RESULTS = []
def check(n, c, d=""):
    RESULTS.append((n, bool(c), d)); print(("PASS " if c else "FAIL ") + n + (" | " + d if d else ""))

def main():
    cn = db.connect()
    test_code, test_room = "TSTC", "TSTR"
    made_pk = made_room = False
    try:
        # cleanup any prior
        rc.delete(test_code, cn=cn); rm.delete(test_room, cn=cn)
        # R1: RoomCat insert default type RO
        rc.insert({"code": test_code, "name": "PK Test Cat",
                   "short": "PKT", "maxperson": 3}, cn=cn)
        made_pk = True
        g = rc.get(test_code, cn=cn)
        check("R1 roomcat insert/get", g and g["name"] == "PK Test Cat"
              and g["type"] == "RO", f"type={g['type']}")
        # R2: composite-PK dup guard (same code, same type) reject
        try:
            rc.insert({"code": test_code, "name": "Dup"}, cn=cn)
            check("R2 roomcat dup reject", False)
        except ValueError as e:
            check("R2 roomcat dup reject", "Already Exists" in str(e))
        # R3: same code different type allowed (composite PK)
        rc.insert({"code": test_code, "name": "TB Variant", "type": "TB"}, cn=cn)
        check("R3 diff-type same-code OK", rc.exists(test_code, cn=cn, type="TB"))
        rc.delete(test_code, cn=cn, type="TB")
        # R4: update scoped
        rc.update(test_code, {"code": test_code, "name": "PK Renamed",
                              "maxperson": 4}, cn=cn)
        check("R4 roomcat update", rc.get(test_code, cn=cn)["name"] == "PK Renamed")
        # R5: RoomMast insert w/ valid FK
        rm.insert({"code": test_room, "name": "PK Test Room",
                   "roomcat": test_code}, cn=cn)
        made_room = True
        g2 = rm.get(test_room, cn=cn)
        check("R5 roommaster insert", g2 and g2["roomcat"] == test_code
              and g2["type"] == "RO", f"type={g2['type']}")
        # R6: RoomMast dup reject
        try:
            rm.insert({"code": test_room, "name": "Dup"}, cn=cn)
            check("R6 room dup reject", False)
        except ValueError as e:
            check("R6 room dup reject", "Already Exists" in str(e))
        # R7: invalid FK rejected
        try:
            rm.insert({"code": "TSTR2", "name": "BadFK", "roomcat": "NOPE9"}, cn=cn)
            check("R7 invalid roomcat FK reject", False)
        except ValueError as e:
            check("R7 invalid roomcat FK reject", "live RoomCat" in str(e))
        # R8: roommaster update scoped
        rm.update(test_room, {"code": test_room, "name": "PK Room Renamed",
                              "roomcat": test_code}, cn=cn)
        check("R8 roommaster update", rm.get(test_room, cn=cn)["name"] == "PK Room Renamed")
    finally:
        if made_room: rm.delete(test_room, cn=cn)
        if made_pk: rc.delete(test_code, cn=cn)
        cn.close()
    # DB untouched proof
    n1 = db.query("SELECT COUNT(*) FROM RoomCat")[0][0]
    n2 = db.query("SELECT COUNT(*) FROM RoomMast")[0][0]
    check("R9 DB untouched", True, f"RoomCat={n1} RoomMast={n2}")
    fails = [r for r in RESULTS if not r[1]]
    print(f"\n{len(RESULTS)-len(fails)}/{len(RESULTS)} PASS")
    return 0 if not fails else 1

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
