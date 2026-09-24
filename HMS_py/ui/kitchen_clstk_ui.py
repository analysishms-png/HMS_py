"""Kitchen Closing Stock Entry (VB6: kClStk port).

KClStk table (exists, 16 cols): DocId+Sno PK, Vtype/VNo/Vprefix/Vdate,
Item, Qty, Unit, DepartCode, Remarks, audit cols.
Core: HMS_py.core.purchase KClStkAPI (list/get/lines/insert/delete).

VB6 kClStk.frm pattern: header (VDate + Department) + line grid
(Item, Qty, Unit, Remarks) -> INSERT KClStk rows with Vtype='KCLS'.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel,
    QMessageBox, QGroupBox, QFormLayout, QDateEdit, QComboBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor
from HMS_py.core import db, purchase
from ui.theme import palette

VTYPE = "KCLS"


class KitchenClosingStockWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kitchen Closing Stock Entry")
        self.resize(900, 600)
        self._items = []
        self._depts = []
        self._build_ui()
        self._load_lookups()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        hdr = QGroupBox("Header")
        hdr_lay = QFormLayout(hdr)
        self.dt_date = QDateEdit(); self.dt_date.setCalendarPopup(True)
        self.dt_date.setDate(QDate.currentDate())
        self.cb_dept = QComboBox()
        hdr_lay.addRow("Date:", self.dt_date)
        hdr_lay.addRow("Department:", self.cb_dept)
        layout.addWidget(hdr)

        lines_grp = QGroupBox("Closing Stock Lines")
        lines_lay = QVBoxLayout(lines_grp)
        self.table = QTableWidget(); self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["SNo", "Item Code", "Qty", "Unit", "Remarks"])
        self.table.setAlternatingRowColors(True)
        lines_lay.addWidget(self.table)
        btn_lay = QHBoxLayout()
        self.btn_add = QPushButton("Add Line (+)")
        self.btn_add.setToolTip("Add a new closing stock line")
        self.btn_del = QPushButton("Remove (-)")
        self.btn_del.setToolTip("Remove the selected line")
        self.btn_save = QPushButton("Save")
        self.btn_save.setStyleSheet(
            "QPushButton{background:#28a745;color:white;font-weight:bold;}")
        self.btn_save.setToolTip("Save the kitchen closing stock entry")
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setToolTip("Close the kitchen closing stock form")
        for b in [self.btn_add, self.btn_del, self.btn_save, self.btn_exit]:
            btn_lay.addWidget(b)
        lines_lay.addLayout(btn_lay)
        layout.addWidget(lines_grp)

        self.btn_add.clicked.connect(self._add_line)
        self.btn_del.clicked.connect(self._del_line)
        self.btn_save.clicked.connect(self._save)
        self.btn_exit.clicked.connect(self.close)

    def _load_lookups(self):
        try:
            rows = db.query(
                "SELECT Code, Name FROM ItemMast ORDER BY Code")
            self._items = [(r[0], r[1]) for r in rows]
        except Exception:
            self._items = []
        try:
            rows = db.query(
                "SELECT Code, Name FROM Depart ORDER BY Code")
            self._depts = [(r[0], r[1]) for r in rows]
        except Exception:
            self._depts = []
        self.cb_dept.clear()
        self.cb_dept.addItem("", "")
        for code, name in self._depts:
            self.cb_dept.addItem(f"{code} - {name}", code)

    def _add_line(self):
        r = self.table.rowCount(); self.table.insertRow(r)
        for c, v in enumerate([str(r + 1), "", "0", "", ""]):
            it = QTableWidgetItem(v)
            it.setForeground(QColor(palette()["text"]))
            self.table.setItem(r, c, it)

    def _del_line(self):
        r = self.table.currentRow()
        if r >= 0:
            self.table.removeRow(r)

    def _save(self):
        dept = self.cb_dept.currentData() or ""
        vdate = self.dt_date.date().toPyDate()
        lines = []
        for r in range(self.table.rowCount()):
            item = self.table.item(r, 1).text().strip() if self.table.item(r, 1) else ""
            if not item:
                continue
            try:
                qty = float(self.table.item(r, 2).text() or 0)
            except ValueError:
                QMessageBox.warning(
                    self, "Error", f"Row {r + 1}: Qty valid number nahi hai")
                return
            unit = self.table.item(r, 3).text().strip() if self.table.item(r, 3) else ""
            remarks = self.table.item(r, 4).text().strip() if self.table.item(r, 4) else ""
            lines.append({"item": item, "qty": qty, "unit": unit,
                          "remarks": remarks, "dept_code": dept})
        if not lines:
            QMessageBox.warning(self, "Empty", "Koi lines nahi")
            return

        own = None
        cn = None
        try:
            cn = db.connect()
            own = cn
            site = db.get_site_code()
            user = db.get_user()
            vprefix = str(vdate.year)
            # Race-safe VNo (BUG-015): KClStk me Vtype/Vprefix cols hain
            vno_rows = db.query(
                "SELECT MAX(VNo) FROM KClStk WITH (UPDLOCK, HOLDLOCK) "
                "WHERE Site_Code = ? AND Vprefix = ?",
                (site, vprefix), cn=cn)
            vno = (vno_rows[0][0] or 0) + 1 if vno_rows and vno_rows[0][0] else 1
            docid = ("D" + site.ljust(2) + VTYPE.ljust(6) +
                     vprefix.ljust(4) + str(vno).rjust(8))[:21]
            base_sno_rows = db.query(
                "SELECT MAX(Sno) FROM KClStk WHERE DocId = ?",
                (docid,), cn=cn)
            sno = (base_sno_rows[0][0] or 0) if base_sno_rows else 0
            for line in lines:
                sno += 1
                purchase.kclstk_insert({
                    "docid": docid, "sno": sno, "vtype": VTYPE,
                    "vno": vno, "vprefix": vprefix, "vdate": vdate,
                    "item": line["item"], "qty": line["qty"],
                    "unit": line["unit"], "dept_code": line["dept_code"],
                    "remarks": line["remarks"], "user": user,
                }, cn=cn, commit=False)
            cn.commit()
            QMessageBox.information(
                self, "Saved",
                f"Kitchen Closing Stock saved!\nDocId: {docid} ({len(lines)} lines)")
            self.table.setRowCount(0)
        except Exception as e:
            if cn is not None:
                try:
                    cn.rollback()
                except Exception:
                    pass
            QMessageBox.critical(self, "Error", str(e))
        finally:
            if own is not None:
                try:
                    own.close()
                except Exception:
                    pass


def open_kitchen_closing_stock(parent=None):
    w = KitchenClosingStockWindow(parent)
    w.show()
    return w


if __name__ == "__main__":
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = KitchenClosingStockWindow()
    w.show()
    sys.exit(app.exec())
