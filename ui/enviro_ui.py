"""Enviro / Parameter UI (VB6 frmEnviro.frm port) — 'Parameter' leaf.

Run: python -m HMS_py.ui.enviro_ui
Menu: General Setup -> 'Parameter' (User_Module GENMas srno=46).
VB6 form 200+ settings ka tha; hum EDITABLE white-list (55 operational
settings) dikhaate hain, finance AC-cols READ-ONLY section me.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QKeySequence, QShortcut
from PyQt6.QtWidgets import (QHBoxLayout, QHeaderView, QLabel, QMessageBox,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QWidget)

from HMS_py.core import enviro
from HMS_py.ui import theme as _theme


def _dark_item(val, readonly=False) -> QTableWidgetItem:
    it = QTableWidgetItem("" if val is None else str(val))
    it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable) if readonly else \
        it.setFlags(it.flags() | Qt.ItemFlag.ItemIsEditable)
    it.setForeground(QColor(_theme.palette()["text"]))
    if readonly:
        it.setBackground(QColor(_theme.palette()["glass_tint"]))
    return it


class EnviroScreen(QWidget):
    """Settings grid: Setting | Value | Type — Save button (F5 reload)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        v = QVBoxLayout(self)
        top = QHBoxLayout()
        self.lblTitle = QLabel("System Parameters (Enviro)")
        top.addWidget(self.lblTitle)
        top.addStretch(1)
        self.btnReload = QPushButton("Reload")
        self.btnReload.setToolTip("Reload settings from database (F5)")
        self.btnReload.clicked.connect(self.reload)
        top.addWidget(self.btnReload)
        v.addLayout(top)

        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents)
        v.addWidget(self.table)

        bar = QHBoxLayout()
        self.btnSave = QPushButton("Save Changes")
        self.btnSave.setDefault(True)
        self.btnSave.setToolTip("Save modified settings (Ctrl+S)")
        self.btnSave.clicked.connect(self._save)
        bar.addWidget(self.btnSave)
        bar.addStretch(1)
        self.lblStatus = QLabel("Ready (finance AC-cols read-only)")
        bar.addWidget(self.lblStatus)
        v.addLayout(bar)

        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._save)
        QShortcut(QKeySequence("F5"), self, activated=self.reload)
        self._rows = []  # [(key, type, orig_value)]
        self.reload()

    def reload(self):
        try:
            data = enviro.get()
        except Exception as e:
            QMessageBox.critical(self, "Enviro", str(e))
            return
        keys = sorted(enviro.EDITABLE)
        self._rows = [(k, enviro.EDITABLE[k], data.get(k)) for k in keys]
        self.table.clear()
        self.table.setRowCount(len(self._rows))
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(
            ["Setting", "Value (editable)", "Type"])
        for r, (k, t, val) in enumerate(self._rows):
            self.table.setItem(r, 0, _dark_item(k, readonly=True))
            shown = "" if val is None else str(val)
            self.table.setItem(r, 1, _dark_item(shown))
            self.table.setItem(r, 2, _dark_item(t, readonly=True))

    def _save(self):
        changes = {}
        for r, (k, t, orig) in enumerate(self._rows):
            it = self.table.item(r, 1)
            new = it.text().strip() if it else ""
            old = "" if orig is None else str(orig)
            if new != old:
                changes[k] = new
        if not changes:
            QMessageBox.information(self, "Enviro", "Koi change nahi")
            return
        try:
            enviro.update_settings(changes)
        except ValueError as e:
            QMessageBox.warning(self, "Validation", str(e))
            self.reload()
            return
        self.lblStatus.setText(
            f"Saved: {len(changes)} setting(s) updated")
        QMessageBox.information(
            self, "Enviro", f"{len(changes)} setting(s) saved")
        self.reload()


def open_enviro(parent=None):
    """Shell ke liye opener ('Parameter' leaf)."""
    w = EnviroScreen(parent)
    w.setWindowFlags(Qt.WindowType.Window)
    w.setWindowTitle("Parameter - Enviro Settings - HMS_py")
    w.resize(860, 620)
    w.show()
    return w


def main():  # pragma: no cover
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = EnviroScreen()
    w.resize(860, 620)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":  # pragma: no cover
    main()
