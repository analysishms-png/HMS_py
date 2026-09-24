import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel,
    QComboBox, QMessageBox, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from HMS_py.core import pos_table
from HMS_py.ui import theme as _theme


class PosTableWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("POS Table Management")
        self.resize(900, 600)
        self.current_code = None
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        form_group = QGroupBox("Table Details")
        form_layout = QFormLayout(form_group)

        self.txt_code = QLineEdit()
        self.txt_code.setPlaceholderText("Table code")
        self.txt_room_name = QLineEdit()
        self.txt_room_name.setPlaceholderText("Room name")
        self.txt_type = QLineEdit()
        self.txt_type.setPlaceholderText("Table type (e.g. Round, Square)")
        self.txt_seating_capacity = QLineEdit()
        self.txt_seating_capacity.setPlaceholderText("Seating capacity")
        self.txt_status = QComboBox()
        self.txt_status.addItems(["Active", "Inactive", "Blocked"])

        form_layout.addRow("Code:", self.txt_code)
        form_layout.addRow("Room Name:", self.txt_room_name)
        form_layout.addRow("Type:", self.txt_type)
        form_layout.addRow("Seating Capacity:", self.txt_seating_capacity)
        form_layout.addRow("Status:", self.txt_status)
        layout.addWidget(form_group)

        btn_layout = QHBoxLayout()
        self.btn_new = QPushButton("New")
        self.btn_new.setToolTip("Add a new table record")
        self.btn_edit = QPushButton("Edit")
        self.btn_edit.setToolTip("Edit the selected table record")
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setToolTip("Delete the selected table record")
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setToolTip("Refresh the table list")
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setToolTip("Close the POS Table Management")

        for b in [self.btn_new, self.btn_edit, self.btn_delete, self.btn_refresh, self.btn_exit]:
            btn_layout.addWidget(b)
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Code", "RoomName", "RoomNo", "Type", "SeatingCapacity", "Status"])
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._on_select)
        layout.addWidget(self.table)

        self.btn_new.clicked.connect(self._new)
        self.btn_edit.clicked.connect(self._edit)
        self.btn_delete.clicked.connect(self._delete)
        self.btn_refresh.clicked.connect(self._load_data)
        self.btn_exit.clicked.connect(self.close)

    def _load_data(self):
        try:
            rows = pos_table.list_all()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        self.table.setRowCount(len(rows) if rows else 0)
        if not rows:
            return
        st = _theme.status_colors()
        status_style = {
            "Active":   (st["success_bg"], st["success_text"]),
            "Inactive": (st["neutral_bg"], st["neutral_text"]),
            "Blocked":  (st["danger_bg"], st["danger_text"]),
        }
        for i, rec in enumerate(rows):
            vals = [rec.get("Code", ""), rec.get("RoomName", ""), rec.get("RoomNo", ""),
                    rec.get("Type", ""), rec.get("SeatingCapacity", ""), rec.get("Status", "")]
            for j, v in enumerate(vals):
                item = QTableWidgetItem(str(v))
                if j == 5:  # Status column — semantic tint + readable text
                    bg, fg = status_style.get(str(v).strip(),
                                              (st["neutral_bg"],
                                               st["neutral_text"]))
                    item.setBackground(QColor(bg))
                    item.setForeground(QColor(fg))
                else:
                    item.setForeground(QColor(_theme.palette()["text"]))
                self.table.setItem(i, j, item)

    def _on_select(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        code = self.table.item(row, 0).text()
        try:
            rec = pos_table.get(code)
        except Exception:
            return
        if rec:
            self.current_code = code
            self.txt_code.setText(str(rec.get("Code", "")))
            self.txt_room_name.setText(str(rec.get("RoomName", "")))
            self.txt_type.setText(str(rec.get("Type", "")))
            self.txt_seating_capacity.setText(str(rec.get("SeatingCapacity", "")))
            idx = self.txt_status.findText(str(rec.get("Status", "Active")))
            if idx >= 0:
                self.txt_status.setCurrentIndex(idx)

    def _collect(self):
        return {
            "Code": self.txt_code.text().strip(),
            "RoomName": self.txt_room_name.text().strip(),
            "Type": self.txt_type.text().strip(),
            "SeatingCapacity": self.txt_seating_capacity.text().strip(),
            "Status": self.txt_status.currentText(),
        }

    def _new(self):
        rec = self._collect()
        if not rec["Code"]:
            QMessageBox.warning(self, "Validation", "Code is required.")
            return
        try:
            pos_table.insert(rec)
            self._load_data()
            QMessageBox.information(self, "Success", "Record added.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _edit(self):
        if not self.current_code:
            QMessageBox.warning(self, "Validation", "Select a record first.")
            return
        rec = self._collect()
        try:
            pos_table.update(self.current_code, rec)
            self._load_data()
            QMessageBox.information(self, "Success", "Record updated.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _delete(self):
        if not self.current_code:
            QMessageBox.warning(self, "Validation", "Select a record first.")
            return
        reply = QMessageBox.question(self, "Confirm", "Delete this record?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                pos_table.delete(self.current_code)
                self.current_code = None
                self._load_data()
                QMessageBox.information(self, "Success", "Record deleted.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))


def open_pos_table(parent=None):
    win = PosTableWindow(parent)
    win.show()
    return win


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PosTableWindow()
    win.show()
    sys.exit(app.exec())
