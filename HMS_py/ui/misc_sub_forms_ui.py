"""Misc Sub-Forms UI (VB6: Opening Stock, Sundry Master, Restaurant Master).

Tables checked:
  - ItemMast (EXISTS, 2161 rows): Code, Name, Unit, MinStock, MaxStock, SaleRate
  - Stock (EXISTS, 13253 rows): DocId, Item, QtyIss, QtyRec, Rate, Vtype...
  - SundryMast (EXISTS, 19 rows): Code, Name, Nature, CalcSign, SysYN
  - RestMast (MISSING) - handled gracefully with info message
  - SubGroup (EXISTS, 415 rows): SubCode, Name, ShortName, GroupCode, Nature

Run: python -m HMS_py.ui.misc_sub_forms_ui
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from HMS_py.ui import theme as _theme
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
                             QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLineEdit,
                             QLabel, QGroupBox, QFormLayout,
                             QHeaderView, QMessageBox, QComboBox)


def _cell(val, fg: str = "") -> QTableWidgetItem:
    it = QTableWidgetItem("" if val is None else str(val))
    it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
    it.setForeground(QColor(fg))
    return it


# ─── Opening Stock Entry ────────────────────────────────────────────
class OpeningStockWindow(QMainWindow):
    """Opening stock: ItemMast grid with opening qty + rate input.
    Saves to Stock table with Vtype='STOP'."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Opening Stock Entry - HMS_py")
        self.resize(900, 550)
        self._build_ui()
        self._load()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        lay = QVBoxLayout(central)

        title = QLabel("Opening Stock Entry")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title)

        info = QLabel("ItemMast se items load ho rahe hain. "
                       "Opening Qty aur Rate daalein, Save dabaein.")
        info.setWordWrap(True)
        info.setStyleSheet(f"color:{_theme.palette()['text_dim']};")
        lay.addWidget(info)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Code", "Item Name", "Unit", "Opening Qty", "Rate", "Amount"])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        lay.addWidget(self.table)

        btn_row = QHBoxLayout()
        btn_save = QPushButton("Save Opening Stock")
        btn_save.setStyleSheet(
            "QPushButton{background:#28a745;color:white;font-weight:bold;"
            "padding:8px 16px;}")
        btn_save.clicked.connect(self._save)
        btn_exit = QPushButton("Exit")
        btn_exit.clicked.connect(self.close)
        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_exit)
        lay.addLayout(btn_row)

        self.statusBar().showMessage("Ready")

    def _load(self):
        try:
            from HMS_py.core import db
            rows = db.query(
                "SELECT Code, Name, ISNULL(Unit,''), ISNULL(MinStock,0), "
                "ISNULL(SaleRate,0) FROM ItemMast WHERE ISNULL(ActiveYN,'Y')='Y' "
                "ORDER BY Code")
            self.table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                code, name, unit = str(r[0] or ""), str(r[1] or ""), str(r[2] or "")
                sale_rate = r[4] or 0
                self.table.setItem(i, 0, _cell(code))
                self.table.setItem(i, 1, _cell(name))
                self.table.setItem(i, 2, _cell(unit))
                qty_cell = QTableWidgetItem("0")
                qty_cell.setForeground(QColor(_theme.palette()["accent"]))
                self.table.setItem(i, 3, qty_cell)
                rate_cell = QTableWidgetItem(str(sale_rate))
                rate_cell.setForeground(QColor(_theme.palette()["accent"]))
                self.table.setItem(i, 4, rate_cell)
                self.table.setItem(i, 5, _cell("0.00"))
            self.statusBar().showMessage(f"{len(rows)} items loaded")
        except Exception as e:
            self.statusBar().showMessage(f"Load error: {e}")

    def _save(self):
        saved = 0
        for i in range(self.table.rowCount()):
            qty_item = self.table.item(i, 3)
            rate_item = self.table.item(i, 4)
            if not qty_item or not rate_item:
                continue
            try:
                qty = float(qty_item.text() or "0")
                rate = float(rate_item.text() or "0")
            except ValueError:
                continue
            if qty <= 0:
                continue
            code_item = self.table.item(i, 0)
            if not code_item:
                continue
            item_code = code_item.text()
            try:
                from HMS_py.core import db
                site = db.get_site_code()
                db.execute(
                    "INSERT INTO Stock (DocId, Sno, Vtype, VNo, Site_Code, "
                    "Vprefix, Vdate, Item, QtyRec, Rate, Amount, VoidYN, "
                    "U_Name, U_EntDt, U_AE, LogSite_Code) "
                    "VALUES (?, 1, 'STOP', 0, ?, '', GETDATE(), ?, ?, ?, "
                    "?, 'N', 'SA', GETDATE(), 'A', ?)",
                    (f"STOP{item_code}{i}", site, item_code, qty, rate,
                     qty * rate, site))
                saved += 1
            except Exception as e:
                self.statusBar().showMessage(f"Save error on {item_code}: {e}")
                return
        QMessageBox.information(
            self, "Opening Stock",
            f"{saved} items ki opening stock save ho gayi." if saved
            else "Koi items with qty > 0 nahi mile.")


# ─── Sundry Master ──────────────────────────────────────────────────
class SundryMasterWindow(QMainWindow):
    """SundryMast CRUD (VB6: SundryMast.frm).
    Table: SundryMast (Code, Name, Nature, CalcSign, SysYN)
    No ShortName column in DB."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sundry Master - HMS_py")
        self.resize(750, 450)
        self._build_ui()
        self._load()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        lay = QVBoxLayout(central)

        title = QLabel("Sundry Master (Expenses)")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title)

        form = QGroupBox("Add / Edit Sundry")
        fl = QFormLayout(form)
        self.txt_code = QLineEdit()
        self.txt_code.setPlaceholderText("e.g. S001")
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Sundry ka naam")
        self.txt_nature = QComboBox()
        self.txt_nature.addItems(["Dr", "Cr"])
        self.txt_calcsign = QLineEdit()
        self.txt_calcsign.setPlaceholderText("+ or -")
        self.txt_calcsign.setMaximumWidth(60)
        fl.addRow("Code:", self.txt_code)
        fl.addRow("Name:", self.txt_name)
        fl.addRow("Nature:", self.txt_nature)
        fl.addRow("Calc Sign:", self.txt_calcsign)
        lay.addWidget(form)

        btn_row = QHBoxLayout()
        btn_add = QPushButton("Add")
        btn_add.setStyleSheet(
            "QPushButton{background:#007bff;color:white;font-weight:bold;}")
        btn_add.clicked.connect(self._add)
        btn_del = QPushButton("Delete Selected")
        btn_del.setStyleSheet(
            "QPushButton{background:#dc3545;color:white;}")
        btn_del.clicked.connect(self._delete)
        btn_exit = QPushButton("Exit")
        btn_exit.clicked.connect(self.close)
        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_del)
        btn_row.addWidget(btn_exit)
        lay.addLayout(btn_row)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Code", "Name", "Nature", "CalcSign"])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        lay.addWidget(self.table)

        self.statusBar().showMessage("Ready")

    def _load(self):
        try:
            from HMS_py.core import db
            rows = db.query(
                "SELECT Code, Name, ISNULL(Nature,''), ISNULL(CalcSign,'') "
                "FROM SundryMast ORDER BY Code")
            self.table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                for j, v in enumerate(r):
                    self.table.setItem(i, j, _cell(v))
            self.statusBar().showMessage(f"{len(rows)} sundries loaded")
        except Exception as e:
            self.statusBar().showMessage(f"Load error: {e}")

    def _add(self):
        code = self.txt_code.text().strip()
        name = self.txt_name.text().strip()
        if not code or not name:
            QMessageBox.warning(
                self, "Input", "Code aur Name zaroori hai.")
            return
        nature = self.txt_nature.currentText()
        calcsign = self.txt_calcsign.text().strip() or "+"
        try:
            from HMS_py.core import db
            db.require_absent("SundryMast", "Code", code, "Sundry Code")
            db.execute(
                "INSERT INTO SundryMast (Code, Name, Nature, CalcSign, SysYN, "
                "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
                "VALUES (?, ?, ?, ?, 'N', '001', 'SA', GETDATE(), 'A', '001')",
                (code, name, nature, calcsign))
            QMessageBox.information(self, "Saved", f"Sundry '{name}' add ho gaya.")
            self.txt_code.clear()
            self.txt_name.clear()
            self.txt_calcsign.clear()
            self._load()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _delete(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select", "Pehle row select karo.")
            return
        code = self.table.item(row, 0)
        if not code:
            return
        code_val = code.text()
        ans = QMessageBox.question(
            self, "Delete", f"Sundry '{code_val}' delete karna hai?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if ans != QMessageBox.StandardButton.Yes:
            return
        try:
            from HMS_py.core import db
            db.execute("DELETE FROM SundryMast WHERE RTRIM(Code) = ?",
                       (code_val,))
            QMessageBox.information(self, "Deleted", f"Sundry '{code_val}' delete ho gaya.")
            self._load()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


# ─── Restaurant / Outlet Master ─────────────────────────────────────
class RestaurantMasterWindow(QMainWindow):
    """Restaurant/Outlet Master (VB6: RestMast.frm).
    NOTE: RestMast table MISSING in DB - form shows graceful message."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Restaurant/Outlet Master - HMS_py")
        self.resize(700, 400)
        self._table_exists = self._check_table()
        self._build_ui()
        if self._table_exists:
            self._load()

    def _check_table(self) -> bool:
        try:
            from HMS_py.core import db
            db.query("SELECT TOP 1 Code FROM RestMast")
            return True
        except Exception:
            return False

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        lay = QVBoxLayout(central)

        title = QLabel("Restaurant / Outlet Master")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title)

        if not self._table_exists:
            msg = QLabel(
                "NOTE: RestMast table is database me nahi hai.\n"
                "VB6 HMS me ye table hota hai par is DB copy me missing hai.\n"
                "Add/Delete functionality kaam nahi karegi.")
            msg.setStyleSheet(f"color:{_theme.palette()['danger']};font-weight:bold;padding:10px;"
                              f"border:1px solid {_theme.palette()['danger']};background:{_theme.palette()['danger_bg']};")
            msg.setWordWrap(True)
            lay.addWidget(msg)
        else:
            form = QGroupBox("Add Restaurant")
            fl = QFormLayout(form)
            self.txt_code = QLineEdit()
            self.txt_code.setPlaceholderText("e.g. R01")
            self.txt_name = QLineEdit()
            self.txt_name.setPlaceholderText("Restaurant/Outlet naam")
            fl.addRow("Code:", self.txt_code)
            fl.addRow("Name:", self.txt_name)
            lay.addWidget(form)

            btn_row = QHBoxLayout()
            btn_add = QPushButton("Add")
            btn_add.setStyleSheet(
                "QPushButton{background:#007bff;color:white;font-weight:bold;}")
            btn_add.clicked.connect(self._add)
            btn_exit = QPushButton("Exit")
            btn_exit.clicked.connect(self.close)
            btn_row.addWidget(btn_add)
            btn_row.addWidget(btn_exit)
            lay.addLayout(btn_row)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Code", "Name"])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        lay.addWidget(self.table)

        self.statusBar().showMessage(
            "Ready" if self._table_exists else "RestMast table missing")

    def _load(self):
        if not self._table_exists:
            return
        try:
            from HMS_py.core import db
            rows = db.query("SELECT Code, Name FROM RestMast ORDER BY Code")
            self.table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                for j, v in enumerate(r):
                    self.table.setItem(i, j, _cell(v))
            self.statusBar().showMessage(f"{len(rows)} restaurants loaded")
        except Exception as e:
            self.statusBar().showMessage(f"Load error: {e}")

    def _add(self):
        if not self._table_exists:
            return
        code = self.txt_code.text().strip()
        name = self.txt_name.text().strip()
        if not code or not name:
            QMessageBox.warning(
                self, "Input", "Code aur Name zaroori hai.")
            return
        try:
            from HMS_py.core import db
            db.require_absent("RestMast", "Code", code, "Restaurant Code")
            db.execute(
                "INSERT INTO RestMast (Code, Name) VALUES (?, ?)",
                (code, name))
            QMessageBox.information(
                self, "Saved", f"Restaurant '{name}' add ho gaya.")
            self.txt_code.clear()
            self.txt_name.clear()
            self._load()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


# ─── Convenience openers ────────────────────────────────────────────
def open_opening_stock(parent=None):
    w = OpeningStockWindow(parent)
    w.show()
    return w


def open_sundry_master(parent=None):
    w = SundryMasterWindow(parent)
    w.show()
    return w


def open_restaurant_master(parent=None):
    w = RestaurantMasterWindow(parent)
    w.show()
    return w


# ─── Standalone test ────────────────────────────────────────────────
if __name__ == "__main__":
    import sys as _sys
    app = QApplication(_sys.argv)
    w = QMainWindow()
    w.setWindowTitle("Misc Sub-Forms Test")
    w.resize(400, 200)
    central = QWidget()
    w.setCentralWidget(central)
    vlay = QVBoxLayout(central)
    b1 = QPushButton("Opening Stock")
    b1.clicked.connect(lambda: open_opening_stock(w))
    b2 = QPushButton("Sundry Master")
    b2.clicked.connect(lambda: open_sundry_master(w))
    b3 = QPushButton("Restaurant Master")
    b3.clicked.connect(lambda: open_restaurant_master(w))
    vlay.addWidget(b1)
    vlay.addWidget(b2)
    vlay.addWidget(b3)
    w.show()
    _sys.exit(app.exec())
