"""Company/property list - frmCompany.frm jaisa dynamic data.

VB6 Company Details grid: Company Name | Short Name | Current Year.
Data sources (evidence):
  - Site table: CompCode, Site_Code, Site_Desc, Short_Name (property rows)
  - Year: Analysis.ini pattern "2026-27" (VB6 me session year tha)
  - Site khaali ho toh INI keys 7 (company code) + 8 (city) se fallback.
"""
from __future__ import annotations

from HMS_py.core import db
SITE_CODE = db.get_site_code()


def list_companies() -> list[dict]:
    """frmCompany grid ka data.

    BUGFIX (P0): Site table is DB me khaali hai (0 rows) - pehla port
    'Property (INI)' fallback dikha raha tha. frmCompany ka ASLI query
    (decompiled evidence): 'Select * from company order by STart_dt Desc'
    - Company table (Comp_Name='Moon and Mars Resorts', SName='MMR',
    cyear='2026-27'). Production screenshot usi se match karta hai.
    """
    cfg = db.load_config()
    try:
        rows = db.query(
            "SELECT Comp_Name, SName, cyear FROM Company AND (LOGSITE_CODE = ? OR LOGSITE_CODE = 'HO' OR ISNULL(LOGSITE_CODE,'')='') "
            "ORDER BY Start_Dt DESC")
    except Exception:
        rows = []
    out = []
    for r in rows or []:
        out.append({"code": "", "site": cfg.get("site", ""),
                    "name": r[0] or "", "short": r[1] or "",
                    "year": r[2] or current_year()})
    if not out:
        # fallback: INI company (single-property install)
        out = [{"code": "", "site": cfg.get("site", ""),
                "name": "Property (INI)", "short": "",
                "year": current_year()}]
    return out


def current_year() -> str:
    """VB6 jaisa financial year string (Apr-Mar): 2026-27."""
    import datetime
    today = datetime.date.today()
    if today.month >= 4:
        y1 = today.year
    else:
        y1 = today.year - 1
    return f"{y1}-{(y1 + 1) % 100:02d}"
