"""ACGROUP CRUD (Account Group master - 31 live rows).
Schema evidence: GroupCode varchar(6) PK, GroupName varchar(50),
GroupNature varchar(1) (A/L), Nature varchar(15), ID int + BlOrd int
(table me hamesha populated, identity NAHI - app khud max+1 likhta hai).
Audit pattern VB6 jaisa: U_Name + U_EntDt(getdate()) + U_AE ('A'/'E').
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
_HO_CLAUSE_AC = "(LOGSITE_CODE = ? OR LOGSITE_CODE = 'HO')"
LIMITS = {"code": 6, "name": 50, "nature": 1, "type": 15}
SELECT_COLS = ("GroupCode, GroupName, GroupNature, Nature, ID, "
               "U_Name, U_EntDt, U_AE")


def _require_group_privilege(cn, need: str, user: str | None = None, comp: str | None = None):
    """VB6 MDIForm1 + FaGrEnt menuHelp guard for Group Accounts."""
    u = (user or USER or "").strip()
    c = (comp or db.get_comp_code() or "2")
    try:
        rows = db.query(
            "SELECT Param_Str AS UPrivilege, Flag FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]='Group Accounts'",
            (u, c), cn=cn)
    except Exception:
        return
    if not rows:
        return
    try:
        priv = (rows[0].UPrivilege or rows[0][0] or "").upper() if hasattr(rows[0], 'UPrivilege') else str(rows[0][0] or "").upper()
        flag = (rows[0].Flag or rows[0][1] or "").upper() if hasattr(rows[0], 'Flag') else str(rows[0][1] or "").upper() if len(rows[0]) > 1 else ""
    except Exception:
        priv, flag = "", ""
    if flag == "Y" or need.upper() in priv:
        return
    raise PermissionError(f"Group Accounts {need}-right denied for user '{u}' (Param_Str='{priv}', Flag='{flag}')")


def _map(r) -> dict:
    return {"code": r.GroupCode, "name": r.GroupName or "",
            "gnature": r.GroupNature or "", "nature": r.Nature or "",
            "id": r.ID, "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}


def _validate(rec: dict, cn=None):
    if len(rec.get("code", "")) > LIMITS["code"]:
        raise ValueError(f"GroupCode max {LIMITS['code']} chars")
    if not rec.get("code", "").strip():
        raise ValueError("GroupCode zaroori hai")
    if len(rec.get("name", "")) > LIMITS["name"]:
        raise ValueError(f"GroupName max {LIMITS['name']} chars")
    if not rec.get("name", "").strip():
        raise ValueError("GroupName zaroori hai")
    gn = (rec.get("gnature") or "").strip().upper()
    if gn and gn not in ("A", "L"):
        raise ValueError("GroupNature 'A' (Asset) ya 'L' (Liability) hona "
                         "chahiye")


def _next_id(cn) -> int:
    row = db.query("SELECT ISNULL(MAX(ID),0)+1 FROM ACGROUP", cn=cn)
    return int(row[0][0])


def list_all(cn=None) -> list[dict]:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM ACGROUP WHERE {_HO_CLAUSE_AC} ORDER BY GroupCode", (SITE_CODE,), cn=cn)
    return [_map(r) for r in rows]


def get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM ACGROUP WHERE GroupCode = ? AND {_HO_CLAUSE_AC}", (code, SITE_CODE),
        cn=cn)
    return _map(rows[0]) if rows else None


def exists(code: str, cn=None) -> bool:
    return bool(db.query(f"SELECT 1 FROM ACGROUP WHERE GroupCode = ? AND {_HO_CLAUSE_AC}",
                         (code, SITE_CODE), cn=cn))


def insert(rec: dict, cn=None, commit: bool = True, user: str | None = None) -> int:
    _validate(rec, cn=cn)
    _require_group_privilege(cn, 'A', user=user)
    nid = _next_id(cn)
    return db.execute(
        "INSERT INTO ACGROUP (ID, GroupCode, GroupName, GroupNature, "
        "Nature, Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code, BlOrd) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?, ?)",
        (nid, rec["code"], rec["name"],
         (rec.get("gnature") or "").upper(), rec.get("nature", ""),
         SITE_CODE, USER, SITE_CODE, nid), cn=cn, commit=commit)


def update(code: str, rec: dict, cn=None, commit: bool = True, user: str | None = None) -> int:
    _validate(rec, cn=cn)
    _require_group_privilege(cn, 'E', user=user)
    return db.execute(
        f"UPDATE ACGROUP SET GroupName = ?, GroupNature = ?, Nature = ?, "
        f"U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE GroupCode = ? AND {_HO_CLAUSE_AC}",
        (rec["name"], (rec.get("gnature") or "").upper(),
         rec.get("nature", ""), USER, code, SITE_CODE), cn=cn, commit=commit)


def delete(code: str, cn=None, commit: bool = True, user: str | None = None) -> int:
    _require_group_privilege(cn, 'D', user=user)
    return db.execute(f"DELETE FROM ACGROUP WHERE GroupCode = ? AND {_HO_CLAUSE_AC}", (code, SITE_CODE),
                      cn=cn, commit=commit)
