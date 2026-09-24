"""TDS Certificate Master CRUD (VB6: FaTDSCertificate.frm - Finance -> TDS Certificate).
Schema evidence (live HMS DB): TDSCerti table - 12 columns.
CertiNo varchar(10) PK, CertiDate datetime, Site_Code varchar(2),
Code varchar(8) FK->TDSCat, FromDate datetime, ToDate datetime,
TDSAmt float, FullName varchar(25), Desig varchar(25),
U_Name varchar(10), U_EntDt datetime, U_AE varchar(1), LogSite_Code varchar(2).
VB6: TDS certificates issued to deductees.
Audit pattern VB6 jaisa: U_Name + U_EntDt(getdate()) + U_AE ('A'/'E')."""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
LIMITS = {"certino": 10, "code": 8, "name": 25, "desig": 25}
SELECT_COLS = (
    "CertiNo, CertiDate, Site_Code, Code, FromDate, ToDate, "
    "TDSAmt, FullName, Desig, U_Name, U_EntDt, U_AE, LogSite_Code"
)


def _map(r) -> dict:
    try:
        return {
            "certino": r.CertiNo or "",
            "certidate": r.CertiDate,
            "site": r.Site_Code or "",
            "code": r.Code or "",
            "fromdate": r.FromDate,
            "todate": r.ToDate,
            "tdsamt": float(r.TDSAmt or 0),
            "fullname": (r.FullName or "").strip(),
            "desig": (r.Desig or "").strip(),
            "uname": r.U_Name or "",
            "u_ae": r.U_AE or "",
        }
    except AttributeError:
        certino, certidate, site, code, fromdate, todate, tdsamt, \
            fullname, desig, un, _, uae, logsite = r
        return {
            "certino": certino or "",
            "certidate": certidate,
            "site": site or "",
            "code": code or "",
            "fromdate": fromdate,
            "todate": todate,
            "tdsamt": float(tdsamt or 0),
            "fullname": (fullname or "").strip(),
            "desig": (desig or "").strip(),
            "uname": un or "",
            "u_ae": uae or "",
        }


def _validate(rec: dict):
    if not rec.get("certino", "").strip():
        raise ValueError("CertiNo zaroori hai")
    if len(rec["certino"]) > LIMITS["certino"]:
        raise ValueError(f"CertiNo max {LIMITS['certino']} chars")
    if not rec.get("code", "").strip():
        raise ValueError("TDSCat Code zaroori hai")
    if len(rec["code"]) > LIMITS["code"]:
        raise ValueError(f"Code max {LIMITS['code']} chars")
    if len(rec.get("fullname", "")) > LIMITS["name"]:
        raise ValueError(f"FullName max {LIMITS['name']} chars")
    if len(rec.get("desig", "")) > LIMITS["desig"]:
        raise ValueError(f"Desig max {LIMITS['desig']} chars")
    try:
        float(rec.get("tdsamt") or 0)
    except (ValueError, TypeError):
        raise ValueError("TDSAmt numeric hona chahiye")


def list_all(cn=None) -> list[dict]:
    rows = db.query(f"SELECT {SELECT_COLS} FROM TDSCerti ORDER BY CertiNo", cn=cn)
    return [_map(r) for r in rows]


def get(certino: str, cn=None) -> dict | None:
    rows = db.query(f"SELECT {SELECT_COLS} FROM TDSCerti WHERE CertiNo = ?", (certino,), cn=cn)
    return _map(rows[0]) if rows else None


def exists(certino: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM TDSCerti WHERE CertiNo = ?", (certino,), cn=cn))


def insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    return db.execute(
        "INSERT INTO TDSCerti (CertiNo, CertiDate, Site_Code, Code, FromDate, "
        "ToDate, TDSAmt, FullName, Desig, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["certino"], rec.get("certidate"),
         SITE_CODE, rec["code"], rec.get("fromdate"), rec.get("todate"),
         float(rec.get("tdsamt") or 0), rec.get("fullname", ""),
         rec.get("desig", ""), USER, SITE_CODE),
        cn=cn, commit=commit)


def update(certino: str, rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    return db.execute(
        "UPDATE TDSCerti SET CertiDate = ?, Code = ?, FromDate = ?, ToDate = ?, "
        "TDSAmt = ?, FullName = ?, Desig = ?, U_Name = ?, U_EntDt = getdate(), "
        "U_AE = 'E' WHERE CertiNo = ?",
        (rec.get("certidate"), rec["code"], rec.get("fromdate"),
         rec.get("todate"), float(rec.get("tdsamt") or 0),
         rec.get("fullname", ""), rec.get("desig", ""), USER, certino),
        cn=cn, commit=commit)


def delete(certino: str, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM TDSCerti WHERE CertiNo = ?", (certino,),
        cn=cn, commit=commit)