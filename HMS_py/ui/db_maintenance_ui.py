"""Database Maintenance UI (VB6: UTL Update DB Nulls port)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QGroupBox, QMessageBox, QProgressBar,
    QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from HMS_py.core import db_maintenance
from ui.theme import palette


class NullUpdateWorker(QThread):
    finished = pyqtSignal(dict)
    def run(self):
        try:
            result = db_maintenance.update_nulls()
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit({"total_affected": 0, "errors": [str(e)], "queries_run": 0})


class DbMaintenanceWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Database Maintenance")
        self.resize(700, 500)
        self._build_ui()
        self._load_summary()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        title = QLabel("Database Maintenance")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        ops = QGroupBox("Operations")
        ops_lay = QVBoxLayout(ops)
        self.btn_nulls = QPushButton("Update Database Nulls")
        self.btn_nulls.setToolTip("Replace NULL values with defaults across all tables")
        self.btn_nulls.setStyleSheet("QPushButton{padding:10px;font-size:11pt;}")
        self.btn_nulls.clicked.connect(self._run_nulls)
        self.btn_refresh = QPushButton("Refresh Summary")
        self.btn_refresh.setToolTip("Reload NULL count summary from database")
        self.btn_refresh.clicked.connect(self._load_summary)
        ops_lay.addWidget(self.btn_nulls)
        ops_lay.addWidget(self.btn_refresh)
        layout.addWidget(ops)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        sum_grp = QGroupBox("NULL Summary")
        sum_lay = QVBoxLayout(sum_grp)
        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(3)
        self.summary_table.setAlternatingRowColors(True)
        self.summary_table.setHorizontalHeaderLabels(["Table", "Column", "NULL Count"])
        sum_lay.addWidget(self.summary_table)
        layout.addWidget(sum_grp)

        btn_lay = QHBoxLayout(); btn_lay.addStretch()
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setToolTip("Close this window")
        self.btn_exit.clicked.connect(self.close)
        btn_lay.addWidget(self.btn_exit)
        layout.addLayout(btn_lay)

    def _load_summary(self):
        try:
            rows = db_maintenance.get_null_summary()
            self.summary_table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                for j, v in enumerate([r["table"], r["column"], str(r["null_count"])]):
                    it = QTableWidgetItem(v)
                    it.setForeground(QColor(palette()["text"]))
                    self.summary_table.setItem(i, j, it)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _run_nulls(self):
        self.progress.setVisible(True)
        self.btn_nulls.setEnabled(False)
        self._worker = NullUpdateWorker()
        self._worker.finished.connect(self._on_done)
        self._worker.start()

    def _on_done(self, result):
        self.progress.setVisible(False)
        self.btn_nulls.setEnabled(True)
        msg = f"Queries run: {result['queries_run']}\nRows affected: {result['total_affected']}"
        if result.get("errors"):
            msg += f"\nErrors: {len(result['errors'])}"
        QMessageBox.information(self, "Done", msg)
        self._load_summary()


def open_db_maintenance(parent=None):
    w = DbMaintenanceWindow(parent); w.show(); return w
