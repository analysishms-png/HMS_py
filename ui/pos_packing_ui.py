import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel,
    QComboBox, QMessageBox, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from HMS_py.core import pos_packing
from HMS_py.ui import theme as _theme


class PosPackingWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("POS Packing Orders")
        self.resize(900, 600)
        self.current_docid = None
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        form_group = QGroupBox("Order Details")
        form_layout = QFormLayout(form_group)

        self.txt_party_name = QLineEdit()
        self.txt_party_name.setPlaceholderText("Party or customer name")
        self.txt_item_name = QLineEdit()
        self.txt_item_name.setPlaceholderText("Item name")
        self.txt_qty = QLineEdit()
        self.txt_qty.setPlaceholderText("Quantity")
        self.txt_remarks = QLineEdit()
        self.txt_remarks.setPlaceholderText("Remarks")
        self.txt_status = QComboBox()
        self.txt_status.addItems(["Pending", "Packed", "Cancelled"])

        form_layout.addRow("Party Name:", self.txt_party_name)
        form_layout.addRow("Item Name:", self.txt_item_name)
        form_layout.addRow("Qty:", self.txt_qty)
        form_layout.addRow("Remarks:", self.txt_remarks)
        form_layout.addRow("Status:", self.txt_status)
        layout.addWidget(form_group)

        btn_layout = QHBoxLayout()
        self.btn_new = QPushButton("New Order")
        self.btn_new.setToolTip("Create a new packing order")
        self.btn_packed = QPushButton("Mark Packed")
        self.btn_packed.setToolTip("Mark the selected order as packed")
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setToolTip("Refresh the packing orders list")
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setToolTip("Close the POS Packing Orders")

        for b in [self.btn_new, self.btn_packed, self.btn_refresh, self.btn_exit]:
            btn_layout.addWidget(b)
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["DocId", "VDate", "PartyName", "ItemName", "Qty", "Status"])
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._on_select)
        layout.addWidget(self.table)

        self.btn_new.clicked.connect(self._new_order)
        self.btn_packed.clicked.connect(self._mark_packed)
        self.btn_refresh.clicked.connect(self._load_data)
        self.btn_exit.clicked.connect(self.close)

    def _load_data(self):
        try:
            rows = pos_packing.list_all()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        self.table.setRowCount(len(rows) if rows else 0)
        if not rows:
            return
        for i, rec in enumerate(rows):
            vals = [rec.get("DocId", ""), rec.get("VDate", ""), rec.get("PartyName", ""),
                    rec.get("ItemName", ""), rec.get("Qty", ""), rec.get("Status", "")]
            for j, v in enumerate(vals):
                item = QTableWidgetItem(str(v))
                item.setForeground(QColor(_theme.palette()["text"]))
                self.table.setItem(i, j, item)

    def _on_select(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        docid = self.table.item(row, 0).text()
        try:
            rec = pos_packing.get(docid)
        except Exception:
            return
        if rec:
            self.current_docid = docid
            self.txt_party_name.setText(str(rec.get("PartyName", "")))
            self.txt_item_name.setText(str(rec.get("ItemName", "")))
            self.txt_qty.setText(str(rec.get("Qty", "")))
            self.txt_remarks.setText(str(rec.get("Remarks", "")))
            idx = self.txt_status.findText(str(rec.get("Status", "Pending")))
            if idx >= 0:
                self.txt_status.setCurrentIndex(idx)

    def _collect(self):
        return {
            "PartyName": self.txt_party_name.text().strip(),
            "ItemName": self.txt_item_name.text().strip(),
            "Qty": self.txt_qty.text().strip(),
            "Remarks": self.txt_remarks.text().strip(),
            "Status": self.txt_status.currentText(),
        }

    def _new_order(self):
        rec = self._collect()
        if not rec["PartyName"]:
            QMessageBox.warning(self, "Validation", "Party Name is required.")
            return
        try:
            pos_packing.insert(rec)
            self._load_data()
            QMessageBox.information(self, "Success", "Order created.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _mark_packed(self):
        if not self.current_docid:
            QMessageBox.warning(self, "Validation", "Select an order first.")
            return
        try:
            rec = pos_packing.get(self.current_docid)
            if rec:
                rec["Status"] = "Packed"
                pos_packing.update(self.current_docid, rec)
                self._load_data()
                QMessageBox.information(self, "Success", "Order marked as packed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


def open_pos_packing(parent=None):
    win = PosPackingWindow(parent)
    win.show()
    return win


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PosPackingWindow()
    win.show()
    sys.exit(app.exec())
