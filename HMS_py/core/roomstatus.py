"""Room Status engine (P4-c) - LIVE SCHEMA, VB6 frm evidence se.

REWRITE REASON: pehle ka version imagined schema pe tha (RoomNo/Status/
CheckOutYN cols jo RoomMast/GuestFolio me exist hi nahi karte - live
probe se pakda gaya). Ye version sirf REAL cols use karta hai.

REAL SCHEMA (live INFORMATION_SCHEMA):
  RoomMast(24): Type('RO'=Room,'TB'=Table,'C','O'), Code varchar(5) PK-ish,
    Name varchar(15), RoomCat, MultPer, MaidStation, RoomStat varchar(1)
    (''=Clean/Vacant, 'D'=Dirty - live census: 58 TB, 28 RO all 'D'),
    Site_Code, LogSite_Code, audit (U_Name/U_EntDt/U_AE).
  RoomOcc(42): DocId+SNo link, FolioNo, RoomNo, RoomRate, ChkInDate/Time,
    DepDate/Time, ChkOutDate/Time, Type, NewRoomNo, Reason, ExtraBed...

VB6 EVIDENCE (decompiled frm):
- FdRoomDisplay.frm:104: select * from roommast where logsite_code=...
- FrmHouseStatus.frm:792: occupied = RoomOcc.Type not in ('O','C') AND
  ChkOutDate IS NULL (join RoomMast on RoomNo)
- FrmHouseStatus.frm:1065: in-house grid = GuestFolio INNER JOIN RoomOcc
  ON gf.DocId=ro.DocId WHERE ro.ChkOutDate IS NULL
- FrmHouseStatus.frm:704: dirty-vacant = RoomMast.RoomStat='D'
- FdCheckOut.frm:3501: reverse check-out = ChkOutTime='',ChkOutDate=NULL
- fdRoomChange.frm:3639: room-move = new RoomOcc row (NewRoomNo concept)

LIVE (18/Sep/2026): 86 RoomMast (28 RO + 58 TB), 6 in-house (304, 303,
202, 206, 307, 208 - PRASHANT PRATAP SINGH/SARIKA, JASMEET SINGH,
ABHIJEET PATHAK, AMAL JOSHY), RoomBLockOut 0 rows.
"""
from __future__ import annotations

import datetime

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()

# RoomMast.RoomStat (varchar(1)) - VB6 RoomStat='D' = Dirty (frm:704)
ROOMSTAT_DIRTY = "D"
ROOMSTAT_CLEAN = ""       # '' = clean/vacant (live: ya 'C' bhi dekha)
ROOMSTAT_MBLOCK = "M"     # maintenance/block (RoomBLockOut empty hai, reserve)


def _blocked_map(cn=None, site: str = SITE_CODE) -> dict:
    """Active RoomBLockOut rows (VB6: Type In ('O','M') + site/HO).
    Returns {room_code: block_type}."""
    try:
        rows = db.query(
            "SELECT DISTINCT RTRIM(RoomCode), RTRIM(ISNULL(Type, 'O')) "
            "FROM RoomBLockOut WHERE RoomCode IS NOT NULL AND "
            "(LogSite_Code = ? OR LogSite_Code = 'HO') AND "
            "ISNULL(Type, '') IN ('O', 'M')",
            (site,), cn=cn)
    except db.pyodbc.Error as e:
        if "208" in str(e) or "Invalid object name" in str(e):
            return {}
        raise
    return {r[0]: (r[1] or "O") for r in rows if r[0]}


def room_rack(cn=None, site: str = SITE_CODE,
              vprefix: str = "2026") -> list[dict]:
    """VB6 Room Display rack: har RO-room ka status + in-house guest.

    Status precedence (frm:792/1065/704 + RoomBLockOut se):
      1. RoomOcc.ChkOutDate IS NULL  -> 'Occupied' (guest naame ke saath)
      2. RoomBLockOut Type O/M      -> 'Out of Order' / 'Maintenance'
      3. RoomMast.RoomStat='D'       -> 'Dirty'
      4. RoomMast.RoomStat='M'       -> 'Maintenance'
      5. warna                       -> 'Vacant'
    Tables (TB) include karte hain (VB6 FdRoomDisplay * select karta tha).
    """
    rooms = db.query(
        "SELECT RTRIM(Type), RTRIM(Code), RTRIM(Name), RTRIM(RoomCat), "
        "MultPer, RTRIM(RoomStat), RTRIM(MaidStation) "
        "FROM RoomMast WHERE (LogSite_Code = ? OR LogSite_Code = 'HO') "
        "ORDER BY Type, Code", (site,), cn=cn)
    # live occupancy: frm:792 pattern (ChkOutDate IS NULL)
    occ = db.query(
        "SELECT RTRIM(ro.RoomNo), ro.FolioNo, RTRIM(gf.Name), "
        "CONVERT(date, ro.ChkInDate), CONVERT(date, ro.DepDate), "
        "ro.DocId, ro.SNo "
        "FROM RoomOcc ro LEFT JOIN GuestFolio gf ON gf.DocId = ro.DocId "
        "WHERE ro.ChkOutDate IS NULL AND ro.Site_Code = ? "
        "AND ro.Vprefix = ? "
        "ORDER BY ro.RoomNo", (site, vprefix), cn=cn)
    occ_map = {}
    for r in occ:
        dep = r[4]
        occ_map[r[0]] = {
            "folio": r[1], "guest": (r[2] or "").strip(),
            "chk_in": r[3],
            "dep": dep.date() if isinstance(dep, datetime.datetime) else dep,
            "docid": (r[5] or "").strip(), "sno": r[6],
        }
    blk = _blocked_map(cn=cn, site=site)
    out = []
    for r in rooms:
        rtype, code, name, rcat, multper, rstat, maid = r
        o = occ_map.get(code)
        btype = blk.get(code)
        if o:
            status = "Occupied"
        elif btype == "M":
            status = "Maintenance"
        elif btype:
            status = "Out of Order"
        elif (rstat or "").strip().upper() == ROOMSTAT_MBLOCK:
            status = "Maintenance"
        elif (rstat or "").strip().upper() == ROOMSTAT_DIRTY:
            status = "Dirty"
        else:
            status = "Vacant"
        out.append({
            "type": rtype, "roomno": code, "name": name,
            "cat": rcat, "multper": multper, "maid": maid,
            "rawstat": (rstat or "").strip(),
            "status": status,
            "block_type": btype or "",
            "folio": o["folio"] if o else None,
            "guest": o["guest"] if o else "",
            "chk_in": o["chk_in"] if o else None,
            "dep": o["dep"] if o else None,
            "occ_docid": o["docid"] if o else "",
            "occ_sno": o["sno"] if o else None,
        })
    return out


def housekeeping_summary(cn=None, site: str = SITE_CODE,
                         vprefix: str = "2026") -> dict:
    """Rack counts (UI summary labels ke liye)."""
    rack = room_rack(cn=cn, site=site, vprefix=vprefix)
    rooms = [r for r in rack if r["type"] == "RO"]
    occ = [r for r in rooms if r["status"] == "Occupied"]
    dirty = [r for r in rooms if r["status"] == "Dirty"]
    maint = [r for r in rooms if r["status"] in ("Maintenance", "Out of Order")]
    total = len(rooms) or 1
    free = len(rooms) - len(occ) - len(dirty) - len(maint)
    return {
        "total": len(rooms), "tables": len(rack) - len(rooms),
        "occupied": len(occ), "dirty": len(dirty),
        "vacant": free if free > 0 else 0,
        "maintenance": len(maint),  # FO-10: RoomBLockOut O/M + RoomStat M
        "occ_pct": round(len(occ) * 100 / total, 1),
        "inhouse_guests": len({r["folio"] for r in occ if r["folio"]}),
    }


def update_hk_status(roomno: str, new_status: str, user: str = USER,
                     cn=None, commit: bool = True,
                     site: str = SITE_CODE) -> int:
    """Housekeeping: RoomMast.RoomStat update (VB6 HK screen).

    RoomStat varchar(1): 'D' = Dirty, '' = Clean, 'M' = Maintenance.
    Occupied room ko clean mark karna block hai (guest andar hai).
    Maintenance/OOO ke liye block_out()/unblock_room() use karo
    (RoomBLockOut table) - yahan sirf RoomStat flip."""
    stat = (new_status or "").strip().upper()
    if stat in ("DIRTY", "D"):
        new = ROOMSTAT_DIRTY
    elif stat in ("CLEAN", "VACANT", ""):
        new = ROOMSTAT_CLEAN
    elif stat in ("MAINTENANCE", "M"):
        new = ROOMSTAT_MBLOCK
    else:
        raise ValueError(
            f"RoomStat '{new_status}' supported nahi "
            "(sirf Clean/Dirty/Maintenance; Out of Order = block_out)")
    occ = db.query(
        "SELECT COUNT(*) FROM RoomOcc WHERE RTRIM(RoomNo) = ? AND "
        "ChkOutDate IS NULL AND Site_Code = ?",
        (roomno, site), cn=cn)
    if occ and occ[0][0]:
        raise ValueError(f"Room {roomno} occupied hai - HK status locked")
    rows = db.query(
        "SELECT COUNT(*) FROM RoomMast WHERE RTRIM(Code) = ? AND "
        "(LogSite_Code = ? OR LogSite_Code = 'HO')", (roomno, site), cn=cn)
    if not rows or not rows[0][0]:
        raise ValueError(f"Room {roomno} RoomMast me nahi mila")
    own = cn is None
    cn = cn or db.connect()
    try:
        n = db.execute(
            "UPDATE RoomMast SET RoomStat = ?, U_Name = ?, "
            "U_EntDt = getdate(), U_AE = 'E' "
            "WHERE RTRIM(Code) = ? AND (LogSite_Code = ? OR "
            "LogSite_Code = 'HO')",
            (new, user, roomno, site), cn=cn, commit=False)
        if commit:
            cn.commit()
        return n
    finally:
        if own:
            cn.close()


# ─── FO-10: RoomBlockOut (VB6 HHouseKeeping / HKRoomBlock) ────────────────
# Live schema: RoomCode, Reasons, FromDate, ToDate, Type, Site_Code,
# U_Name, U_EntDt, U_AE, LogSite_Code, VTime. Type: 'O' (out-of-order
# w/ Reasons+dates), 'M' (maintenance w/ FromDate).

def list_blocks(cn=None, site: str = SITE_CODE, top: int = 200) -> list[dict]:
    """RoomBLockOut browse (shell 'Room Block' leaf)."""
    rows = db.query(
        f"SELECT TOP {int(top)} RTRIM(RoomCode), RTRIM(ISNULL(Reasons, '')), "
        "FromDate, ToDate, RTRIM(ISNULL(Type, '')), RTRIM(ISNULL(U_Name, '')), "
        "U_EntDt FROM RoomBLockOut WHERE RoomCode IS NOT NULL AND "
        "(LogSite_Code = ? OR LogSite_Code = 'HO') "
        "ORDER BY U_EntDt DESC", (site,), cn=cn)
    return [{"roomno": r[0] or "", "reason": r[1] or "",
             "from_date": r[2], "to_date": r[3],
             "type": r[4] or "", "user": r[5] or "",
             "ent_dt": r[6]} for r in rows]


def block_out(roomno: str, block_type: str = "O", reason: str = "",
              from_date=None, to_date=None, user: str = USER,
              cn=None, commit: bool = True,
              site: str = SITE_CODE) -> int:
    """FO-10: room ko out-of-order / maintenance mark karo.

    VB6 insert (HHouseKeeping.frm:774 Type='O' full cols; HKRoomBlock
    .frm:1221 Type='M' FromDate-only). Occupied room block nahi ho sakta.
    Returns rows affected (insert count)."""
    roomno = (roomno or "").strip()
    if not roomno:
        raise ValueError("RoomNo zaroori hai")
    btype = (block_type or "O").strip().upper()
    if btype not in ("O", "M"):
        raise ValueError(f"Block type '{block_type}' nahi (sirf O/M)")
    if btype == "O" and not (reason or "").strip():
        raise ValueError("Out-of-Order block ke liye reason zaroori hai")
    occ = db.query(
        "SELECT COUNT(*) FROM RoomOcc WHERE RTRIM(RoomNo) = ? AND "
        "ChkOutDate IS NULL AND Site_Code = ?",
        (roomno, site), cn=cn)
    if occ and occ[0][0]:
        raise ValueError(f"Room {roomno} occupied hai - block nahi ho sakta")
    rows = db.query(
        "SELECT COUNT(*) FROM RoomMast WHERE RTRIM(Code) = ? AND "
        "(LogSite_Code = ? OR LogSite_Code = 'HO')", (roomno, site), cn=cn)
    if not rows or not rows[0][0]:
        raise ValueError(f"Room {roomno} RoomMast me nahi mila")
    already = db.query(
        "SELECT COUNT(*) FROM RoomBLockOut WHERE RTRIM(RoomCode) = ? AND "
        "RTRIM(ISNULL(Type, '')) = ? AND (LogSite_Code = ? OR "
        "LogSite_Code = 'HO')", (roomno, btype, site), cn=cn)
    if already and already[0][0]:
        raise ValueError(f"Room {roomno} pehle se Type={btype} blocked hai")
    fd = from_date or datetime.date.today()
    td = to_date
    if isinstance(fd, datetime.datetime):
        fd = fd.date()
    if isinstance(td, datetime.datetime):
        td = td.date()
    if btype == "O" and td is None:
        td = fd
    own = cn is None
    cn = cn or db.connect()
    try:
        if btype == "O":
            n = db.execute(
                "INSERT INTO RoomBLockOut (RoomCode, Reasons, FromDate, "
                "ToDate, Type, Site_Code, U_Name, U_EntDt, U_AE, "
                "LogSite_Code, VTime) "
                "VALUES (?, ?, ?, ?, 'O', ?, ?, getdate(), 'A', ?, "
                "CONVERT(varchar(5), getdate(), 108))",
                (roomno, (reason or "").strip()[:100], fd, td, site, user,
                 site), cn=cn, commit=False)
        else:  # 'M' - HKRoomBlock.frm:1221 FromDate-only
            n = db.execute(
                "INSERT INTO RoomBLockOut (RoomCode, Type, Site_Code, "
                "U_Name, FromDate, LogSite_Code, VTime) "
                "VALUES (?, 'M', ?, ?, ?, ?, "
                "CONVERT(varchar(5), getdate(), 108))",
                (roomno, site, user, fd, site), cn=cn, commit=False)
        # RoomStat 'M' bhi flip (rack RoomStat fallback)
        db.execute(
            "UPDATE RoomMast SET RoomStat = 'M', U_Name = ?, "
            "U_EntDt = getdate(), U_AE = 'E' WHERE RTRIM(Code) = ? AND "
            "(LogSite_Code = ? OR LogSite_Code = 'HO')",
            (user, roomno, site), cn=cn, commit=False)
        if commit:
            cn.commit()
        return n
    finally:
        if own:
            cn.close()


def unblock_room(roomno: str, block_type: str = "O", user: str = USER,
                 cn=None, commit: bool = True,
                 site: str = SITE_CODE) -> int:
    """FO-10: block hatao (VB6 HHouseKeeping.frm:762
    'delete from RoomBlockOut where RoomCode=... And Type=O')."""
    roomno = (roomno or "").strip()
    if not roomno:
        raise ValueError("RoomNo zaroori hai")
    btype = (block_type or "O").strip().upper()
    if btype not in ("O", "M", ""):
        raise ValueError(f"Block type '{block_type}' nahi (sirf O/M)")
    own = cn is None
    cn = cn or db.connect()
    try:
        if btype:
            n = db.execute(
                "DELETE FROM RoomBLockOut WHERE RTRIM(RoomCode) = ? AND "
                "RTRIM(ISNULL(Type, '')) = ? AND (LogSite_Code = ? OR "
                "LogSite_Code = 'HO')",
                (roomno, btype, site), cn=cn, commit=False)
        else:
            n = db.execute(
                "DELETE FROM RoomBLockOut WHERE RTRIM(RoomCode) = ? AND "
                "(LogSite_Code = ? OR LogSite_Code = 'HO')",
                (roomno, site), cn=cn, commit=False)
        # agar koi block bacha na ho to RoomStat 'M' clear
        left = db.query(
            "SELECT COUNT(*) FROM RoomBLockOut WHERE RTRIM(RoomCode) = ? "
            "AND RTRIM(ISNULL(Type, '')) IN ('O', 'M') AND "
            "(LogSite_Code = ? OR LogSite_Code = 'HO')",
            (roomno, site), cn=cn)
        if not left or not left[0][0]:
            db.execute(
                "UPDATE RoomMast SET RoomStat = '', U_Name = ?, "
                "U_EntDt = getdate(), U_AE = 'E' WHERE RTRIM(Code) = ? AND "
                "RTRIM(ISNULL(RoomStat, '')) = 'M' AND "
                "(LogSite_Code = ? OR LogSite_Code = 'HO')",
                (user, roomno, site), cn=cn, commit=False)
        if commit:
            cn.commit()
        return n
    finally:
        if own:
            cn.close()


def move_room(docid: str, sno: int, new_room: str, reason: str = "",
              user: str = USER, cn=None, commit: bool = True,
              site: str = SITE_CODE) -> int:
    """Room change (VB6 fdRoomChange.frm:3676 live pattern):
    Update RoomOcc Set RoomNo=<new> + audit; NewRoomNo/Reason cols
    VB6 me change-history ke liye the (30-col INSERT naya SNo banata
    tha - hum minimal UPDATE karte hain, history Reason me)."""
    cur = db.query(
        "SELECT COUNT(*) FROM RoomOcc WHERE DocId = ? AND SNo = ? AND "
        "ChkOutDate IS NULL AND Site_Code = ?", (docid, sno, site), cn=cn)
    if not cur or not cur[0][0]:
        raise ValueError("Open RoomOcc row nahi mili (galat docid/sno "
                         "ya pehle se checked-out)")
    own = cn is None
    cn = cn or db.connect()
    try:
        n = db.execute(
            "UPDATE RoomOcc SET RoomNo = ?, NewRoomNo = ?, Reason = ?, "
            "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' "
            "WHERE DocId = ? AND SNo = ? AND ChkOutDate IS NULL AND "
            "Site_Code = ?",
            (new_room, new_room, (reason or "").strip()[:50], user,
             docid, sno, site), cn=cn, commit=False)
        if commit:
            cn.commit()
        return n
    finally:
        if own:
            cn.close()


def room_availability(arr, dep, cn=None, site: str = SITE_CODE,
                      vprefix: str = "2026") -> list[dict]:
    """Free rooms date-range ke liye (VB6 FrmHouseStatus:699 pattern:
    Code NOT IN open-RoomOcc) + Dirty flag alag se."""
    rooms = db.query(
        "SELECT RTRIM(Code), RTRIM(Name), RTRIM(RoomCat), RoomStat "
        "FROM RoomMast WHERE RTRIM(Type) = 'RO' AND (LogSite_Code = ? OR "
        "LogSite_Code = 'HO') ORDER BY Code", (site,), cn=cn)
    busy = db.query(
        "SELECT DISTINCT RTRIM(RoomNo) FROM RoomOcc WHERE ChkOutDate IS "
        "NULL AND Site_Code = ? AND Vprefix = ?", (site, vprefix), cn=cn)
    busy_set = {r[0] for r in busy}
    return [{"roomno": r[0], "name": r[1], "cat": r[2],
             "free": r[0] not in busy_set,
             "dirty": (r[3] or "").strip().upper() == ROOMSTAT_DIRTY}
            for r in rooms]
