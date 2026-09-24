"""Database Backup UI (VB6: UTL_Index=8 port).

Full backup, log truncate, shrink database operations.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QGroupBox, QTextEdit, QMessageBox, QProgressBar,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from HMS_py.core import db_backup


class BackupWorker(QThread):
    """Background thread for backup operations."""
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)

    def __init__(self, operation: str):
        super().__init__()
        self.operation = operation

    def run(self):
        try:
            if self.operation == "full":
                self.progress.emit("Starting full database backup...")
                result = db_backup.backup_and_shrink()
            elif self.operation == "backup_only":
                self.progress.emit("Starting database backup...")
                result = db_backup.backup_database()
            elif self.operation == "log_only":
                self.progress.emit("Truncating transaction log...")
                result = db_backup.backup_transaction_log()
            elif self.operation == "shrink_only":
                self.progress.emit("Shrinking database...")
                result = db_backup.shrink_database()
            else:
                result = {"success": False, "message": "Unknown operation"}
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit({"success": False, "message": str(e)})


class DbBackupWindow(QMainWindow):
    """Database Backup utility form."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Database Backup")
        self.resize(700, 500)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Title
        title = QLabel("Database Backup & Maintenance")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Operations
        ops_group = QGroupBox("Operations")
        ops_layout = QVBoxLayout(ops_group)

        btn_style = "QPushButton { padding: 10px; font-size: 11pt; }"

        self.btn_full = QPushButton("Full Backup + Log Truncate + Shrink (Recommended)")
        self.btn_full.setToolTip("Run full backup, truncate log, and shrink database")
        self.btn_full.setStyleSheet(btn_style)
        self.btn_full.clicked.connect(lambda: self._run("full"))

        self.btn_backup = QPushButton("Backup Only")
        self.btn_backup.setToolTip("Backup database without log truncate or shrink")
        self.btn_backup.setStyleSheet(btn_style)
        self.btn_backup.clicked.connect(lambda: self._run("backup_only"))

        self.btn_log = QPushButton("Truncate Transaction Log Only")
        self.btn_log.setToolTip("Truncate the transaction log to free space")
        self.btn_log.setStyleSheet(btn_style)
        self.btn_log.clicked.connect(lambda: self._run("log_only"))

        self.btn_shrink = QPushButton("Shrink Database Only")
        self.btn_shrink.setToolTip("Shrink database to reclaim unused space")
        self.btn_shrink.setStyleSheet(btn_style)
        self.btn_shrink.clicked.connect(lambda: self._run("shrink_only"))

        for b in [self.btn_full, self.btn_backup, self.btn_log, self.btn_shrink]:
            ops_layout.addWidget(b)
        layout.addWidget(ops_group)

        # Progress
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # indeterminate
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Log
        log_group = QGroupBox("Operation Log")
        log_layout = QVBoxLayout(log_group)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        log_layout.addWidget(self.log)
        layout.addWidget(log_group)

        # Exit
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setToolTip("Close this window")
        self.btn_exit.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_exit)
        layout.addLayout(btn_layout)

    def _run(self, operation: str):
        self.progress.setVisible(True)
        self._set_buttons(False)
        self._worker = BackupWorker(operation)
        self._worker.finished.connect(self._on_done)
        self._worker.progress.connect(lambda msg: self.log.append(msg))
        self._worker.start()

    def _on_done(self, result: dict):
        self.progress.setVisible(False)
        self._set_buttons(True)
        success = result.get("success", False)
        msg = result.get("message", "No message")
        if "backup_file" in result:
            msg += f"\nFile: {result['backup_file']}"
        if "size_mb" in result:
            msg += f"\nSize: {result['size_mb']:.1f} MB"
        if "duration_sec" in result:
            msg += f"\nDuration: {result['duration_sec']:.1f}s"
        self.log.append(f"\n{'SUCCESS' if success else 'FAILED'}: {msg}")
        if success:
            QMessageBox.information(self, "Success", msg)
        else:
            QMessageBox.critical(self, "Failed", msg)

    def _set_buttons(self, enabled: bool):
        for b in [self.btn_full, self.btn_backup, self.btn_log, self.btn_shrink]:
            b.setEnabled(enabled)


def open_db_backup(parent=None):
    w = DbBackupWindow(parent)
    w.show()
    return w
