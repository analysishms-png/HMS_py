"""Door Lock UI Module — VB6 frmGodrejLockSettings port.

Provides DoorLockForm QDialog for configuring Godrej electronic door locks.
"""
from __future__ import annotations

import os
import sys
from typing import Optional, TYPE_CHECKING

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QLineEdit, QPushButton,
    QCheckBox, QGroupBox, QTabWidget, QWidget,
    QApplication, QDialogButtonBox,
)
from PyQt6.QtCore import Qt

if TYPE_CHECKING:
    from HMS_py.core.godrej_locks import LockConfig


class DoorLockForm(QDialog):
    """Godrej Lock Settings dialog.

    Maps all VB6 frmGodrejLockSettings.frm controls to Qt widgets.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Godrej Lock Settings")
        self.setMinimumSize(700, 600)
        self._build_ui()
        self._load_defaults()

    def _build_ui(self):
        """Build the dialog UI."""
        layout = QVBoxLayout(self)

        # Top tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Connection tab
        conn_tab = QWidget()
        self.tab_widget.addTab(conn_tab, "Connection")
        self._build_connection_tab(conn_tab)

        # System tab
        sys_tab = QWidget()
        self.tab_widget.addTab(sys_tab, "System")
        self._build_system_tab(sys_tab)

        # Card tab
        card_tab = QWidget()
        self.tab_widget.addTab(card_tab, "Card")
        self._build_card_tab(card_tab)

        # Lift tab
        lift_tab = QWidget()
        self.tab_widget.addTab(lift_tab, "Lift")
        self._build_lift_tab(lift_tab)

        # Door tab
        door_tab = QWidget()
        self.tab_widget.addTab(door_tab, "Door")
        self._build_door_tab(door_tab)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_read = QPushButton("&Read")
        self.btn_write = QPushButton("&Write")
        self.btn_save_exit = QPushButton("Save &Exit")
        self.btn_exit = QPushButton("E&xit")
        btn_layout.addWidget(self.btn_read)
        btn_layout.addWidget(self.btn_write)
        btn_layout.addWidget(self.btn_save_exit)
        btn_layout.addWidget(self.btn_exit)
        layout.addLayout(btn_layout)

    def _build_connection_tab(self, parent):
        """Build Connection tab."""
        grid = QGridLayout(parent)
        row = 0

        grid.addWidget(QLabel("Reader Model:"), row, 0)
        self.cmb_reader_model = QComboBox()
        self.cmb_reader_model.addItems(["RW-21", "RW-22", "8602-1M-57BA"])
        grid.addWidget(self.cmb_reader_model, row, 1)
        row += 1

        grid.addWidget(QLabel("Port:"), row, 0)
        self.cmb_port = QComboBox()
        self.cmb_port.addItems(["COM1", "COM2", "COM3", "COM4"])
        grid.addWidget(self.cmb_port, row, 1)
        row += 1

        grid.addWidget(QLabel("Power Switch:"), row, 0)
        self.cmb_power_switch = QComboBox()
        self.cmb_power_switch.addItems(["ON", "OFF"])
        grid.addWidget(self.cmb_power_switch, row, 1)
        row += 1

        grid.addWidget(QLabel("Repeat Times:"), row, 0)
        self.txt_repeat_times = QLineEdit("1")
        grid.addWidget(self.txt_repeat_times, row, 1)
        row += 1

    def _build_system_tab(self, parent):
        """Build System tab."""
        grid = QGridLayout(parent)
        row = 0

        grid.addWidget(QLabel("System Password:"), row, 0)
        self.txt_system_pwd = QLineEdit()
        grid.addWidget(self.txt_system_pwd, row, 1)
        row += 1

        grid.addWidget(QLabel("Sector No:"), row, 0)
        self.txt_sector_no = QLineEdit("0")
        self.txt_sector_no.setMaxLength(2)
        grid.addWidget(self.txt_sector_no, row, 1)
        row += 1

        grid.addWidget(QLabel("PS Sector:"), row, 0)
        self.txt_ps_sector = QLineEdit("15")
        grid.addWidget(self.txt_ps_sector, row, 1)
        row += 1

        grid.addWidget(QLabel("PS W:"), row, 0)
        self.txt_ps_w = QLineEdit("FFFFFFFFFFFF")
        grid.addWidget(self.txt_ps_w, row, 1)
        row += 1

        grid.addWidget(QLabel("Data Sector:"), row, 0)
        self.txt_data_sector = QLineEdit("3")
        grid.addWidget(self.txt_data_sector, row, 1)
        row += 1

        grid.addWidget(QLabel("Data Pwd:"), row, 0)
        self.txt_data_pwd = QLineEdit()
        grid.addWidget(self.txt_data_pwd, row, 1)
        row += 1

    def _build_card_tab(self, parent):
        """Build Card tab."""
        grid = QGridLayout(parent)
        row = 0

        grid.addWidget(QLabel("CN:"), row, 0)
        self.txt_cn = QLineEdit("1")
        grid.addWidget(self.txt_cn, row, 1)
        row += 1

        grid.addWidget(QLabel("NC:"), row, 0)
        self.txt_nc = QLineEdit("0000")
        grid.addWidget(self.txt_nc, row, 1)
        row += 1

        grid.addWidget(QLabel("GI:"), row, 0)
        self.txt_gi = QLineEdit()
        grid.addWidget(self.txt_gi, row, 1)
        row += 1

        grid.addWidget(QLabel("BT:"), row, 0)
        self.txt_bt = QLineEdit()
        grid.addWidget(self.txt_bt, row, 1)
        row += 1

        grid.addWidget(QLabel("LC:"), row, 0)
        self.txt_lc = QLineEdit()
        grid.addWidget(self.txt_lc, row, 1)
        row += 1

        grid.addWidget(QLabel("MC:"), row, 0)
        self.txt_mc = QLineEdit()
        grid.addWidget(self.txt_mc, row, 1)
        row += 1

        grid.addWidget(QLabel("GN:"), row, 0)
        self.txt_gn = QLineEdit()
        grid.addWidget(self.txt_gn, row, 1)
        row += 1

        grid.addWidget(QLabel("ET:"), row, 0)
        self.txt_et = QLineEdit()
        grid.addWidget(self.txt_et, row, 1)
        row += 1

    def _build_lift_tab(self, parent):
        """Build Lift tab."""
        grid = QGridLayout(parent)
        row = 0

        self.chk_lift = QCheckBox("Enable Lift")
        self.chk_lift.setChecked(True)
        grid.addWidget(self.chk_lift, row, 0, 1, 2)
        row += 1

        grid.addWidget(QLabel("Lift ET:"), row, 0)
        self.txt_lift_et = QLineEdit()
        grid.addWidget(self.txt_lift_et, row, 1)
        row += 1

        grid.addWidget(QLabel("Lift BT:"), row, 0)
        self.txt_lift_bt = QLineEdit()
        grid.addWidget(self.txt_lift_bt, row, 1)
        row += 1

        grid.addWidget(QLabel("Lift CN:"), row, 0)
        self.txt_lift_cn = QLineEdit()
        grid.addWidget(self.txt_lift_cn, row, 1)
        row += 1

        grid.addWidget(QLabel("Lift Data:"), row, 0)
        self.txt_lift_data = QLineEdit()
        grid.addWidget(self.txt_lift_data, row, 1)
        row += 1

        grid.addWidget(QLabel("Lift Begin:"), row, 0)
        self.txt_lift_begin = QLineEdit()
        grid.addWidget(self.txt_lift_begin, row, 1)
        row += 1

        grid.addWidget(QLabel("Lift End:"), row, 0)
        self.txt_lift_end = QLineEdit()
        grid.addWidget(self.txt_lift_end, row, 1)
        row += 1

        grid.addWidget(QLabel("Lift Max:"), row, 0)
        self.txt_lift_max = QLineEdit()
        grid.addWidget(self.txt_lift_max, row, 1)
        row += 1

    def _build_door_tab(self, parent):
        """Build Door tab."""
        grid = QGridLayout(parent)
        row = 0

        self.chk_data = QCheckBox("Enable Data")
        self.chk_data.setChecked(True)
        grid.addWidget(self.chk_data, row, 0, 1, 2)
        row += 1

        grid.addWidget(QLabel("Door ID:"), row, 0)
        self.txt_door_id = QLineEdit("1")
        grid.addWidget(self.txt_door_id, row, 1)
        row += 1

        grid.addWidget(QLabel("Guest Sex:"), row, 0)
        self.txt_guest_sex = QLineEdit("0")
        grid.addWidget(self.txt_guest_sex, row, 1)
        row += 1

        grid.addWidget(QLabel("Guest Name:"), row, 0)
        self.txt_guest_name = QLineEdit("abcdefgh")
        grid.addWidget(self.txt_guest_name, row, 1)
        row += 1

        grid.addWidget(QLabel("Card No:"), row, 0)
        self.txt_card_no = QLineEdit("000001")
        grid.addWidget(self.txt_card_no, row, 1)
        row += 1

        grid.addWidget(QLabel("Begin Time:"), row, 0)
        self.txt_begin_time = QLineEdit()
        grid.addWidget(self.txt_begin_time, row, 1)
        row += 1

        grid.addWidget(QLabel("Begin Time2:"), row, 0)
        self.txt_begin_time2 = QLineEdit()
        grid.addWidget(self.txt_begin_time2, row, 1)
        row += 1

        grid.addWidget(QLabel("Data:"), row, 0)
        self.txt_data = QLineEdit()
        grid.addWidget(self.txt_data, row, 1)
        row += 1

        self.chk_ps = QCheckBox("PS Enabled")
        self.chk_ps.setChecked(True)
        grid.addWidget(self.chk_ps, row, 0, 1, 2)
        row += 1

    def _load_defaults(self):
        """Load default values into fields."""
        self.cmb_reader_model.setCurrentText("RW-21")
        self.cmb_port.setCurrentText("COM1")
        self.txt_repeat_times.setText("1")
        self.txt_sector_no.setText("0")
        self.txt_ps_sector.setText("15")
        self.txt_ps_w.setText("FFFFFFFFFFFF")
        self.txt_data_sector.setText("3")
        self.txt_door_id.setText("1")
        self.txt_guest_sex.setText("0")
        self.txt_guest_name.setText("abcdefgh")
        self.txt_cn.setText("1")
        self.txt_nc.setText("0000")
        self.txt_card_no.setText("000001")
        self.chk_lift.setChecked(True)
        self.chk_data.setChecked(True)
        self.chk_ps.setChecked(True)

    def _get_config(self) -> "LockConfig":
        """Return LockConfig from current form values."""
        from HMS_py.core.godrej_locks import LockConfig
        return LockConfig(
            reader_model=self.cmb_reader_model.currentText(),
            reader_port=self.cmb_port.currentText(),
            log_site_code=self.txt_guest_name.text()[:8],
            sector_no=self.txt_sector_no.text(),
            ps_sector_no=self.txt_ps_sector.text(),
            ps_w=self.txt_ps_w.text(),
            data_sector_no=self.txt_data_sector.text(),
            door_id=self.txt_door_id.text(),
            card_no=self.txt_card_no.text(),
            guest_sex=self.txt_guest_sex.text(),
            guest_name=self.txt_guest_name.text(),
            cn=self.txt_cn.text(),
            nc=self.txt_nc.text(),
            repeat_times=self.txt_repeat_times.text(),
        )

    def _load_config(self, cfg: "LockConfig"):
        """Load LockConfig into form fields."""
        self.cmb_reader_model.setCurrentText(cfg.reader_model)
        self.cmb_port.setCurrentText(cfg.reader_port)
        self.txt_door_id.setText(str(cfg.door_id))
        self.txt_guest_name.setText(cfg.guest_name)
        self.txt_sector_no.setText(cfg.sector_no)
        self.txt_ps_sector.setText(cfg.ps_sector_no)
        self.txt_ps_w.setText(cfg.ps_w)
        self.txt_data_sector.setText(cfg.data_sector_no)
        self.txt_card_no.setText(cfg.card_no)
        self.txt_guest_sex.setText(cfg.guest_sex)
        self.txt_cn.setText(cfg.cn)
        self.txt_nc.setText(cfg.nc)
        self.txt_repeat_times.setText(cfg.repeat_times)

    def _validate(self) -> list[str]:
        """Validate all form fields. Returns list of error strings."""
        from HMS_py.core.godrej_locks import validate_field
        errors: list[str] = []
        checks = [
            ("Sector No", self.txt_sector_no.text().strip(), 2),
            ("PS Sector No", self.txt_ps_sector.text().strip(), 3),
            ("Data Sector No", self.txt_data_sector.text().strip(), 3),
            ("CN", self.txt_cn.text().strip(), 4),
            ("NC", self.txt_nc.text().strip(), 4),
            ("DoorID", self.txt_door_id.text().strip(), 2),
            ("GuestSex", self.txt_guest_sex.text().strip(), 1),
            ("CardNo", self.txt_card_no.text().strip(), 6),
            ("RepeatTimes", self.txt_repeat_times.text().strip(), 6),
        ]
        for name, val, maxlen in checks:
            e = validate_field(name, val, maxlen)
            if e:
                errors.append(e)
        return errors


def open_door_lock() -> bool:
    """Open door lock settings dialog."""
    from HMS_py.ui.door_lock_ui import DoorLockForm
    dlg = DoorLockForm()
    result = dlg.exec()
    dlg.close()
    return result == QDialog.DialogCode.Accepted


def open_door_lock_with_site(site_code: str) -> bool:
    """Open door lock settings for a specific site."""
    from HMS_py.ui.door_lock_ui import DoorLockForm
    dlg = DoorLockForm()
    result = dlg.exec()
    dlg.close()
    return result == QDialog.DialogCode.Accepted


if __name__ == "__main__":
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
    dlg = DoorLockForm()
    dlg.show()
    sys.exit(app.exec())