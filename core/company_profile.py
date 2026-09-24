"""Company Profile + misc dialogs core (VB6 ports, parity matrix row).

salmarCompProfile -> company_profile:
  Filler  : SELECT * FROM CompanyProfile WHERE Site_Code='<site>'
            AND (LogSite_Code='<site>' OR LogSite_Code='HO')
  IniGrid : rows = FieldName / FieldValue pairs; PicturePath row shows
            image preview.
  CmdSave : per grid row
            UPDATE CompanyProfile
               SET FieldValue = <new>, Site_Code = '<site>',
                   LogSite_Code = '<site>', U_Name = '<user>',
                   U_EntDt = <now>, U_AE = 'E'
             WHERE FieldName = '<row FieldName>'
"""
from __future__ import annotations

from datetime import datetime

from HMS_py.core import db

SITE_CODE = db.get_site_code()
USER = db.get_user()


def profile_fields() -> list[dict]:
    """CompanyProfile rows (VB6 IniGrid fill-query). Empty -> []."""
    return [
        {"field": str(r[0] or ""), "value": str(r[1] or "")}
        for r in db.query(
            "SELECT FieldName, FieldValue FROM CompanyProfile "
            "WHERE Site_Code = ? AND (LogSite_Code = ? OR LogSite_Code = 'HO') "
            "ORDER BY FieldName",
            (SITE_CODE, SITE_CODE))
    ]


def save_profile(values: dict[str, str]) -> int:
    """VB6 CmdSave: per-row UPDATE (audit columns U_Name/U_EntDt/U_AE).

    Returns rows updated. FieldName rows absent in DB are skipped
    (VB6 grid is pre-filled from the same query, so parity holds).
    """
    cn = db.connect(db.load_config())
    try:
        cur = cn.cursor()
        n = 0
        now = datetime.now()
        for field, value in values.items():
            cur.execute(
                "UPDATE CompanyProfile "
                "SET FieldValue = ?, Site_Code = ?, LogSite_Code = ?, "
                "    U_Name = ?, U_EntDt = ?, U_AE = 'E' "
                "WHERE FieldName = ?",
                (str(value), SITE_CODE, SITE_CODE, USER, now, str(field)))
            n += cur.rowcount if cur.rowcount and cur.rowcount > 0 else 0
        cn.commit()
        return n
    finally:
        cn.close()
