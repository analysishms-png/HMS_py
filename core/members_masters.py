"""Members Management Masters (VB6: Main Setup -> Members Mgmt).

Database evidence (live HMS):
- MemCatMast: Member categories - EXISTS (1 row)
  Schema: Code varchar(6) PK, Name varchar(30), ShortName varchar(6),
  Subscription float, Corporate float, ChildAgeLmt smallint,
  FBilling varchar(1), Status varchar(10), MessAcYN varchar(1),
  Surcharge float, Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code
- FacilityMast: Club facilities - EXISTS (0 rows)
  Schema: Code varchar(6) PK, Name varchar(30), ShortName varchar(6),
  ChargeType varchar(10), ChargeUnit varchar(10), AcCode varchar(10),
  TaxStru varchar(6), UnitRate float, ActiveYN varchar(1),
  RoundOff float, ROffType varchar(5), MeterReading varchar(1),
  SACCode varchar(20), Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code

NOTE: MemberMast/Member table does NOT exist - members managed via
GuestProf in this installation (single-site HMS with no active membership
module). MemberCategory = MemCatMast. CorporateMember = CompanyMast.
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()


def _f(v, default: float = 0.0) -> float:
    try:
        if v in (None, ""):
            return default
        return float(v)
    except (TypeError, ValueError):
        return default


def _i(v, default: int = 0) -> int:
    try:
        if v in (None, ""):
            return default
        return int(float(v))
    except (TypeError, ValueError):
        return default


# ============================================================
# Member Category Master (MemCatMast)
# ============================================================
MEMCAT_LIMITS = {"code": 6, "name": 30, "short": 6, "status": 10}
MEMCAT_COLS = ("Code, Name, ShortName, Subscription, Corporate, "
               "ChildAgeLmt, FBilling, Status, MessAcYN, Surcharge, "
               "U_Name, U_EntDt, U_AE")


def _map_memcat(r) -> dict:
    try:
        return {"code": r.Code, "name": (r.Name or "").strip(),
                "short": (r.ShortName or "").strip(),
                "subscription": _f(r.Subscription),
                "corporate": _f(r.Corporate),
                "childage": _i(r.ChildAgeLmt),
                "fbilling": r.FBilling or "N",
                "status": r.Status or "",
                "messac": r.MessAcYN or "N",
                "surcharge": _f(r.Surcharge),
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        c, n, sn, sub, corp, ca, fb, st, ma, sur, un, _, uae = r
        return {"code": c, "name": (n or "").strip(),
                "short": (sn or "").strip(),
                "subscription": _f(sub),
                "corporate": _f(corp),
                "childage": _i(ca), "fbilling": fb or "N",
                "status": st or "", "messac": ma or "N",
                "surcharge": _f(sur),
                "u_name": un or "", "u_ae": uae or ""}


def memcat_list(cn=None) -> list[dict]:
    return [_map_memcat(r) for r in db.query(
        f"SELECT {MEMCAT_COLS} FROM MemCatMast ORDER BY Code", cn=cn)]


def memcat_get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {MEMCAT_COLS} FROM MemCatMast WHERE Code = ?", (code,), cn=cn)
    return _map_memcat(rows[0]) if rows else None


def memcat_exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM MemCatMast WHERE Code = ?", (code,), cn=cn))


def memcat_insert(rec: dict, cn=None, commit=True) -> int:
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "INSERT INTO MemCatMast (Code, Name, ShortName, Subscription, "
        "Corporate, ChildAgeLmt, FBilling, Status, MessAcYN, Surcharge, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"], rec.get("short", ""),
         float(rec.get("subscription") or 0),
         float(rec.get("corporate") or 0),
         int(rec.get("childage") or 0),
         rec.get("fbilling", "N"), rec.get("status", ""),
         rec.get("messac", "N"), float(rec.get("surcharge") or 0),
         SITE_CODE, USER, SITE_CODE), cn=cn, commit=commit)


def memcat_update(code: str, rec: dict, cn=None, commit=True) -> int:
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "UPDATE MemCatMast SET Name = ?, ShortName = ?, Subscription = ?, "
        "Corporate = ?, ChildAgeLmt = ?, FBilling = ?, Status = ?, "
        "MessAcYN = ?, Surcharge = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec["name"], rec.get("short", ""),
         float(rec.get("subscription") or 0),
         float(rec.get("corporate") or 0),
         int(rec.get("childage") or 0),
         rec.get("fbilling", "N"), rec.get("status", ""),
         rec.get("messac", "N"), float(rec.get("surcharge") or 0),
         USER, code), cn=cn, commit=commit)


def memcat_delete(code: str, cn=None, commit=True) -> int:
    return db.execute(
        "DELETE FROM MemCatMast WHERE Code = ?", (code,), cn=cn, commit=commit)


class _MemCatAPI:
    LIMITS = MEMCAT_LIMITS
    @staticmethod
    def list_all(cn=None): return memcat_list(cn)
    @staticmethod
    def get(code, cn=None): return memcat_get(code, cn)
    @staticmethod
    def exists(code, cn=None): return memcat_exists(code, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return memcat_insert(rec, cn, commit)
    @staticmethod
    def update(code, rec, cn=None, commit=True): return memcat_update(code, rec, cn, commit)
    @staticmethod
    def delete(code, cn=None, commit=True): return memcat_delete(code, cn, commit)

MemCatAPI = _MemCatAPI()


# ============================================================
# Facility Master (club facilities/amenities)
# ============================================================
FACILITY_LIMITS = {"code": 6, "name": 30, "short": 6,
                   "chargetype": 10, "chargeunit": 10,
                   "accode": 10, "taxstru": 6, "saccode": 20}
FACILITY_COLS = ("Code, Name, ShortName, ChargeType, ChargeUnit, AcCode, "
                 "TaxStru, UnitRate, ActiveYN, RoundOff, SACCode, "
                 "U_Name, U_EntDt, U_AE")


def _map_facility(r) -> dict:
    try:
        return {"code": r.Code, "name": (r.Name or "").strip(),
                "short": (r.ShortName or "").strip(),
                "chargetype": r.ChargeType or "",
                "chargeunit": r.ChargeUnit or "",
                "accode": r.AcCode or "",
                "taxstru": r.TaxStru or "",
                "unitrate": float(r.UnitRate or 0),
                "active": r.ActiveYN or "Y",
                "roundoff": float(r.RoundOff or 0),
                "saccode": (r.SACCode or "").strip(),
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        c, n, sn, ct, cu, ac, ts, ur, act, ro, sac, un, _, uae = r
        return {"code": c, "name": (n or "").strip(),
                "short": (sn or "").strip(),
                "chargetype": ct or "", "chargeunit": cu or "",
                "accode": ac or "", "taxstru": ts or "",
                "unitrate": float(ur or 0), "active": act or "Y",
                "roundoff": float(ro or 0), "saccode": (sac or "").strip(),
                "u_name": un or "", "u_ae": uae or ""}


def facility_list(cn=None) -> list[dict]:
    return [_map_facility(r) for r in db.query(
        f"SELECT {FACILITY_COLS} FROM FacilityMast ORDER BY Code", cn=cn)]


def facility_get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {FACILITY_COLS} FROM FacilityMast WHERE Code = ?", (code,), cn=cn)
    return _map_facility(rows[0]) if rows else None


def facility_exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM FacilityMast WHERE Code = ?", (code,), cn=cn))


def facility_insert(rec: dict, cn=None, commit=True) -> int:
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "INSERT INTO FacilityMast (Code, Name, ShortName, ChargeType, "
        "ChargeUnit, AcCode, TaxStru, UnitRate, ActiveYN, RoundOff, "
        "SACCode, Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"], rec.get("short", ""),
         rec.get("chargetype", ""), rec.get("chargeunit", ""),
         rec.get("accode", ""), rec.get("taxstru", ""),
         float(rec.get("unitrate") or 0), rec.get("active", "Y"),
         float(rec.get("roundoff") or 0), rec.get("saccode", ""),
         SITE_CODE, USER, SITE_CODE), cn=cn, commit=commit)


def facility_update(code: str, rec: dict, cn=None, commit=True) -> int:
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "UPDATE FacilityMast SET Name = ?, ShortName = ?, ChargeType = ?, "
        "ChargeUnit = ?, AcCode = ?, TaxStru = ?, UnitRate = ?, "
        "ActiveYN = ?, RoundOff = ?, SACCode = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec["name"], rec.get("short", ""), rec.get("chargetype", ""),
         rec.get("chargeunit", ""), rec.get("accode", ""),
         rec.get("taxstru", ""), float(rec.get("unitrate") or 0),
         rec.get("active", "Y"), float(rec.get("roundoff") or 0),
         rec.get("saccode", ""), USER, code), cn=cn, commit=commit)


def facility_delete(code: str, cn=None, commit=True) -> int:
    return db.execute(
        "DELETE FROM FacilityMast WHERE Code = ?", (code,), cn=cn, commit=commit)


class _FacilityAPI:
    LIMITS = FACILITY_LIMITS
    @staticmethod
    def list_all(cn=None): return facility_list(cn)
    @staticmethod
    def get(code, cn=None): return facility_get(code, cn)
    @staticmethod
    def exists(code, cn=None): return facility_exists(code, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return facility_insert(rec, cn, commit)
    @staticmethod
    def update(code, rec, cn=None, commit=True): return facility_update(code, rec, cn, commit)
    @staticmethod
    def delete(code, cn=None, commit=True): return facility_delete(code, cn, commit)

FacilityAPI = _FacilityAPI()


# ============================================================
# Membership Revenue Master
# Table: MembershipRevMast - Code varchar PK, Description varchar,
#   AcountYN, ACPosting, TaxStru, SubsDetails, RefundableYN,
#   SubsChargeYN, AcCode, Status, audit cols
# ============================================================
MEMREV_LIMITS = {"code": 6, "desc": 50, "taxstru": 6, "accode": 10, "status": 10}
MEMREV_COLS = ("Code, Description, AcountYN, ACPosting, TaxStru, "
               "SubsDetails, RefundableYN, SubsChargeYN, AcCode, Status, "
               "U_Name, U_EntDt, U_AE")


def _map_memrev(r) -> dict:
    try:
        return {"code": r.Code, "desc": (r.Description or "").strip(),
                "acountyn": r.AcountYN or "N",
                "acposting": r.ACPosting or "",
                "taxstru": r.TaxStru or "",
                "subsdetails": (r.SubsDetails or "").strip(),
                "refundableyn": r.RefundableYN or "N",
                "subschargeyn": r.SubsChargeYN or "N",
                "accode": r.AcCode or "",
                "status": r.Status or "",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        c, d, ay, ap, ts, sd, ry, sy, ac, st, un, _, uae = r
        return {"code": c, "desc": (d or "").strip(),
                "acountyn": ay or "N", "acposting": ap or "",
                "taxstru": ts or "", "subsdetails": (sd or "").strip(),
                "refundableyn": ry or "N", "subschargeyn": sy or "N",
                "accode": ac or "", "status": st or "",
                "u_name": un or "", "u_ae": uae or ""}


def memrev_list(cn=None) -> list[dict]:
    return [_map_memrev(r) for r in db.query(
        f"SELECT {MEMREV_COLS} FROM MembershipRevMast ORDER BY Code", cn=cn)]


def memrev_get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {MEMREV_COLS} FROM MembershipRevMast WHERE Code = ?",
        (code,), cn=cn)
    return _map_memrev(rows[0]) if rows else None


def memrev_exists(code: str, cn=None) -> bool:
    return bool(db.query(
        "SELECT 1 FROM MembershipRevMast WHERE Code = ?", (code,), cn=cn))


def memrev_insert(rec: dict, cn=None, commit=True) -> int:
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if not rec.get("desc", "").strip():
        raise ValueError("Description zaroori hai")
    return db.execute(
        "INSERT INTO MembershipRevMast (Code, Description, AcountYN, "
        "ACPosting, TaxStru, SubsDetails, RefundableYN, SubsChargeYN, "
        "AcCode, Status, Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["desc"], rec.get("acountyn", "N"),
         rec.get("acposting", ""), rec.get("taxstru", ""),
         rec.get("subsdetails", ""), rec.get("refundableyn", "N"),
         rec.get("subschargeyn", "N"), rec.get("accode", ""),
         rec.get("status", ""), SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def memrev_update(code: str, rec: dict, cn=None, commit=True) -> int:
    if not rec.get("desc", "").strip():
        raise ValueError("Description zaroori hai")
    return db.execute(
        "UPDATE MembershipRevMast SET Description = ?, AcountYN = ?, "
        "ACPosting = ?, TaxStru = ?, SubsDetails = ?, RefundableYN = ?, "
        "SubsChargeYN = ?, AcCode = ?, Status = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec["desc"], rec.get("acountyn", "N"), rec.get("acposting", ""),
         rec.get("taxstru", ""), rec.get("subsdetails", ""),
         rec.get("refundableyn", "N"), rec.get("subschargeyn", "N"),
         rec.get("accode", ""), rec.get("status", ""),
         USER, code), cn=cn, commit=commit)


def memrev_delete(code: str, cn=None, commit=True) -> int:
    return db.execute(
        "DELETE FROM MembershipRevMast WHERE Code = ?", (code,),
        cn=cn, commit=commit)


class _MemRevAPI:
    LIMITS = MEMREV_LIMITS
    @staticmethod
    def list_all(cn=None): return memrev_list(cn)
    @staticmethod
    def get(code, cn=None): return memrev_get(code, cn)
    @staticmethod
    def exists(code, cn=None): return memrev_exists(code, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return memrev_insert(rec, cn, commit)
    @staticmethod
    def update(code, rec, cn=None, commit=True): return memrev_update(code, rec, cn, commit)
    @staticmethod
    def delete(code, cn=None, commit=True): return memrev_delete(code, cn, commit)

MemRevAPI = _MemRevAPI()
