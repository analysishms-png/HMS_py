import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QMessageBox, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt
from HMS_py.core import sys_config


class SysConfigWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System Configuration")
        self.resize(700, 500)
        self._build_ui()
        self._load_config()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        form_group = QGroupBox("Configuration Settings")
        form_layout = QFormLayout(form_group)

        self.txt_roundoff = QLineEdit()
        self.txt_roundoff.setPlaceholderText("e.g. 1")
        self.txt_date_lock = QLineEdit()
        self.txt_date_lock.setPlaceholderText("YYYY-MM-DD")
        self.txt_site_code = QLineEdit()
        self.txt_site_code.setPlaceholderText("e.g. KK")
        self.txt_nckot = QLineEdit()
        self.txt_nckot.setPlaceholderText("e.g. 10")

        form_layout.addRow("RoundOffSetting:", self.txt_roundoff)
        form_layout.addRow("DateLock:", self.txt_date_lock)
        form_layout.addRow("SiteCode:", self.txt_site_code)
        form_layout.addRow("NCKOTPercentage:", self.txt_nckot)
        layout.addWidget(form_group)

        btn_layout = QHBoxLayout()
        self.btn_load = QPushButton("Load")
        self.btn_load.setToolTip("Load configuration from database")
        self.btn_save = QPushButton("Save")
        self.btn_save.setToolTip("Save configuration to database")
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setToolTip("Close this window")

        for b in [self.btn_load, self.btn_save, self.btn_exit]:
            btn_layout.addWidget(b)
        layout.addLayout(btn_layout)

        self.btn_load.clicked.connect(self._load_config)
        self.btn_save.clicked.connect(self._save_config)
        self.btn_exit.clicked.connect(self.close)

    def _load_config(self):
        try:
            rec = sys_config.get_config()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        if rec:
            self.txt_roundoff.setText(str(rec.get("RoundOffSetting", "")))
            self.txt_date_lock.setText(str(rec.get("DateLock", "")))
            self.txt_site_code.setText(str(rec.get("SiteCode", "")))
            self.txt_nckot.setText(str(rec.get("NCKOTPercentage", "")))

    def _collect(self):
        return {
            "RoundOffSetting": self.txt_roundoff.text().strip(),
            "DateLock": self.txt_date_lock.text().strip(),
            "SiteCode": self.txt_site_code.text().strip(),
            "NCKOTPercentage": self.txt_nckot.text().strip(),
        }

    def _save_config(self):
        rec = self._collect()
        try:
            sys_config.update_config(rec)
            QMessageBox.information(self, "Success", "Configuration saved.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


def open_sys_config(parent=None):
    win = SysConfigWindow(parent)
    win.show()
    return win


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SysConfigWindow()
    win.show()
    sys.exit(app.exec())
