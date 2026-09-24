"""Generic master form - TopCtrl state-machine (Idle/Add/Edit) ke saath.

Naya master banane ke liye sirf ek MasterConfig dena hai:
    cfg = MasterConfig(title=..., fields=[Field(...)], api=<core module>,
                       delete_guard=lambda code: ...)
UI + validation + CRUD wiring automatic. PlanMaster iska special-case hai;
Sundry/Narr direct config se bante hain (P2).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from dataclasses import dataclass, field as dc_field

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QKeySequence, QShortcut
from PyQt6.QtWidgets import (QDialog, QFormLayout, QHBoxLayout, QLabel,
                             QLineEdit, QMessageBox, QPushButton,
                             QTableWidget, QTableWidgetItem, QVBoxLayout,
                             QAbstractItemView, QHeaderView, QGroupBox,
                             QWidget)

from HMS_py.ui import theme as _theme


@dataclass
class Field:
    name: str            # dict key in core module records
    label: str
    max_len: int = 0
    required: bool = False
    default: str = ""
    placeholder: str = ""


@dataclass
class MasterConfig:
    title: str
    columns: list       # grid columns: (header, dict-key)
    fields: list        # editable Field list
    api: object         # core module: list_all/get/exists/insert/update/delete
    pk_key: str = "code"
    delete_guard: object = None   # fn(code) -> error-str | None
    sample_prefix: str = "PYT"


class BaseMasterForm(QDialog):
    def __init__(self, cfg: MasterConfig, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.setWindowTitle(cfg.title)
        self.setMinimumSize(680, 520)
        self.resize(720, 540)
        self.state = "Idle"
        self.edit_pk = None
        self._rec_from_ui = None      # fn: ui -> record dict (set by subclass)
        self._rec_to_ui = None        # fn: record dict -> ui

        p = _theme.palette()
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(12)

        # --- Table section ---
        tbl_grp = QGroupBox(f"{cfg.title} List")
        tbl_lay = QVBoxLayout(tbl_grp)

        # Search bar
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search...")
        self._search.setMinimumHeight(32)
        self._search.setStyleSheet(
            f"QLineEdit {{ padding: 6px 10px; border: 1px solid {p['border']}; "
            f"border-radius: 6px; font-size: 13px; color: {p['text']}; "
            f"background: {p['glass_tint']}; }}"
            f"QLineEdit:focus {{ border: 2px solid {p['accent']}; }}"
        )
        self._search.textChanged.connect(self._filter_table)
        tbl_lay.addWidget(self._search)

        self.tbl = QTableWidget(0, len(cfg.columns))
        self.tbl.setHorizontalHeaderLabels([c[0] for c in cfg.columns])
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setShowGrid(True)
        self.tbl.setSortingEnabled(True)
        hdr = self.tbl.horizontalHeader()
        hdr.setStretchLastSection(True)
        for i in range(len(cfg.columns) - 1):
            hdr.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl.cellDoubleClicked.connect(lambda *_: self._on_edit())
        tbl_lay.addWidget(self.tbl)
        root.addWidget(tbl_grp, stretch=1)

        # --- Form section ---
        form_grp = QGroupBox("Record Details")
        form_lay = QFormLayout(form_grp)
        form_lay.setSpacing(10)
        form_lay.setContentsMargins(16, 12, 16, 12)
        self.edits = {}
        self._field_labels = {}
        for f in cfg.fields:
            e = QLineEdit()
            if f.max_len:
                e.setMaxLength(f.max_len)
            if f.placeholder:
                e.setPlaceholderText(f.placeholder)
            e.setMinimumHeight(32)
            e.setStyleSheet(
                f"QLineEdit {{ padding: 6px 10px; border: 1px solid {p['border']}; "
                f"border-radius: 6px; font-size: 13px; color: {p['text']}; "
                f"background: {p['glass_tint']}; }}"
                f"QLineEdit:focus {{ border: 2px solid {p['accent']}; }}"
            )
            # Required indicator
            label_text = f.label
            if f.required:
                label_text += ' <span style="color:#dc2626; font-weight:bold;">*</span>'
            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"font-size: 12px; font-weight: 500; color: {p['text']};")
            self._field_labels[f.name] = lbl
            form_lay.addRow(lbl, e)
            self.edits[f.name] = e
        root.addWidget(form_grp)

        # --- Tab order ---
        prev_widget = None
        for f in cfg.fields:
            w = self.edits[f.name]
            if prev_widget is not None:
                QWidget.setTabOrder(prev_widget, w)
            prev_widget = w

        # --- Button bar ---
        btn_grp = QGroupBox()
        btn_lay = QHBoxLayout(btn_grp)
        btn_lay.setContentsMargins(0, 4, 0, 4)
        btn_lay.setSpacing(8)

        self.btnNew = QPushButton("  New (Ctrl+N)")
        self.btnNew.setProperty("accent", True)
        self.btnNew.setMinimumHeight(34)
        self.btnNew.setToolTip("Create a new record (Ctrl+N)")

        self.btnEdit = QPushButton("  Edit (Ctrl+E)")
        self.btnEdit.setMinimumHeight(34)
        self.btnEdit.setToolTip("Edit selected record (Ctrl+E)")

        self.btnDelete = QPushButton("  Delete (Ctrl+D)")
        self.btnDelete.setProperty("role", "danger")
        self.btnDelete.setMinimumHeight(34)
        self.btnDelete.setToolTip("Delete selected record (Ctrl+D)")

        self.btnSave = QPushButton("  Save (Ctrl+S)")
        self.btnSave.setProperty("accent", True)
        self.btnSave.setMinimumHeight(34)
        self.btnSave.setToolTip("Save changes (Ctrl+S)")

        self.btnCancel = QPushButton("  Cancel (Esc)")
        self.btnCancel.setMinimumHeight(34)
        self.btnCancel.setToolTip("Cancel current operation (Esc)")

        self.btnExit = QPushButton("  Exit")
        self.btnExit.setMinimumHeight(34)
        self.btnExit.setToolTip("Close this form")

        for b in (self.btnNew, self.btnEdit, self.btnDelete, self.btnSave,
                  self.btnCancel, self.btnExit):
            btn_lay.addWidget(b)
        btn_lay.addStretch()
        root.addWidget(btn_grp)

        # --- Status bar ---
        self.lblState = QLabel("Ready")
        self.lblState.setStyleSheet(
            f"font-size: 11px; color: {p['text_dim']}; padding: 4px 0; "
            f"border-top: 1px solid {p['border']};"
        )
        root.addWidget(self.lblState)

        # --- Signals ---
        self.btnNew.clicked.connect(self._on_new)
        self.btnEdit.clicked.connect(self._on_edit)
        self.btnDelete.clicked.connect(self._on_delete)
        self.btnSave.clicked.connect(self._on_save)
        self.btnCancel.clicked.connect(self._on_cancel)
        self.btnExit.clicked.connect(self.reject)

        # Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+N"), self, activated=self._on_new)
        QShortcut(QKeySequence("Ctrl+E"), self, activated=self._on_edit)
        QShortcut(QKeySequence("Ctrl+D"), self, activated=self._on_delete)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._on_save)
        QShortcut(QKeySequence("Escape"), self, activated=self._on_cancel)
        QShortcut(QKeySequence("F5"), self, activated=lambda: self.reload())

        self.set_state(False)
        self.reload()

    def _filter_table(self, text: str):
        """Filter table rows by search text."""
        text = text.lower()
        for r in range(self.tbl.rowCount()):
            match = False
            for c in range(self.tbl.columnCount()):
                item = self.tbl.item(r, c)
                if item and text in item.text().lower():
                    match = True
                    break
            self.tbl.setRowHidden(r, not match)

    # ---------- helpers to override ----------
    def record_from_ui(self) -> dict:
        if self._rec_from_ui:
            return self._rec_from_ui()
        rec = {}
        for f in self.cfg.fields:
            rec[f.name] = self.edits[f.name].text().strip()
        return rec

    def record_to_ui(self, rec: dict):
        if self._rec_to_ui:
            self._rec_to_ui(rec)
            return
        for f in self.cfg.fields:
            self.edits[f.name].setText(str(rec.get(f.name, "")))

    def grid_row_values(self, rec: dict) -> tuple:
        return tuple(str(rec.get(k, "")) for _, k in self.cfg.columns)

    # ---------- state machine (TopCtrl pattern) ----------
    def set_state(self, enabled: bool):
        p = _theme.palette()
        for e in self.edits.values():
            e.setEnabled(enabled)
        for b in (self.btnNew, self.btnEdit, self.btnDelete):
            b.setEnabled(not enabled)
        for b in (self.btnSave, self.btnCancel):
            b.setEnabled(enabled)
        self.state = ("Add" if self.edit_pk is None else "Edit") if enabled \
            else "Idle"
        state_colors = {
            "Idle": p.get("text_dim", "#64748b"),
            "Add": p.get("success", "#059669"),
            "Edit": p.get("warning", "#d97706"),
        }
        color = state_colors.get(self.state, p["text_dim"])
        self.lblState.setText(f"  State: {self.state}")
        self.lblState.setStyleSheet(
            f"font-size: 11px; color: {color}; padding: 4px 0; "
            f"border-top: 1px solid {p['border']}; font-weight: 600;"
        )

    def _clear_fields(self):
        for f in self.cfg.fields:
            self.edits[f.name].setText(f.default)

    # ---------- data ----------
    def reload(self):
        rows = self.cfg.api.list_all()
        self.tbl.setRowCount(len(rows))
        p = _theme.palette()
        for r, rec in enumerate(rows):
            for c, val in enumerate(self.grid_row_values(rec)):
                it = QTableWidgetItem(val)
                it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
                it.setForeground(QColor(p["text"]))
                self.tbl.setItem(r, c, it)

    def _selected_pk(self):
        r = self.tbl.currentRow()
        if r < 0:
            return None
        col = next((i for i, (_, k) in enumerate(self.cfg.columns)
                    if k == self.cfg.pk_key), 0)
        item = self.tbl.item(r, col)
        return item.text() if item else None

    # ---------- handlers ----------
    def _on_new(self):
        self.edit_pk = None
        self._clear_fields()
        self.set_state(True)
        next(iter(self.edits.values())).setFocus()

    def _on_edit(self):
        pk = self._selected_pk()
        if not pk:
            QMessageBox.information(self, "Edit",
                                    "Please select a record to edit")
            return
        rec = self.cfg.api.get(pk)
        if not rec:
            return
        self.edit_pk = pk
        self.record_to_ui(rec)
        pk_edit = self.edits.get(self.cfg.pk_key)
        if pk_edit:
            pk_edit.setEnabled(False)
        self.set_state(True)
        self.state = "Edit"
        self.lblState.setText("  State: Edit")
        if pk_edit:
            pk_edit.setEnabled(False)

    def _on_save(self):
        try:
            rec = self.record_from_ui()
            pk = rec.get(self.cfg.pk_key, "").strip()
            if not pk:
                QMessageBox.warning(self, "Validation",
                                    f"{self.cfg.pk_key.upper()} is required")
                return
            # Validate required fields
            for f in self.cfg.fields:
                if f.required and not rec.get(f.name, "").strip():
                    QMessageBox.warning(self, "Validation",
                                        f"{f.label} is required")
                    self.edits[f.name].setFocus()
                    return
            if self.state == "Add":
                if self.cfg.api.exists(pk):
                    QMessageBox.warning(self, "Validation",
                                        f"{pk} already exists")
                    return
                self.cfg.api.insert(rec)
            else:
                self.cfg.api.update(self.edit_pk, rec)
        except ValueError as e:
            QMessageBox.warning(self, "Save", str(e))
            return
        except Exception as e:
            QMessageBox.critical(self, "Database Error",
                                 f"Unable to save: {e}")
            return
        self.edit_pk = None
        self.set_state(False)
        self.reload()

    def _on_cancel(self):
        self.edit_pk = None
        self._clear_fields()
        self.set_state(False)

    def _on_delete(self):
        pk = self._selected_pk()
        if not pk:
            QMessageBox.information(self, "Delete",
                                    "Please select a record to delete")
            return
        if self.cfg.delete_guard:
            err = self.cfg.delete_guard(pk)
            if err:
                QMessageBox.warning(self, "Delete", err)
                return
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{pk}'?\n\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.cfg.api.delete(pk)
                self.reload()
            except Exception as e:
                QMessageBox.critical(self, "Delete Error",
                                     f"Unable to delete: {e}")


def make_delete_guard(sample_prefix: str = "PYT"):
    """Safety: production records protected, sirf test-prefix deletable."""
    def guard(pk: str):
        if not pk.upper().startswith(sample_prefix.upper()):
            return (f"Safety: only {sample_prefix}* test-records can be deleted "
                    "(production data is protected)")
        return None
    return guard
