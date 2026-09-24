"""Banquet Setup Masters (VB6: Main Setup -> Banquet / Hall).

Database evidence (live HMS):
- VenueMast: already ported in venue.py (Venue Master)
- VenueFeatures: EXISTS - venue code + feature tags
  Schema: VenueCode varchar(5) FK->VenueMast, Feature varchar(50),
  Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code
  NOTE: PK = (VenueCode, Feature) composite
- CatalogMast: EXISTS - banquet item catalog
  Schema: Code varchar(6) PK, ItemCode varchar(8) FK->ItemMast,
  RestCode varchar(6) FK->Depart, Name varchar(50),
  ItemCatCode varchar(6), Category varchar(30),
  Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code
- GroupProf: EXISTS - group profile (used by Banquet + Reservation)
  Schema: Code varchar(6) PK, Name varchar(50), Add1/Add2 varchar(50),
  City varchar(6), Type varchar(7), ConName varchar(40), PhoneNo varchar(35),
  Comments1/2/3 varchar(100), TravelAgency varchar(50),
  MarketSeg varchar(6), BusSource varchar(6), GroupType varchar(20),
  Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code

NOTE: EventsMast/BanquetMenuCategory/BanquetItemGroup/BanquetMenuItem
do NOT exist in this database (VB6 banquet transactions used existing
VenueMast + CatalogMast + Depart + ItemMast combination).
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()


# ============================================================
# Venue Features (banquet hall amenities)
# ============================================================
VENFEATURE_LIMITS = {"venue": 5, "feature": 50}
VENFEATURE_COLS = "VenueCode, Feature, U_Name, U_EntDt, U_AE"


def _map_venfeature(r) -> dict:
    try:
        return {"venue": r.VenueCode or "", "feature": (r.Feature or "").strip(),
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        vc, ft, un, _, uae = r
        return {"venue": vc or "", "feature": (ft or "").strip(),
                "u_name": un or "", "u_ae": uae or ""}


def venfeature_list(cn=None, venue_code: str = "") -> list[dict]:
    if venue_code:
        rows = db.query(
            f"SELECT {VENFEATURE_COLS} FROM VenueFeatures WHERE VenueCode = ? "
            "ORDER BY Feature", (venue_code,), cn=cn)
    else:
        rows = db.query(
            f"SELECT {VENFEATURE_COLS} FROM VenueFeatures ORDER BY VenueCode, Feature",
            cn=cn)
    return [_map_venfeature(r) for r in rows]


def venfeature_list_all(cn=None) -> list[dict]:
    """BaseMasterForm compatible - returns all with composite key as 'code'."""
    rows = db.query(
        "SELECT VenueCode, Feature, U_Name, U_EntDt, U_AE "
        "FROM VenueFeatures ORDER BY VenueCode, Feature", cn=cn)
    out = []
    for r in rows:
        d = _map_venfeature(r)
        d["code"] = f"{d['venue']}|{d['feature']}"  # composite PK display
        d["name"] = d["feature"]
        out.append(d)
    return out


def venfeature_exists_row(venue: str, feature: str, cn=None) -> bool:
    return bool(db.query(
        "SELECT 1 FROM VenueFeatures WHERE VenueCode = ? AND Feature = ?",
        (venue, feature), cn=cn))


def venfeature_insert(rec: dict, cn=None, commit=True) -> int:
    venue = rec.get("venue", "").strip()
    feature = rec.get("feature", "").strip() or rec.get("name", "").strip()
    if not venue:
        raise ValueError("VenueCode zaroori hai")
    if not feature:
        raise ValueError("Feature zaroori hai")
    if venfeature_exists_row(venue, feature, cn=cn):
        raise ValueError(f"'{venue} - {feature}' pehle se hai")
    return db.execute(
        "INSERT INTO VenueFeatures (VenueCode, Feature, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, getdate(), 'A', ?)",
        (venue, feature, SITE_CODE, USER, SITE_CODE), cn=cn, commit=commit)


def venfeature_delete_row(venue: str, feature: str, cn=None, commit=True) -> int:
    return db.execute(
        "DELETE FROM VenueFeatures WHERE VenueCode = ? AND Feature = ?",
        (venue, feature), cn=cn, commit=commit)


# BaseMasterForm-compatible wrapper for VenueFeatures
class _VenFeatureAPI:
    LIMITS = VENFEATURE_LIMITS
    pk_key = "code"

    @staticmethod
    def list_all(cn=None): return venfeature_list_all(cn)

    @staticmethod
    def get(code: str, cn=None) -> dict | None:
        """code = 'VENUE|FEATURE' composite."""
        parts = code.split("|", 1)
        if len(parts) != 2:
            return None
        rows = db.query(
            "SELECT VenueCode, Feature, U_Name, U_EntDt, U_AE "
            "FROM VenueFeatures WHERE VenueCode = ? AND Feature = ?",
            (parts[0], parts[1]), cn=cn)
        if not rows:
            return None
        d = _map_venfeature(rows[0])
        d["code"] = code
        d["name"] = d["feature"]
        return d

    @staticmethod
    def exists(code: str, cn=None) -> bool:
        parts = code.split("|", 1)
        if len(parts) != 2:
            return False
        return venfeature_exists_row(parts[0], parts[1], cn)

    @staticmethod
    def insert(rec: dict, cn=None, commit=True) -> int:
        return venfeature_insert(rec, cn, commit)

    @staticmethod
    def update(code: str, rec: dict, cn=None, commit=True) -> int:
        # Feature update = delete + re-insert
        parts = code.split("|", 1)
        venfeature_delete_row(parts[0], parts[1], cn=cn, commit=False)
        return venfeature_insert(rec, cn=cn, commit=commit)

    @staticmethod
    def delete(code: str, cn=None, commit=True) -> int:
        parts = code.split("|", 1)
        if len(parts) != 2:
            raise ValueError("Invalid composite key")
        return venfeature_delete_row(parts[0], parts[1], cn, commit)

VenFeatureAPI = _VenFeatureAPI()


# ============================================================
# Catalog Master (Banquet item catalog)
# ============================================================
CATALOG_LIMITS = {"code": 6, "name": 50, "itemcode": 8,
                  "rest": 6, "itemcat": 6, "category": 30}
CATALOG_COLS = ("Code, ItemCode, RestCode, Name, ItemCatCode, Category, "
                "U_Name, U_EntDt, U_AE")


def _map_catalog(r) -> dict:
    try:
        return {"code": r.Code, "name": (r.Name or "").strip(),
                "itemcode": r.ItemCode or "", "rest": r.RestCode or "",
                "itemcat": r.ItemCatCode or "", "category": r.Category or "",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        c, ic, rc, n, icc, cat, un, _, uae = r
        return {"code": c, "name": (n or "").strip(),
                "itemcode": ic or "", "rest": rc or "",
                "itemcat": icc or "", "category": cat or "",
                "u_name": un or "", "u_ae": uae or ""}


def catalog_list(cn=None) -> list[dict]:
    return [_map_catalog(r) for r in db.query(
        f"SELECT {CATALOG_COLS} FROM CatalogMast ORDER BY Code", cn=cn)]


def catalog_get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {CATALOG_COLS} FROM CatalogMast WHERE Code = ?", (code,), cn=cn)
    return _map_catalog(rows[0]) if rows else None


def catalog_exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM CatalogMast WHERE Code = ?", (code,), cn=cn))


def catalog_insert(rec: dict, cn=None, commit=True) -> int:
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "INSERT INTO CatalogMast (Code, ItemCode, RestCode, Name, "
        "ItemCatCode, Category, Site_Code, U_Name, U_EntDt, U_AE, "
        "LogSite_Code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec.get("itemcode", ""), rec.get("rest", ""),
         rec["name"], rec.get("itemcat", ""), rec.get("category", ""),
         SITE_CODE, USER, SITE_CODE), cn=cn, commit=commit)


def catalog_update(code: str, rec: dict, cn=None, commit=True) -> int:
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "UPDATE CatalogMast SET ItemCode = ?, RestCode = ?, Name = ?, "
        "ItemCatCode = ?, Category = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec.get("itemcode", ""), rec.get("rest", ""), rec["name"],
         rec.get("itemcat", ""), rec.get("category", ""),
         USER, code), cn=cn, commit=commit)


def catalog_delete(code: str, cn=None, commit=True) -> int:
    return db.execute(
        "DELETE FROM CatalogMast WHERE Code = ?", (code,), cn=cn, commit=commit)


class _CatalogAPI:
    LIMITS = CATALOG_LIMITS
    @staticmethod
    def list_all(cn=None): return catalog_list(cn)
    @staticmethod
    def get(code, cn=None): return catalog_get(code, cn)
    @staticmethod
    def exists(code, cn=None): return catalog_exists(code, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return catalog_insert(rec, cn, commit)
    @staticmethod
    def update(code, rec, cn=None, commit=True): return catalog_update(code, rec, cn, commit)
    @staticmethod
    def delete(code, cn=None, commit=True): return catalog_delete(code, cn, commit)

CatalogAPI = _CatalogAPI()


# ============================================================
# Group Profile (used by Banquet + Reservation groups)
# ============================================================
GROUPPROF_LIMITS = {"code": 6, "name": 50, "add1": 50, "add2": 50,
                    "city": 6, "type": 7, "conname": 40, "phone": 35,
                    "mkt": 6, "bus": 6, "gtype": 20}
GROUPPROF_COLS = ("Code, Name, Add1, Add2, City, Type, ConName, PhoneNo, "
                  "Comments1, TravelAgency, MarketSeg, BusSource, GroupType, "
                  "U_Name, U_EntDt, U_AE")


def _map_groupprof(r) -> dict:
    try:
        return {"code": r.Code, "name": (r.Name or "").strip(),
                "add1": (r.Add1 or "").strip(), "add2": (r.Add2 or "").strip(),
                "city": r.City or "", "type": r.Type or "",
                "conname": (r.ConName or "").strip(),
                "phone": (r.PhoneNo or "").strip(),
                "comments": (r.Comments1 or "").strip(),
                "travel": (r.TravelAgency or "").strip(),
                "mktseg": r.MarketSeg or "", "bussrc": r.BusSource or "",
                "gtype": r.GroupType or "",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        c, n, a1, a2, cy, ty, cn2, ph, com, tra, mkt, bus, gt, un, _, uae = r
        return {"code": c, "name": (n or "").strip(),
                "add1": (a1 or "").strip(), "add2": (a2 or "").strip(),
                "city": cy or "", "type": ty or "",
                "conname": (cn2 or "").strip(), "phone": (ph or "").strip(),
                "comments": (com or "").strip(),
                "travel": (tra or "").strip(),
                "mktseg": mkt or "", "bussrc": bus or "",
                "gtype": gt or "", "u_name": un or "", "u_ae": uae or ""}


def groupprof_list(cn=None, top: int = 300) -> list[dict]:
    return [_map_groupprof(r) for r in db.query(
        f"SELECT TOP {int(top)} {GROUPPROF_COLS} FROM GroupProf ORDER BY Code",
        cn=cn)]


def groupprof_get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {GROUPPROF_COLS} FROM GroupProf WHERE Code = ?", (code,), cn=cn)
    return _map_groupprof(rows[0]) if rows else None


def groupprof_exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM GroupProf WHERE Code = ?", (code,), cn=cn))


def groupprof_insert(rec: dict, cn=None, commit=True) -> int:
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "INSERT INTO GroupProf (Code, Name, Add1, Add2, City, Type, "
        "ConName, PhoneNo, Comments1, TravelAgency, MarketSeg, BusSource, "
        "GroupType, Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"], rec.get("add1", ""), rec.get("add2", ""),
         rec.get("city", ""), rec.get("type", ""), rec.get("conname", ""),
         rec.get("phone", ""), rec.get("comments", ""),
         rec.get("travel", ""), rec.get("mktseg", ""), rec.get("bussrc", ""),
         rec.get("gtype", ""), SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def groupprof_update(code: str, rec: dict, cn=None, commit=True) -> int:
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "UPDATE GroupProf SET Name = ?, Add1 = ?, Add2 = ?, City = ?, "
        "Type = ?, ConName = ?, PhoneNo = ?, Comments1 = ?, "
        "TravelAgency = ?, MarketSeg = ?, BusSource = ?, GroupType = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec["name"], rec.get("add1", ""), rec.get("add2", ""),
         rec.get("city", ""), rec.get("type", ""), rec.get("conname", ""),
         rec.get("phone", ""), rec.get("comments", ""),
         rec.get("travel", ""), rec.get("mktseg", ""), rec.get("bussrc", ""),
         rec.get("gtype", ""), USER, code), cn=cn, commit=commit)


def groupprof_delete(code: str, cn=None, commit=True) -> int:
    if not code.upper().startswith("PYT"):
        raise ValueError("Safety: sirf PYT* test group profiles delete hote hain")
    return db.execute(
        "DELETE FROM GroupProf WHERE Code = ?", (code,), cn=cn, commit=commit)


class _GroupProfAPI:
    LIMITS = GROUPPROF_LIMITS
    @staticmethod
    def list_all(cn=None): return groupprof_list(cn)
    @staticmethod
    def get(code, cn=None): return groupprof_get(code, cn)
    @staticmethod
    def exists(code, cn=None): return groupprof_exists(code, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return groupprof_insert(rec, cn, commit)
    @staticmethod
    def update(code, rec, cn=None, commit=True): return groupprof_update(code, rec, cn, commit)
    @staticmethod
    def delete(code, cn=None, commit=True): return groupprof_delete(code, cn, commit)

GroupProfAPI = _GroupProfAPI()


# ============================================================
# Function Type Master (Events / function types)
# Table: FunctionType - Code varchar PK, Name varchar, Status varchar, audit cols
# ============================================================
FUNCTYPE_LIMITS = {"code": 6, "name": 30, "status": 10}
FUNCTYPE_COLS = "Code, Name, Status, U_Name, U_EntDt, U_AE"


def _map_functype(r) -> dict:
    try:
        return {"code": r.Code, "name": (r.Name or "").strip(),
                "status": r.Status or "",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        c, n, st, un, _, uae = r
        return {"code": c, "name": (n or "").strip(),
                "status": st or "",
                "u_name": un or "", "u_ae": uae or ""}


def functype_list(cn=None) -> list[dict]:
    return [_map_functype(r) for r in db.query(
        f"SELECT {FUNCTYPE_COLS} FROM FunctionType ORDER BY Code", cn=cn)]


def functype_get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {FUNCTYPE_COLS} FROM FunctionType WHERE Code = ?",
        (code,), cn=cn)
    return _map_functype(rows[0]) if rows else None


def functype_exists(code: str, cn=None) -> bool:
    return bool(db.query(
        "SELECT 1 FROM FunctionType WHERE Code = ?", (code,), cn=cn))


def functype_insert(rec: dict, cn=None, commit=True) -> int:
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "INSERT INTO FunctionType (Code, Name, Status, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"], rec.get("status", ""),
         SITE_CODE, USER, SITE_CODE), cn=cn, commit=commit)


def functype_update(code: str, rec: dict, cn=None, commit=True) -> int:
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "UPDATE FunctionType SET Name = ?, Status = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec["name"], rec.get("status", ""), USER, code),
        cn=cn, commit=commit)


def functype_delete(code: str, cn=None, commit=True) -> int:
    return db.execute(
        "DELETE FROM FunctionType WHERE Code = ?", (code,), cn=cn, commit=commit)


class _FuncTypeAPI:
    LIMITS = FUNCTYPE_LIMITS
    @staticmethod
    def list_all(cn=None): return functype_list(cn)
    @staticmethod
    def get(code, cn=None): return functype_get(code, cn)
    @staticmethod
    def exists(code, cn=None): return functype_exists(code, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return functype_insert(rec, cn, commit)
    @staticmethod
    def update(code, rec, cn=None, commit=True): return functype_update(code, rec, cn, commit)
    @staticmethod
    def delete(code, cn=None, commit=True): return functype_delete(code, cn, commit)

FuncTypeAPI = _FuncTypeAPI()
