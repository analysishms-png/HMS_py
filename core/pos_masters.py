"""POS Setup Masters (VB6: Main Setup -> Point of Sale).

Database evidence (live HMS):
- POS outlets = Depart table (Code/Name/KotYn/POS/OutletYN) -- already ported
  in depart.py. POS setup masters use Depart as the outlet container.
- SessionMast: POS sessions (Breakfast/Lunch/Dinner) - EXISTS in DB
  Schema: Code varchar(6) PK, Name varchar(30), FromTime varchar(10),
  ToTime varchar(10), Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code
- SchemeMast: Discount/promotion schemes - EXISTS in DB
  Schema: Code varchar(6) PK, Name varchar(30), Startdate datetime,
  Enddate datetime, FromTime varchar(10), ToTime varchar(10), Days varchar(7),
  Active varchar(1), Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code
- DeliveryBoy: Delivery staff - EXISTS in DB
  Schema: Code varchar(6) PK, Name varchar(30), ActiveYN varchar(1),
  Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code
- ItemCatMast: Item category (POS item grouping) - EXISTS in DB
  Schema: Code varchar(6) PK, Name varchar(30), RoundOff float,
  AcName varchar(10), OutletYN varchar(1), TaxStru varchar(6),
  CatType varchar(10), RestCode varchar(6), DrCr varchar(2),
  RevCode varchar(6), Status varchar(10), TaxP float
- HappyHours: Outlet-wise happy hour discounts - EXISTS in DB
  (child of SchemeMast + Depart - browse only, complex insert)

NOTE: OutletMast/ServerMast/TableMast/MenuGroup/MenuCategory/MenuItem
tables do NOT exist in this DB (VB6 stored these in Depart + ItemMast).
Those VB6 menu items map to existing Depart (outlet) + ItemCatMast (category).
"""
from __future__ import annotations

import datetime
from HMS_py.core import db
from HMS_py.core.menu import menu_name_allowed

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()


def _require_permission(menu_name: str, user: str = "SA"):
    if not menu_name_allowed(menu_name, user):
        raise PermissionError(f"{menu_name} ko user rights mein nahi hai")


# ============================================================
# Session Master (Breakfast/Lunch/Dinner sessions)
# ============================================================
SESSION_LIMITS = {"code": 6, "name": 30, "time": 10}
SESSION_COLS = "Code, Name, FromTime, ToTime, U_Name, U_EntDt, U_AE"


def _map_session(r) -> dict:
    try:
        return {"code": r.Code, "name": (r.Name or "").strip(),
                "fromtime": r.FromTime or "", "totime": r.ToTime or "",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        c, n, ft, tt, un, _, uae = r
        return {"code": c, "name": (n or "").strip(),
                "fromtime": ft or "", "totime": tt or "",
                "u_name": un or "", "u_ae": uae or ""}


def session_list(cn=None) -> list[dict]:
    return [_map_session(r) for r in db.query(
        f"SELECT {SESSION_COLS} FROM SessionMast ORDER BY Code", cn=cn)]


def session_get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {SESSION_COLS} FROM SessionMast WHERE Code = ?",
        (code,), cn=cn)
    return _map_session(rows[0]) if rows else None


def session_exists(code: str, cn=None) -> bool:
    return bool(db.query(
        "SELECT 1 FROM SessionMast WHERE Code = ?", (code,), cn=cn))


def session_insert(rec: dict, cn=None, commit=True, user: str = "SA") -> int:
    _require_permission("Session Master", user)
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "INSERT INTO SessionMast (Code, Name, FromTime, ToTime, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"], rec.get("fromtime", ""),
         rec.get("totime", ""), SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def session_update(code: str, rec: dict, cn=None, commit=True) -> int:
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "UPDATE SessionMast SET Name = ?, FromTime = ?, ToTime = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec["name"], rec.get("fromtime", ""), rec.get("totime", ""),
         USER, code), cn=cn, commit=commit)


def session_delete(code: str, cn=None, commit=True) -> int:
    return db.execute(
        "DELETE FROM SessionMast WHERE Code = ?", (code,), cn=cn, commit=commit)


# BaseMasterForm-compatible API wrapper
class _SessionAPI:
    LIMITS = SESSION_LIMITS
    @staticmethod
    def list_all(cn=None): return session_list(cn)
    @staticmethod
    def get(code, cn=None): return session_get(code, cn)
    @staticmethod
    def exists(code, cn=None): return session_exists(code, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True, user="SA"): return session_insert(rec, cn, commit, user=user)
    @staticmethod
    def update(code, rec, cn=None, commit=True, user="SA"): return session_update(code, rec, cn, commit)
    @staticmethod
    def delete(code, cn=None, commit=True, user="SA"): return session_delete(code, cn, commit)

SessionAPI = _SessionAPI()


# ============================================================
# Scheme Master (discount/promotion schemes)
# ============================================================
SCHEME_LIMITS = {"code": 6, "name": 30, "days": 7}
SCHEME_COLS = ("Code, Name, Startdate, Enddate, FromTime, ToTime, "
               "Days, Active, U_Name, U_EntDt, U_AE")


def _map_scheme(r) -> dict:
    def _dt(v):
        if v is None: return None
        return v.date() if isinstance(v, datetime.datetime) else v
    try:
        return {"code": r.Code, "name": (r.Name or "").strip(),
                "startdate": _dt(r.Startdate), "enddate": _dt(r.Enddate),
                "fromtime": r.FromTime or "", "totime": r.ToTime or "",
                "days": r.Days or "", "active": r.Active or "Y",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        c, n, sd, ed, ft, tt, dy, act, un, _, uae = r
        return {"code": c, "name": (n or "").strip(),
                "startdate": _dt(sd), "enddate": _dt(ed),
                "fromtime": ft or "", "totime": tt or "",
                "days": dy or "", "active": act or "Y",
                "u_name": un or "", "u_ae": uae or ""}


def scheme_list(cn=None) -> list[dict]:
    return [_map_scheme(r) for r in db.query(
        f"SELECT {SCHEME_COLS} FROM SchemeMast ORDER BY Code", cn=cn)]


def scheme_get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {SCHEME_COLS} FROM SchemeMast WHERE Code = ?", (code,), cn=cn)
    return _map_scheme(rows[0]) if rows else None


def scheme_exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM SchemeMast WHERE Code = ?", (code,), cn=cn))


def scheme_insert(rec: dict, cn=None, commit=True, user: str = "SA") -> int:
    _require_permission("Scheme Master", user)
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    sd = rec.get("startdate") or datetime.date.today()
    ed = rec.get("enddate") or datetime.date.today()
    return db.execute(
        "INSERT INTO SchemeMast (Code, Name, Startdate, Enddate, FromTime, "
        "ToTime, Days, Active, Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"], sd, ed,
         rec.get("fromtime", ""), rec.get("totime", ""),
         rec.get("days", ""), rec.get("active", "Y"),
         SITE_CODE, USER, SITE_CODE), cn=cn, commit=commit)


def scheme_update(code: str, rec: dict, cn=None, commit=True) -> int:
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    sd = rec.get("startdate") or datetime.date.today()
    ed = rec.get("enddate") or datetime.date.today()
    return db.execute(
        "UPDATE SchemeMast SET Name = ?, Startdate = ?, Enddate = ?, "
        "FromTime = ?, ToTime = ?, Days = ?, Active = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec["name"], sd, ed,
         rec.get("fromtime", ""), rec.get("totime", ""),
         rec.get("days", ""), rec.get("active", "Y"),
         USER, code), cn=cn, commit=commit)


def scheme_delete(code: str, cn=None, commit=True) -> int:
    return db.execute(
        "DELETE FROM SchemeMast WHERE Code = ?", (code,), cn=cn, commit=commit)


class _SchemeAPI:
    LIMITS = SCHEME_LIMITS
    @staticmethod
    def list_all(cn=None): return scheme_list(cn)
    @staticmethod
    def get(code, cn=None): return scheme_get(code, cn)
    @staticmethod
    def exists(code, cn=None): return scheme_exists(code, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True, user="SA"): return scheme_insert(rec, cn, commit, user=user)
    @staticmethod
    def update(code, rec, cn=None, commit=True, user="SA"): return scheme_update(code, rec, cn, commit)
    @staticmethod
    def delete(code, cn=None, commit=True, user="SA"): return scheme_delete(code, cn, commit)

SchemeAPI = _SchemeAPI()


# ============================================================
# Delivery Boy Master
# ============================================================
DELBOY_LIMITS = {"code": 6, "name": 30}
DELBOY_COLS = "Code, Name, ActiveYN, U_Name, U_EntDt, U_AE"


def _map_delboy(r) -> dict:
    try:
        return {"code": r.Code, "name": (r.Name or "").strip(),
                "active": r.ActiveYN or "Y",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        c, n, act, un, _, uae = r
        return {"code": c, "name": (n or "").strip(), "active": act or "Y",
                "u_name": un or "", "u_ae": uae or ""}


def delboy_list(cn=None) -> list[dict]:
    return [_map_delboy(r) for r in db.query(
        f"SELECT {DELBOY_COLS} FROM DeliveryBoy ORDER BY Code", cn=cn)]


def delboy_get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {DELBOY_COLS} FROM DeliveryBoy WHERE Code = ?", (code,), cn=cn)
    return _map_delboy(rows[0]) if rows else None


def delboy_exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM DeliveryBoy WHERE Code = ?", (code,), cn=cn))


def delboy_insert(rec: dict, cn=None, commit=True, user: str = "SA") -> int:
    _require_permission("Delivery Boy", user)
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "INSERT INTO DeliveryBoy (Code, Name, ActiveYN, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"], rec.get("active", "Y"),
         SITE_CODE, USER, SITE_CODE), cn=cn, commit=commit)


def delboy_update(code: str, rec: dict, cn=None, commit=True) -> int:
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "UPDATE DeliveryBoy SET Name = ?, ActiveYN = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec["name"], rec.get("active", "Y"), USER, code),
        cn=cn, commit=commit)


def delboy_delete(code: str, cn=None, commit=True) -> int:
    return db.execute(
        "DELETE FROM DeliveryBoy WHERE Code = ?", (code,), cn=cn, commit=commit)


class _DelBoyAPI:
    LIMITS = DELBOY_LIMITS
    @staticmethod
    def list_all(cn=None): return delboy_list(cn)
    @staticmethod
    def get(code, cn=None): return delboy_get(code, cn)
    @staticmethod
    def exists(code, cn=None): return delboy_exists(code, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True, user="SA"): return delboy_insert(rec, cn, commit, user=user)
    @staticmethod
    def update(code, rec, cn=None, commit=True, user="SA"): return delboy_update(code, rec, cn, commit)
    @staticmethod
    def delete(code, cn=None, commit=True, user="SA"): return delboy_delete(code, cn, commit)

DelBoyAPI = _DelBoyAPI()


# ============================================================
# Item Category Master (POS grouping: ItemCatMast)
# ============================================================
ITEMCAT_LIMITS = {"code": 6, "name": 30, "taxstru": 6,
                  "cattype": 10, "rest": 6, "revcode": 6, "status": 10}
ITEMCAT_COLS = ("Code, Name, RoundOff, AcName, OutletYN, TaxStru, "
                "CatType, RestCode, DrCr, RevCode, Status, TaxP, "
                "U_Name, U_EntDt, U_AE")


def _safe_float(v, default=0.0):
    try:
        return float(v)
    except (ValueError, TypeError):
        return default


def _map_itemcat(r) -> dict:
    try:
        return {"code": r.Code, "name": (r.Name or "").strip(),
                "roundoff": _safe_float(r.RoundOff),
                "acname": (r.AcName or "").strip(),
                "outletyn": r.OutletYN or "N",
                "taxstru": r.TaxStru or "",
                "cattype": r.CatType or "",
                "rest": r.RestCode or "",
                "drcr": r.DrCr or "",
                "revcode": r.RevCode or "",
                "status": r.Status or "",
                "taxp": _safe_float(r.TaxP),
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        c, n, ro, an, oyn, ts, ct, rc, dc, rvc, st, tp, un, _, uae = r
        return {"code": c, "name": (n or "").strip(),
                "roundoff": _safe_float(ro), "acname": (an or "").strip(),
                "outletyn": oyn or "N", "taxstru": ts or "",
                "cattype": ct or "", "rest": rc or "",
                "drcr": dc or "", "revcode": rvc or "",
                "status": st or "", "taxp": _safe_float(tp),
                "u_name": un or "", "u_ae": uae or ""}


def itemcat_list(cn=None) -> list[dict]:
    return [_map_itemcat(r) for r in db.query(
        f"SELECT {ITEMCAT_COLS} FROM ItemCatMast ORDER BY Code", cn=cn)]


def itemcat_get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {ITEMCAT_COLS} FROM ItemCatMast WHERE Code = ?", (code,), cn=cn)
    return _map_itemcat(rows[0]) if rows else None


def itemcat_exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM ItemCatMast WHERE Code = ?", (code,), cn=cn))


def itemcat_insert(rec: dict, cn=None, commit=True, user: str = "SA") -> int:
    _require_permission("Item List", user)
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "INSERT INTO ItemCatMast (Code, Name, RoundOff, AcName, OutletYN, "
        "TaxStru, CatType, RestCode, DrCr, RevCode, Status, TaxP, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"], float(rec.get("roundoff") or 0),
         rec.get("acname", ""), rec.get("outletyn", "N"),
         rec.get("taxstru", ""), rec.get("cattype", ""),
         rec.get("rest", ""), rec.get("drcr", ""),
         rec.get("revcode", ""), rec.get("status", ""),
         float(rec.get("taxp") or 0), SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def itemcat_update(code: str, rec: dict, cn=None, commit=True) -> int:
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "UPDATE ItemCatMast SET Name = ?, RoundOff = ?, AcName = ?, "
        "OutletYN = ?, TaxStru = ?, CatType = ?, RestCode = ?, "
        "DrCr = ?, RevCode = ?, Status = ?, TaxP = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec["name"], float(rec.get("roundoff") or 0),
         rec.get("acname", ""), rec.get("outletyn", "N"),
         rec.get("taxstru", ""), rec.get("cattype", ""),
         rec.get("rest", ""), rec.get("drcr", ""),
         rec.get("revcode", ""), rec.get("status", ""),
         float(rec.get("taxp") or 0), USER, code),
        cn=cn, commit=commit)


def itemcat_delete(code: str, cn=None, commit=True) -> int:
    return db.execute(
        "DELETE FROM ItemCatMast WHERE Code = ?", (code,), cn=cn, commit=commit)


class _ItemCatAPI:
    LIMITS = ITEMCAT_LIMITS
    @staticmethod
    def list_all(cn=None): return itemcat_list(cn)
    @staticmethod
    def get(code, cn=None): return itemcat_get(code, cn)
    @staticmethod
    def exists(code, cn=None): return itemcat_exists(code, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True, user="SA"): return itemcat_insert(rec, cn, commit, user=user)
    @staticmethod
    def update(code, rec, cn=None, commit=True, user="SA"): return itemcat_update(code, rec, cn, commit)
    @staticmethod
    def delete(code, cn=None, commit=True, user="SA"): return itemcat_delete(code, cn, commit)

ItemCatAPI = _ItemCatAPI()


# ============================================================
# NC Type Master (Non-Chargeable type)
# Table: NCTypeMast - NCTYPE varchar PK, NCPer float, audit cols
# ============================================================
NCTYPE_LIMITS = {"code": 6, "ncper": 5}
NCTYPE_COLS = "NCTYPE, NCPer, U_Name, U_EntDt, U_AE"


def _map_nctype(r) -> dict:
    try:
        return {"code": r.NCTYPE, "ncper": float(r.NCPer or 0),
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        c, np, un, _, uae = r
        return {"code": c, "ncper": float(np or 0),
                "u_name": un or "", "u_ae": uae or ""}


def nctype_list(cn=None) -> list[dict]:
    return [_map_nctype(r) for r in db.query(
        f"SELECT {NCTYPE_COLS} FROM NCTypeMast ORDER BY NCTYPE", cn=cn)]


def nctype_get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {NCTYPE_COLS} FROM NCTypeMast WHERE NCTYPE = ?",
        (code,), cn=cn)
    return _map_nctype(rows[0]) if rows else None


def nctype_exists(code: str, cn=None) -> bool:
    return bool(db.query(
        "SELECT 1 FROM NCTypeMast WHERE NCTYPE = ?", (code,), cn=cn))


def nctype_insert(rec: dict, cn=None, commit=True, user: str = "SA") -> int:
    _require_permission("NC Type", user)
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    return db.execute(
        "INSERT INTO NCTypeMast (NCTYPE, NCPer, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], float(rec.get("ncper") or 0),
         SITE_CODE, USER, SITE_CODE), cn=cn, commit=commit)


def nctype_update(code: str, rec: dict, cn=None, commit=True) -> int:
    return db.execute(
        "UPDATE NCTypeMast SET NCPer = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE NCTYPE = ?",
        (float(rec.get("ncper") or 0), USER, code), cn=cn, commit=commit)


def nctype_delete(code: str, cn=None, commit=True) -> int:
    return db.execute(
        "DELETE FROM NCTypeMast WHERE NCTYPE = ?", (code,), cn=cn, commit=commit)


class _NCTypeAPI:
    LIMITS = NCTYPE_LIMITS
    @staticmethod
    def list_all(cn=None): return nctype_list(cn)
    @staticmethod
    def get(code, cn=None): return nctype_get(code, cn)
    @staticmethod
    def exists(code, cn=None): return nctype_exists(code, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True, user="SA"): return nctype_insert(rec, cn, commit, user=user)
    @staticmethod
    def update(code, rec, cn=None, commit=True, user="SA"): return nctype_update(code, rec, cn, commit)
    @staticmethod
    def delete(code, cn=None, commit=True, user="SA"): return nctype_delete(code, cn, commit)

NCTypeAPI = _NCTypeAPI()


# ============================================================
# Waiter / Server Master
# Table: Waiter - Code varchar PK, Name varchar, ActiveYN, RestCode, audit cols
# ============================================================
WAITER_LIMITS = {"code": 6, "name": 30, "rest": 6}
WAITER_COLS = "Code, Name, ActiveYN, RestCode, U_Name, U_EntDt, U_AE"


def _map_waiter(r) -> dict:
    try:
        return {"code": r.Code, "name": (r.Name or "").strip(),
                "active": r.ActiveYN or "Y", "rest": r.RestCode or "",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        c, n, act, rc, un, _, uae = r
        return {"code": c, "name": (n or "").strip(),
                "active": act or "Y", "rest": rc or "",
                "u_name": un or "", "u_ae": uae or ""}


def waiter_list(cn=None) -> list[dict]:
    return [_map_waiter(r) for r in db.query(
        f"SELECT {WAITER_COLS} FROM Waiter ORDER BY Code", cn=cn)]


def waiter_get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {WAITER_COLS} FROM Waiter WHERE Code = ?", (code,), cn=cn)
    return _map_waiter(rows[0]) if rows else None


def waiter_exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM Waiter WHERE Code = ?", (code,), cn=cn))


def waiter_insert(rec: dict, cn=None, commit=True, user: str = "SA") -> int:
    _require_permission("Waiter", user)
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "INSERT INTO Waiter (Code, Name, ActiveYN, RestCode, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"], rec.get("active", "Y"),
         rec.get("rest", ""), SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def waiter_update(code: str, rec: dict, cn=None, commit=True) -> int:
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "UPDATE Waiter SET Name = ?, ActiveYN = ?, RestCode = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec["name"], rec.get("active", "Y"), rec.get("rest", ""),
         USER, code), cn=cn, commit=commit)


def waiter_delete(code: str, cn=None, commit=True) -> int:
    return db.execute(
        "DELETE FROM Waiter WHERE Code = ?", (code,), cn=cn, commit=commit)


class _WaiterAPI:
    LIMITS = WAITER_LIMITS
    @staticmethod
    def list_all(cn=None): return waiter_list(cn)
    @staticmethod
    def get(code, cn=None): return waiter_get(code, cn)
    @staticmethod
    def exists(code, cn=None): return waiter_exists(code, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True, user="SA"): return waiter_insert(rec, cn, commit, user=user)
    @staticmethod
    def update(code, rec, cn=None, commit=True, user="SA"): return waiter_update(code, rec, cn, commit)
    @staticmethod
    def delete(code, cn=None, commit=True, user="SA"): return waiter_delete(code, cn, commit)

WaiterAPI = _WaiterAPI()


# ============================================================
# Shift Master
# Table: ShiftMast - Code varchar PK, Name varchar, FromTime varchar, ToTime varchar, audit cols
# ============================================================
SHIFT_LIMITS = {"code": 6, "name": 30, "fromtime": 10, "totime": 10}
SHIFT_COLS = "Code, Name, FromTime, ToTime, U_Name, U_EntDt, U_AE"


def _map_shift(r) -> dict:
    try:
        return {"code": r.Code, "name": (r.Name or "").strip(),
                "fromtime": r.FromTime or "", "totime": r.ToTime or "",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        c, n, ft, tt, un, _, uae = r
        return {"code": c, "name": (n or "").strip(),
                "fromtime": ft or "", "totime": tt or "",
                "u_name": un or "", "u_ae": uae or ""}


def shift_list(cn=None) -> list[dict]:
    return [_map_shift(r) for r in db.query(
        f"SELECT {SHIFT_COLS} FROM ShiftMast ORDER BY Code", cn=cn)]


def shift_get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {SHIFT_COLS} FROM ShiftMast WHERE Code = ?", (code,), cn=cn)
    return _map_shift(rows[0]) if rows else None


def shift_exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM ShiftMast WHERE Code = ?", (code,), cn=cn))


def shift_insert(rec: dict, cn=None, commit=True, user: str = "SA") -> int:
    _require_permission("Shift Master", user)
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "INSERT INTO ShiftMast (Code, Name, FromTime, ToTime, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"], rec.get("fromtime", ""),
         rec.get("totime", ""), SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def shift_update(code: str, rec: dict, cn=None, commit=True) -> int:
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "UPDATE ShiftMast SET Name = ?, FromTime = ?, ToTime = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec["name"], rec.get("fromtime", ""), rec.get("totime", ""),
         USER, code), cn=cn, commit=commit)


def shift_delete(code: str, cn=None, commit=True) -> int:
    return db.execute(
        "DELETE FROM ShiftMast WHERE Code = ?", (code,), cn=cn, commit=commit)


class _ShiftAPI:
    LIMITS = SHIFT_LIMITS
    @staticmethod
    def list_all(cn=None): return shift_list(cn)
    @staticmethod
    def get(code, cn=None): return shift_get(code, cn)
    @staticmethod
    def exists(code, cn=None): return shift_exists(code, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True, user="SA"): return shift_insert(rec, cn, commit, user=user)
    @staticmethod
    def update(code, rec, cn=None, commit=True, user="SA"): return shift_update(code, rec, cn, commit)
    @staticmethod
    def delete(code, cn=None, commit=True, user="SA"): return shift_delete(code, cn, commit)

ShiftAPI = _ShiftAPI()


# ============================================================
# Combo Pack Master
# Table: ComboPackHead - ComboCode varchar PK, Name varchar, ComboName varchar,
#        Rate float, Active varchar, ServiceCharge float, RestCode, audit cols
# Table: ComboPackDetail - ComboCode + ItemCode + Qty child rows
# ============================================================
COMBO_LIMITS = {"code": 6, "name": 30, "comboname": 30, "rest": 6}
COMBOHEAD_COLS = ("ComboCode, Name, ComboName, Rate, Active, "
                  "ServiceCharge, RestCode, U_Name, U_EntDt, U_AE")


def _map_combo(r) -> dict:
    try:
        return {"code": r.ComboCode, "name": (r.Name or "").strip(),
                "comboname": (r.ComboName or "").strip(),
                "rate": float(r.Rate or 0), "active": r.Active or "Y",
                "servicecharge": float(r.ServiceCharge or 0),
                "rest": r.RestCode or "",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        c, n, cn2, rt, act, sc, rc, un, _, uae = r
        return {"code": c, "name": (n or "").strip(),
                "comboname": (cn2 or "").strip(),
                "rate": float(rt or 0), "active": act or "Y",
                "servicecharge": float(sc or 0),
                "rest": rc or "", "u_name": un or "", "u_ae": uae or ""}


def combo_list(cn=None) -> list[dict]:
    return [_map_combo(r) for r in db.query(
        f"SELECT {COMBOHEAD_COLS} FROM ComboPackHead ORDER BY ComboCode", cn=cn)]


def combo_get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {COMBOHEAD_COLS} FROM ComboPackHead WHERE ComboCode = ?",
        (code,), cn=cn)
    if not rows:
        return None
    d = _map_combo(rows[0])
    d["items"] = combo_detail(code, cn=cn)
    return d


def combo_exists(code: str, cn=None) -> bool:
    return bool(db.query(
        "SELECT 1 FROM ComboPackHead WHERE ComboCode = ?", (code,), cn=cn))


def combo_detail(code: str, cn=None) -> list[dict]:
    rows = db.query(
        "SELECT ComboCode, ItemCode, Qty FROM ComboPackDetail "
        "WHERE ComboCode = ? ORDER BY ItemCode", (code,), cn=cn)
    out = []
    for r in rows:
        try:
            out.append({"code": r.ComboCode, "itemcode": r.ItemCode or "",
                        "qty": float(r.Qty or 0)})
        except AttributeError:
            cc, ic, q = r
            out.append({"code": cc, "itemcode": ic or "", "qty": float(q or 0)})
    return out


def combo_insert(rec: dict, cn=None, commit=True, user: str = "SA") -> int:
    _require_permission("Combo Pack", user)
    if not rec.get("code", "").strip():
        raise ValueError("ComboCode zaroori hai")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    items = rec.get("items", [])
    own = cn is None
    cn = cn or db.connect()
    try:
        db.execute(
            "INSERT INTO ComboPackHead (ComboCode, Name, ComboName, Rate, "
            "Active, ServiceCharge, RestCode, Site_Code, U_Name, U_EntDt, "
            "U_AE, LogSite_Code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
            (rec["code"], rec["name"], rec.get("comboname", ""),
             float(rec.get("rate") or 0), rec.get("active", "Y"),
             float(rec.get("servicecharge") or 0), rec.get("rest", ""),
             SITE_CODE, USER, SITE_CODE), cn=cn, commit=False)
        for item in items:
            db.execute(
                "INSERT INTO ComboPackDetail (ComboCode, ItemCode, Qty, "
                "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
                "VALUES (?, ?, ?, ?, ?, getdate(), 'A', ?)",
                (rec["code"], item.get("itemcode", ""),
                 float(item.get("qty") or 0), SITE_CODE, USER, SITE_CODE),
                cn=cn, commit=False)
        if commit:
            cn.commit()
        return 0
    except Exception:
        if own:
            try:
                cn.rollback()
            except Exception:
                pass
        raise
    finally:
        if own:
            cn.close()


def combo_update(code: str, rec: dict, cn=None, commit=True) -> int:
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    own = cn is None
    cn = cn or db.connect()
    try:
        db.execute(
            "UPDATE ComboPackHead SET Name = ?, ComboName = ?, Rate = ?, "
            "Active = ?, ServiceCharge = ?, RestCode = ?, "
            "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE ComboCode = ?",
            (rec["name"], rec.get("comboname", ""),
             float(rec.get("rate") or 0), rec.get("active", "Y"),
             float(rec.get("servicecharge") or 0), rec.get("rest", ""),
             USER, code), cn=cn, commit=False)
        if "items" in rec:
            db.execute("DELETE FROM ComboPackDetail WHERE ComboCode = ?",
                       (code,), cn=cn, commit=False)
            for item in rec["items"]:
                db.execute(
                    "INSERT INTO ComboPackDetail (ComboCode, ItemCode, Qty, "
                    "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
                    "VALUES (?, ?, ?, ?, ?, getdate(), 'A', ?)",
                    (code, item.get("itemcode", ""),
                     float(item.get("qty") or 0), SITE_CODE, USER, SITE_CODE),
                    cn=cn, commit=False)
        if commit:
            cn.commit()
        return 0
    except Exception:
        if own:
            try:
                cn.rollback()
            except Exception:
                pass
        raise
    finally:
        if own:
            cn.close()


def combo_delete(code: str, cn=None, commit=True) -> int:
    own = cn is None
    cn = cn or db.connect()
    try:
        db.execute("DELETE FROM ComboPackDetail WHERE ComboCode = ?",
                   (code,), cn=cn, commit=False)
        r = db.execute("DELETE FROM ComboPackHead WHERE ComboCode = ?",
                       (code,), cn=cn, commit=False)
        if commit:
            cn.commit()
        return r
    except Exception:
        if own:
            try:
                cn.rollback()
            except Exception:
                pass
        raise
    finally:
        if own:
            cn.close()


class _ComboAPI:
    LIMITS = COMBO_LIMITS
    @staticmethod
    def list_all(cn=None): return combo_list(cn)
    @staticmethod
    def get(code, cn=None): return combo_get(code, cn)
    @staticmethod
    def exists(code, cn=None): return combo_exists(code, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True, user="SA"): return combo_insert(rec, cn, commit, user=user)
    @staticmethod
    def update(code, rec, cn=None, commit=True, user="SA"): return combo_update(code, rec, cn, commit)
    @staticmethod
    def delete(code, cn=None, commit=True, user="SA"): return combo_delete(code, cn, commit)

ComboAPI = _ComboAPI()
