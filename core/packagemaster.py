"""Package Master CRUD (VB6: 'Package Master' - Main Setup -> Front Office).

Schema evidence (live HMS DB): PlanMast table.
  Code varchar(5) PK, Name varchar(25), Total float,
  Plan_Package varchar(7), PercentApp varchar(3),
  ActiveYN varchar(3), RoomPer numeric, RoomRate numeric,
  PackageAmount numeric, DiscAppYN char(3), DiscAppON char(25),
  Nights smallint, Adults smallint, Childs smallint,
  RRIncTax char(3), RoomCat varchar(6), Tariff varchar(25) NOT NULL,
  RoomTaxStru varchar(6), MapCode varchar(20),
  Site_Code varchar(2), U_Name varchar(10), U_EntDt datetime,
  U_AE varchar(1), LogSite_Code varchar(2), App_Date datetime NOT NULL.
Audit pattern VB6 jaisa: U_Name + U_EntDt(getdate()) + U_AE ('A'/'E').
"""
from __future__ import annotations

import datetime

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
LIMITS = {
    "code": 5, "name": 25, "plan_package": 7,
}
SELECT_COLS = (
    "Code, Name, Total, Plan_Package, PercentApp, ActiveYN, "
    "RoomPer, RoomRate, PackageAmount, DiscAppYN, DiscAppON, "
    "Nights, Adults, Childs, RRIncTax, RoomCat, Tariff, "
    "RoomTaxStru, MapCode, U_Name, U_EntDt, U_AE"
)


def _map(r) -> dict:
    def _dt(v):
        if v is None:
            return None
        if isinstance(v, datetime.datetime):
            return v.date()
        return v
    try:
        return {
            "code": r.Code, "name": (r.Name or "").strip(),
            "total": float(r.Total or 0),
            "plan_package": r.Plan_Package or "",
            "percent_app": r.PercentApp or "",
            "active": r.ActiveYN or "Y",
            "room_per": float(r.RoomPer or 0),
            "room_rate": float(r.RoomRate or 0),
            "pkg_amount": float(r.PackageAmount or 0),
            "disc_yn": r.DiscAppYN or "",
            "disc_on": r.DiscAppON or "",
            "nights": r.Nights or 0,
            "adults": r.Adults or 0,
            "childs": r.Childs or 0,
            "rr_inc_tax": r.RRIncTax or "",
            "room_cat": r.RoomCat or "",
            "tariff": r.Tariff or "",
            "room_tax_stru": r.RoomTaxStru or "",
            "map_code": r.MapCode or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        c, n, tot, pp, pa, act, rp, rr, pa2, dy, do, \
            ni, ad, ch, rit, rc, tf, rts, mc, un, _, uae = r
        return {
            "code": c, "name": (n or "").strip(),
            "total": float(tot or 0), "plan_package": pp or "",
            "percent_app": pa or "", "active": act or "Y",
            "room_per": float(rp or 0), "room_rate": float(rr or 0),
            "pkg_amount": float(pa2 or 0), "disc_yn": dy or "",
            "disc_on": do or "", "nights": ni or 0,
            "adults": ad or 0, "childs": ch or 0,
            "rr_inc_tax": rit or "", "room_cat": rc or "",
            "tariff": tf or "", "room_tax_stru": rts or "",
            "map_code": mc or "", "u_name": un or "", "u_ae": uae or "",
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
    if len(rec.get("plan_package", "")) > LIMITS["plan_package"]:
        raise ValueError(f"Plan_Package max {LIMITS['plan_package']} chars")
    for k in ("total", "room_per", "room_rate", "pkg_amount"):
        try:
            float(rec.get(k) or 0)
        except (ValueError, TypeError):
            raise ValueError(f"{k} numeric hona chahiye")


def list_all(cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM PlanMast WHERE (LOGSITE_CODE = ? OR LOGSITE_CODE = 'HO' OR ISNULL(LOGSITE_CODE,'')='') ORDER BY Code", cn=cn)
    return [_map(r) for r in rows]


def get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM PlanMast WHERE Code = ?",
        (code,), cn=cn)
    return _map(rows[0]) if rows else None


def exists(code: str, cn=None) -> bool:
    return bool(db.query(
        "SELECT 1 FROM PlanMast WHERE Code = ?", (code,), cn=cn))


def insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    db.require_absent("PlanMast", "Code", rec["code"],
              "Package Code")
    return db.execute(
        "INSERT INTO PlanMast (Code, Name, Total, Plan_Package, "
        "PercentApp, ActiveYN, RoomPer, RoomRate, PackageAmount, "
        "DiscAppYN, DiscAppON, Nights, Adults, Childs, RRIncTax, "
        "RoomCat, Tariff, RoomTaxStru, MapCode, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code, App_Date) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
        "?, ?, getdate(), 'A', ?, getdate())",
        (rec["code"], rec["name"], float(rec.get("total") or 0),
         rec.get("plan_package", ""), rec.get("percent_app", ""),
         rec.get("active", "Y"), float(rec.get("room_per") or 0),
         float(rec.get("room_rate") or 0), float(rec.get("pkg_amount") or 0),
         rec.get("disc_yn", ""), rec.get("disc_on", ""),
         int(rec.get("nights") or 0), int(rec.get("adults") or 0),
         int(rec.get("childs") or 0), rec.get("rr_inc_tax", ""),
         rec.get("room_cat", ""), rec.get("tariff", "0"),
         rec.get("room_tax_stru", ""), rec.get("map_code", ""),
         SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def update(code: str, rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    return db.execute(
        "UPDATE PlanMast SET Name = ?, Total = ?, Plan_Package = ?, "
        "PercentApp = ?, ActiveYN = ?, RoomPer = ?, RoomRate = ?, "
        "PackageAmount = ?, DiscAppYN = ?, DiscAppON = ?, "
        "Nights = ?, Adults = ?, Childs = ?, RRIncTax = ?, "
        "RoomCat = ?, Tariff = ?, RoomTaxStru = ?, MapCode = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec["name"], float(rec.get("total") or 0),
         rec.get("plan_package", ""), rec.get("percent_app", ""),
         rec.get("active", "Y"), float(rec.get("room_per") or 0),
         float(rec.get("room_rate") or 0), float(rec.get("pkg_amount") or 0),
         rec.get("disc_yn", ""), rec.get("disc_on", ""),
         int(rec.get("nights") or 0), int(rec.get("adults") or 0),
         int(rec.get("childs") or 0), rec.get("rr_inc_tax", ""),
         rec.get("room_cat", ""), rec.get("tariff", "0"),
         rec.get("room_tax_stru", ""), rec.get("map_code", ""),
         USER, code),
        cn=cn, commit=commit)


def delete(code: str, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM PlanMast WHERE Code = ?", (code,), cn=cn,
        commit=commit)
