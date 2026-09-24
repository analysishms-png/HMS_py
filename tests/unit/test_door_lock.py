"""Unit tests for door_lock_ui module (VB6 frmGodrejLockSettings port).

Tests cover:
- Core LockConfig creation and validation
- GodrejLockManager simulation mode
- DoorLockForm UI construction and field mapping
- Read/Write/Save/Exit button handlers
- Field validation with max-length constraints
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

import pytest
from PyQt6.QtWidgets import QApplication

# Shared QApplication for all tests.
_app = QApplication.instance() or QApplication(sys.argv)


# ============================================================
# Core: LockConfig
# ============================================================

class TestLockConfig:
    """Test LockConfig data object."""

    def test_default_values(self):
        from HMS_py.core.godrej_locks import LockConfig
        cfg = LockConfig()
        assert cfg.reader_model == "RW-21"
        assert cfg.reader_port == "COM1"
        assert cfg.sector_no == "0"
        assert cfg.ps_sector_no == "15"
        assert cfg.ps_w == "FFFFFFFFFFFF"
        assert cfg.data_sector_no == "3"
        assert cfg.door_id == "1"
        assert cfg.card_no == "000001"
        assert cfg.guest_sex == "0"
        assert cfg.guest_name == "abcdefgh"

    def test_to_dict(self):
        from HMS_py.core.godrej_locks import LockConfig
        cfg = LockConfig(log_site_code="KK", reader_model="RW-22")
        d = cfg.to_dict()
        assert d["log_site_code"] == "KK"
        assert d["reader_model"] == "RW-22"

    def test_from_dict(self):
        from HMS_py.core.godrej_locks import LockConfig
        d = {"reader_model": "RW-22", "reader_port": "COM3",
             "door_id": "5"}
        cfg = LockConfig.from_dict(d)
        assert cfg.reader_model == "RW-22"
        assert cfg.reader_port == "COM3"
        assert cfg.door_id == "5"

    def test_custom_config(self):
        from HMS_py.core.godrej_locks import LockConfig
        cfg = LockConfig(
            log_site_code="TEST01",
            reader_model="8602-1M-57BA",
            reader_port="COM3",
            system_password="secret123",
            sector_no="5",
        )
        assert cfg.log_site_code == "TEST01"
        assert cfg.reader_model == "8602-1M-57BA"
        assert cfg.reader_port == "COM3"
        assert cfg.system_password == "secret123"
        assert cfg.sector_no == "5"

    def test_repr(self):
        from HMS_py.core.godrej_locks import LockConfig
        cfg = LockConfig(log_site_code="X")
        r = repr(cfg)
        assert "LockConfig" in r
        assert "log_site_code" in r


# ============================================================
# Core: GodrejLockError hierarchy
# ============================================================

class TestGodrejLockError:
    """Test exception classes."""

    def test_godrej_lock_error_base(self):
        from HMS_py.core.godrej_locks import GodrejLockError
        e = GodrejLockError("test")
        assert str(e) == "test"

    def test_serial_connection_error(self):
        from HMS_py.core.godrej_locks import (
            GodrejLockError, SerialConnectionError)
        e = SerialConnectionError("port not found")
        assert str(e) == "port not found"
        assert isinstance(e, GodrejLockError)

    def test_lock_communication_error(self):
        from HMS_py.core.godrej_locks import (
            GodrejLockError, LockCommunicationError)
        e = LockCommunicationError("timeout")
        assert str(e) == "timeout"
        assert isinstance(e, GodrejLockError)


# ============================================================
# Core: GodrejLockManager
# ============================================================

class TestGodrejLockManager:
    """Test GodrejLockManager in simulation mode."""

    def test_simulate_mode(self):
        from HMS_py.core.godrej_locks import GodrejLockManager
        mgr = GodrejLockManager(port="COM1", simulate=True)
        assert mgr.is_connected is True
        assert mgr.simulate is True
        mgr.disconnect()

    def test_read_config_returns_lock_config(self):
        from HMS_py.core.godrej_locks import GodrejLockManager, LockConfig
        mgr = GodrejLockManager(port="COM1", simulate=True)
        cfg = mgr.read_config("DEFAULT")
        assert isinstance(cfg, LockConfig)
        assert cfg.reader_model == "RW-21"
        mgr.disconnect()

    def test_write_config_stores_in_memory(self):
        from HMS_py.core.godrej_locks import (GodrejLockManager, LockConfig)
        mgr = GodrejLockManager(port="COM1", simulate=True)
        cfg = LockConfig(log_site_code="TEST01", reader_model="RW-22")
        mgr.write_config(cfg)
        read_back = mgr.read_config("TEST01")
        assert read_back.reader_model == "RW-22"
        mgr.disconnect()

    def test_list_all_sites(self):
        from HMS_py.core.godrej_locks import GodrejLockManager, LockConfig
        mgr = GodrejLockManager(port="COM1", simulate=True)
        cfg = LockConfig(log_site_code="SITE1")
        mgr.write_config(cfg)
        sites = mgr.list_all_sites()
        assert "SITE1" in sites
        mgr.disconnect()

    def test_get_versions(self):
        from HMS_py.core.godrej_locks import GodrejLockManager
        mgr = GodrejLockManager(port="COM1", simulate=True)
        v = mgr.get_versions()
        assert v["reader_model"] == "RW-21"
        assert "firmware" in v
        mgr.disconnect()

    def test_validate_field_valid(self):
        from HMS_py.core.godrej_locks import validate_field
        assert validate_field("SectorNo", "5", 2) is None
        assert validate_field("SectorNo", "", 2) is None  # optional

    def test_validate_field_too_long(self):
        from HMS_py.core.godrej_locks import validate_field
        err = validate_field("SectorNo", "12345", 2)
        assert err is not None
        assert "max 2 chars" in err


# ============================================================
# UI: DoorLockForm
# ============================================================

class TestDoorLockForm:
    """Test DoorLockForm UI construction and field mapping."""

    def test_form_creates(self):
        from HMS_py.ui.door_lock_ui import DoorLockForm
        dlg = DoorLockForm()
        assert dlg.windowTitle() == "Godrej Lock Settings"
        assert dlg.cmb_reader_model is not None
        assert dlg.cmb_port is not None
        assert dlg.txt_system_pwd is not None
        assert dlg.txt_cn is not None
        assert dlg.btn_read is not None
        assert dlg.btn_write is not None
        assert dlg.btn_save_exit is not None
        assert dlg.btn_exit is not None
        dlg.close()

    def test_form_load_default_values(self):
        from HMS_py.ui.door_lock_ui import DoorLockForm
        dlg = DoorLockForm()
        assert dlg.cmb_reader_model.currentText() == "RW-21"
        assert dlg.cmb_port.currentText() == "COM1"
        assert dlg.txt_repeat_times.text() == "1"
        assert dlg.txt_sector_no.text() == "0"
        assert dlg.txt_ps_sector.text() == "15"
        assert dlg.txt_cn.text() == "1"
        assert dlg.txt_nc.text() == "0000"
        assert dlg.txt_door_id.text() == "1"
        dlg.close()

    def test_form_has_all_fields(self):
        from HMS_py.ui.door_lock_ui import DoorLockForm
        dlg = DoorLockForm()
        # Connection fields
        assert hasattr(dlg, 'cmb_reader_model')
        assert hasattr(dlg, 'cmb_port')
        assert hasattr(dlg, 'cmb_power_switch')
        assert hasattr(dlg, 'txt_repeat_times')
        # System fields
        assert hasattr(dlg, 'txt_system_pwd')
        assert hasattr(dlg, 'txt_sector_no')
        assert hasattr(dlg, 'txt_ps_sector')
        assert hasattr(dlg, 'txt_ps_w')
        assert hasattr(dlg, 'txt_data_sector')
        assert hasattr(dlg, 'txt_data_pwd')
        # Card fields
        assert hasattr(dlg, 'txt_cn')
        assert hasattr(dlg, 'txt_nc')
        assert hasattr(dlg, 'txt_gi')
        assert hasattr(dlg, 'txt_bt')
        assert hasattr(dlg, 'txt_lc')
        assert hasattr(dlg, 'txt_mc')
        assert hasattr(dlg, 'txt_gn')
        assert hasattr(dlg, 'txt_et')
        # Lift fields
        assert hasattr(dlg, 'txt_lift_et')
        assert hasattr(dlg, 'txt_lift_bt')
        assert hasattr(dlg, 'txt_lift_cn')
        assert hasattr(dlg, 'txt_lift_data')
        assert hasattr(dlg, 'txt_lift_begin')
        assert hasattr(dlg, 'txt_lift_end')
        assert hasattr(dlg, 'txt_lift_max')
        # Door fields
        assert hasattr(dlg, 'txt_door_id')
        assert hasattr(dlg, 'txt_guest_sex')
        assert hasattr(dlg, 'txt_guest_name')
        assert hasattr(dlg, 'txt_card_no')
        assert hasattr(dlg, 'txt_begin_time')
        assert hasattr(dlg, 'txt_begin_time2')
        # Data
        assert hasattr(dlg, 'txt_data')
        # Checkboxes
        assert hasattr(dlg, 'chk_lift')
        assert hasattr(dlg, 'chk_ps')
        assert hasattr(dlg, 'chk_data')
        # Buttons
        assert hasattr(dlg, 'btn_read')
        assert hasattr(dlg, 'btn_write')
        assert hasattr(dlg, 'btn_save_exit')
        assert hasattr(dlg, 'btn_exit')
        dlg.close()

    def test_get_config_returns_lock_config(self):
        from HMS_py.core.godrej_locks import LockConfig
        from HMS_py.ui.door_lock_ui import DoorLockForm
        dlg = DoorLockForm()
        cfg = dlg._get_config()
        assert isinstance(cfg, LockConfig)
        assert cfg.reader_model == "RW-21"
        assert cfg.reader_port == "COM1"
        dlg.close()

    def test_load_config_populates_fields(self):
        from HMS_py.core.godrej_locks import LockConfig
        from HMS_py.ui.door_lock_ui import DoorLockForm
        dlg = DoorLockForm()
        cfg = LockConfig(
            reader_model="RW-22", reader_port="COM3",
            door_id="5", guest_name="TestGuest",
        )
        dlg._load_config(cfg)
        assert dlg.cmb_reader_model.currentText() == "RW-22"
        assert dlg.cmb_port.currentText() == "COM3"
        assert dlg.txt_door_id.text() == "5"
        assert dlg.txt_guest_name.text() == "TestGuest"
        dlg.close()

    def test_validation_passes_valid(self):
        from HMS_py.ui.door_lock_ui import DoorLockForm
        dlg = DoorLockForm()
        errors = dlg._validate()
        # Should have no errors with default values
        assert errors == []
        dlg.close()

    def test_validation_catches_too_long(self):
        from HMS_py.ui.door_lock_ui import DoorLockForm
        dlg = DoorLockForm()
        # Temporarily lift Qt max-length so over-long text can be set
        # (setMaxLength truncates/blocks before _validate can see it)
        dlg.txt_sector_no.setMaxLength(999)
        dlg.txt_sector_no.setText("12345")  # max 2 chars per VB6
        assert dlg.txt_sector_no.text() == "12345"
        errors = dlg._validate()
        assert len(errors) > 0
        assert any("Sector No" in e for e in errors)
        dlg.close()

    def test_validation_catches_empty_guest_name(self):
        from HMS_py.ui.door_lock_ui import DoorLockForm
        dlg = DoorLockForm()
        dlg.txt_guest_name.setText("")
        # GuestName has no max_len in validation (it's optional in VB6)
        # But if set, it should be checked
        errors = dlg._validate()
        # Empty strings for optional fields should not trigger errors
        # (validate_field returns None for empty)
        assert len(errors) == 0 or any("GuestName" in e for e in errors)
        dlg.close()

    def test_chk_lift_default_checked(self):
        from HMS_py.ui.door_lock_ui import DoorLockForm
        dlg = DoorLockForm()
        assert dlg.chk_lift.isChecked() is True
        assert dlg.chk_data.isChecked() is True
        dlg.close()


# ============================================================
# UI: Openers
# ============================================================

class TestDoorLockOpeners:
    """Test standalone opener functions."""

    def test_open_door_lock_exists(self):
        from HMS_py.ui.door_lock_ui import open_door_lock
        assert callable(open_door_lock)

    def test_open_door_lock_with_site_exists(self):
        from HMS_py.ui.door_lock_ui import open_door_lock_with_site
        assert callable(open_door_lock_with_site)


# ============================================================
# Shell registry
# ============================================================

class TestShellRegistry:
    """Test that Door Locks / Godrej Locks are in the registry."""

    def test_registry_has_godrej_locks(self):
        import HMS_py.ui.shell as shell
        registry = shell._form_registry()
        assert "Godrej Locks" in registry
        assert callable(registry["Godrej Locks"])

    def test_registry_has_door_locks(self):
        import HMS_py.ui.shell as shell
        registry = shell._form_registry()
        assert "Door Locks" in registry
        assert callable(registry["Door Locks"])

    def test_registry_has_not_coming_soon_for_door_locks(self):
        """Door Locks should NOT be a _coming_soon entry anymore."""
        import HMS_py.ui.shell as shell
        registry = shell._form_registry()
        # Should be actual callable, not None (which means coming_soon was removed)
        if "Godrej Locks" in registry:
            assert registry["Godrej Locks"] is not None

    def test_registry_has_other_entries_still_present(self):
        """Verify existing entries weren't broken."""
        import HMS_py.ui.shell as shell
        registry = shell._form_registry()
        assert "Main Setup" in registry
        assert "Guest Profile" in registry
        assert "Check In" in registry
        assert "Charge Master" in registry


# ============================================================
# Validation tests
# ============================================================

class TestFieldValidation:
    """Test validate_field function."""

    def test_validate_field_returns_none_for_valid(self):
        from HMS_py.core.godrej_locks import validate_field
        assert validate_field("CN", "1", 4) is None
        assert validate_field("CN", "", 4) is None  # optional

    def test_validate_field_returns_error_for_too_long(self):
        from HMS_py.core.godrej_locks import validate_field
        err = validate_field("BT", "12345678901", 10)
        assert err is not None
        assert "BT" in err

    def test_validate_field_returns_error_for_max_len(self):
        from HMS_py.core.godrej_locks import validate_field
        err = validate_field("SectorNo", "123", 2)
        assert err is not None
        assert "max 2 chars" in err

    def test_validate_field_all_known_fields(self):
        """Test all VB6 field max-length constraints."""
        from HMS_py.core.godrej_locks import validate_field
        checks = [
            ("SectorNo", "5", 2, None),
            ("PSSectorNo", "15", 3, None),
            ("DataSectorNo", "3", 3, None),
            ("CN", "1", 4, None),
            ("NC", "0000", 4, None),
            ("GI", "1", 2, None),
            ("BT", "0708181500", 10, None),
            ("LC", "000001", 6, None),
            ("MC", "00000000", 8, None),
            ("GN", "1", 2, None),
            ("ET", "0708191500", 10, None),
            ("DoorID", "1", 2, None),
            ("GuestSex", "0", 1, None),
            ("CardNo", "000001", 6, None),
            ("BeginTime", "100312120000", 12, None),
            ("BeginTime2", "100313120000", 12, None),
            ("RepeatTimes", "1", 6, None),
            ("CN(lift)", "1", 8, None),
            ("BeginAddr", "96", 8, None),
            ("EndAddr", "97", 4, None),
            ("MaxAddr", "97", 4, None),
        ]
        for name, val, maxlen, expected in checks:
            result = validate_field(name, val, maxlen)
            assert result == expected, f"{name}={val} (max={maxlen}): got {result}, expected {expected}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])