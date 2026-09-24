"""Smart Card Registration Master (VB6: Main Setup -> Smart Card).

Database evidence (live HMS):
- SmartCardRegistration: Card registration/issuance
  Schema: Code varchar(6) PK, CardType varchar(10), CardNo varchar(20),
  Name varchar(50), Addr varchar(100), Phone varchar(20),
  CashAmt float, SecurityAmt float, IssDate datetime,
  ValidUpto datetime, BlockedYN varchar(1), CurrBal float,
  SecurBal float, MemberCode varchar(6),
  Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code
"""
from __future__ import annotations

import datetime
from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()


SMARTCARD_LIMITS = {"code": 6, "cardtype": 10, "cardno": 20,
                    "name": 50, "addr": 100, "phone": 20,
                    "membercode": 6}
SMARTCARD_COLS = ("Code, CardType, CardNo, Name, Addr, Phone, "
                  "CashAmt, SecurityAmt, IssDate, ValidUpto, "
                  "BlockedYN, CurrBal, SecurBal, MemberCode, "
                  "U_Name, U_EntDt, U_AE")


def _map_smartcard(r) -> dict:
    def _dt(v):
        if v is None:
            return None
        return v.date() if isinstance(v, datetime.datetime) else v
    try:
        return {"code": r.Code, "cardtype": r.CardType or "",
                "cardno": r.CardNo or "", "name": (r.Name or "").strip(),
                "addr": (r.Addr or "").strip(), "phone": (r.Phone or "").strip(),
                "cashamt": float(r.CashAmt or 0),
                "securityamt": float(r.SecurityAmt or 0),
                "issdate": _dt(r.IssDate),
                "validupto": _dt(r.ValidUpto),
                "blocked": r.BlockedYN or "N",
                "currbal": float(r.CurrBal or 0),
                "securbal": float(r.SecurBal or 0),
                "membercode": r.MemberCode or "",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        (c, ct, cn2, n, a, ph, ca, sa, iss, vu,
         bl, cb, sb, mc, un, _, uae) = r
        return {"code": c, "cardtype": ct or "",
                "cardno": cn2 or "", "name": (n or "").strip(),
                "addr": (a or "").strip(), "phone": (ph or "").strip(),
                "cashamt": float(ca or 0), "securityamt": float(sa or 0),
                "issdate": _dt(iss), "validupto": _dt(vu),
                "blocked": bl or "N", "currbal": float(cb or 0),
                "securbal": float(sb or 0), "membercode": mc or "",
                "u_name": un or "", "u_ae": uae or ""}


def smartcard_list(cn=None, limit: int = 500) -> list[dict]:
    return [_map_smartcard(r) for r in db.query(
        f"SELECT TOP {int(limit)} {SMARTCARD_COLS} "
        "FROM SmartCardRegistration ORDER BY Code", cn=cn)]


def smartcard_get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {SMARTCARD_COLS} FROM SmartCardRegistration WHERE Code = ?",
        (code,), cn=cn)
    return _map_smartcard(rows[0]) if rows else None


def smartcard_exists(code: str, cn=None) -> bool:
    return bool(db.query(
        "SELECT 1 FROM SmartCardRegistration WHERE Code = ?",
        (code,), cn=cn))


def smartcard_insert(rec: dict, cn=None, commit=True) -> int:
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "INSERT INTO SmartCardRegistration (Code, CardType, CardNo, "
        "Name, Addr, Phone, CashAmt, SecurityAmt, IssDate, ValidUpto, "
        "BlockedYN, CurrBal, SecurBal, MemberCode, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
        "getdate(), 'A', ?)",
        (rec["code"], rec.get("cardtype", ""), rec.get("cardno", ""),
         rec["name"], rec.get("addr", ""), rec.get("phone", ""),
         float(rec.get("cashamt") or 0),
         float(rec.get("securityamt") or 0),
         rec.get("issdate"), rec.get("validupto"),
         rec.get("blocked", "N"),
         float(rec.get("currbal") or 0),
         float(rec.get("securbal") or 0),
         rec.get("membercode", ""),
         SITE_CODE, USER, SITE_CODE), cn=cn, commit=commit)


def smartcard_update(code: str, rec: dict, cn=None, commit=True) -> int:
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "UPDATE SmartCardRegistration SET CardType = ?, CardNo = ?, "
        "Name = ?, Addr = ?, Phone = ?, CashAmt = ?, SecurityAmt = ?, "
        "IssDate = ?, ValidUpto = ?, BlockedYN = ?, CurrBal = ?, "
        "SecurBal = ?, MemberCode = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec.get("cardtype", ""), rec.get("cardno", ""),
         rec["name"], rec.get("addr", ""), rec.get("phone", ""),
         float(rec.get("cashamt") or 0),
         float(rec.get("securityamt") or 0),
         rec.get("issdate"), rec.get("validupto"),
         rec.get("blocked", "N"),
         float(rec.get("currbal") or 0),
         float(rec.get("securbal") or 0),
         rec.get("membercode", ""),
         USER, code), cn=cn, commit=commit)


def smartcard_delete(code: str, cn=None, commit=True) -> int:
    return db.execute(
        "DELETE FROM SmartCardRegistration WHERE Code = ?",
        (code,), cn=cn, commit=commit)


class _SmartCardAPI:
    LIMITS = SMARTCARD_LIMITS
    @staticmethod
    def list_all(cn=None, limit=500): return smartcard_list(cn, limit)
    @staticmethod
    def get(code, cn=None): return smartcard_get(code, cn)
    @staticmethod
    def exists(code, cn=None): return smartcard_exists(code, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return smartcard_insert(rec, cn, commit)
    @staticmethod
    def update(code, rec, cn=None, commit=True): return smartcard_update(code, rec, cn, commit)
    @staticmethod
    def delete(code, cn=None, commit=True): return smartcard_delete(code, cn, commit)

SmartCardAPI = _SmartCardAPI()
