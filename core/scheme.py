"""Scheme + Happy Hours masters (VB6 POSMAST index-9/10/11 port).

EVIDENCE:
- HMS.bas:133A790-1002: POSMAST index 9 -> SchemeMast form; 10/11 ->
  pHappyHours/NewHappyHours.
- Live schemas:
  SchemeMast: Code(6) PK-ish, Name(50), Startdate, Enddate, FromTime(5),
              ToTime(5), Days(4), Active(1) + audit cols.
  SchemeItemDetail: (sample-verified: Code/Sno/ItemCode/DiscountType/DiscountValue)
  HappyHoursHead: SchemeCode(6), ItemCat(6), ItemGroup(6), RestCode(6),
              AppDate, FromTime(5), ToTime(5), DiscountType(10) + audit.
  HappyHours: SchemeCode(6), RestCode(6), ItemCode(8), AppDate,
              DiscountType(10), DiscountValue(8), FromTime(5), ToTime(5)+audit.
All READ-heavy; writes go through _validate + require_absent-style guards.
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
LIMITS = {"code": 6, "name": 50, "time": 5, "days": 4, "active": 1,
          "discounttype": 10}


# ---------------------------------------------------------------- SchemeMast
def _v_date(s: str, label: str):
    import datetime
    s = (s or "").strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"{label} invalid date ({s})")


def _v_time(s: str, label: str) -> str:
    import datetime
    s = (s or "").strip()
    if not s:
        return ""
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.datetime.strptime(s, fmt).strftime("%H:%M")
        except ValueError:
            continue
    raise ValueError(f"{label} invalid time ({s})")


def scheme_validate(rec: dict):
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if len(rec["code"]) > LIMITS["code"]:
        raise ValueError(f"Code max {LIMITS['code']}")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    if len(rec["name"]) > LIMITS["name"]:
        raise ValueError(f"Name max {LIMITS['name']}")
    _v_date(rec.get("startdate"), "Startdate")
    _v_date(rec.get("enddate"), "Enddate")
    _v_time(rec.get("fromtime"), "FromTime")
    _v_time(rec.get("totime"), "ToTime")


SCHEME_COLS = ("Code, Name, Startdate, Enddate, FromTime, ToTime, Days, "
               "Active, U_Name, U_EntDt, U_AE")


def _smap(r) -> dict:
    return {"code": r.Code, "name": r.Name or "",
            "startdate": (r.Startdate.isoformat() if r.Startdate else ""),
            "enddate": (r.Enddate.isoformat() if r.Enddate else ""),
            "fromtime": (r.FromTime or "").strip()[:5] if r.FromTime else "",
            "totime": (r.ToTime or "").strip()[:5] if r.ToTime else "",
            "days": str(r.Days) if r.Days is not None else "",
            "active": (r.Active or "").strip() if r.Active else "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}


def scheme_list(cn=None) -> list[dict]:
    rows = db.query(f"SELECT {SCHEME_COLS} FROM SchemeMast ORDER BY Code",
                    cn=cn)
    return [_smap(r) for r in rows]


def scheme_get(code: str, cn=None) -> dict | None:
    rows = db.query(f"SELECT {SCHEME_COLS} FROM SchemeMast WHERE Code = ?",
                    (code,), cn=cn)
    return _smap(rows[0]) if rows else None


def scheme_insert(rec: dict, cn=None, commit: bool = True) -> int:
    scheme_validate(rec)
    db.require_absent("SchemeMast", "Code", rec["code"], "Scheme Code")
    return db.execute(
        "INSERT INTO SchemeMast (Code, Name, Startdate, Enddate, FromTime, "
        "ToTime, Days, Active, Site_Code, U_Name, U_EntDt, U_AE, "
        "LogSite_Code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), "
        "'A', ?)",
        (rec["code"], rec["name"],
         rec.get("startdate") or None, rec.get("enddate") or None,
         rec.get("fromtime", ""), rec.get("totime", ""),
         rec.get("days", ""), rec.get("active", "Y"),
         SITE_CODE, USER, SITE_CODE), cn=cn, commit=commit)


def scheme_update(code: str, rec: dict, cn=None,
                  commit: bool = True) -> int:
    scheme_validate({**rec, "code": code})
    return db.execute(
        "UPDATE SchemeMast SET Name = ?, Startdate = ?, Enddate = ?, "
        "FromTime = ?, ToTime = ?, Days = ?, Active = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec["name"], rec.get("startdate") or None,
         rec.get("enddate") or None, rec.get("fromtime", ""),
         rec.get("totime", ""), rec.get("days", ""),
         rec.get("active", "Y"), USER, code), cn=cn, commit=commit)


def scheme_delete(code: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM SchemeMast WHERE Code = ?", (code,),
                      cn=cn, commit=commit)


# -------------------------------------------------------- HappyHoursHead
HHH_COLS = ("SchemeCode, ItemCat, ItemGroup, RestCode, AppDate, FromTime, "
            "ToTime, DiscountType, U_Name, U_EntDt, U_AE")


def _hmap(r) -> dict:
    return {"schemecode": r.SchemeCode, "itemcat": r.ItemCat or "",
            "itemgroup": r.ItemGroup or "", "restcode": r.RestCode or "",
            "appdate": (r.AppDate.isoformat() if r.AppDate else ""),
            "fromtime": (r.FromTime or "").strip()[:5] if r.FromTime else "",
            "totime": (r.ToTime or "").strip()[:5] if r.ToTime else "",
            "discounttype": r.DiscountType or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}


def happyhead_list(cn=None, schemecode: str = "") -> list[dict]:
    if schemecode:
        rows = db.query(f"SELECT {HHH_COLS} FROM HappyHoursHead "
                        "WHERE SchemeCode = ? ORDER BY AppDate",
                        (schemecode,), cn=cn)
    else:
        rows = db.query(f"SELECT {HHH_COLS} FROM HappyHoursHead "
                        "ORDER BY AppDate", cn=cn)
    return [_hmap(r) for r in rows]


def happyhead_insert(rec: dict, cn=None, commit: bool = True) -> int:
    if not rec.get("schemecode", "").strip():
        raise ValueError("SchemeCode zaroori hai")
    _v_time(rec.get("fromtime"), "FromTime")
    _v_time(rec.get("totime"), "ToTime")
    if len(rec.get("discounttype", "")) > LIMITS["discounttype"]:
        raise ValueError("DiscountType max 10")
    return db.execute(
        "INSERT INTO HappyHoursHead (SchemeCode, ItemCat, ItemGroup, "
        "RestCode, AppDate, FromTime, ToTime, DiscountType, Site_Code, "
        "U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["schemecode"], rec.get("itemcat", ""),
         rec.get("itemgroup", ""), rec.get("restcode", ""),
         rec.get("appdate") or None, rec.get("fromtime", ""),
         rec.get("totime", ""), rec.get("discounttype", ""),
         SITE_CODE, USER, SITE_CODE), cn=cn, commit=commit)


def happyhead_delete(schemecode: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM HappyHoursHead WHERE SchemeCode = ?",
                      (schemecode,), cn=cn, commit=commit)


# ------------------------------------------------------------- HappyHours
HH_COLS = ("SchemeCode, RestCode, ItemCode, AppDate, DiscountType, "
           "DiscountValue, FromTime, ToTime, U_Name, U_EntDt, U_AE")


def _hhmap(r) -> dict:
    return {"schemecode": r.SchemeCode, "restcode": r.RestCode or "",
            "itemcode": r.ItemCode or "",
            "appdate": (r.AppDate.isoformat() if r.AppDate else ""),
            "discounttype": r.DiscountType or "",
            "discountvalue": r.DiscountValue or 0.0,
            "fromtime": (r.FromTime or "").strip()[:5] if r.FromTime else "",
            "totime": (r.ToTime or "").strip()[:5] if r.ToTime else "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}


def happyhours_list(cn=None, schemecode: str = "") -> list[dict]:
    if schemecode:
        rows = db.query(f"SELECT {HH_COLS} FROM HappyHours "
                        "WHERE SchemeCode = ? ORDER BY AppDate, ItemCode",
                        (schemecode,), cn=cn)
    else:
        rows = db.query(f"SELECT {HH_COLS} FROM HappyHours "
                        "ORDER BY AppDate, ItemCode", cn=cn)
    return [_hhmap(r) for r in rows]


def happyhours_insert(rec: dict, cn=None, commit: bool = True) -> int:
    if not rec.get("schemecode", "").strip():
        raise ValueError("SchemeCode zaroori hai")
    if not rec.get("itemcode", "").strip():
        raise ValueError("ItemCode zaroori hai")
    _v_time(rec.get("fromtime"), "FromTime")
    _v_time(rec.get("totime"), "ToTime")
    return db.execute(
        "INSERT INTO HappyHours (SchemeCode, RestCode, ItemCode, AppDate, "
        "DiscountType, DiscountValue, FromTime, ToTime, Site_Code, "
        "U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["schemecode"], rec.get("restcode", ""), rec["itemcode"],
         rec.get("appdate") or None, rec.get("discounttype", ""),
         float(rec.get("discountvalue") or 0), rec.get("fromtime", ""),
         rec.get("totime", ""), SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def happyhours_delete(schemecode: str, cn=None,
                      commit: bool = True) -> int:
    return db.execute("DELETE FROM HappyHours WHERE SchemeCode = ?",
                      (schemecode,), cn=cn, commit=commit)
