"""KOT Entry UI (VB6: RsKOTEntry - Front Office -> POS -> KOT Entry).

VB6 pattern:
- FGrid for item lines (item, qty, rate, amount, table, waiter, nc_type)
- Lookups: DGItem (items), DGTable (tables), DGWaiter (waiters), DGNCType
- TopCtrl1 state machine: Add/Edit/Browse
- Buttons: Print, Save, Void, Member, Member Card, etc.
- Outlet selection via DGRest

This implementation: Custom form with header (outlet, date, waiter) + editable grid for lines."""
from __future__ import annotations

import os
import sys
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QApplication, QComboBox, QDateEdit, QDialog,
                             QFormLayout, QHBoxLayout, QLabel, QLineEdit,
                             QMessageBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)

from HMS_py.core import pos
from HMS_py.ui.base_master import make_delete_guard
from HMS_py.ui import theme as _theme


class KOTEntryForm(QDialog):
    """KOT Entry - VB6 RsKOTEntry pattern."""

    LINE_COLS = [
        ("SNo", "sno"), ("Item Code", "item"), ("Item Name", "name"),
        ("Qty", "qty"), ("Unit", "unit"), ("Rate", "rate"),
        ("Amount", "amount"), ("Table", "table"), ("Waiter", "waiter"),
        ("NC Type", "nc_type"), ("Remarks", "remarks"),
    ]

    def __init__(self, parent=None, user: str = "SA"):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("KOT Entry (P5) - HMS_py")
        self.resize(1200, 700)
        self.state = "Idle"
        self.edit_docid = None
        self._tax_codes = []

        root = QVBoxLayout(self)

        # ---- Header fields ----
        header_wrap = QWidget()
        header_form = QFormLayout(header_wrap)

        self.cb_outlet = QComboBox()
        self.de_vdate = QDateEdit(date.today())
        self.de_vdate.setCalendarPopup(True)
        self.cb_waiter = QComboBox()

        header_form.addRow("Outlet *", self.cb_outlet)
        header_form.addRow("Date", self.de_vdate)
        header_form.addRow("Waiter", self.cb_waiter)
        root.addWidget(header_wrap)

        # ---- Lines grid ----
        self.grid = QTableWidget(0, len(self.LINE_COLS))
        self.grid.setHorizontalHeaderLabels([c[0] for c in self.LINE_COLS])
        self.grid.horizontalHeader().setStretchLastSection(True)
        self.grid.setAlternatingRowColors(True)
        self.grid.cellChanged.connect(self._on_cell_changed)
        root.addWidget(self.grid)

        # ---- Status label ----
        self.lbl_state = QLabel("State: Idle | New: Ctrl+N | Save: Ctrl+S | Void: Ctrl+D")
        _st = _theme.status_colors()
        self.lbl_state.setStyleSheet(
            f"color:{_st['neutral_text']}; font-weight:bold; padding:4px;"
            f"background:{_st['neutral_bg']}; border-radius:6px;")
        root.addWidget(self.lbl_state)

        # ---- Buttons ----
        btns = QHBoxLayout()
        self.btn_new = QPushButton("New (Ctrl+N)")
        self.btn_new.setToolTip("Start a new KOT entry (Ctrl+N)")
        self.btn_save = QPushButton("Save (Ctrl+S)")
        self.btn_save.setToolTip("Save the current KOT (Ctrl+S)")
        self.btn_void = QPushButton("Void (Ctrl+D)")
        self.btn_void.setToolTip("Void the current KOT (Ctrl+D)")
        self.btn_print = QPushButton("Print KOT")
        self.btn_print.setToolTip("Print the current KOT")
        self.btn_cancel = QPushButton("Cancel (Esc)")
        self.btn_cancel.setToolTip("Cancel editing and reset form (Esc)")
        self.btn_close = QPushButton("Close")
        self.btn_close.setToolTip("Close the KOT Entry form")
        for b in (self.btn_new, self.btn_save, self.btn_void,
                  self.btn_print, self.btn_cancel, self.btn_close):
            btns.addWidget(b)
        root.addLayout(btns)

        # Signals
        self.btn_new.clicked.connect(self._on_new)
        self.btn_save.clicked.connect(self._on_save)
        self.btn_void.clicked.connect(self._on_void)
        self.btn_print.clicked.connect(self._on_print)
        self.btn_cancel.clicked.connect(self._on_cancel)
        self.btn_close.clicked.connect(self.reject)
        self.cb_outlet.currentIndexChanged.connect(self._on_outlet_changed)

        # Keyboard shortcuts
        from PyQt6.QtGui import QShortcut, QKeySequence
        QShortcut(QKeySequence("Ctrl+N"), self, activated=self._on_new)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._on_save)
        QShortcut(QKeySequence("Ctrl+D"), self, activated=self._on_void)
        QShortcut(QKeySequence("Escape"), self, activated=self._on_cancel)
        QShortcut(QKeySequence("F5"), self, activated=self.reload)

        # Load lookup data
        self._load_lookups()

        self.set_state(False)
        self.reload()

    def _load_lookups(self):
        """Load outlets, waiters, nc_types."""
        try:
            outlets = pos.get_outlets()
            self.cb_outlet.clear()
            for o in outlets:
                self.cb_outlet.addItem(f"{o['code']} - {o['name']}", o['code'])
            
            waiters = pos.get_waiters()
            self.cb_waiter.clear()
            self.cb_waiter.addItem("", "")
            for w in waiters:
                self.cb_waiter.addItem(f"{w['code']} - {w['name']}", w['code'])
            
            nc_types = pos.get_nc_types()
            self._nc_types = nc_types
        except Exception as e:
            QMessageBox.warning(self, "Lookups", f"Could not load lookup data: {e}")

    def _on_outlet_changed(self, idx: int):
        """Reload tables and items when outlet changes."""
        outlet_code = self.cb_outlet.currentData()
        if not outlet_code:
            return
        try:
            # Update tables combo (column 7 - Table)
            tables = pos.get_tables(outlet_code)
            self._tables = tables
            
            # Update items for item column combo
            items = pos.get_items(outlet_code)
            self._items = items
        except Exception as e:
            QMessageBox.warning(self, "Outlet Change", f"Could not load tables/items: {e}")

    def _get_table_combo(self) -> QComboBox:
        combo = QComboBox()
        combo.addItem("", "")
        for t in getattr(self, '_tables', []):
            combo.addItem(f"{t['code']} - {t['name']}", t['code'])
        return combo

    def _get_item_combo(self) -> QComboBox:
        combo = QComboBox()
        combo.addItem("", "")
        combo.setEditable(True)
        for it in getattr(self, '_items', []):
            combo.addItem(f"{it['code']} - {it['name']}", it['code'])
        return combo

    def _get_nc_type_combo(self) -> QComboBox:
        combo = QComboBox()
        combo.addItem("", "")
        for nc in getattr(self, '_nc_types', []):
            combo.addItem(f"{nc['code']} - {nc['name']}", nc['code'])
        return combo

    def _get_waiter_combo(self) -> QComboBox:
        combo = QComboBox()
        combo.addItem("", "")
        for w in pos.get_waiters():
            combo.addItem(f"{w['code']} - {w['name']}", w['code'])
        return combo

    def _empty_line_row(self, sno: int) -> dict:
        return {
            "sno": sno, "item": "", "name": "", "qty": 0, "unit": "",
            "rate": 0, "amount": 0, "table": "", "waiter": "",
            "nc_type": "", "remarks": "",
        }

    def _populate_grid(self, lines: list[dict]):
        self.grid.blockSignals(True)
        self.grid.setRowCount(len(lines))
        for r, line in enumerate(lines):
            self._set_grid_row(r, line)
        # Add one empty row for adding
        if lines:
            self.grid.insertRow(len(lines))
            self._set_grid_row(len(lines), self._empty_line_row(len(lines) + 1))
        self.grid.blockSignals(False)

    def _set_grid_row(self, row: int, line: dict):
        # SNo (read-only)
        sno_item = QTableWidgetItem(str(line.get("sno", row + 1)))
        sno_item.setFlags(sno_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        sno_item.setForeground(QColor(_theme.palette()["text"]))
        self.grid.setItem(row, 0, sno_item)

        # Item Code - combo
        combo = self._get_item_combo()
        idx = combo.findData(line.get("item", ""))
        if idx >= 0:
            combo.setCurrentIndex(idx)
        self.grid.setCellWidget(row, 1, combo)

        # Item Name (read-only, auto-filled)
        name_item = QTableWidgetItem(line.get("name", ""))
        name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        name_item.setForeground(QColor(_theme.palette()["text"]))
        self.grid.setItem(row, 2, name_item)

        # Qty
        qty_item = QTableWidgetItem(str(line.get("qty", 0)))
        qty_item.setForeground(QColor(_theme.palette()["text"]))
        self.grid.setItem(row, 3, qty_item)

        # Unit (read-only)
        unit_item = QTableWidgetItem(line.get("unit", ""))
        unit_item.setFlags(unit_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        unit_item.setForeground(QColor(_theme.palette()["text"]))
        self.grid.setItem(row, 4, unit_item)

        # Rate
        rate_item = QTableWidgetItem(str(line.get("rate", 0)))
        rate_item.setForeground(QColor(_theme.palette()["text"]))
        self.grid.setItem(row, 5, rate_item)

        # Amount (read-only)
        amt_item = QTableWidgetItem(str(line.get("amount", 0)))
        amt_item.setFlags(amt_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        amt_item.setForeground(QColor(_theme.palette()["text"]))
        self.grid.setItem(row, 6, amt_item)

        # Table - combo
        combo = self._get_table_combo()
        idx = combo.findData(line.get("table", ""))
        if idx >= 0:
            combo.setCurrentIndex(idx)
        self.grid.setCellWidget(row, 7, combo)

        # Waiter - combo
        combo = self._get_waiter_combo()
        idx = combo.findData(line.get("waiter", ""))
        if idx >= 0:
            combo.setCurrentIndex(idx)
        self.grid.setCellWidget(row, 8, combo)

        # NC Type - combo
        combo = self._get_nc_type_combo()
        idx = combo.findData(line.get("nc_type", ""))
        if idx >= 0:
            combo.setCurrentIndex(idx)
        self.grid.setCellWidget(row, 9, combo)

        # Remarks
        rem_item = QTableWidgetItem(line.get("remarks", ""))
        rem_item.setForeground(QColor(_theme.palette()["text"]))
        self.grid.setItem(row, 10, rem_item)

    def _on_cell_changed(self, row: int, col: int):
        """Handle cell changes - auto-calc amount, auto-fill name/unit from item."""
        # Item selection changed
        if col == 1:
            combo = self.grid.cellWidget(row, 1)
            if combo:
                item_code = combo.currentData()
                if item_code:
                    # Find item details
                    for it in getattr(self, '_items', []):
                        if it['code'] == item_code:
                            # Update name
                            name_item = self.grid.item(row, 2)
                            if name_item:
                                name_item.setText(it['name'])
                            # Update unit
                            unit_item = self.grid.item(row, 4)
                            if unit_item:
                                unit_item.setText(it['unit'])
                            # Update rate if not set (BUG-019: parse failure pe
                            # bhi overwrite karo, otherwise invalid text"0" ban jata hai)
                            rate_item = self.grid.item(row, 5)
                            if rate_item:
                                try:
                                    cur_rate = float(rate_item.text() or 0)
                                except ValueError:
                                    cur_rate = 0.0
                                if cur_rate == 0:
                                    rate_item.setText(str(it['rate']))
                            break
        
        # Auto-calc amount when qty or rate changes
        if col in (3, 5):  # Qty or Rate
            qty_item = self.grid.item(row, 3)
            rate_item = self.grid.item(row, 5)
            amt_item = self.grid.item(row, 6)
            if qty_item and rate_item and amt_item:
                try:
                    qty = float(qty_item.text() or 0)
                    rate = float(rate_item.text() or 0)
                    amt_item.setText(str(round(qty * rate, 2)))
                except ValueError:
                    amt_item.setText("0")
        
        # Auto-add row when last row gets item
        if col == 1:
            combo = self.grid.cellWidget(row, 1)
            if combo and combo.currentData():
                if row == self.grid.rowCount() - 1:
                    self.grid.blockSignals(True)
                    self.grid.insertRow(row + 1)
                    self._set_grid_row(row + 1, self._empty_line_row(row + 2))
                    self.grid.blockSignals(False)

    def _get_grid_lines(self) -> list[dict]:
        lines = []
        for r in range(self.grid.rowCount()):
            sno_item = self.grid.item(r, 0)
            if not sno_item or not sno_item.text().strip():
                continue
            try:
                sno = int(sno_item.text())
            except ValueError:
                # BUG-019 fix: invalid SNo silently skip mat karo -
                # user ko batao kaunsi row invalid hai
                raise ValueError(f"Row {r + 1}: SNo '{sno_item.text()}' valid number nahi hai")

            # Item from combo
            combo = self.grid.cellWidget(r, 1)
            item_code = combo.currentData() if combo else ""

            if not item_code:
                continue

            # Name
            name_item = self.grid.item(r, 2)
            name = name_item.text() if name_item else ""

            # Qty
            qty_item = self.grid.item(r, 3)
            try:
                qty = float(qty_item.text() or 0)
            except ValueError:
                raise ValueError(f"Row {r + 1}: Qty '{qty_item.text()}' valid number nahi hai")

            # Unit
            unit_item = self.grid.item(r, 4)
            unit = unit_item.text() if unit_item else ""

            # Rate
            rate_item = self.grid.item(r, 5)
            try:
                rate = float(rate_item.text() or 0)
            except ValueError:
                raise ValueError(f"Row {r + 1}: Rate '{rate_item.text()}' valid number nahi hai")

            # Amount
            amt_item = self.grid.item(r, 6)
            try:
                amount = float(amt_item.text() or 0)
            except ValueError:
                amount = 0

            # Table from combo
            combo = self.grid.cellWidget(r, 7)
            table = combo.currentData() if combo else ""

            # Waiter from combo
            combo = self.grid.cellWidget(r, 8)
            waiter = combo.currentData() if combo else ""

            # NC Type from combo
            combo = self.grid.cellWidget(r, 9)
            nc_type = combo.currentData() if combo else ""

            # Remarks
            rem_item = self.grid.item(r, 10)
            remarks = rem_item.text() if rem_item else ""

            if item_code:
                lines.append({
                    "sno": sno, "item": item_code, "name": name,
                    "qty": qty, "unit": unit, "rate": rate, "amount": amount,
                    "table": table, "waiter": waiter, "nc_type": nc_type,
                    "remarks": remarks, "outlet": self.cb_outlet.currentData(),
                })
        return lines

    def reload(self):
        """Reload KOT list (not implemented for entry form - shows empty/new)."""
        self._clear_form()

    def _clear_form(self):
        self.edit_docid = None
        self.cb_outlet.setCurrentIndex(0)
        self.de_vdate.setDate(date.today())
        self.cb_waiter.setCurrentIndex(0)
        self.grid.setRowCount(0)
        self.grid.insertRow(0)
        self._set_grid_row(0, self._empty_line_row(1))

    def set_state(self, enabled: bool):
        self.cb_outlet.setEnabled(enabled)
        self.de_vdate.setEnabled(enabled)
        self.cb_waiter.setEnabled(enabled)
        
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
        self.btn_save.setEnabled(enabled)
        self.btn_void.setEnabled(not enabled and self.edit_docid is not None)
        self.btn_print.setEnabled(not enabled and self.edit_docid is not None)
        self.btn_cancel.setEnabled(enabled)

        self.state = "Add" if enabled and self.edit_docid is None else \
                       "Edit" if enabled else "Idle"
        self.lbl_state.setText(f"State: {self.state}")
        # State-aware color: Add/Edit = accent tint (active work),
        # Idle = neutral (status palette se, theme-synced).
        st = _theme.status_colors()
        if self.state == "Idle":
            bg, fg = st["neutral_bg"], st["neutral_text"]
        else:
            t = _theme.palette()
            bg, fg = t["accent_soft"], t["text"]
        self.lbl_state.setStyleSheet(
            f"color:{fg}; font-weight:bold; padding:4px;"
            f"background:{bg}; border-radius:6px;")

    def _on_new(self):
        self.edit_docid = None
        self._clear_form()
        self.set_state(True)
        self.cb_outlet.setFocus()

    def _on_save(self):
        outlet = self.cb_outlet.currentData()
        if not outlet:
            QMessageBox.warning(self, "Save", "Outlet zaroori hai")
            return
        
        lines = self._get_grid_lines()
        if not lines:
            QMessageBox.warning(self, "Save", "At least one KOT line required")
            return

        vdate = self.de_vdate.date().toPyDate()
        waiter = self.cb_waiter.currentData() or ""

        try:
            if self.state == "Add":
                result = pos.create_kot(lines, outlet, vdate, waiter=waiter, user=self.user)
            else:
                result = pos.update_kot(self.edit_docid, lines, self.user)
                result = {"docid": self.edit_docid, "lines_inserted": len(lines)}

            QMessageBox.information(self, "Save",
                f"KOT saved: {result['docid']} ({result.get('vno', result.get('lines_inserted', 0))} lines)")
            self.set_state(False)
            self.reload()
        except ValueError as e:
            QMessageBox.warning(self, "Save", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Save", f"DB error: {e}")

    def _on_void(self):
        if not self.edit_docid:
            QMessageBox.information(self, "Void", "Pehe KOT select/edit karein")
            return
        
        if QMessageBox.question(self, "Void KOT",
                f"KOT {self.edit_docid} void karein?") != QMessageBox.StandardButton.Yes:
            return
        
        try:
            pos.void_kot(self.edit_docid, user=self.user)
            QMessageBox.information(self, "Void", "KOT voided successfully")
            self.reload()
        except Exception as e:
            QMessageBox.critical(self, "Void", f"DB error: {e}")

    def _on_print(self):
        if not self.edit_docid:
            QMessageBox.information(self, "Print", "Pehe KOT select karein")
            return
        QMessageBox.information(self, "Print", 
            f"KOT Print for {self.edit_docid} - not implemented yet (VB6 uses Crystal Reports)")

    def _on_cancel(self):
        self.set_state(False)
        self.reload()


def open_kot_entry(parent=None, user: str = "SA"):
    KOTEntryForm(parent, user=user).exec()


def main() -> int:
    app = QApplication(sys.argv)
    w = KOTEntryForm()
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())