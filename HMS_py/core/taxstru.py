"""Tax Structure Master CRUD (VB6: FrmTaxStruMast - Main Setup -> General Setup).

Schema evidence (live HMS DB): TaxStru table.
  Code varchar(6) PK (compound with Sno), Name varchar(35),
  Sno smallint (line number within structure),
  TaxCode varchar(6) FK -> RevMast.Code (FieldType='T'),
  Nature varchar(25) ('On Base Amt','On Running Total','On Prev. Tax Amt'),
  Rate float (percentage), Limit float, Limit1 float,
  CondApp varchar(25) ('<','<=','>','>=','=','Between'),
  CompOperator varchar(9),
  TaxBeforeDisc varchar(3) ('Yes'/'No'),
  Site_Code(2), U_Name(10), U_EntDt, U_AE(1), LogSite_Code(2).

VB6 FrmTaxStruMast: grid-based entry (FGrid) with Sno rows per Code.
Each Tax Structure (Code) has multiple tax lines (Sno 1..n).
Audit pattern VB6 jaisa: U_Name + U_EntDt(getdate()) + U_AE ('A'/'E').
Code pattern live: 'KK' + 4 digits (KK0002...).
Next code: Max(CAST(SUBSTRING(Code,3,4) AS INT)) + 1."""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
LIMITS = {"code": 6, "name": 35, "taxcode": 6, "nature": 25,
          "condapp": 25, "compop": 9, "taxbeforedisc": 3}
SELECT_COLS = ("Code, Name, Sno, TaxCode, Nature, Rate, "
               "Limit, Limit1, CondApp, CompOperator, TaxBeforeDisc, "
               "U_Name, U_EntDt, U_AE")


def _map(r) -> dict:
    try:
        return {
            "code": r.Code,
            "name": (r.Name or "").strip(),
            "sno": r.Sno,
            "taxcode": r.TaxCode or "",
            "nature": r.Nature or "On Base Amt",
            "rate": float(r.Rate or 0),
            "limit": float(r.Limit or 0),
            "limit1": float(r.Limit1 or 0),
            "condapp": r.CondApp or "",
            "compop": r.CompOperator or "",
            "taxbeforedisc": r.TaxBeforeDisc or "No",
            "u_name": r.U_Name or "",
            "u_ae": r.U_AE or "",
        }
    except AttributeError:
        code, name, sno, taxcode, nature, rate, limit, _, _, _, u_name, _, u_ae, condapp, logsite, compop, taxbeforedisc, limit1 = r
        return {
            "code": code,
            "name": (name or "").strip(),
            "sno": sno,
            "taxcode": taxcode or "",
            "nature": nature or "On Base Amt",
            "rate": float(rate or 0),
            "limit": float(limit or 0),
            "limit1": float(limit1 or 0),
            "condapp": condapp or "",
            "compop": compop or "",
            "taxbeforedisc": taxbeforedisc or "No",
            "u_name": u_name or "",
            "u_ae": u_ae or "",
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
    if not rec.get("taxcode", "").strip():
        raise ValueError("TaxCode zaroori hai")
    if len(rec["taxcode"]) > LIMITS["taxcode"]:
        raise ValueError(f"TaxCode max {LIMITS['taxcode']} chars")
    if len(rec.get("nature", "")) > LIMITS["nature"]:
        raise ValueError(f"Nature max {LIMITS['nature']} chars")
    if len(rec.get("condapp", "")) > LIMITS["condapp"]:
        raise ValueError(f"CondApp max {LIMITS['condapp']} chars")
    if len(rec.get("compop", "")) > LIMITS["compop"]:
        raise ValueError(f"CompOperator max {LIMITS['compop']} chars")
    if len(rec.get("taxbeforedisc", "")) > LIMITS["taxbeforedisc"]:
        raise ValueError(f"TaxBeforeDisc max {LIMITS['taxbeforedisc']} chars")
    # Validate rate
    try:
        r = float(rec.get("rate") or 0)
        if not (0 <= r <= 100):
            raise ValueError("Rate 0-100 ke beech honi chahiye")
    except (TypeError, ValueError):
        raise ValueError("Rate numeric hona chahiye")
    # Validate Sno
    try:
        s = int(rec.get("sno") or 0)
        if s < 1:
            raise ValueError("Sno >= 1 hona chahiye")
    except (TypeError, ValueError):
        raise ValueError("Sno integer hona chahiye")


def list_all(cn=None) -> list[dict]:
    rows = db.query(f"SELECT {SELECT_COLS} FROM TaxStru ORDER BY Code, Sno", cn=cn)
    return [_map(r) for r in rows]


def list_by_code(code: str, cn=None) -> list[dict]:
    """Get all lines (Sno) for a tax structure code."""
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM TaxStru WHERE Code = ? ORDER BY Sno",
        (code,), cn=cn)
    return [_map(r) for r in rows]


def get(code: str, sno: int, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM TaxStru WHERE Code = ? AND Sno = ?",
        (code, sno), cn=cn)
    return _map(rows[0]) if rows else None


def exists(code: str, sno: int, cn=None) -> bool:
    return bool(db.query(
        "SELECT 1 FROM TaxStru WHERE Code = ? AND Sno = ?",
        (code, sno), cn=cn))


def exists_code(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM TaxStru WHERE Code = ?", (code,), cn=cn))


def next_code(cn=None) -> str:
    """VB6 pattern: 'KK' + max 4-digit suffix + 1."""
    rows = db.query(
        "SELECT MAX(Code) FROM TaxStru WHERE Code LIKE 'KK%' AND LEN(Code) = 6 "
        "AND ISNUMERIC(SUBSTRING(Code, 3, 4)) = 1",
        cn=cn)
    mx = rows[0][0] if rows and rows[0][0] else "KK0000"
    return f"KK{int(mx[2:]) + 1:04d}"


def next_sno(code: str, cn=None) -> int:
    """Next Sno for a given tax structure code."""
    rows = db.query(
        "SELECT MAX(Sno) FROM TaxStru WHERE Code = ?", (code,), cn=cn)
    return (rows[0][0] or 0) + 1 if rows and rows[0][0] else 1


def insert(rec: dict, cn=None, commit: bool = True) -> int:
    """Insert a single tax structure line (Code + Sno)."""
    _validate(rec)
    return db.execute(
        "INSERT INTO TaxStru (Code, Name, Sno, TaxCode, Nature, Rate, "
        "Limit, Limit1, Site_Code, U_Name, U_EntDt, U_AE, "
        "CondApp, LogSite_Code, CompOperator, TaxBeforeDisc) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?, ?, ?, ?)",
        (rec["code"], rec["name"], rec["sno"], rec["taxcode"],
         rec.get("nature", "On Base Amt"), float(rec.get("rate") or 0),
         float(rec.get("limit") or 0), float(rec.get("limit1") or 0),
         SITE_CODE, USER,
         rec.get("condapp", ""), SITE_CODE,
         rec.get("compop", ""), rec.get("taxbeforedisc", "No")),
        cn=cn, commit=commit)


def insert_structure(code: str, name: str, lines: list[dict], cn=None,
                     commit: bool = True) -> int:
    """Insert a complete tax structure with multiple lines (Sno 1..n).
    lines = [{taxcode, nature, rate, limit, limit1, condapp, compop, taxbeforedisc}, ...]
    """
    if not lines:
        raise ValueError("At least one tax line required")

    own = cn is None
    cn = cn or db.connect()
    try:
        for i, line in enumerate(lines, 1):
            sno = i
            db.execute(
                "INSERT INTO TaxStru (Code, Name, Sno, TaxCode, Nature, Rate, "
                "Limit, Limit1, Site_Code, U_Name, U_EntDt, U_AE, "
                "CondApp, LogSite_Code, CompOperator, TaxBeforeDisc) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?, ?, ?, ?)",
                (code, name, sno, line["taxcode"],
                 line.get("nature", "On Base Amt"), float(line.get("rate") or 0),
                 float(line.get("limit") or 0), float(line.get("limit1") or 0),
                 SITE_CODE, USER,
                 line.get("condapp", ""), SITE_CODE,
                 line.get("compop", ""), line.get("taxbeforedisc", "No")),
                cn=cn, commit=False)
        if commit:
            cn.commit()
        return len(lines)
    finally:
        if own:
            cn.close()


def update(code: str, sno: int, rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec)
    return db.execute(
        "UPDATE TaxStru SET Name = ?, TaxCode = ?, Nature = ?, Rate = ?, "
        "Limit = ?, Limit1 = ?, CondApp = ?, CompOperator = ?, "
        "TaxBeforeDisc = ?, U_Name = ?, U_EntDt = getdate(), U_AE = 'E' "
        "WHERE Code = ? AND Sno = ?",
        (rec["name"], rec["taxcode"], rec.get("nature", "On Base Amt"),
         float(rec.get("rate") or 0), float(rec.get("limit") or 0),
         float(rec.get("limit1") or 0),
         rec.get("condapp", ""), rec.get("compop", ""),
         rec.get("taxbeforedisc", "No"), USER, code, sno),
        cn=cn, commit=commit)


def update_structure(code: str, name: str, lines: list[dict], cn=None,
                     commit: bool = True) -> int:
    """Replace all lines for a tax structure code with new lines."""
    own = cn is None
    cn = cn or db.connect()
    try:
        # Delete existing lines for this code
        db.execute("DELETE FROM TaxStru WHERE Code = ?", (code,), cn=cn, commit=False)
        # Insert new lines
        for i, line in enumerate(lines, 1):
            sno = i
            db.execute(
                "INSERT INTO TaxStru (Code, Name, Sno, TaxCode, Nature, Rate, "
                "Limit, Limit1, Site_Code, U_Name, U_EntDt, U_AE, "
                "CondApp, LogSite_Code, CompOperator, TaxBeforeDisc) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?, ?, ?, ?)",
                (code, name, sno, line["taxcode"],
                 line.get("nature", "On Base Amt"), float(line.get("rate") or 0),
                 float(line.get("limit") or 0), float(line.get("limit1") or 0),
                 SITE_CODE, USER,
                 line.get("condapp", ""), SITE_CODE,
                 line.get("compop", ""), line.get("taxbeforedisc", "No")),
                cn=cn, commit=False)
        if commit:
            cn.commit()
        return len(lines)
    finally:
        if own:
            cn.close()


def delete(code: str, sno: int, cn=None, commit: bool = True) -> int:
    """Delete a single tax structure line."""
    return db.execute(
        "DELETE FROM TaxStru WHERE Code = ? AND Sno = ?",
        (code, sno), cn=cn, commit=commit)


def delete_structure(code: str, cn=None, commit: bool = True) -> int:
    """Delete entire tax structure (all Sno lines)."""
    return db.execute("DELETE FROM TaxStru WHERE Code = ?", (code,), cn=cn, commit=commit)


def get_tax_codes(cn=None) -> list[dict]:
    """Get available tax codes from RevMast (FieldType='T')."""
    rows = db.query(
        "SELECT Code, Name FROM RevMast WHERE FieldType = 'T' AND "
        "(LogSite_Code = ? OR LogSite_Code = 'HO') ORDER BY Name",
        (SITE_CODE,), cn=cn)
    return [{"code": r[0], "name": (r[1] or "").strip()} for r in rows]


def get_structures_summary(cn=None) -> list[dict]:
    """Get unique tax structures (Code + Name) for dropdown/list."""
    rows = db.query(
        "SELECT DISTINCT Code, Name FROM TaxStru ORDER BY Code", cn=cn)
    return [{"code": r[0], "name": (r[1] or "").strip()} for r in rows]


# ============================================================
# Tax calculation (VB6 pPBill Proc tax engine - PI-4)
# ============================================================
def calculate(tax_stru_code: str, base_amount: float,
              cn=None) -> dict:
    """Compute taxes for one TaxStru structure on a taxable base.

    VB6 pPBill: loads TaxStru lines (Sno order), applies each Rate
    according to Nature:
      - 'On Base Amt'      : base * rate%
      - 'On Running Total' : (base + prev_taxes) * rate%
      - 'On Prev. Tax Amt' : sum(prev tax amounts) * rate%
    CondApp/Limit/Limit1: slab guard (apply only if amount in range).
    Splits CGST/SGST/IGST when TaxCode is one of those; otherwise
    accumulates into 'other'. Returns dict with per-code breakdown.
    """
    base = float(base_amount or 0)
    rows = list_by_code(tax_stru_code, cn=cn)
    if not rows:
        return {"total_tax": 0.0, "cgst": 0.0, "sgst": 0.0,
                "igst": 0.0, "service": 0.0, "other": 0.0,
                "lines": [], "roundoff": 0.0, "net": base}

    running = base
    prev_tax_sum = 0.0
    lines_out = []
    cgst = sgst = igst = service = other = 0.0

    for row in rows:
        rate = float(row.get("rate") or 0)
        nature = (row.get("nature") or "On Base Amt").strip()
        taxcode = (row.get("taxcode") or "").strip().upper()
        condapp = (row.get("condapp") or "").strip()
        limit = float(row.get("limit") or 0)
        limit1 = float(row.get("limit1") or 0)

        # Slab condition on current base (CondApp semantics)
        if condapp in ("<", "<=", ">", ">=", "=", "Between") and limit:
            ok = True
            if condapp == "<":
                ok = base < limit
            elif condapp == "<=":
                ok = base <= limit
            elif condapp == ">":
                ok = base > limit
            elif condapp == ">=":
                ok = base >= limit
            elif condapp == "=":
                ok = abs(base - limit) < 0.005
            elif condapp == "Between":
                ok = limit <= base <= (limit1 or limit)
            if not ok:
                lines_out.append({"taxcode": taxcode, "rate": rate,
                                  "amount": 0.0, "skipped": True})
                continue

        if nature.startswith("On Running"):
            amt = running * rate / 100.0
        elif nature.startswith("On Prev"):
            amt = prev_tax_sum * rate / 100.0
        else:  # On Base Amt (default)
            amt = base * rate / 100.0

        amt = round(amt, 2)
        running += amt
        prev_tax_sum += amt
        if taxcode == "CGST":
            cgst += amt
        elif taxcode == "SGST":
            sgst += amt
        elif taxcode == "IGST":
            igst += amt
        elif taxcode in ("SERVICE", "SCHRG", "SERVICECHARGE"):
            service += amt
        else:
            other += amt
        lines_out.append({"taxcode": taxcode, "rate": rate,
                          "amount": amt, "nature": nature,
                          "skipped": False})

    total = round(cgst + sgst + igst + service + other, 2)
    # VB6 pPBill: NetAmt = total + tax, RoundOff to nearest rupee
    net_before_ro = round(base + total, 2)
    roundoff = round(net_before_ro) - net_before_ro
    roundoff = round(roundoff, 2)
    return {"total_tax": total, "cgst": round(cgst, 2),
            "sgst": round(sgst, 2), "igst": round(igst, 2),
            "service": round(service, 2), "other": round(other, 2),
            "lines": lines_out, "roundoff": roundoff,
            "net": round(net_before_ro + roundoff, 2)}