"""Inventory UI (P5): Godown master + Indent/Purchase/Stock browsers + Document entry.

Run: python -m HMS_py.ui.inventory
Menu wiring: Inventory -> 'Indent'/'Pending Indent'/'Purchase Register'/
'Stock Summary'/'Stock Register'/'Purchase Register'. Godown master = full CRUD.
Documents: Indent, GIN (Purchase Receipt), Purchase Order, Stock Issue/Receive/Adjustment.
All with PYT* guard for test safety."""
from __future__ import annotations

import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QApplication, QComboBox, QDateEdit, QDialog,
                             QDoubleSpinBox, QFormLayout, QHBoxLayout, QLabel,
                             QLineEdit, QMessageBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)

from HMS_py.core import inventory as inv
from HMS_py.ui import theme as _theme
from HMS_py.ui.base_master import (BaseMasterForm, Field, MasterConfig,
                                   make_delete_guard)


def _dark_item(val) -> QTableWidgetItem:
    if isinstance(val, (datetime.date, datetime.datetime)):
        val = f"{val:%d/%b/%y}"
    it = QTableWidgetItem("" if val is None else str(val))
    it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
    it.setForeground(QColor(_theme.palette()["text"]))
    return it


def _combo(choices: list, current: str = "") -> QComboBox:
    cb = QComboBox()
    for code, name in choices:
        cb.addItem(f"{code} - {name}", code)
    if current:
        idx = cb.findData(current)
        if idx >= 0:
            cb.setCurrentIndex(idx)
    return cb


# ============================================================
# Godown Master
# ============================================================
def godown_config() -> MasterConfig:
    import types
    return MasterConfig(
        title="Godown Master (P5) - HMS_py",
        columns=[("Code", "code"), ("Name", "name"), ("Short", "short"),
                 ("Depart", "depart"), ("Sys", "sysyn")],
        fields=[
            Field("code", "Code", max_len=inv.LIMITS["code"], required=True),
            Field("name", "Name", max_len=inv.LIMITS["name"], required=True),
            Field("short", "ShortName", max_len=inv.LIMITS["short"]),
            Field("depart", "DepartCode (FK)", max_len=inv.LIMITS["depart"]),
            Field("sysyn", "Sys Y/N", max_len=1),
        ],
        api=types.SimpleNamespace(
            list_all=inv.godown_list,
            get=inv.godown_get,
            exists=inv.godown_exists,
            insert=lambda rec: inv.godown_insert(rec),
            update=lambda code, rec: inv.godown_update(code, rec),
            delete=lambda code: inv.godown_delete(code),
        ),
        pk_key="code",
        delete_guard=make_delete_guard("PYT"),
    )


def open_godown(parent=None):
    BaseMasterForm(godown_config(), parent).exec()


# ============================================================
# Indent Browser + Entry
# ============================================================
class IndentForm(QDialog):
    """Indent CRUD (VB6 PIndent pattern)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Indent Master (P5) - HMS_py")
        self.resize(900, 600)
        self.edit_docid = None
        self.state = "Idle"

        root = QVBoxLayout(self)

        # Header
        header = QWidget()
        hform = QFormLayout(header)
        self.cb_dept = QComboBox()
        self.de_vdate = QDateEdit(datetime.date.today())
        self.de_vdate.setCalendarPopup(True)
        self.cb_godown = QComboBox()
        self.ed_remarks = QLineEdit()
        self.ed_remarks.setPlaceholderText("Enter remarks")
        self.cb_clear = QComboBox()
        self.cb_clear.addItems(["N", "Y"])

        hform.addRow("Department *", self.cb_dept)
        hform.addRow("Date", self.de_vdate)
        hform.addRow("Godown", self.cb_godown)
        hform.addRow("Remarks", self.ed_remarks)
        hform.addRow("Cleared (Y/N)", self.cb_clear)
        root.addWidget(header)

        # Grid for browse
        self.tbl = QTableWidget(0, 5)
        self.tbl.setHorizontalHeaderLabels(["DocId", "VNo", "Date", "Department", "Cleared"])
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.cellDoubleClicked.connect(self._on_edit)
        root.addWidget(self.tbl)

        # PI-5: Indent1 line grid (VB6 PIndent FGrid pattern)
        lines_grp = QWidget()
        lines_lay = QVBoxLayout(lines_grp)
        lines_lay.setContentsMargins(0, 0, 0, 0)
        lines_lay.addWidget(QLabel("Indent Lines (Indent1)"))
        self.grid = QTableWidget(0, 5)
        self.grid.setHorizontalHeaderLabels(
            ["SNo", "Item Code", "Qty", "Unit", "Rate"])
        self.grid.horizontalHeader().setStretchLastSection(True)
        self.grid.setAlternatingRowColors(True)
        lines_lay.addWidget(self.grid)
        line_btns = QHBoxLayout()
        self.btn_add_line = QPushButton("Add Line (+)")
        self.btn_add_line.setToolTip("Add an indent line")
        self.btn_del_line = QPushButton("Remove Line (-)")
        self.btn_del_line.setToolTip("Remove selected indent line")
        line_btns.addWidget(self.btn_add_line)
        line_btns.addWidget(self.btn_del_line)
        line_btns.addStretch()
        lines_lay.addLayout(line_btns)
        root.addWidget(lines_grp)
        self.btn_add_line.clicked.connect(self._add_line)
        self.btn_del_line.clicked.connect(self._del_line)

        # Status
        self.lbl_state = QLabel("State: Idle | New: Ctrl+N | Edit: Ctrl+E | Save: Ctrl+S")
        self.lbl_state.setStyleSheet(f"color:{_theme.palette()['text']}; padding:4px; background:{_theme.palette()['glass_tint']};")
        root.addWidget(self.lbl_state)

        # Buttons
        btns = QHBoxLayout()
        self.btn_new = QPushButton("New (Ctrl+N)")
        self.btn_new.setToolTip("Create a new indent (Ctrl+N)")
        self.btn_edit = QPushButton("Edit (Ctrl+E)")
        self.btn_edit.setToolTip("Edit the selected indent (Ctrl+E)")
        self.btn_save = QPushButton("Save (Ctrl+S)")
        self.btn_save.setToolTip("Save the current indent (Ctrl+S)")
        self.btn_cancel = QPushButton("Cancel (Esc)")
        self.btn_cancel.setToolTip("Cancel editing and return to idle state (Esc)")
        self.btn_close = QPushButton("Close")
        self.btn_close.setToolTip("Close the indent form")
        for b in (self.btn_new, self.btn_edit, self.btn_save, self.btn_cancel, self.btn_close):
            btns.addWidget(b)
        root.addLayout(btns)

        self.btn_new.clicked.connect(self._on_new)
        self.btn_edit.clicked.connect(self._on_edit)
        self.btn_save.clicked.connect(self._on_save)
        self.btn_cancel.clicked.connect(self._on_cancel)
        self.btn_close.clicked.connect(self.reject)

        from PyQt6.QtGui import QShortcut, QKeySequence
        QShortcut(QKeySequence("Ctrl+N"), self, activated=self._on_new)
        QShortcut(QKeySequence("Ctrl+E"), self, activated=self._on_edit)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._on_save)
        QShortcut(QKeySequence("Escape"), self, activated=self._on_cancel)

        self._load_combos()
        self.set_state(False)
        self.reload()

    def _load_combos(self):
        # Departments
        from HMS_py.core import depart
        depts = depart.depart_list()
        self.cb_dept.clear()
        for d in depts:
            self.cb_dept.addItem(f"{d['code']} - {d['name']}", d['code'])
        # Godowns
        godowns = inv.godown_list()
        self.cb_godown.clear()
        for g in godowns:
            self.cb_godown.addItem(f"{g['code']} - {g['name']}", g['code'])

    def reload(self):
        rows = inv.indent_list()
        self.tbl.setRowCount(len(rows))
        for r, i in enumerate(rows):
            for c, v in enumerate([i["docid"], i["vno"], i["vdate"], i["dept"], i["clear"] or "N"]):
                self.tbl.setItem(r, c, _dark_item(v))

    def set_state(self, enabled: bool):
        self.cb_dept.setEnabled(enabled)
        self.de_vdate.setEnabled(enabled)
        self.cb_godown.setEnabled(enabled)
        self.ed_remarks.setEnabled(enabled)
        self.cb_clear.setEnabled(enabled)
        self.grid.setEnabled(enabled)
        self.btn_add_line.setEnabled(enabled)
        self.btn_del_line.setEnabled(enabled)

        self.btn_new.setEnabled(not enabled)
        self.btn_edit.setEnabled(not enabled)
        self.btn_save.setEnabled(enabled)
        self.btn_cancel.setEnabled(enabled)

        self.state = "Add" if enabled and self.edit_docid is None else ("Edit" if enabled else "Idle")
        self.lbl_state.setText(f"State: {self.state}")

    def _add_line(self):
        r = self.grid.rowCount()
        self.grid.insertRow(r)
        for c, v in enumerate([str(r + 1), "", "0", "", "0"]):
            it = QTableWidgetItem(str(v))
            it.setFlags(it.flags() | Qt.ItemFlag.ItemIsEditable)
            it.setForeground(QColor(_theme.palette()["text"]))
            self.grid.setItem(r, c, it)

    def _del_line(self):
        r = self.grid.currentRow()
        if r >= 0:
            self.grid.removeRow(r)
            for i in range(self.grid.rowCount()):
                self.grid.setItem(i, 0, _dark_item(str(i + 1)))

    def _collect_lines(self) -> list[dict]:
        lines = []
        for r in range(self.grid.rowCount()):
            item_it = self.grid.item(r, 1)
            item = item_it.text().strip() if item_it else ""
            if not item:
                continue
            try:
                qty = float(self.grid.item(r, 2).text() or 0) if self.grid.item(r, 2) else 0
                rate = float(self.grid.item(r, 4).text() or 0) if self.grid.item(r, 4) else 0
            except ValueError:
                raise ValueError(f"Line row {r + 1}: Qty/Rate invalid")
            unit_it = self.grid.item(r, 3)
            unit = unit_it.text().strip() if unit_it else ""
            lines.append({"item": item, "qty": qty, "unit": unit,
                          "rate": rate, "amount": qty * rate})
        return lines

    def _load_lines(self, docid: str):
        self.grid.setRowCount(0)
        from HMS_py.core import purchase as purch
        try:
            rows = purch.indent1_lines(docid)
        except Exception:
            rows = []
        for i, row in enumerate(rows):
            self.grid.insertRow(i)
            vals = [str(row.get("sno") or i + 1), row.get("item", ""),
                    str(row.get("qty") or 0), row.get("unit", ""),
                    str(row.get("rate") or 0)]
            for c, v in enumerate(vals):
                it = QTableWidgetItem(str(v))
                it.setForeground(QColor(_theme.palette()["text"]))
                self.grid.setItem(i, c, it)

    def _on_new(self):
        self.edit_docid = None
        self.cb_dept.setCurrentIndex(0)
        self.de_vdate.setDate(datetime.date.today())
        self.cb_godown.setCurrentIndex(0)
        self.ed_remarks.clear()
        self.cb_clear.setCurrentIndex(0)
        self.grid.setRowCount(0)
        self.set_state(True)

    def _on_edit(self):
        r = self.tbl.currentRow()
        if r < 0:
            QMessageBox.information(self, "Edit", "Pehele row select karein")
            return
        docid = self.tbl.item(r, 0).text()
        rec = inv.indent_get(docid)
        if not rec:
            return
        self.edit_docid = docid
        self.cb_dept.setCurrentText(f"{rec['dept']} - ...")
        self.de_vdate.setDate(rec["vdate"])
        self.cb_godown.setCurrentText(f"{rec['godown']} - ...")
        self.ed_remarks.setText(rec["remarks"])
        self.cb_clear.setCurrentText(rec["clear"] or "N")
        self._load_lines(docid)
        self.set_state(True)

    def _on_save(self):
        dept = self.cb_dept.currentData()
        if not dept:
            QMessageBox.warning(self, "Save", "Department zaroori hai")
            return

        vdate = self.de_vdate.date().toPyDate()
        remarks = self.ed_remarks.text().strip()
        clear = self.cb_clear.currentText()
        godown = self.cb_godown.currentData() or ""
        try:
            lines = self._collect_lines()
        except ValueError as e:
            QMessageBox.warning(self, "Save", str(e))
            return

        try:
            from HMS_py.core import purchase as purch
            if self.state == "Add":
                result = inv.indent_create(dept, vdate, godown,
                                           remarks=remarks, user="PYADMIN")
                docid = result["docid"]
                vno = result.get("vno", 0)
            else:
                docid = self.edit_docid
                inv.indent_update(docid, dept, vdate, godown,
                                  remarks=remarks, clear=clear,
                                  user="PYADMIN")
                existing = inv.indent_get(docid) or {}
                vno = existing.get("vno", 0)
            # PI-5: save Indent1 lines via INDENT1API (shared path)
            if lines:
                purch.INDENT1API.delete_all(docid)
                for i, line in enumerate(lines, 1):
                    rec = dict(line)
                    rec.update({"docid": docid, "sno": i,
                                "vtype": "RQ", "vno": vno,
                                "vdate": vdate, "vprefix": "2026",
                                "clear_yn": clear if clear == "Y" else ""})
                    purch.INDENT1API.insert(rec)
            QMessageBox.information(
                self, "Save",
                f"Indent saved! ({len(lines)} lines) DocId: {docid}")
            self.set_state(False)
            self.reload()
        except Exception as e:
            QMessageBox.critical(self, "Save", f"Error: {e}")

    def _on_cancel(self):
        self.set_state(False)

    def closeEvent(self, event):
        self.reject()


def open_indent(parent=None):
    IndentForm(parent).exec()


# ============================================================
# GIN / Purchase Receipt Browser + Entry
# ============================================================
class GINForm(QDialog):
    """GIN (Purchase Receipt) - header + lines grid."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Purchase Receipt / GIN (P5) - HMS_py")
        self.resize(1100, 650)
        self.edit_docid = None
        self.state = "Idle"
        self.lines = []  # list of dicts for grid

        root = QVBoxLayout(self)

        # Header
        header = QWidget()
        hform = QFormLayout(header)
        self.ed_party = QLineEdit()
        self.ed_party.setPlaceholderText("Party code")
        self.ed_party_name = QLineEdit()
        self.ed_party_name.setPlaceholderText("Party name")
        self.de_vdate = QDateEdit(datetime.date.today())
        self.de_vdate.setCalendarPopup(True)
        self.cb_godown = QComboBox()
        self.ed_remarks = QLineEdit()
        self.ed_remarks.setPlaceholderText("Enter remarks")
        self.ed_oc = QLineEdit()  # OC DocId
        self.ed_oc.setPlaceholderText("OC DocId (optional)")
        self.ed_pord = QLineEdit()  # PO DocId
        self.ed_pord.setPlaceholderText("PO DocId (optional)")

        hform.addRow("Party Code *", self.ed_party)
        hform.addRow("Party Name", self.ed_party_name)
        hform.addRow("Date", self.de_vdate)
        hform.addRow("Godown", self.cb_godown)
        hform.addRow("OC DocId", self.ed_oc)
        hform.addRow("PO DocId", self.ed_pord)
        hform.addRow("Remarks", self.ed_remarks)
        root.addWidget(header)

        # Lines grid
        self.grid = QTableWidget(0, 10)
        self.grid.setHorizontalHeaderLabels([
            "SNo", "Item", "Qty", "Unit", "Rate", "Amount",
            "Tax%", "Disc%", "Godown", "Remarks"
        ])
        self.grid.horizontalHeader().setStretchLastSection(True)
        self.grid.setAlternatingRowColors(True)
        self.grid.cellChanged.connect(self._on_cell_changed)
        root.addWidget(self.grid)

        # Buttons for lines
        line_btns = QHBoxLayout()
        self.btn_add_line = QPushButton("Add Line (Ins)")
        self.btn_add_line.setToolTip("Add a new line to the GIN grid (Ins)")
        self.btn_del_line = QPushButton("Del Line (Del)")
        self.btn_del_line.setToolTip("Remove the selected line from the grid (Del)")
        line_btns.addWidget(self.btn_add_line)
        line_btns.addWidget(self.btn_del_line)
        root.addLayout(line_btns)

        self.btn_add_line.clicked.connect(self._add_line)
        self.btn_del_line.clicked.connect(self._del_line)

        # Browse list (for reload)
        self.tbl = QTableWidget(0, 4)
        self.tbl.setHorizontalHeaderLabels(["VNo", "Date", "Party", "DocId"])
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.setMaximumHeight(150)
        self.tbl.setVisible(False)
        root.addWidget(self.tbl)

        # Status
        self.lbl_state = QLabel("State: Idle | New: Ctrl+N | Save: Ctrl+S")
        self.lbl_state.setStyleSheet(f"color:{_theme.palette()['text']}; padding:4px; background:{_theme.palette()['glass_tint']};")
        root.addWidget(self.lbl_state)

        # Main buttons
        btns = QHBoxLayout()
        self.btn_new = QPushButton("New (Ctrl+N)")
        self.btn_new.setToolTip("Start a new GIN entry (Ctrl+N)")
        self.btn_save = QPushButton("Save (Ctrl+S)")
        self.btn_save.setToolTip("Save the GIN header and lines (Ctrl+S)")
        self.btn_cancel = QPushButton("Cancel (Esc)")
        self.btn_cancel.setToolTip("Cancel current entry and return to idle (Esc)")
        self.btn_close = QPushButton("Close")
        self.btn_close.setToolTip("Close the GIN form")
        for b in (self.btn_new, self.btn_save, self.btn_cancel, self.btn_close):
            btns.addWidget(b)
        root.addLayout(btns)

        self.btn_new.clicked.connect(self._on_new)
        self.btn_save.clicked.connect(self._on_save)
        self.btn_cancel.clicked.connect(self._on_cancel)
        self.btn_close.clicked.connect(self.reject)

        from PyQt6.QtGui import QShortcut, QKeySequence
        QShortcut(QKeySequence("Ctrl+N"), self, activated=self._on_new)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._on_save)
        QShortcut(QKeySequence("Escape"), self, activated=self._on_cancel)

        self._load_combos()
        self.set_state(False)
        self.reload()

    def _load_combos(self):
        godowns = inv.godown_list()
        self.cb_godown.clear()
        for g in godowns:
            self.cb_godown.addItem(f"{g['code']} - {g['name']}", g['code'])

    def reload(self):
        """Load GIN list for browse mode."""
        rows = inv.purchase_list()
        self.tbl.setRowCount(len(rows))
        self.tbl.setHorizontalHeaderLabels(["VNo", "Date", "Party", "DocId"])
        for r, i in enumerate(rows):
            for c, v in enumerate([i["vno"], i["vdate"], i["party_name"], i["docid"]]):
                self.tbl.setItem(r, c, _dark_item(v))

    def set_state(self, enabled: bool):
        """Enable/disable form fields based on mode."""
        self.ed_party.setEnabled(enabled)
        self.ed_party_name.setEnabled(enabled)
        self.de_vdate.setEnabled(enabled)
        self.cb_godown.setEnabled(enabled)
        self.ed_remarks.setEnabled(enabled)
        self.ed_oc.setEnabled(enabled)
        self.ed_pord.setEnabled(enabled)
        self.grid.setEnabled(enabled)
        self.btn_add_line.setEnabled(enabled)
        self.btn_del_line.setEnabled(enabled)

        self.btn_new.setEnabled(not enabled)
        self.btn_save.setEnabled(enabled)
        self.btn_cancel.setEnabled(enabled)

        if enabled and self.edit_docid is None:
            self.state = "Add"
        elif enabled:
            self.state = "Edit"
        else:
            self.state = "Idle"
        self.lbl_state.setText(f"State: {self.state}")

    def _on_new(self):
        """Start new GIN entry."""
        self.edit_docid = None
        self.ed_party.clear()
        self.ed_party_name.clear()
        self.de_vdate.setDate(datetime.date.today())
        self.cb_godown.setCurrentIndex(0)
        self.ed_remarks.clear()
        self.ed_oc.clear()
        self.ed_pord.clear()
        self.grid.setRowCount(0)
        self.lines = []
        self.set_state(True)
        self.ed_party.setFocus()

    def _on_edit(self, row=None, col=None):
        """Load existing GIN for editing."""
        if row is None:
            r = self.tbl.currentRow()
        else:
            r = row
        if r < 0:
            return
        docid = self.tbl.item(r, 3).text()
        header = inv.gin_get(docid)
        if not header:
            return
        self.edit_docid = docid
        self.ed_party.setText(header["party_code"])
        self.ed_party_name.setText(header["party_name"])
        self.de_vdate.setDate(header["vdate"])
        godown_idx = self.cb_godown.findData(header["godown"])
        if godown_idx >= 0:
            self.cb_godown.setCurrentIndex(godown_idx)
        self.ed_remarks.setText(header["remark"])
        self.ed_oc.setText(header["oc_docid"])
        self.ed_pord.setText(header["pord_docid"])
        
        # Load lines
        lines = inv.gin_lines(docid)
        self.grid.setRowCount(len(lines))
        for i, line in enumerate(lines):
            for c, v in enumerate([
                str(line["sno"]), line["item"], str(line["qty_rec"]), 
                line["unit"], str(line["rate"]), str(line["amount"]),
                str(line["tax_per"]), str(line["disc_per"]), 
                line["godown"], line["remarks"]
            ]):
                self.grid.setItem(i, c, _dark_item(v))
            self.lines.append(line)
        
        self.set_state(True)

    def _on_save(self):
        """Save GIN header + lines."""
        party_code = self.ed_party.text().strip()
        party_name = self.ed_party_name.text().strip()
        godown = self.cb_godown.currentData() or ""
        vdate = self.de_vdate.date().toPyDate()
        remarks = self.ed_remarks.text().strip()
        
        if not party_code:
            QMessageBox.warning(self, "Save", "Party code zaroori hai")
            return
        if not party_name:
            QMessageBox.warning(self, "Save", "Party name zaroori hai")
            return
        if self.grid.rowCount() == 0:
            QMessageBox.warning(self, "Save", "Koi lines nahi")
            return
        
        # Build lines from grid
        lines = []
        for r in range(self.grid.rowCount()):
            item = self.grid.item(r, 1).text().strip() if self.grid.item(r, 1) else ""
            if not item:
                continue
            try:
                qty_rec = float(self.grid.item(r, 2).text() or 0)
                unit = self.grid.item(r, 3).text().strip() if self.grid.item(r, 3) else ""
                rate = float(self.grid.item(r, 4).text() or 0)
                amount = float(self.grid.item(r, 5).text() or 0)
                tax_per = float(self.grid.item(r, 6).text() or 0)
                disc_per = float(self.grid.item(r, 7).text() or 0)
                godown_line = self.grid.item(r, 8).text().strip() if self.grid.item(r, 8) else godown
                remarks_line = self.grid.item(r, 9).text().strip() if self.grid.item(r, 9) else ""
            except ValueError:
                QMessageBox.warning(self, "Error", f"Row {r+1}: Invalid numeric value")
                return
            
            tax_amt = amount * tax_per / 100
            disc_amt = amount * disc_per / 100
            
            lines.append({
                "item": item,
                "qty_rec": qty_rec,
                "unit": unit,
                "rate": rate,
                "amount": amount,
                "tax_per": tax_per,
                "tax_amt": tax_amt,
                "disc_per": disc_per,
                "disc_amt": disc_amt,
                "godown": godown_line,
                "remarks": remarks_line,
                "party_code": party_code,
                "party_name": party_name,
            })
        
        if not lines:
            QMessageBox.warning(self, "Empty", "Koi valid lines nahi")
            return
        
        try:
            result = inv.gin_create(
                party_code=party_code,
                party_name=party_name,
                godown=godown,
                vdate=vdate,
                lines=lines,
                remark=remarks,
                user="PYADMIN"
            )
            QMessageBox.information(self, "Saved", f"GIN saved!\nDocId: {result['docid']}")
            self.set_state(False)
            self.reload()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _on_cancel(self):
        """Cancel edit/new mode."""
        self.edit_docid = None
        self.ed_party.clear()
        self.ed_party_name.clear()
        self.de_vdate.setDate(datetime.date.today())
        self.cb_godown.setCurrentIndex(0)
        self.ed_remarks.clear()
        self.ed_oc.clear()
        self.ed_pord.clear()
        self.grid.setRowCount(0)
        self.lines = []
        self.set_state(False)

    def _add_line(self):
        """Add new line to grid."""
        r = self.grid.rowCount()
        self.grid.insertRow(r)
        self.grid.setItem(r, 0, _dark_item(str(r + 1)))
        for c in range(1, 10):
            self.grid.setItem(r, c, _dark_item(""))

    def _del_line(self):
        """Delete selected line from grid."""
        r = self.grid.currentRow()
        if r >= 0:
            self.grid.removeRow(r)
            # Renumber SNo
            for i in range(self.grid.rowCount()):
                self.grid.setItem(i, 0, _dark_item(str(i + 1)))

    def _on_cell_changed(self, row, col):
        """Auto-calculate amount when Qty/Rate changes."""
        if col not in (2, 4):  # Qty or Rate column
            return
        try:
            qty = float(self.grid.item(row, 2).text() or 0) if self.grid.item(row, 2) else 0
            rate = float(self.grid.item(row, 4).text() or 0) if self.grid.item(row, 4) else 0
            amount = qty * rate
            self.grid.blockSignals(True)
            self.grid.setItem(row, 5, _dark_item(f"{amount:.2f}"))
            self.grid.blockSignals(False)
        except ValueError:
            pass


# ============================================================
# Main Inventory Browser (read-only views)
# ============================================================
class InvBrowser(QDialog):
    """Indent / Purchase / Stock-balance / Stock Register / Purchase Register."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Inventory Browser (P5) - HMS_py")
        self.resize(1060, 560)
        root = QVBoxLayout(self)

        self.tbl = QTableWidget(0, 5)
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.tbl)

        self.lblState = QLabel(
            "State: Indents | Ctrl+I = Indents, Ctrl+U = Purchase Register, "
            "Ctrl+B = Stock Summary, Ctrl+R = Stock Register, Ctrl+P = Purchase Register")
        root.addWidget(self.lblState)

        btns = QHBoxLayout()
        self.btnIndent = QPushButton("Indents (Ctrl+I)")
        self.btnIndent.setToolTip("View indent list (Ctrl+I)")
        self.btnPur = QPushButton("Purchase Register (Ctrl+U)")
        self.btnPur.setToolTip("View purchase register (Ctrl+U)")
        self.btnStock = QPushButton("Stock Summary (Ctrl+B)")
        self.btnStock.setToolTip("View stock summary (Ctrl+B)")
        self.btnReg = QPushButton("Stock Register (Ctrl+R)")
        self.btnReg.setToolTip("View stock register (Ctrl+R)")
        self.btnPurReg = QPushButton("Purchase Register (Ctrl+P)")
        self.btnPurReg.setToolTip("View purchase register (Ctrl+P)")
        self.btnClose = QPushButton("Close")
        self.btnClose.setToolTip("Close the inventory browser")
        for b in (self.btnIndent, self.btnPur, self.btnStock, self.btnReg, self.btnPurReg, self.btnClose):
            btns.addWidget(b)
        root.addLayout(btns)

        self.btnIndent.clicked.connect(self._indent)
        self.btnPur.clicked.connect(self._pur)
        self.btnStock.clicked.connect(self._stock)
        self.btnReg.clicked.connect(self._reg)
        self.btnPurReg.clicked.connect(self._purreg)
        self.btnClose.clicked.connect(self.reject)

        from PyQt6.QtGui import QShortcut, QKeySequence
        QShortcut(QKeySequence("Ctrl+I"), self, activated=self._indent)
        QShortcut(QKeySequence("Ctrl+U"), self, activated=self._pur)
        QShortcut(QKeySequence("Ctrl+B"), self, activated=self._stock)
        QShortcut(QKeySequence("Ctrl+R"), self, activated=self._reg)
        QShortcut(QKeySequence("Ctrl+P"), self, activated=self._purreg)

        self._indent()

    def _indent(self):
        rows = inv.indent_list()
        self.tbl.setRowCount(len(rows))
        self.tbl.setHorizontalHeaderLabels(
            ["VNo", "Date", "Department", "Cleared", "Godown"])
        for r, i in enumerate(rows):
            for c, v in enumerate([i["vno"], i["vdate"], i["dept"],
                                   i["clear"] or "N", i["godown"]]):
                self.tbl.setItem(r, c, _dark_item(v))
        self.setWindowTitle("Inventory - Indents (P5) - HMS_py")

    def _pur(self):
        rows = inv.purchase_list()
        self.tbl.setRowCount(len(rows))
        self.tbl.setHorizontalHeaderLabels(
            ["VNo", "Date", "Party", "", ""])
        for r, p in enumerate(rows):
            for c, v in enumerate([p["vno"], p["vdate"], p["party"], "", ""]):
                self.tbl.setItem(r, c, _dark_item(v))
        self.setWindowTitle("Inventory - Purchase Register (P5) - HMS_py")

    def _stock(self):
        rows = inv.stock_balance()
        self.tbl.setRowCount(len(rows))
        self.tbl.setHorizontalHeaderLabels(
            ["Godown", "Item", "Balance", "", ""])
        for r, s in enumerate(rows):
            for c, v in enumerate([s["godown_name"] or s["godown"],
                                   s["item_name"] or s["item"],
                                   s["bal"], "", ""]):
                self.tbl.setItem(r, c, _dark_item(v))
        self.setWindowTitle("Inventory - Stock Summary (P5) - HMS_py")

    def _reg(self):
        rows = inv.stock_register()
        self.tbl.setRowCount(len(rows))
        self.tbl.setHorizontalHeaderLabels(
            ["DocId", "VType", "VNo", "Date", "Item", "Godown",
             "QtyIss", "QtyRec", "Rate", "Amount", "User"])
        for r, s in enumerate(rows):
            vals = [s["docid"], s["vtype"], s["vno"], s["vdate"],
                    s["item"], s["godown"], s["qty_iss"], s["qty_rec"],
                    s["rate"], s["amount"], s["user"]]
            for c, v in enumerate(vals):
                self.tbl.setItem(r, c, _dark_item(v))
        self.setWindowTitle("Inventory - Stock Register (P5) - HMS_py")

    def _purreg(self):
        rows = inv.purchase_register()
        self.tbl.setRowCount(len(rows))
        self.tbl.setHorizontalHeaderLabels(
            ["DocId", "VNo", "Date", "Party", "VType"])
        for r, p in enumerate(rows):
            for c, v in enumerate([p["docid"], p["vno"], p["vdate"],
                                   p["party"], p["vtype"]]):
                self.tbl.setItem(r, c, _dark_item(v))
        self.setWindowTitle("Inventory - Purchase Register (P5) - HMS_py")


def open_inv(parent=None):
    InvBrowser(parent).exec()


def open_indent_ui(parent=None):
    IndentForm(parent).exec()


def open_gin(parent=None):
    GINForm(parent).exec()


def open_godown_ui(parent=None):
    BaseMasterForm(godown_config(), parent).exec()


class StockTransferForm(QDialog):
    """Minimal VB6-style transfer form for inter-godown stock movement."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Stock Transfer (BMTC) - HMS_py")
        self.resize(600, 260)

        root = QVBoxLayout(self)
        form = QFormLayout()

        self.cb_item = QComboBox()
        self.cb_from = QComboBox()
        self.cb_to = QComboBox()
        self.spin_qty = QDoubleSpinBox()
        self.spin_qty.setRange(0.01, 999999)
        self.spin_qty.setDecimals(2)
        self.spin_rate = QDoubleSpinBox()
        self.spin_rate.setRange(0, 999999)
        self.spin_rate.setDecimals(2)
        self.ed_date = QDateEdit(datetime.date.today())
        self.ed_date.setCalendarPopup(True)
        self.ed_remark = QLineEdit()
        self.ed_remark.setPlaceholderText("Enter transfer remark")

        form.addRow("Item *", self.cb_item)
        form.addRow("From Godown *", self.cb_from)
        form.addRow("To Godown *", self.cb_to)
        form.addRow("Qty", self.spin_qty)
        form.addRow("Rate", self.spin_rate)
        form.addRow("Date", self.ed_date)
        form.addRow("Remark", self.ed_remark)
        root.addLayout(form)

        btns = QHBoxLayout()
        self.btn_save = QPushButton("Save")
        self.btn_save.setToolTip("Save the stock transfer")
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setToolTip("Cancel and close the form")
        btns.addStretch()
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_cancel)
        root.addLayout(btns)

        self.btn_save.clicked.connect(self._save)
        self.btn_cancel.clicked.connect(self.reject)

        self._load()

    def _load(self):
        from HMS_py.core import item as item_mod
        items = item_mod.list_all()
        self.cb_item.clear()
        for it in items[:500]:
            self.cb_item.addItem(f"{it['code']} - {it['name']}", it['code'])

        godowns = inv.godown_list()
        self.cb_from.clear(); self.cb_to.clear()
        for g in godowns:
            code = g['code']
            label = f"{code} - {g['name']}"
            self.cb_from.addItem(label, code)
            self.cb_to.addItem(label, code)

    def _save(self):
        item = self.cb_item.currentData()
        from_g = self.cb_from.currentData()
        to_g = self.cb_to.currentData()
        qty = float(self.spin_qty.value())
        rate = float(self.spin_rate.value())

        if not item or not from_g or not to_g:
            QMessageBox.warning(self, "Stock Transfer", "Item aur godown sab required hain")
            return
        if from_g == to_g:
            QMessageBox.warning(self, "Stock Transfer", "Source aur destination godown same nahi ho sakta")
            return
        if qty <= 0:
            QMessageBox.warning(self, "Stock Transfer", "Qty > 0 hona chahiye")
            return
        try:
            inv.stock_transfer(
                item=item,
                from_godown=from_g,
                to_godown=to_g,
                qty=qty,
                unit="",
                rate=rate,
                vdate=self.ed_date.date().toPyDate(),
                remarks=self.ed_remark.text().strip(),
            )
            QMessageBox.information(self, "Stock Transfer", "Transfer saved successfully")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Stock Transfer", f"Error: {e}")


def open_stock_transfer(parent=None):
    StockTransferForm(parent).exec()


# ============================================================
# eInvoice Config Screen (P6-5)
# ============================================================
class EInvoiceConfigForm(QDialog):
    """eInvoice Configuration Screen - reads/writes eInvoiceEnviro table."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("eInvoice Configuration (P6-5) - HMS_py")
        self.resize(500, 300)

        root = QVBoxLayout(self)

        form = QFormLayout()
        self.ed_asp_id = QLineEdit()
        self.ed_asp_id.setMaxLength(50)
        self.ed_asp_id.setPlaceholderText("ASP provider ID")
        self.ed_asp_pwd = QLineEdit()
        self.ed_asp_pwd.setMaxLength(50)
        self.ed_asp_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.ed_asp_pwd.setPlaceholderText("ASP provider password")
        self.ed_einv_user = QLineEdit()
        self.ed_einv_user.setMaxLength(50)
        self.ed_einv_user.setPlaceholderText("eInvoice portal username")
        self.ed_einv_pwd = QLineEdit()
        self.ed_einv_pwd.setMaxLength(50)
        self.ed_einv_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.ed_einv_pwd.setPlaceholderText("eInvoice portal password")

        form.addRow("ASP ID *", self.ed_asp_id)
        form.addRow("ASP Password *", self.ed_asp_pwd)
        form.addRow("eInvoice User *", self.ed_einv_user)
        form.addRow("eInvoice Password *", self.ed_einv_pwd)
        root.addLayout(form)

        self.lbl_state = QLabel("State: Loading...")
        self.lbl_state.setStyleSheet(f"color:{_theme.palette()['text']}; padding:4px; background:{_theme.palette()['glass_tint']};")
        root.addWidget(self.lbl_state)

        btns = QHBoxLayout()
        self.btn_save = QPushButton("Save (Ctrl+S)")
        self.btn_save.setToolTip("Save eInvoice configuration (Ctrl+S)")
        self.btn_cancel = QPushButton("Cancel (Esc)")
        self.btn_cancel.setToolTip("Cancel and close (Esc)")
        btns.addStretch()
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_cancel)
        root.addLayout(btns)

        self.btn_save.clicked.connect(self._save)
        self.btn_cancel.clicked.connect(self.reject)

        from PyQt6.QtGui import QShortcut, QKeySequence
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._save)
        QShortcut(QKeySequence("Escape"), self, activated=self.reject)

        self._load()

    def _load(self):
        try:
            rec = inv.einvoice_get()
            if rec:
                self.ed_asp_id.setText(rec.get("asp_id", ""))
                self.ed_asp_pwd.setText(rec.get("asp_pwd", ""))
                self.ed_einv_user.setText(rec.get("einv_user", ""))
                self.ed_einv_pwd.setText(rec.get("einv_pwd", ""))
                self.lbl_state.setText("State: Loaded existing config")
            else:
                self.lbl_state.setText("State: No config found (new entry)")
        except ValueError as e:
            if "not present" in str(e):
                self.lbl_state.setText("State: eInvoiceEnviro table missing - config disabled")
                self.ed_asp_id.setEnabled(False)
                self.ed_asp_pwd.setEnabled(False)
                self.ed_einv_user.setEnabled(False)
                self.ed_einv_pwd.setEnabled(False)
                self.btn_save.setEnabled(False)
            else:
                self.lbl_state.setText(f"State: Error - {e}")

    def _save(self):
        asp_id = self.ed_asp_id.text().strip()
        asp_pwd = self.ed_asp_pwd.text().strip()
        einv_user = self.ed_einv_user.text().strip()
        einv_pwd = self.ed_einv_pwd.text().strip()

        if not all([asp_id, asp_pwd, einv_user, einv_pwd]):
            QMessageBox.warning(self, "eInvoice Config", "Sab fields zaroori hain")
            return

        try:
            inv.einvoice_upsert({
                "asp_id": asp_id,
                "asp_pwd": asp_pwd,
                "einv_user": einv_user,
                "einv_pwd": einv_pwd,
            })
            QMessageBox.information(self, "eInvoice Config", "Configuration saved successfully")
            self.accept()
        except ValueError as e:
            if "not present" in str(e):
                QMessageBox.warning(self, "eInvoice Config", "eInvoiceEnviro table not found in DB")
            else:
                QMessageBox.critical(self, "eInvoice Config", f"Error: {e}")
        except Exception as e:
            QMessageBox.critical(self, "eInvoice Config", f"Error: {e}")


def open_einvoice_config(parent=None):
    EInvoiceConfigForm(parent).exec()


# ============================================================
# Kitchen Stock Report (P7-1) - KSISS/KSREC
# ============================================================
class KitchenStockReportForm(QDialog):
    """Kitchen Stock Report (KitchenStkRep.txt)
    VB6 Evidence: MatRep_Click, Material > Reports
    Source Tables: Stock + ItemMast
    Output: Kitchen, GrpName, Item, KitchenStock, Unit
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kitchen Stock Report (KitchenStkRep) - HMS_py")
        self.resize(800, 500)

        root = QVBoxLayout(self)

        # Filters
        filter_row = QHBoxLayout()
        self.ed_item = QLineEdit()
        self.ed_item.setPlaceholderText("Item Code (optional)")
        self.de_from = QDateEdit(datetime.date.today() - datetime.timedelta(days=30))
        self.de_from.setCalendarPopup(True)
        self.de_to = QDateEdit(datetime.date.today())
        self.de_to.setCalendarPopup(True)
        self.btn_refresh = QPushButton("Refresh (F5)")
        self.btn_refresh.setToolTip("Refresh the kitchen stock report (F5)")

        filter_row.addWidget(QLabel("Item:"))
        filter_row.addWidget(self.ed_item)
        filter_row.addWidget(QLabel("From:"))
        filter_row.addWidget(self.de_from)
        filter_row.addWidget(QLabel("To:"))
        filter_row.addWidget(self.de_to)
        filter_row.addWidget(self.btn_refresh)
        filter_row.addStretch()
        root.addLayout(filter_row)

        # Results table
        self.tbl = QTableWidget(0, 5)
        self.tbl.setHorizontalHeaderLabels([
            "Kitchen", "GrpName", "Item", "KitchenStock", "Unit"
        ])
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.tbl)

        # Summary
        self.lbl_summary = QLabel("Rows: 0")
        self.lbl_summary.setStyleSheet(f"color:{_theme.palette()['text']}; padding:4px; background:{_theme.palette()['glass_tint']}; font-weight:bold;")
        root.addWidget(self.lbl_summary)

        # Buttons
        btns = QHBoxLayout()
        self.btn_close = QPushButton("Close")
        self.btn_close.setToolTip("Close the kitchen stock report")
        btns.addStretch()
        btns.addWidget(self.btn_close)
        root.addLayout(btns)

        # Connections
        self.btn_refresh.clicked.connect(self.refresh)
        self.btn_close.clicked.connect(self.reject)

        # F5 shortcut
        from PyQt6.QtGui import QShortcut, QKeySequence
        QShortcut(QKeySequence("F5"), self, activated=self.refresh)

        # Initial load
        self.refresh()

    def refresh(self):
        item = self.ed_item.text().strip() or None
        from_dt = self.de_from.date().toPyDate()
        to_dt = self.de_to.date().toPyDate()

        # Use the core function that matches VB6 KitchenStkRep
        rows = inv.kitchen_stock_report(
            cn=None,
            vdate_from=from_dt,
            vdate_to=to_dt,
            top=500
        )

        # Filter by item if specified
        if item:
            rows = [r for r in rows if r["item"].upper().startswith(item.upper())]

        self.tbl.setRowCount(len(rows))
        for r, s in enumerate(rows):
            vals = [
                s["kitchen"] or "",  # Empty string for kitchen items, 'KITCHEN' for store items
                s["grp_name"] or "",
                s["item"] or "",
                s["kitchen_stock"],
                s["unit"] or ""
            ]
            for c, v in enumerate(vals):
                self.tbl.setItem(r, c, _dark_item(v))

        self.lbl_summary.setText(f"Rows: {len(rows)}")


class KitchenStockSummaryForm(QDialog):
    """Kitchen Stock Summary (KitchenStkSumm.txt)
    VB6 Evidence: Kitchen Stock Summary report
    Source Tables: Stock
    Output: Item, IssuedToKitchen, KitchenStockValue
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kitchen Stock Summary (KitchenStkSumm) - HMS_py")
        self.resize(800, 500)

        root = QVBoxLayout(self)

        # Filters
        filter_row = QHBoxLayout()
        self.ed_item = QLineEdit()
        self.ed_item.setPlaceholderText("Item Code (optional)")
        self.de_from = QDateEdit(datetime.date.today() - datetime.timedelta(days=30))
        self.de_from.setCalendarPopup(True)
        self.de_to = QDateEdit(datetime.date.today())
        self.de_to.setCalendarPopup(True)
        self.btn_refresh = QPushButton("Refresh (F5)")
        self.btn_refresh.setToolTip("Refresh the kitchen stock summary (F5)")

        filter_row.addWidget(QLabel("Item:"))
        filter_row.addWidget(self.ed_item)
        filter_row.addWidget(QLabel("From:"))
        filter_row.addWidget(self.de_from)
        filter_row.addWidget(QLabel("To:"))
        filter_row.addWidget(self.de_to)
        filter_row.addWidget(self.btn_refresh)
        filter_row.addStretch()
        root.addLayout(filter_row)

        # Results table
        self.tbl = QTableWidget(0, 3)
        self.tbl.setHorizontalHeaderLabels([
            "Item", "IssuedToKitchen", "KitchenStockValue"
        ])
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.tbl)

        # Summary
        self.lbl_summary = QLabel("Rows: 0")
        self.lbl_summary.setStyleSheet(f"color:{_theme.palette()['text']}; padding:4px; background:{_theme.palette()['glass_tint']}; font-weight:bold;")
        root.addWidget(self.lbl_summary)

        # Buttons
        btns = QHBoxLayout()
        self.btn_close = QPushButton("Close")
        self.btn_close.setToolTip("Close the kitchen stock summary")
        btns.addStretch()
        btns.addWidget(self.btn_close)
        root.addLayout(btns)

        # Connections
        self.btn_refresh.clicked.connect(self.refresh)
        self.btn_close.clicked.connect(self.reject)

        # F5 shortcut
        from PyQt6.QtGui import QShortcut, QKeySequence
        QShortcut(QKeySequence("F5"), self, activated=self.refresh)

        # Initial load
        self.refresh()

    def refresh(self):
        item = self.ed_item.text().strip() or None
        from_dt = self.de_from.date().toPyDate()
        to_dt = self.de_to.date().toPyDate()

        # Use the core function that matches VB6 KitchenStkSumm
        rows = inv.kitchen_stock_summary(
            cn=None,
            vdate_from=from_dt,
            vdate_to=to_dt,
            top=500
        )

        # Filter by item if specified
        if item:
            rows = [r for r in rows if r["item"].upper().startswith(item.upper())]

        self.tbl.setRowCount(len(rows))
        for r, s in enumerate(rows):
            vals = [
                s["item"] or "",
                s["issued_to_kitchen"],
                s["kitchen_stock_value"]
            ]
            for c, v in enumerate(vals):
                self.tbl.setItem(r, c, _dark_item(v))

        self.lbl_summary.setText(f"Rows: {len(rows)}")


def open_kitchen_stock_report(parent=None):
    KitchenStockReportForm(parent).exec()


def open_kitchen_stock_summary(parent=None):
    KitchenStockSummaryForm(parent).exec()


def main() -> int:
    app = QApplication(sys.argv)
    w = InvBrowser()
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())