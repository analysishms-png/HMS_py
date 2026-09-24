"""Tax Structure Master UI (VB6: FrmTaxStruMast - Main Setup -> General Setup).

Structure: Header (Code, Name) + Grid lines (Sno, TaxCode, Nature, Rate, Limit, Limit1, CondApp, CompOperator, TaxBeforeDisc).

VB6 FrmTaxStruMast: FGrid for lines, TopCtrl for header, DGHelp/DGTaxMast for lookups.

This implementation: Custom form with header fields + editable grid for lines."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QApplication, QComboBox, QDateEdit, QDialog,
                             QFormLayout, QHBoxLayout, QLabel, QLineEdit,
                             QMessageBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)

from HMS_py.core import taxstru
from HMS_py.ui.base_master import make_delete_guard
from HMS_py.ui import theme as _theme


class TaxStruForm(QDialog):
    """Tax Structure Master - Header + Lines grid."""

    LINE_COLS = [
        ("SNo", "sno"), ("Tax Code", "taxcode"), ("Nature", "nature"),
        ("Rate %", "rate"), ("Limit", "limit"), ("Limit1", "limit1"),
        ("Cond Apply", "condapp"), ("Comp Operator", "compop"),
        ("Tax Before Disc", "taxbeforedisc"),
    ]

    NATURES = ["On Base Amt", "On Running Total", "On Prev. Tax Amt"]
    COND_APPS = ["", "<", "<=", ">", ">=", "=", "Between"]
    TAX_BEFORE_DISC = ["No", "Yes"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tax Structure Master - HMS_py")
        self.resize(1100, 650)
        self.state = "Idle"
        self.edit_code = None
        self._tax_codes = []  # cached from RevMast

        root = QVBoxLayout(self)

        # ---- Header fields ----
        header_wrap = QWidget()
        header_form = QFormLayout(header_wrap)

        self.ed_code = QLineEdit()
        self.ed_code.setMaxLength(taxstru.LIMITS["code"])
        self.ed_name = QLineEdit()
        self.ed_name.setMaxLength(taxstru.LIMITS["name"])

        header_form.addRow("Structure Code (KK####)", self.ed_code)
        header_form.addRow("Structure Name", self.ed_name)
        root.addWidget(header_wrap)

        # ---- Lines grid ----
        self.grid = QTableWidget(0, len(self.LINE_COLS))
        self.grid.setHorizontalHeaderLabels([c[0] for c in self.LINE_COLS])
        self.grid.setAlternatingRowColors(True)
        self.grid.horizontalHeader().setStretchLastSection(True)
        # Make grid editable
        self.grid.cellChanged.connect(self._on_cell_changed)
        root.addWidget(self.grid)

# ---- Status label ----
        self.lbl_state = QLabel("State: Idle | New: Ctrl+N | Edit: Ctrl+E | Save: Ctrl+S | Delete: Ctrl+D")
        self.lbl_state.setStyleSheet(f"color:{_theme.palette()['text']}; padding:4px; background:{_theme.palette()['glass_tint']};")
        root.addWidget(self.lbl_state)

        # ---- Buttons ----
        btns = QHBoxLayout()
        self.btn_new = QPushButton("New (Ctrl+N)")
        self.btn_new.setToolTip("Add new tax structure")
        self.btn_edit = QPushButton("Edit (Ctrl+E)")
        self.btn_edit.setToolTip("Edit existing tax structure")
        self.btn_delete = QPushButton("Delete (Ctrl+D)")
        self.btn_delete.setToolTip("Delete tax structure")
        self.btn_save = QPushButton("Save (Ctrl+S)")
        self.btn_save.setToolTip("Save changes")
        self.btn_cancel = QPushButton("Cancel (Esc)")
        self.btn_cancel.setToolTip("Cancel current operation")
        self.btn_close = QPushButton("Close")
        self.btn_close.setToolTip("Close this window")
        for b in (self.btn_new, self.btn_edit, self.btn_delete,
                  self.btn_save, self.btn_cancel, self.btn_close):
            btns.addWidget(b)
        root.addLayout(btns)

        # Signals
        self.btn_new.clicked.connect(self._on_new)
        self.btn_edit.clicked.connect(self._on_edit)
        self.btn_delete.clicked.connect(self._on_delete)
        self.btn_save.clicked.connect(self._on_save)
        self.btn_cancel.clicked.connect(self._on_cancel)
        self.btn_close.clicked.connect(self.reject)

        # Keyboard shortcuts
        from PyQt6.QtGui import QShortcut, QKeySequence
        QShortcut(QKeySequence("Ctrl+N"), self, activated=self._on_new)
        QShortcut(QKeySequence("Ctrl+E"), self, activated=self._on_edit)
        QShortcut(QKeySequence("Ctrl+D"), self, activated=self._on_delete)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._on_save)
        QShortcut(QKeySequence("Escape"), self, activated=self._on_cancel)
        QShortcut(QKeySequence("F5"), self, activated=self.reload)

        # Load tax codes for dropdown
        self._load_tax_codes()

        self.set_state(False)
        self.reload()

    def _load_tax_codes(self):
        """Load tax codes from RevMast for dropdown."""
        try:
            self._tax_codes = taxstru.get_tax_codes()
        except Exception as e:
            self._tax_codes = []
            QMessageBox.warning(self, "Tax Codes", f"Could not load tax codes: {e}")

    def _tax_code_combo(self) -> QComboBox:
        """Create a combo box with tax codes."""
        combo = QComboBox()
        combo.setEditable(True)
        for tc in self._tax_codes:
            combo.addItem(f"{tc['code']} - {tc['name']}", tc['code'])
        return combo

    def _nature_combo(self) -> QComboBox:
        combo = QComboBox()
        combo.addItems(self.NATURES)
        return combo

    def _condapp_combo(self) -> QComboBox:
        combo = QComboBox()
        combo.addItems(self.COND_APPS)
        return combo

    def _taxbeforedisc_combo(self) -> QComboBox:
        combo = QComboBox()
        combo.addItems(self.TAX_BEFORE_DISC)
        return combo

    def _empty_line_row(self, sno: int) -> dict:
        """Create an empty line dict for given SNo."""
        return {
            "sno": sno,
            "taxcode": "",
            "nature": "On Base Amt",
            "rate": 0.0,
            "limit": 0.0,
            "limit1": 0.0,
            "condapp": "",
            "compop": "",
            "taxbeforedisc": "No",
        }

    def _populate_grid(self, lines: list[dict]):
        """Fill grid with lines."""
        self.grid.blockSignals(True)
        self.grid.setRowCount(len(lines))
        for r, line in enumerate(lines):
            self._set_grid_row(r, line)
        # Add one empty row for adding new lines
        if lines:
            self.grid.insertRow(len(lines))
            self._set_grid_row(len(lines), self._empty_line_row(len(lines) + 1))
        self.grid.blockSignals(False)

    def _set_grid_row(self, row: int, line: dict):
        """Set a single grid row with editors where needed."""
        # SNo (read-only)
        sno_item = QTableWidgetItem(str(line.get("sno", row + 1)))
        sno_item.setFlags(sno_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        sno_item.setForeground(QColor(_theme.palette()["text"]))
        self.grid.setItem(row, 0, sno_item)

        # TaxCode - combo
        combo = self._tax_code_combo()
        idx = combo.findData(line.get("taxcode", ""))
        if idx >= 0:
            combo.setCurrentIndex(idx)
        self.grid.setCellWidget(row, 1, combo)

        # Nature - combo
        combo = self._nature_combo()
        idx = combo.findText(line.get("nature", "On Base Amt"))
        if idx >= 0:
            combo.setCurrentIndex(idx)
        self.grid.setCellWidget(row, 2, combo)

        # Rate
        rate_item = QTableWidgetItem(str(line.get("rate", 0)))
        rate_item.setForeground(QColor(_theme.palette()["text"]))
        self.grid.setItem(row, 3, rate_item)

        # Limit
        limit_item = QTableWidgetItem(str(line.get("limit", 0)))
        limit_item.setForeground(QColor(_theme.palette()["text"]))
        self.grid.setItem(row, 4, limit_item)

        # Limit1
        limit1_item = QTableWidgetItem(str(line.get("limit1", 0)))
        limit1_item.setForeground(QColor(_theme.palette()["text"]))
        self.grid.setItem(row, 5, limit1_item)

        # CondApp - combo
        combo = self._condapp_combo()
        idx = combo.findText(line.get("condapp", ""))
        if idx >= 0:
            combo.setCurrentIndex(idx)
        self.grid.setCellWidget(row, 6, combo)

        # CompOperator
        compop_item = QTableWidgetItem(line.get("compop", ""))
        compop_item.setForeground(QColor(_theme.palette()["text"]))
        self.grid.setItem(row, 7, compop_item)

        # TaxBeforeDisc - combo
        combo = self._taxbeforedisc_combo()
        idx = combo.findText(line.get("taxbeforedisc", "No"))
        if idx >= 0:
            combo.setCurrentIndex(idx)
        self.grid.setCellWidget(row, 8, combo)

    def _get_grid_lines(self) -> list[dict]:
        """Extract lines from grid.

        BUG-018 fix: pehle invalid rows silently skip ho rahi thi —
        ab validation error raise hota hai taaki user ka data na ude.
        """
        lines = []
        for r in range(self.grid.rowCount()):
            sno_item = self.grid.item(r, 0)
            if not sno_item or not sno_item.text().strip():
                continue
            try:
                sno = int(sno_item.text())
            except ValueError:
                raise ValueError(
                    f"Row {r + 1}: SNo '{sno_item.text()}' valid number nahi hai")

            # TaxCode from combo
            combo = self.grid.cellWidget(r, 1)
            taxcode = combo.currentData() if combo else ""

            # Nature from combo
            combo = self.grid.cellWidget(r, 2)
            nature = combo.currentText() if combo else "On Base Amt"

            # Rate
            rate_item = self.grid.item(r, 3)
            try:
                rate = float(rate_item.text() if rate_item else 0)
            except ValueError:
                raise ValueError(
                    f"Row {r + 1}: Rate '{rate_item.text() if rate_item else ''}' valid number nahi hai")

            # Limit
            limit_item = self.grid.item(r, 4)
            try:
                limit = float(limit_item.text() if limit_item else 0)
            except ValueError:
                raise ValueError(
                    f"Row {r + 1}: Limit '{limit_item.text() if limit_item else ''}' valid number nahi hai")

            # Limit1
            limit1_item = self.grid.item(r, 5)
            try:
                limit1 = float(limit1_item.text() if limit1_item else 0)
            except ValueError:
                raise ValueError(
                    f"Row {r + 1}: Limit1 '{limit1_item.text() if limit1_item else ''}' valid number nahi hai")

            # CondApp from combo
            combo = self.grid.cellWidget(r, 6)
            condapp = combo.currentText() if combo else ""

            # CompOperator
            compop_item = self.grid.item(r, 7)
            compop = compop_item.text() if compop_item else ""

            # TaxBeforeDisc from combo
            combo = self.grid.cellWidget(r, 8)
            taxbeforedisc = combo.currentText() if combo else "No"

            if taxcode:  # Only include lines with tax code
                lines.append({
                    "sno": sno,
                    "taxcode": taxcode,
                    "nature": nature,
                    "rate": rate,
                    "limit": limit,
                    "limit1": limit1,
                    "condapp": condapp,
                    "compop": compop,
                    "taxbeforedisc": taxbeforedisc,
                })
        return lines

    def _on_cell_changed(self, row: int, col: int):
        """Handle cell changes - auto-add row when last row gets data."""
        if col == 1:  # TaxCode column
            combo = self.grid.cellWidget(row, 1)
            if combo and combo.currentData():
                # Check if this is the last row and has data
                if row == self.grid.rowCount() - 1:
                    # Add new empty row
                    self.grid.blockSignals(True)
                    self.grid.insertRow(row + 1)
                    self._set_grid_row(row + 1, self._empty_line_row(row + 2))
                    self.grid.blockSignals(False)

    def reload(self):
        """Load all tax structures."""
        try:
            all_lines = taxstru.list_all()
            # Group by code
            structures = {}
            for line in all_lines:
                code = line["code"]
                if code not in structures:
                    structures[code] = {"name": line["name"], "lines": []}
                structures[code]["lines"].append(line)

            # For now, show first structure or empty
            if structures and not self.edit_code:
                first_code = next(iter(structures))
                self._load_structure(first_code, structures[first_code])
            elif self.edit_code and self.edit_code in structures:
                self._load_structure(self.edit_code, structures[self.edit_code])
            else:
                self._clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Reload Error", str(e))

    def _load_structure(self, code: str, struct: dict):
        """Load a specific structure into form."""
        self.edit_code = code
        self.ed_code.setText(code)
        self.ed_name.setText(struct["name"])
        # Sort lines by sno
        lines = sorted(struct["lines"], key=lambda x: x["sno"])
        self._populate_grid(lines)

    def _clear_form(self):
        self.edit_code = None
        self.ed_code.clear()
        self.ed_name.clear()
        self.grid.setRowCount(0)
        # Add one empty row
        self.grid.insertRow(0)
        self._set_grid_row(0, self._empty_line_row(1))

    def set_state(self, enabled: bool):
        """TopCtrl pattern state machine."""
        self.ed_code.setEnabled(enabled)
        self.ed_name.setEnabled(enabled)
        # Grid editing controlled by enabled
        for r in range(self.grid.rowCount()):
            for c in range(self.grid.columnCount()):
                item = self.grid.item(r, c)
                if item:
                    item.setFlags(
                        (item.flags() | Qt.ItemFlag.ItemIsEditable) if enabled
                        else (item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    )
                widget = self.grid.cellWidget(r, c)
                if widget:
                    widget.setEnabled(enabled)

        self.btn_new.setEnabled(not enabled)
        self.btn_edit.setEnabled(not enabled)
        self.btn_delete.setEnabled(not enabled)
        self.btn_save.setEnabled(enabled)
        self.btn_cancel.setEnabled(enabled)

        self.state = ("Add" if self.edit_code is None else "Edit") if enabled else "Idle"
        self.lbl_state.setText(f"State: {self.state}")

    def _on_new(self):
        self.edit_code = None
        self._clear_form()
        self.set_state(True)
        self.ed_code.setText(taxstru.next_code())
        self.ed_code.setFocus()

    def _on_edit(self):
        # For now, show a dialog to pick structure to edit
        from PyQt6.QtWidgets import QInputDialog
        structs = taxstru.get_structures_summary()
        if not structs:
            QMessageBox.information(self, "Edit", "No structures to edit")
            return
        names = [f"{s['code']} - {s['name']}" for s in structs]
        code, ok = QInputDialog.getItem(self, "Edit Structure", "Select:", names, 0, False)
        if ok and code:
            sel_code = code.split(" - ")[0]
            lines = taxstru.list_by_code(sel_code)
            if lines:
                self._load_structure(sel_code, {"name": lines[0]["name"], "lines": lines})
                self.set_state(True)
                self.ed_code.setEnabled(False)  # PK not editable in edit mode

    def _on_save(self):
        code = self.ed_code.text().strip()
        name = self.ed_name.text().strip()
        if not code:
            QMessageBox.warning(self, "Save", "Structure Code zaroori hai")
            return
        if not name:
            QMessageBox.warning(self, "Save", "Structure Name zaroori hai")
            return

        lines = self._get_grid_lines()
        if not lines:
            QMessageBox.warning(self, "Save", "At least one tax line required")
            return

        try:
            if self.state == "Add":
                if taxstru.exists_code(code):
                    QMessageBox.warning(self, "Save", f"{code} pehle se maujood hai")
                    return
                taxstru.insert_structure(code, name, lines)
            else:
                taxstru.update_structure(code, name, lines)
            QMessageBox.information(self, "Save", "Tax Structure saved successfully")
            self.set_state(False)
            self.reload()
        except ValueError as e:
            # BUG-018 fix: grid validation errors ab user ko dikhengi
            # (pehle save fail hota tha bina wajah bataye)
            QMessageBox.warning(self, "Save", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Save", f"DB error: {e}")

    def _on_cancel(self):
        self.set_state(False)
        self.reload()

    def _on_delete(self):
        if not self.edit_code:
            QMessageBox.information(self, "Delete", "Pehe structure select/edit karein")
            return
        err = make_delete_guard("PYT")(self.edit_code)
        if err:
            QMessageBox.warning(self, "Delete", err)
            return
        if QMessageBox.question(self, "Delete",
                f"Tax Structure '{self.edit_code}' delete karein? (All lines will be removed)") \
                != QMessageBox.StandardButton.Yes:
            return
        try:
            taxstru.delete_structure(self.edit_code)
            QMessageBox.information(self, "Delete", "Deleted successfully")
            self.reload()
        except Exception as e:
            QMessageBox.critical(self, "Delete", f"DB error: {e}")


def open_taxstru(parent=None):
    TaxStruForm(parent).exec()


def main() -> int:
    app = QApplication(sys.argv)
    w = TaxStruForm()
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())