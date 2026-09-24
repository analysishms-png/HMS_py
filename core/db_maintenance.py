"""Database Maintenance Utilities – Update NULL columns to defaults.

VB6 port: UTL menu → Null-fix routines. Identifies rows where ISNULL
columns and sets sensible defaults. Safe to run multiple times (idempotent).
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()

UPDATE_NULLS_QUERIES = [
    # GuestFolio – ISNULL defaults
    "UPDATE GuestFolio SET GuestName = 'UNKNOWN' WHERE GuestName IS NULL",
    "UPDATE GuestFolio SET GuestAdd1 = '' WHERE GuestAdd1 IS NULL",
    "UPDATE GuestFolio SET GuestAdd2 = '' WHERE GuestAdd2 IS NULL",
    "UPDATE GuestFolio SET GuestCity = '' WHERE GuestCity IS NULL",
    "UPDATE GuestFolio SET GuestState = '' WHERE GuestState IS NULL",
    "UPDATE GuestFolio SET GuestCountry = '' WHERE GuestCountry IS NULL",
    "UPDATE GuestFolio SET GuestPin = '' WHERE GuestPin IS NULL",
    "UPDATE GuestFolio SET GuestPhone = '' WHERE GuestPhone IS NULL",
    "UPDATE GuestFolio SET GuestEmail = '' WHERE GuestEmail IS NULL",
    # Booking – ISNULL defaults
    "UPDATE Booking SET Remarks = '' WHERE Remarks IS NULL",
    "UPDATE Booking SET CancelReason = '' WHERE CancelReason IS NULL",
    # RoomOcc – ISNULL defaults
    "UPDATE RoomOcc SET Remarks = '' WHERE Remarks IS NULL",
    # Stock – ISNULL defaults
    "UPDATE Stock SET Remark = '' WHERE Remark IS NULL",
]


def update_nulls(cn=None) -> dict:
    """Run all UPDATE_NULLS_QUERIES and return summary.

    Returns:
        {total_affected: int, errors: list[str], queries_run: int}
    """
    own = cn is None
    cn = cn or db.connect()
    total_affected = 0
    errors: list[str] = []
    try:
        for idx, sql in enumerate(UPDATE_NULLS_QUERIES, 1):
            try:
                cur = cn.cursor()
                cur.execute(sql)
                total_affected += cur.rowcount
                cn.commit()
            except Exception as exc:
                errors.append(f"Query {idx} failed: {exc}")
                try:
                    cn.rollback()
                except Exception:
                    pass
        return {
            "total_affected": total_affected,
            "errors": errors,
            "queries_run": len(UPDATE_NULLS_QUERIES),
        }
    finally:
        if own:
            cn.close()


def get_null_summary(cn=None) -> list[dict]:
    """Check key tables for remaining NULLs in commonly-nullable columns.

    Returns:
        [{table, column, null_count}, ...]
    """
    checks = [
        ("GuestFolio", "GuestName"),
        ("GuestFolio", "GuestAdd1"),
        ("GuestFolio", "GuestAdd2"),
        ("GuestFolio", "GuestCity"),
        ("GuestFolio", "GuestState"),
        ("GuestFolio", "GuestCountry"),
        ("GuestFolio", "GuestPin"),
        ("GuestFolio", "GuestPhone"),
        ("GuestFolio", "GuestEmail"),
        ("Booking", "Remarks"),
        ("Booking", "CancelReason"),
        ("RoomOcc", "Remarks"),
        ("Stock", "Remark"),
    ]
    results: list[dict] = []
    own = cn is None
    cn = cn or db.connect()
    try:
        for table, column in checks:
            try:
                rows = db.query(
                    f"SELECT COUNT(*) AS cnt FROM [{table}] WHERE [{column}] IS NULL",
                    cn=cn,
                )
                cnt = rows[0].cnt if rows else 0
                if cnt > 0:
                    results.append({
                        "table": table,
                        "column": column,
                        "null_count": cnt,
                    })
            except Exception:
                pass
        return results
    finally:
        if own:
            cn.close()
