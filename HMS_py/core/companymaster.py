"""Company Master CRUD (VB6: 'Company Master' - Main Setup -> Front Office).

Schema: GroupProf table (corporate clients / travel agents).
  Code varchar(8) PK, Name varchar(50), Add1/Add2 varchar(50),
  City varchar(6), Type varchar(7), ConName varchar(35),
  PhoneNo varchar(35), Comments1 varchar(30),
  TravelAgency varchar(8), MarketSeg varchar(5), BusSource varchar(5),
  GroupType varchar(5),
  Site_Code varchar(2), U_Name varchar(10), U_EntDt datetime,
  U_AE varchar(1), LogSite_Code varchar(2).
NOTE: GroupProf has 0 rows in live DB. Table exists but no data.
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
LIMITS = {
    "code": 8, "name": 50, "add1": 50, "add2": 50,
    "city": 6, "type": 7, "contact": 35, "phone": 35,
}
SELECT_COLS = (
    "Code, Name, Add1, Add2, City, Type, ConName, PhoneNo, "
    "Comments1, TravelAgency, MarketSeg, BusSource, GroupType, "
    "U_Name, U_EntDt, U_AE"
)


def _map(r) -> dict:
    try:
        return {
            "code": r.Code, "name": (r.Name or "").strip(),
            "add1": (r.Add1 or "").strip(),
            "add2": (r.Add2 or "").strip(),
            "city": r.City or "",
            "type": r.Type or "",
            "contact": (r.ConName or "").strip(),
            "phone": (r.PhoneNo or "").strip(),
            "comments": (r.Comments1 or "").strip(),
            "travel_agency": r.TravelAgency or "",
            "market_seg": r.MarketSeg or "",
            "bus_source": r.BusSource or "",
            "group_type": r.GroupType or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        c, n, a1, a2, cy, tp, cn2, ph, cm, ta, ms, bs, gt, un, _, uae = r
        return {
            "code": c, "name": (n or "").strip(),
            "add1": (a1 or "").strip(), "add2": (a2 or "").strip(),
            "city": cy or "", "type": tp or "",
            "contact": (cn2 or "").strip(), "phone": (ph or "").strip(),
            "comments": (cm or "").strip(),
            "travel_agency": ta or "", "market_seg": ms or "",
            "bus_source": bs or "", "group_type": gt or "",
            "u_name": un or "", "u_ae": uae or "",
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


def list_all(cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM GroupProf ORDER BY Code", cn=cn)
    return [_map(r) for r in rows]


def get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM GroupProf WHERE Code = ?",
        (code,), cn=cn)
    return _map(rows[0]) if rows else None


def exists(code: str, cn=None) -> bool:
    return bool(db.query(
        "SELECT 1 FROM GroupProf WHERE Code = ?", (code,), cn=cn))


def insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    db.require_absent("GroupProf", "Code", rec["code"], "Company Code")
    return db.execute(
        "INSERT INTO GroupProf (Code, Name, Add1, Add2, City, Type, "
        "ConName, PhoneNo, Comments1, TravelAgency, MarketSeg, "
        "BusSource, GroupType, Site_Code, U_Name, U_EntDt, U_AE, "
        "LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
        "getdate(), 'A', ?)",
        (rec["code"], rec["name"], rec.get("add1", ""),
         rec.get("add2", ""), rec.get("city", ""), rec.get("type", ""),
         rec.get("contact", ""), rec.get("phone", ""),
         rec.get("comments", ""), rec.get("travel_agency", ""),
         rec.get("market_seg", ""), rec.get("bus_source", ""),
         rec.get("group_type", ""), SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def update(code: str, rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    return db.execute(
        "UPDATE GroupProf SET Name = ?, Add1 = ?, Add2 = ?, City = ?, "
        "Type = ?, ConName = ?, PhoneNo = ?, Comments1 = ?, "
        "TravelAgency = ?, MarketSeg = ?, BusSource = ?, GroupType = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec["name"], rec.get("add1", ""), rec.get("add2", ""),
         rec.get("city", ""), rec.get("type", ""),
         rec.get("contact", ""), rec.get("phone", ""),
         rec.get("comments", ""), rec.get("travel_agency", ""),
         rec.get("market_seg", ""), rec.get("bus_source", ""),
         rec.get("group_type", ""), USER, code),
        cn=cn, commit=commit)


def delete(code: str, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM GroupProf WHERE Code = ?", (code,),
        cn=cn, commit=commit)
