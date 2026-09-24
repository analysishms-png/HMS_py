"""Account Merge Utility – merge two SubGroup codes into one.

VB6 port: CompMast merge flow. Moves LEDGER, LEDGERADJ, and
SUBGROUPCURRBAL records from old_code → new_code, then deletes the
orphan SubGroup row. All operations within a single transaction.
"""
from __future__ import annotations

from HMS_py.core import db


def preview_merge(old_code: str, new_code: str, cn=None) -> dict:
    """Preview how many records would be affected by merging old → new.

    Returns:
        {ledger: int, ledgeradj: int, subgroupcurrbal: int, old_exists: bool, new_exists: bool}
    """
    own = cn is None
    cn = cn or db.connect()
    try:
        def _count(table: str) -> int:
            rows = db.query(
                f"SELECT COUNT(*) AS cnt FROM [{table}] WHERE RTRIM([SubCode]) = ?",
                (old_code.strip(),), cn=cn,
            )
            return rows[0].cnt if rows else 0

        old_rows = db.query(
            "SELECT 1 FROM [SubGroup] WHERE RTRIM([SubCode]) = ?",
            (old_code.strip(),), cn=cn,
        )
        new_rows = db.query(
            "SELECT 1 FROM [SubGroup] WHERE RTRIM([SubCode]) = ?",
            (new_code.strip(),), cn=cn,
        )

        return {
            "ledger": _count("LEDGER"),
            "ledgeradj": _count("LEDGERADJ"),
            "subgroupcurrbal": _count("SUBGROUPCURRBAL"),
            "old_exists": len(old_rows) > 0,
            "new_exists": len(new_rows) > 0,
        }
    finally:
        if own:
            cn.close()


def merge_accounts(old_code: str, new_code: str, cn=None,
                   commit: bool = True) -> dict:
    """Merge old_code into new_code across LEDGER, LEDGERADJ, SUBGROUPCURRBAL.

    Steps:
        1. Validate both codes exist in SubGroup.
        2. UPDATE LEDGER SET SubCode = new WHERE SubCode = old.
        3. UPDATE LEDGERADJ SET SubCode = new WHERE SubCode = old.
        4. UPDATE SUBGROUPCURRBAL SET SubCode = new WHERE SubCode = old.
        5. DELETE old SubGroup row.
        6. Commit (if commit=True).

    Returns:
        {merged: str, into: str, records_updated: int}
    Raises:
        ValueError if either code is missing or identical.
    """
    old_code = old_code.strip()
    new_code = new_code.strip()

    if old_code == new_code:
        raise ValueError("Old and new codes are identical")

    own = cn is None
    cn = cn or db.connect()
    try:
        old_rows = db.query(
            "SELECT 1 FROM [SubGroup] WHERE RTRIM([SubCode]) = ?",
            (old_code,), cn=cn,
        )
        if not old_rows:
            raise ValueError(f"Old code '{old_code}' not found in SubGroup")

        new_rows = db.query(
            "SELECT 1 FROM [SubGroup] WHERE RTRIM([SubCode]) = ?",
            (new_code,), cn=cn,
        )
        if not new_rows:
            raise ValueError(f"New code '{new_code}' not found in SubGroup")

        total = 0

        for table in ("LEDGER", "LEDGERADJ", "SUBGROUPCURRBAL"):
            n = db.execute(
                f"UPDATE [{table}] SET [SubCode] = ? WHERE RTRIM([SubCode]) = ?",
                (new_code, old_code), cn=cn, commit=False,
            )
            total += n

        db.execute(
            "DELETE FROM [SubGroup] WHERE RTRIM([SubCode]) = ?",
            (old_code,), cn=cn, commit=False,
        )

        if commit:
            cn.commit()

        return {
            "merged": old_code,
            "into": new_code,
            "records_updated": total,
        }
    except Exception:
        try:
            cn.rollback()
        except Exception:
            pass
        raise
    finally:
        if own:
            cn.close()
