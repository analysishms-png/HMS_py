"""Room Master CRUD (VB6: 'Room Master' - Main Setup -> Front Office).

Schema (live RoomMast): **composite PK (Type, Code, RestCode, LogSite_Code)**
  Type varchar(2) ('RO'/'TB' live), Code varchar(5) PK part (room no),
  Name varchar(15), RoomCat varchar(5), Extension smallint, MultPer smallint,
  RevCode varchar(6), MaidStation varchar(6), InclCount varchar(1),
  ConRoom1-4 varchar(5), RestCode varchar(6), TaxStru varchar(6),
  RoomStat varchar(1), HallRent float, PicPath varchar(250),
  DoorLockID varchar(20), Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code.
Type default 'RO'; RestCode/LogSite_Code engine-set (per-site rows).
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
DEFAULT_TYPE = "RO"
LIMITS = {
    "type": 2, "code": 5, "name": 15, "roomcat": 5,
    "revcode": 6, "maidstation": 6, "restcode": 6, "taxstru": 6,
    "picpath": 250, "doorlockid": 20,
}
SELECT_COLS = (
    "Type, Code, Name, RoomCat, Extension, MultPer, RevCode, "
    "MaidStation, InclCount, ConRoom1, ConRoom2, ConRoom3, ConRoom4, "
    "RestCode, TaxStru, RoomStat, HallRent, PicPath, DoorLockID, "
    "U_Name, U_EntDt, U_AE"
)


def _map(r) -> dict:
    return {
        "type": r.Type or DEFAULT_TYPE, "code": r.Code,
        "name": r.Name or "", "roomcat": r.RoomCat or "",
        "extension": r.Extension or 0, "multper": r.MultPer or 0,
        "revcode": r.RevCode or "", "maidstation": r.MaidStation or "",
        "inclcount": r.InclCount or "",
        "conroom1": r.ConRoom1 or "", "conroom2": r.ConRoom2 or "",
        "conroom3": r.ConRoom3 or "", "conroom4": r.ConRoom4 or "",
        "restcode": r.RestCode or "", "taxstru": r.TaxStru or "",
        "roomstat": r.RoomStat or "", "hallrent": r.HallRent or 0.0,
        "picpath": r.PicPath or "", "doorlockid": r.DoorLockID or "",
        "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
    }


def _validate(rec: dict):
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if len(rec["code"]) > LIMITS["code"]:
        raise ValueError(f"Code max {LIMITS['code']} chars")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    if len(rec["name"]) > LIMITS["name"]:
        raise ValueError(f"Name max {LIMITS['name']} chars")
    t = (rec.get("type") or DEFAULT_TYPE).strip() or DEFAULT_TYPE
    if len(t) > LIMITS["type"]:
        raise ValueError(f"Type max {LIMITS['type']} chars")
    for k in ("roomcat", "revcode", "maidstation", "restcode", "taxstru"):
        if len(rec.get(k, "")) > LIMITS[k]:
            raise ValueError(f"{k} max {LIMITS[k]} chars")


def list_all(cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM RoomMast WHERE (LOGSITE_CODE = ? OR LOGSITE_CODE = 'HO' OR ISNULL(LOGSITE_CODE,'')='') ORDER BY Code", cn=cn)
    return [_map(r) for r in rows]


def get(code: str, cn=None, type: str = DEFAULT_TYPE,
        restcode: str = "") -> dict | None:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM RoomMast WHERE Code = ? AND Type = ? "
        "AND RestCode = ?", (code, type, restcode), cn=cn)
    return _map(rows[0]) if rows else None


def exists(code: str, cn=None, type: str = DEFAULT_TYPE,
           restcode: str = "") -> bool:
    return bool(db.query(
        "SELECT 1 FROM RoomMast WHERE Code = ? AND Type = ? AND RestCode = ?",
        (code, type, restcode), cn=cn))


def insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    typ = (rec.get("type") or DEFAULT_TYPE).strip() or DEFAULT_TYPE
    rest = rec.get("restcode", "")
    # composite PK (Type, Code, RestCode, LogSite_Code) — scoped guard
    if db.query(
            "SELECT 1 FROM RoomMast WHERE RTRIM(Code) = ? AND Type = ? "
            "AND RestCode = ?", (rec["code"].strip(), typ, rest), cn=cn):
        raise ValueError(f"Room Code '{rec['code']}' Already Exists "
                         f"(Type {typ})")
    # FK validation: RoomCat (VB6 roommaster form validates category link)
    cat = rec.get("roomcat", "")
    if cat:
        from HMS_py.core import roomcategory
        if not roomcategory.exists(cat, cn=cn, type="RO"):
            raise ValueError(f"Room Category '{cat}' live RoomCat me nahi "
                             "(RO) — pehle category banao")
    return db.execute(
        "INSERT INTO RoomMast (Type, Code, Name, RoomCat, Extension, "
        "MultPer, RevCode, MaidStation, InclCount, ConRoom1, ConRoom2, "
        "ConRoom3, ConRoom4, RestCode, TaxStru, RoomStat, HallRent, "
        "PicPath, DoorLockID, Site_Code, U_Name, U_EntDt, U_AE, "
        "LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
        "?, ?, ?, ?, getdate(), 'A', ?)",
        (typ, rec["code"], rec["name"],
         rec.get("roomcat", ""), int(rec.get("extension") or 0),
         int(rec.get("multper") or 0), rec.get("revcode", ""),
         rec.get("maidstation", ""), rec.get("inclcount", ""),
         rec.get("conroom1", ""), rec.get("conroom2", ""),
         rec.get("conroom3", ""), rec.get("conroom4", ""),
         rest, rec.get("taxstru", ""),
         rec.get("roomstat", ""), float(rec.get("hallrent") or 0),
         rec.get("picpath", ""), rec.get("doorlockid", ""),
         SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def update(code: str, rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    typ = (rec.get("type") or DEFAULT_TYPE).strip() or DEFAULT_TYPE
    return db.execute(
        "UPDATE RoomMast SET Name = ?, RoomCat = ?, "
        "Extension = ?, MultPer = ?, RevCode = ?, MaidStation = ?, "
        "InclCount = ?, ConRoom1 = ?, ConRoom2 = ?, ConRoom3 = ?, "
        "ConRoom4 = ?, TaxStru = ?, RoomStat = ?, "
        "HallRent = ?, PicPath = ?, DoorLockID = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' "
        "WHERE Code = ? AND Type = ? AND RestCode = ?",
        (rec["name"], rec.get("roomcat", ""),
         int(rec.get("extension") or 0), int(rec.get("multper") or 0),
         rec.get("revcode", ""), rec.get("maidstation", ""),
         rec.get("inclcount", ""), rec.get("conroom1", ""),
         rec.get("conroom2", ""), rec.get("conroom3", ""),
         rec.get("conroom4", ""), rec.get("taxstru", ""),
         rec.get("roomstat", ""), float(rec.get("hallrent") or 0),
         rec.get("picpath", ""), rec.get("doorlockid", ""),
         USER, code, typ, rec.get("restcode", "")),
        cn=cn, commit=commit)


def delete(code: str, cn=None, commit: bool = True,
           type: str = DEFAULT_TYPE, restcode: str = "") -> int:
    return db.execute(
        "DELETE FROM RoomMast WHERE Code = ? AND Type = ? AND RestCode = ?",
        (code, type, restcode), cn=cn, commit=commit)
