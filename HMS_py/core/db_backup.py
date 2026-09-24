"""Database Backup Utility (VB6: UTL_Click Index=8 port).

VB6 pattern:
1. sp_dropdevice 'HOTELBKUP'
2. sp_addumpdevice 'Disk','HOTELBKUP','<path>\\HOTELBKUP'
3. BACKUP DATABASE TO HOTELBKUP
4. ZIP creation via CGZipFiles
5. BACKUP LOG WITH TRUNCATE_ONLY
6. DBCC SHRINKDATABASE
"""
from __future__ import annotations

import os
import time
from datetime import datetime

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")


def get_backup_path(cn=None) -> str:
    """Get backup path from Company table or default.

    VB6 pattern: reads from Company table's backup path column,
    falls back to a standard path if not configured.
    """
    rows = db.query(
        "SELECT TOP 1 Repo_Path, CentralData_Path FROM Company WHERE SiteCode = ? "
        "OR HeadOffice = 1",
        (SITE_CODE,), cn=cn,
    )
    if rows:
        # Try Repo_Path first, then CentralData_Path
        for idx in (0, 1):
            val = rows[0][idx] if len(rows[0]) > idx else None
            if val:
                path = str(val).strip()
                if path:
                    return path

    # Fallback: use Analysis.ini reports path parent + Backup
    try:
        cfg = db.load_config()
        reports = cfg.get("reports", r"C:\Drive\HMS2526\Reports")
        backup = os.path.join(os.path.dirname(reports), "Backup")
    except Exception:
        backup = r"C:\Drive\HMS2526\Backup"

    return backup


def _get_db_name(cn=None) -> str:
    """Get current database name from connection."""
    rows = db.query("SELECT DB_NAME() AS dbname", cn=cn)
    if rows:
        return str(rows[0].dbname or "")
    try:
        cfg = db.load_config()
        return cfg.get("database", "Moondata2627")
    except Exception:
        return "Moondata2627"


def _get_server(cn=None) -> str:
    """Get current server name."""
    try:
        cfg = db.load_config()
        return cfg.get("server", "Localhost")
    except Exception:
        return "Localhost"


def backup_database(db_name: str = None, cn=None) -> dict:
    """Full database backup using SQL Server BACKUP command.

    VB6 pattern:
      sp_addumpdevice 'Disk', 'HOTELBKUP', '<path>\\HOTELBKUP'
      BACKUP DATABASE [db] TO HOTELBKUP WITH INIT

    Returns: {success, backup_file, size_mb, duration_sec, message}
    """
    from HMS_py.core.db import _validate_identifier
    own = cn is None
    cn = cn or db.connect()
    try:
        if not db_name:
            db_name = _get_db_name(cn)

        # Validate db_name to prevent SQL injection
        _validate_identifier(db_name, "database")

        backup_path = get_backup_path(cn)
        os.makedirs(backup_path, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(
            backup_path, f"{db_name}_FULL_{timestamp}.bak"
        )

        # Drop old device if exists (VB6 step 1)
        try:
            cn.cursor().execute("sp_dropdevice 'HOTELBKUP'")
        except Exception:
            pass

        # Add dump device (VB6 step 2)
        try:
            cn.cursor().execute(
                "sp_addumpdevice 'Disk', 'HOTELBKUP', ?",
                (backup_file,),
            )
        except Exception:
            pass

        # Execute backup (VB6 step 3) - parameterized
        start = time.time()
        cur = cn.cursor()
        cur.execute(
            f"BACKUP DATABASE [{db_name}] TO DISK = ? WITH INIT, "
            "NAME = ?, DESCRIPTION = ?",
            (backup_file,
             f"{db_name} Full Backup",
             f"Auto backup created on {datetime.now().isoformat()}"),
        )
        duration = time.time() - start

        # Get file size
        size_mb = 0.0
        if os.path.isfile(backup_file):
            size_mb = os.path.getsize(backup_file) / (1024 * 1024)

        return {
            "success": True,
            "backup_file": backup_file,
            "size_mb": round(size_mb, 2),
            "duration_sec": round(duration, 2),
            "message": f"Backup successful: {backup_file} ({size_mb:.1f} MB)",
        }

    except Exception as e:
        return {
            "success": False,
            "backup_file": "",
            "size_mb": 0.0,
            "duration_sec": 0.0,
            "message": f"Backup failed: {e}",
        }
    finally:
        if own:
            cn.close()


def backup_transaction_log(db_name: str = None, cn=None) -> dict:
    """Truncate transaction log after backup.

    VB6 step 5: BACKUP LOG [db] WITH TRUNCATE_ONLY

    Returns: {success, message}
    """
    from HMS_py.core.db import _validate_identifier
    own = cn is None
    cn = cn or db.connect()
    try:
        if not db_name:
            db_name = _get_db_name(cn)

        # Validate db_name to prevent SQL injection
        _validate_identifier(db_name, "database")

        cur = cn.cursor()
        cur.execute(f"BACKUP LOG [{db_name}] WITH TRUNCATE_ONLY")

        return {
            "success": True,
            "message": f"Transaction log truncated for {db_name}",
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Log truncation failed: {e}",
        }
    finally:
        if own:
            cn.close()


def shrink_database(db_name: str = None, cn=None) -> dict:
    """Shrink database after log truncation.

    VB6 step 6: DBCC SHRINKDATABASE([db], 0, TRUNCATEONLY)

    Returns: {success, message}
    """
    from HMS_py.core.db import _validate_identifier
    own = cn is None
    cn = cn or db.connect()
    try:
        if not db_name:
            db_name = _get_db_name(cn)

        # Validate db_name to prevent SQL injection
        _validate_identifier(db_name, "database")

        cur = cn.cursor()
        cur.execute(f"DBCC SHRINKDATABASE([{db_name}], 0, TRUNCATEONLY)")

        return {
            "success": True,
            "message": f"Database {db_name} shrunk successfully",
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Shrink failed: {e}",
        }
    finally:
        if own:
            cn.close()


def backup_and_shrink(db_name: str = None, cn=None) -> dict:
    """Complete backup cycle: full backup + log truncate + shrink.

    VB6 UTL_Click Index=8 full flow.

    Returns: {backup, log_truncate, shrink, overall_success}
    """
    own = cn is None
    cn = cn or db.connect()
    try:
        # Step 1-4: Full backup
        backup_result = backup_database(db_name=db_name, cn=cn)
        if not backup_result["success"]:
            return {
                "backup": backup_result,
                "log_truncate": None,
                "shrink": None,
                "overall_success": False,
            }

        # Step 5: Truncate transaction log
        log_result = backup_transaction_log(db_name=db_name, cn=cn)

        # Step 6: Shrink database
        shrink_result = shrink_database(db_name=db_name, cn=cn)

        return {
            "backup": backup_result,
            "log_truncate": log_result,
            "shrink": shrink_result,
            "overall_success": True,
        }

    except Exception as e:
        return {
            "backup": {"success": False, "message": str(e)},
            "log_truncate": None,
            "shrink": None,
            "overall_success": False,
        }
    finally:
        if own:
            cn.close()


class _DBBackupAPI:
    @staticmethod
    def get_backup_path(cn=None):
        return get_backup_path(cn)

    @staticmethod
    def backup_database(db_name=None, cn=None):
        return backup_database(db_name, cn)

    @staticmethod
    def backup_transaction_log(db_name=None, cn=None):
        return backup_transaction_log(db_name, cn)

    @staticmethod
    def shrink_database(db_name=None, cn=None):
        return shrink_database(db_name, cn)

    @staticmethod
    def backup_and_shrink(db_name=None, cn=None):
        return backup_and_shrink(db_name, cn)

DBBackupAPI = _DBBackupAPI()
