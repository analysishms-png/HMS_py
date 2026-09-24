"""EPABX Setup Masters (VB6: Main Setup -> EPABX).

Database evidence (live HMS):
- TelCallType: Call type master (Local/STD/ISD etc.)
  Schema: Code varchar(6) PK, CallType varchar(30), ShortName varchar(10),
  ACCode varchar(10), TaxStru varchar(6), audit cols
- TelCallCode: STD code master (area codes)
  Schema: STDCode varchar(6) PK, CallTypeCode varchar(6) FK->TelCallType,
  Description varchar(30), PulseInSec float, audit cols
- TelExt: Extension master (phone extensions mapped to rooms/shops)
  Schema: Code varchar(6) PK, Description varchar(30),
  Extension varchar(10), Type varchar(10), RoomNo varchar(6),
  ShopNo varchar(6), DepCode varchar(6), PulseRate float, audit cols
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()


# ============================================================
# Tel Call Type Master
# Table: TelCallType - Code varchar PK, CallType varchar,
#        ShortName varchar, ACCode, TaxStru, audit cols
# ============================================================
CALLTYPE_LIMITS = {"code": 6, "calltype": 30, "shortname": 10,
                   "accode": 10, "taxstru": 6}
CALLTYPE_COLS = "Code, CallType, ShortName, ACCode, TaxStru, U_Name, U_EntDt, U_AE"


def _map_calltype(r) -> dict:
    try:
        return {"code": r.Code, "calltype": (r.CallType or "").strip(),
                "shortname": (r.ShortName or "").strip(),
                "accode": r.ACCode or "",
                "taxstru": r.TaxStru or "",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        c, ct, sn, ac, ts, un, _, uae = r
        return {"code": c, "calltype": (ct or "").strip(),
                "shortname": (sn or "").strip(),
                "accode": ac or "", "taxstru": ts or "",
                "u_name": un or "", "u_ae": uae or ""}


def calltype_list(cn=None) -> list[dict]:
    return [_map_calltype(r) for r in db.query(
        f"SELECT {CALLTYPE_COLS} FROM TelCallType ORDER BY Code", cn=cn)]


def calltype_get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {CALLTYPE_COLS} FROM TelCallType WHERE Code = ?",
        (code,), cn=cn)
    return _map_calltype(rows[0]) if rows else None


def calltype_exists(code: str, cn=None) -> bool:
    return bool(db.query(
        "SELECT 1 FROM TelCallType WHERE Code = ?", (code,), cn=cn))


def calltype_insert(rec: dict, cn=None, commit=True) -> int:
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if not rec.get("calltype", "").strip():
        raise ValueError("CallType zaroori hai")
    db.require_absent("TelCallType", "Code", rec["code"], "Call Type Code")
    return db.execute(
        "INSERT INTO TelCallType (Code, CallType, ShortName, ACCode, "
        "TaxStru, Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["calltype"], rec.get("shortname", ""),
         rec.get("accode", ""), rec.get("taxstru", ""),
         SITE_CODE, USER, SITE_CODE), cn=cn, commit=commit)


def calltype_update(code: str, rec: dict, cn=None, commit=True) -> int:
    if not rec.get("calltype", "").strip():
        raise ValueError("CallType zaroori hai")
    return db.execute(
        "UPDATE TelCallType SET CallType = ?, ShortName = ?, "
        "ACCode = ?, TaxStru = ?, U_Name = ?, U_EntDt = getdate(), "
        "U_AE = 'E' WHERE Code = ?",
        (rec["calltype"], rec.get("shortname", ""),
         rec.get("accode", ""), rec.get("taxstru", ""),
         USER, code), cn=cn, commit=commit)


def calltype_delete(code: str, cn=None, commit=True) -> int:
    return db.execute(
        "DELETE FROM TelCallType WHERE Code = ?", (code,), cn=cn, commit=commit)


class _CallTypeAPI:
    LIMITS = CALLTYPE_LIMITS
    @staticmethod
    def list_all(cn=None): return calltype_list(cn)
    @staticmethod
    def get(code, cn=None): return calltype_get(code, cn)
    @staticmethod
    def exists(code, cn=None): return calltype_exists(code, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return calltype_insert(rec, cn, commit)
    @staticmethod
    def update(code, rec, cn=None, commit=True): return calltype_update(code, rec, cn, commit)
    @staticmethod
    def delete(code, cn=None, commit=True): return calltype_delete(code, cn, commit)

CallTypeAPI = _CallTypeAPI()


# ============================================================
# Tel Call Code Master (STD codes)
# Table: TelCallCode - STDCode varchar PK, CallTypeCode varchar,
#        Description varchar, PulseInSec float, audit cols
# ============================================================
CALLCODE_LIMITS = {"stdcode": 6, "calltype": 6, "desc": 30}
CALLCODE_COLS = "STDCode, CallTypeCode, Description, PulseInSec, U_Name, U_EntDt, U_AE"


def _map_callcode(r) -> dict:
    try:
        return {"stdcode": r.STDCode, "calltype": r.CallTypeCode or "",
                "desc": (r.Description or "").strip(),
                "pulse": float(r.PulseInSec or 0),
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        sc, cc, d, p, un, _, uae = r
        return {"stdcode": sc, "calltype": cc or "",
                "desc": (d or "").strip(),
                "pulse": float(p or 0),
                "u_name": un or "", "u_ae": uae or ""}


def callcode_list(cn=None) -> list[dict]:
    return [_map_callcode(r) for r in db.query(
        f"SELECT {CALLCODE_COLS} FROM TelCallCode ORDER BY STDCode", cn=cn)]


def callcode_get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {CALLCODE_COLS} FROM TelCallCode WHERE STDCode = ?",
        (code,), cn=cn)
    return _map_callcode(rows[0]) if rows else None


def callcode_exists(code: str, cn=None) -> bool:
    return bool(db.query(
        "SELECT 1 FROM TelCallCode WHERE STDCode = ?", (code,), cn=cn))


def callcode_insert(rec: dict, cn=None, commit=True) -> int:
    if not rec.get("stdcode", "").strip():
        raise ValueError("STDCode zaroori hai")
    if not rec.get("desc", "").strip():
        raise ValueError("Description zaroori hai")
    db.require_absent("TelCallCode", "STDCode", rec["stdcode"], "STD Code")
    return db.execute(
        "INSERT INTO TelCallCode (STDCode, CallTypeCode, Description, "
        "PulseInSec, Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["stdcode"], rec.get("calltype", ""), rec["desc"],
         float(rec.get("pulse") or 0), SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def callcode_update(code: str, rec: dict, cn=None, commit=True) -> int:
    if not rec.get("desc", "").strip():
        raise ValueError("Description zaroori hai")
    return db.execute(
        "UPDATE TelCallCode SET CallTypeCode = ?, Description = ?, "
        "PulseInSec = ?, U_Name = ?, U_EntDt = getdate(), "
        "U_AE = 'E' WHERE STDCode = ?",
        (rec.get("calltype", ""), rec["desc"],
         float(rec.get("pulse") or 0), USER, code),
        cn=cn, commit=commit)


def callcode_delete(code: str, cn=None, commit=True) -> int:
    return db.execute(
        "DELETE FROM TelCallCode WHERE STDCode = ?", (code,),
        cn=cn, commit=commit)


class _CallCodeAPI:
    LIMITS = CALLCODE_LIMITS
    @staticmethod
    def list_all(cn=None): return callcode_list(cn)
    @staticmethod
    def get(code, cn=None): return callcode_get(code, cn)
    @staticmethod
    def exists(code, cn=None): return callcode_exists(code, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return callcode_insert(rec, cn, commit)
    @staticmethod
    def update(code, rec, cn=None, commit=True): return callcode_update(code, rec, cn, commit)
    @staticmethod
    def delete(code, cn=None, commit=True): return callcode_delete(code, cn, commit)

CallCodeAPI = _CallCodeAPI()


# ============================================================
# Tel Extension Master
# Table: TelExt - Code varchar PK, Description varchar,
#        Extension varchar, Type varchar, RoomNo varchar,
#        ShopNo varchar, DepCode varchar, PulseRate float, audit cols
# ============================================================
TELEXT_LIMITS = {"code": 6, "desc": 30, "extension": 10, "type": 10,
                 "room": 6, "shop": 6, "dept": 6}
TELEXT_COLS = ("Code, Description, Extension, Type, RoomNo, ShopNo, "
               "DepCode, PulseRate, U_Name, U_EntDt, U_AE")


def _map_telext(r) -> dict:
    try:
        return {"code": r.Code, "desc": (r.Description or "").strip(),
                "extension": r.Extension or "", "type": r.Type or "",
                "room": r.RoomNo or "", "shop": r.ShopNo or "",
                "dept": r.DepCode or "",
                "pulserate": float(r.PulseRate or 0),
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        c, d, ext, t, rm, sh, dp, pr, un, _, uae = r
        return {"code": c, "desc": (d or "").strip(),
                "extension": ext or "", "type": t or "",
                "room": rm or "", "shop": sh or "",
                "dept": dp or "",
                "pulserate": float(pr or 0),
                "u_name": un or "", "u_ae": uae or ""}


def telext_list(cn=None) -> list[dict]:
    return [_map_telext(r) for r in db.query(
        f"SELECT {TELEXT_COLS} FROM TelExt ORDER BY Code", cn=cn)]


def telext_get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {TELEXT_COLS} FROM TelExt WHERE Code = ?",
        (code,), cn=cn)
    return _map_telext(rows[0]) if rows else None


def telext_exists(code: str, cn=None) -> bool:
    return bool(db.query(
        "SELECT 1 FROM TelExt WHERE Code = ?", (code,), cn=cn))


def telext_insert(rec: dict, cn=None, commit=True) -> int:
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if not rec.get("desc", "").strip():
        raise ValueError("Description zaroori hai")
    db.require_absent("TelExt", "Code", rec["code"], "Extension Code")
    return db.execute(
        "INSERT INTO TelExt (Code, Description, Extension, Type, "
        "RoomNo, ShopNo, DepCode, PulseRate, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["desc"], rec.get("extension", ""),
         rec.get("type", ""), rec.get("room", ""),
         rec.get("shop", ""), rec.get("dept", ""),
         float(rec.get("pulserate") or 0),
         SITE_CODE, USER, SITE_CODE), cn=cn, commit=commit)


def telext_update(code: str, rec: dict, cn=None, commit=True) -> int:
    if not rec.get("desc", "").strip():
        raise ValueError("Description zaroori hai")
    return db.execute(
        "UPDATE TelExt SET Description = ?, Extension = ?, Type = ?, "
        "RoomNo = ?, ShopNo = ?, DepCode = ?, PulseRate = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec["desc"], rec.get("extension", ""), rec.get("type", ""),
         rec.get("room", ""), rec.get("shop", ""),
         rec.get("dept", ""), float(rec.get("pulserate") or 0),
         USER, code), cn=cn, commit=commit)


def telext_delete(code: str, cn=None, commit=True) -> int:
    return db.execute(
        "DELETE FROM TelExt WHERE Code = ?", (code,), cn=cn, commit=commit)


class _TelExtAPI:
    LIMITS = TELEXT_LIMITS
    @staticmethod
    def list_all(cn=None): return telext_list(cn)
    @staticmethod
    def get(code, cn=None): return telext_get(code, cn)
    @staticmethod
    def exists(code, cn=None): return telext_exists(code, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return telext_insert(rec, cn, commit)
    @staticmethod
    def update(code, rec, cn=None, commit=True): return telext_update(code, rec, cn, commit)
    @staticmethod
    def delete(code, cn=None, commit=True): return telext_delete(code, cn, commit)

TelExtAPI = _TelExtAPI()
