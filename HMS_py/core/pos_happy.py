"""POS Happy Hours / Promotions - HappyHours/HappyHoursHead/SchemeItemDetail/FreeItemDetail CRUD.

Tables verified in DB KailashData2526:
  HappyHours       - happy hour pricing (SchemeCode+RestCode+ItemCode, DiscountType/Value)
  HappyHoursHead   - happy hour header (SchemeCode+ItemCat+RestCode)
  SchemeItemDetail - scheme items (Code+SNo, ItemCode, Qty, Rate)
  FreeItemDetail   - free items (Code+SNo, FreeItem, FreeQty)
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()


# ============================================================
# HappyHours - Happy Hour Pricing
# ============================================================
_HAPPYHOURS_COLS = (
    "SchemeCode, RestCode, ItemCode, AppDate, DiscountType, DiscountValue, "
    "U_Name, U_EntDt, U_AE, Site_Code, LogSite_Code, FromTime, ToTime, "
    "Active, EndDate"
)


def _map_happyhours(r) -> dict:
    try:
        return {
            "schemecode": r.SchemeCode or "", "restcode": r.RestCode or "",
            "itemcode": r.ItemCode or "", "appdate": r.AppDate,
            "discounttype": r.DiscountType or "",
            "discountvalue": float(r.DiscountValue or 0),
            "fromtime": r.FromTime or "", "totime": r.ToTime or "",
            "active": r.Active or "Y", "enddate": r.EndDate,
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        vals = list(r)
        return {
            "schemecode": vals[0] or "", "restcode": vals[1] or "",
            "itemcode": vals[2] or "", "appdate": vals[3],
            "discounttype": vals[4] or "",
            "discountvalue": float(vals[5] or 0),
            "fromtime": vals[11] if len(vals) > 11 else "",
            "totime": vals[12] if len(vals) > 12 else "",
            "active": vals[13] if len(vals) > 13 else "Y",
            "enddate": vals[14] if len(vals) > 14 else None,
            "u_name": vals[6] or "", "u_ae": vals[8] or "",
        }


def _validate_happyhours(rec: dict):
    if not rec.get("schemecode", "").strip():
        raise ValueError("SchemeCode zaroori hai")
    if not rec.get("itemcode", "").strip():
        raise ValueError("ItemCode zaroori hai")


def happyhours_list(cn=None, limit: int = 500) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} {_HAPPYHOURS_COLS} FROM HappyHours ORDER BY SchemeCode",
        cn=cn)
    return [_map_happyhours(r) for r in rows]


def happyhours_list_by_scheme(schemecode: str, cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {_HAPPYHOURS_COLS} FROM HappyHours WHERE SchemeCode = ? ORDER BY ItemCode",
        (schemecode,), cn=cn)
    return [_map_happyhours(r) for r in rows]


def happyhours_get(schemecode: str, restcode: str, itemcode: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {_HAPPYHOURS_COLS} FROM HappyHours "
        "WHERE SchemeCode = ? AND RestCode = ? AND ItemCode = ?",
        (schemecode, restcode, itemcode), cn=cn)
    return _map_happyhours(rows[0]) if rows else None


def happyhours_insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate_happyhours(rec)
    return db.execute(
        "INSERT INTO HappyHours (SchemeCode, RestCode, ItemCode, AppDate, "
        "DiscountType, DiscountValue, U_Name, U_EntDt, U_AE, Site_Code, "
        "LogSite_Code, FromTime, ToTime, Active, EndDate) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?, ?, ?, ?, ?, ?)",
        (rec["schemecode"], rec["restcode"], rec["itemcode"],
         rec.get("appdate"), rec.get("discounttype", ""),
         float(rec.get("discountvalue") or 0), USER, SITE_CODE,
         SITE_CODE, rec.get("fromtime", ""), rec.get("totime", ""),
         rec.get("active", "Y"), rec.get("enddate")),
        cn=cn, commit=commit)


def happyhours_update(schemecode: str, restcode: str, itemcode: str,
                      rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "UPDATE HappyHours SET DiscountType = ?, DiscountValue = ?, "
        "FromTime = ?, ToTime = ?, Active = ?, EndDate = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' "
        "WHERE SchemeCode = ? AND RestCode = ? AND ItemCode = ?",
        (rec.get("discounttype", ""), float(rec.get("discountvalue") or 0),
         rec.get("fromtime", ""), rec.get("totime", ""),
         rec.get("active", "Y"), rec.get("enddate"), USER,
         schemecode, restcode, itemcode),
        cn=cn, commit=commit)


def happyhours_delete(schemecode: str, restcode: str, itemcode: str,
                      cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM HappyHours WHERE SchemeCode = ? AND RestCode = ? AND ItemCode = ?",
        (schemecode, restcode, itemcode), cn=cn, commit=commit)


class _HappyHoursAPI:
    LIMITS = {"schemecode": 6, "restcode": 6, "itemcode": 10}
    @staticmethod
    def list_all(cn=None, limit=500): return happyhours_list(cn, limit)
    @staticmethod
    def list_by_scheme(schemecode, cn=None): return happyhours_list_by_scheme(schemecode, cn)
    @staticmethod
    def get(schemecode, restcode, itemcode, cn=None): return happyhours_get(schemecode, restcode, itemcode, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return happyhours_insert(rec, cn, commit)
    @staticmethod
    def update(schemecode, restcode, itemcode, rec, cn=None, commit=True): return happyhours_update(schemecode, restcode, itemcode, rec, cn, commit)
    @staticmethod
    def delete(schemecode, restcode, itemcode, cn=None, commit=True): return happyhours_delete(schemecode, restcode, itemcode, cn, commit)

HappyHoursAPI = _HappyHoursAPI()


# ============================================================
# HappyHoursHead - Happy Hour Header
# ============================================================
_HAPPYHOURSHEAD_COLS = (
    "SchemeCode, ItemCat, ItemGroup, RestCode, AppDate, FromTime, ToTime, "
    "U_Name, U_AE, Site_Code, LogSite_Code, DiscountType, DiscountValue, "
    "U_EntDt, EndDate"
)


def _map_happyhourshead(r) -> dict:
    try:
        return {
            "schemecode": r.SchemeCode or "", "itemcat": r.ItemCat or "",
            "itemgroup": r.ItemGroup or "", "restcode": r.RestCode or "",
            "appdate": r.AppDate, "fromtime": r.FromTime or "",
            "totime": r.ToTime or "",
            "discounttype": r.DiscountType or "",
            "discountvalue": float(r.DiscountValue or 0),
            "enddate": r.EndDate,
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        vals = list(r)
        return {
            "schemecode": vals[0] or "", "itemcat": vals[1] or "",
            "itemgroup": vals[2] or "", "restcode": vals[3] or "",
            "appdate": vals[4], "fromtime": vals[5] or "",
            "totime": vals[6] or "",
            "discounttype": vals[11] if len(vals) > 11 else "",
            "discountvalue": float(vals[12] if len(vals) > 12 else 0),
            "enddate": vals[14] if len(vals) > 14 else None,
            "u_name": vals[7] or "", "u_ae": vals[8] or "",
        }


def _validate_head(rec: dict):
    if not rec.get("schemecode", "").strip():
        raise ValueError("SchemeCode zaroori hai")


def happyhourshead_list(cn=None, limit: int = 500) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} {_HAPPYHOURSHEAD_COLS} FROM HappyHoursHead ORDER BY SchemeCode",
        cn=cn)
    return [_map_happyhourshead(r) for r in rows]


def happyhourshead_get(schemecode: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {_HAPPYHOURSHEAD_COLS} FROM HappyHoursHead WHERE SchemeCode = ?",
        (schemecode,), cn=cn)
    return _map_happyhourshead(rows[0]) if rows else None


def happyhourshead_insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate_head(rec)
    return db.execute(
        "INSERT INTO HappyHoursHead (SchemeCode, ItemCat, ItemGroup, RestCode, "
        "AppDate, FromTime, ToTime, U_Name, U_AE, Site_Code, LogSite_Code, "
        "DiscountType, DiscountValue, U_EntDt, EndDate) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), ?)",
        (rec["schemecode"], rec.get("itemcat", ""), rec.get("itemgroup", ""),
         rec.get("restcode", ""), rec.get("appdate"),
         rec.get("fromtime", ""), rec.get("totime", ""),
         USER, "A", SITE_CODE, SITE_CODE,
         rec.get("discounttype", ""), float(rec.get("discountvalue") or 0),
         rec.get("enddate")),
        cn=cn, commit=commit)


def happyhourshead_update(schemecode: str, rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "UPDATE HappyHoursHead SET ItemCat = ?, ItemGroup = ?, RestCode = ?, "
        "FromTime = ?, ToTime = ?, DiscountType = ?, DiscountValue = ?, "
        "EndDate = ?, U_Name = ?, U_EntDt = getdate(), U_AE = 'E' "
        "WHERE SchemeCode = ?",
        (rec.get("itemcat", ""), rec.get("itemgroup", ""),
         rec.get("restcode", ""), rec.get("fromtime", ""),
         rec.get("totime", ""), rec.get("discounttype", ""),
         float(rec.get("discountvalue") or 0), rec.get("enddate"),
         USER, schemecode),
        cn=cn, commit=commit)


def happyhourshead_delete(schemecode: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM HappyHoursHead WHERE SchemeCode = ?",
                      (schemecode,), cn=cn, commit=commit)


class _HappyHoursHeadAPI:
    LIMITS = {"schemecode": 6, "itemcat": 6, "itemgroup": 6, "restcode": 6}
    @staticmethod
    def list_all(cn=None, limit=500): return happyhourshead_list(cn, limit)
    @staticmethod
    def get(schemecode, cn=None): return happyhourshead_get(schemecode, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return happyhourshead_insert(rec, cn, commit)
    @staticmethod
    def update(schemecode, rec, cn=None, commit=True): return happyhourshead_update(schemecode, rec, cn, commit)
    @staticmethod
    def delete(schemecode, cn=None, commit=True): return happyhourshead_delete(schemecode, cn, commit)

HappyHoursHeadAPI = _HappyHoursHeadAPI()


# ============================================================
# SchemeItemDetail - Scheme Items
# ============================================================
_SCHEMEITEM_COLS = (
    "Code, SNo, SchemeCode, Appdate, Enddate, FromTime, ToTime, RestCode, "
    "ItemCode, Qty, Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code, "
    "Days, Active, Rate"
)


def _map_schemeitem(r) -> dict:
    try:
        return {
            "code": r.Code or "", "sno": int(r.SNo or 0),
            "schemecode": r.SchemeCode or "", "appdate": r.Appdate,
            "enddate": r.Enddate, "fromtime": r.FromTime or "",
            "totime": r.ToTime or "", "restcode": r.RestCode or "",
            "itemcode": r.ItemCode or "", "qty": float(r.Qty or 0),
            "days": r.Days or "", "active": r.Active or "Y",
            "rate": float(r.Rate or 0),
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        vals = list(r)
        return {
            "code": vals[0] or "", "sno": int(vals[1] or 0),
            "schemecode": vals[2] or "", "appdate": vals[3],
            "enddate": vals[4], "fromtime": vals[5] or "",
            "totime": vals[6] or "", "restcode": vals[7] or "",
            "itemcode": vals[8] or "", "qty": float(vals[9] or 0),
            "days": vals[15] if len(vals) > 15 else "",
            "active": vals[16] if len(vals) > 16 else "Y",
            "rate": float(vals[17] if len(vals) > 17 else 0),
            "u_name": vals[11] or "", "u_ae": vals[13] or "",
        }


def _validate_schemeitem(rec: dict):
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if not rec.get("itemcode", "").strip():
        raise ValueError("ItemCode zaroori hai")


def schemeitem_list(cn=None, limit: int = 500) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} {_SCHEMEITEM_COLS} FROM SchemeItemDetail ORDER BY Code",
        cn=cn)
    return [_map_schemeitem(r) for r in rows]


def schemeitem_list_by_code(code: str, cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {_SCHEMEITEM_COLS} FROM SchemeItemDetail WHERE Code = ? ORDER BY SNo",
        (code,), cn=cn)
    return [_map_schemeitem(r) for r in rows]


def schemeitem_get(code: str, sno: int, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {_SCHEMEITEM_COLS} FROM SchemeItemDetail WHERE Code = ? AND SNo = ?",
        (code, sno), cn=cn)
    return _map_schemeitem(rows[0]) if rows else None


def schemeitem_insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate_schemeitem(rec)
    return db.execute(
        "INSERT INTO SchemeItemDetail (Code, SNo, SchemeCode, Appdate, "
        "Enddate, FromTime, ToTime, RestCode, ItemCode, Qty, Site_Code, "
        "U_Name, U_EntDt, U_AE, LogSite_Code, Days, Active, Rate) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?, "
        "?, ?, ?)",
        (rec["code"], int(rec.get("sno") or 0), rec.get("schemecode", ""),
         rec.get("appdate"), rec.get("enddate"),
         rec.get("fromtime", ""), rec.get("totime", ""),
         rec.get("restcode", ""), rec.get("itemcode", ""),
         float(rec.get("qty") or 0), SITE_CODE, USER, SITE_CODE,
         rec.get("days", ""), rec.get("active", "Y"),
         float(rec.get("rate") or 0)),
        cn=cn, commit=commit)


def schemeitem_delete(code: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM SchemeItemDetail WHERE Code = ?", (code,),
                      cn=cn, commit=commit)


class _SchemeItemDetailAPI:
    LIMITS = {"code": 6, "schemecode": 6, "itemcode": 10}
    @staticmethod
    def list_all(cn=None, limit=500): return schemeitem_list(cn, limit)
    @staticmethod
    def list_by_code(code, cn=None): return schemeitem_list_by_code(code, cn)
    @staticmethod
    def get(code, sno, cn=None): return schemeitem_get(code, sno, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return schemeitem_insert(rec, cn, commit)
    @staticmethod
    def delete(code, cn=None, commit=True): return schemeitem_delete(code, cn, commit)

SchemeItemDetailAPI = _SchemeItemDetailAPI()


# ============================================================
# FreeItemDetail - Free Items
# ============================================================
_FREEITEM_COLS = (
    "Code, SNo, SchemeCode, RestCode, FreeItem, FreeQty, "
    "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code"
)


def _map_freeitem(r) -> dict:
    try:
        return {
            "code": r.Code or "", "sno": int(r.SNo or 0),
            "schemecode": r.SchemeCode or "", "restcode": r.RestCode or "",
            "freeitem": r.FreeItem or "", "freeqty": float(r.FreeQty or 0),
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        vals = list(r)
        return {
            "code": vals[0] or "", "sno": int(vals[1] or 0),
            "schemecode": vals[2] or "", "restcode": vals[3] or "",
            "freeitem": vals[4] or "", "freeqty": float(vals[5] or 0),
            "u_name": vals[7] or "", "u_ae": vals[9] or "",
        }


def _validate_freeitem(rec: dict):
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if not rec.get("freeitem", "").strip():
        raise ValueError("FreeItem zaroori hai")


def freeitem_list(cn=None, limit: int = 500) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} {_FREEITEM_COLS} FROM FreeItemDetail ORDER BY Code",
        cn=cn)
    return [_map_freeitem(r) for r in rows]


def freeitem_list_by_code(code: str, cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {_FREEITEM_COLS} FROM FreeItemDetail WHERE Code = ? ORDER BY SNo",
        (code,), cn=cn)
    return [_map_freeitem(r) for r in rows]


def freeitem_get(code: str, sno: int, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {_FREEITEM_COLS} FROM FreeItemDetail WHERE Code = ? AND SNo = ?",
        (code, sno), cn=cn)
    return _map_freeitem(rows[0]) if rows else None


def freeitem_insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate_freeitem(rec)
    return db.execute(
        "INSERT INTO FreeItemDetail (Code, SNo, SchemeCode, RestCode, "
        "FreeItem, FreeQty, Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], int(rec.get("sno") or 0), rec.get("schemecode", ""),
         rec.get("restcode", ""), rec["freeitem"],
         float(rec.get("freeqty") or 0), SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def freeitem_delete(code: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM FreeItemDetail WHERE Code = ?", (code,),
                      cn=cn, commit=commit)


class _FreeItemDetailAPI:
    LIMITS = {"code": 6, "schemecode": 6, "freeitem": 10}
    @staticmethod
    def list_all(cn=None, limit=500): return freeitem_list(cn, limit)
    @staticmethod
    def list_by_code(code, cn=None): return freeitem_list_by_code(code, cn)
    @staticmethod
    def get(code, sno, cn=None): return freeitem_get(code, sno, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return freeitem_insert(rec, cn, commit)
    @staticmethod
    def delete(code, cn=None, commit=True): return freeitem_delete(code, cn, commit)

FreeItemDetailAPI = _FreeItemDetailAPI()
