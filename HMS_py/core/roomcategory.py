"""Room Category master CRUD (VB6: Room Cat - Main Setup -> Front Office).

Schema (live RoomCat): **composite PK (Type, Code)** — Type varchar(2) NN
('RO' live; RoomMast bhi 'RO'/'TB'), Code varchar(5) NN, Name varchar(25),
ShortName(6), RevCode(6), MaxPerson smallint.
VB6 evidence: RoomCat forms Type+Code dono use karte hain; hum default
Type='RO' scope karte hain (single-code API compat ke saath).
Audit: U_Name + U_EntDt(getdate()) + U_AE ('A'/'E').
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
DEFAULT_TYPE = "RO"
LIMITS = {"code": 5, "name": 25, "short": 6, "revcode": 6, "type": 2}
SELECT_COLS = "Type, Code, Name, ShortName, MaxPerson, RevCode, " \
              "U_Name, U_EntDt, U_AE"


def _map(r) -> dict:
    return {"type": r.Type or DEFAULT_TYPE, "code": r.Code,
            "name": r.Name or "", "short": r.ShortName or "",
            "maxperson": r.MaxPerson or 0, "revcode": r.RevCode or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}


def _validate(rec: dict):
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if len(rec["code"]) > LIMITS["code"]:
        raise ValueError(f"Code max {LIMITS['code']} chars")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    if len(rec["name"]) > LIMITS["name"]:
        raise ValueError(f"Name max {LIMITS['name']} chars")
    if len(rec.get("short", "")) > LIMITS["short"]:
        raise ValueError(f"ShortName max {LIMITS['short']} chars")
    t = (rec.get("type") or DEFAULT_TYPE).strip() or DEFAULT_TYPE
    if len(t) > LIMITS["type"]:
        raise ValueError(f"Type max {LIMITS['type']} chars")


def list_all(cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM RoomCat WHERE (LOGSITE_CODE = ? OR LOGSITE_CODE = 'HO' OR ISNULL(LOGSITE_CODE,'')='') ORDER BY Code", cn=cn)
    return [_map(r) for r in rows]


def get(code: str, cn=None, type: str = DEFAULT_TYPE) -> dict | None:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM RoomCat WHERE Code = ? AND Type = ?",
        (code, type), cn=cn)
    return _map(rows[0]) if rows else None


def exists(code: str, cn=None, type: str = DEFAULT_TYPE) -> bool:
    return bool(db.query(
        "SELECT 1 FROM RoomCat WHERE Code = ? AND Type = ?",
        (code, type), cn=cn))


def insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    typ = (rec.get("type") or DEFAULT_TYPE).strip() or DEFAULT_TYPE
    # composite PK (Type, Code) — scoped duplicate guard
    if db.query("SELECT 1 FROM RoomCat WHERE RTRIM(Code) = ? AND Type = ?",
                (rec["code"].strip(), typ), cn=cn):
        raise ValueError(f"Room Category Code '{rec['code']}' "
                         f"Already Exists (Type {typ})")
    return db.execute(
        "INSERT INTO RoomCat (Type, Code, Name, ShortName, MaxPerson, "
        "RevCode, Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (typ, rec["code"], rec["name"], rec.get("short", ""),
         int(rec.get("maxperson") or 0), rec.get("revcode", ""),
         SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def update(code: str, rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    typ = (rec.get("type") or DEFAULT_TYPE).strip() or DEFAULT_TYPE
    return db.execute(
        "UPDATE RoomCat SET Name = ?, ShortName = ?, MaxPerson = ?, "
        "RevCode = ?, U_Name = ?, U_EntDt = getdate(), U_AE = 'E' "
        "WHERE Code = ? AND Type = ?",
        (rec["name"], rec.get("short", ""),
         int(rec.get("maxperson") or 0), rec.get("revcode", ""),
         USER, code, typ),
        cn=cn, commit=commit)


def delete(code: str, cn=None, commit: bool = True,
           type: str = DEFAULT_TYPE) -> int:
    return db.execute(
        "DELETE FROM RoomCat WHERE Code = ? AND Type = ?", (code, type),
        cn=cn, commit=commit)
