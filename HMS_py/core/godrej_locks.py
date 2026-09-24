"""Godrej Door Lock Module — Core Logic.

Ports VB6 frmGodrejLockSettings.frm. Manages electronic door lock
configuration via serial communication with Godrej card readers.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional


# =============================================================
# Exceptions
# =============================================================
class GodrejLockError(Exception):
    """Base exception for Godrej lock operations."""
    pass


class SerialConnectionError(GodrejLockError):
    """Serial port connection error."""
    pass


class LockCommunicationError(GodrejLockError):
    """Lock communication timeout/error."""
    pass


# =============================================================
# LockConfig — Data model for door lock configuration
# =============================================================
@dataclass
class LockConfig:
    """Configuration for a Godrej electronic door lock.

    Fields match VB6 frmGodrejLockSettings.frm controls.
    """
    log_site_code: str = "KK"
    reader_model: str = "RW-21"
    reader_port: str = "COM1"
    system_password: str = ""
    sector_no: str = "0"
    ps_sector_no: str = "15"
    ps_w: str = "FFFFFFFFFFFF"
    data_sector_no: str = "3"
    door_id: str = "1"
    card_no: str = "000001"
    guest_sex: str = "0"
    guest_name: str = "abcdefgh"
    cn: str = "1"
    nc: str = "0000"
    gi: str = ""
    bt: str = ""
    lc: str = ""
    mc: str = ""
    gn: str = ""
    et: str = ""
    lift_et: str = ""
    lift_bt: str = ""
    lift_cn: str = ""
    lift_data: str = ""
    lift_begin: str = ""
    lift_end: str = ""
    lift_max: str = ""
    lift_begin_addr: str = ""
    lift_end_addr: str = ""
    lift_max_addr: str = ""
    begin_time: str = ""
    begin_time2: str = ""
    data: str = ""
    repeat_times: str = "1"
    power_switch: str = "ON"
    active: bool = True

    DEFAULT_VALUES: dict = field(default_factory=lambda: {
        "reader_model": "RW-21",
        "reader_port": "COM1",
        "sector_no": "0",
        "ps_sector_no": "15",
        "ps_w": "FFFFFFFFFFFF",
        "data_sector_no": "3",
        "door_id": "1",
        "card_no": "000001",
        "guest_sex": "0",
        "guest_name": "abcdefgh",
        "cn": "1",
        "nc": "0000",
    })

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {k: v for k, v in self.__dict__.items()
                if k != 'DEFAULT_VALUES'}

    @classmethod
    def from_dict(cls, d: dict) -> "LockConfig":
        """Create LockConfig from dictionary."""
        return cls(**d)

    def __repr__(self) -> str:
        return f"LockConfig(reader_model={self.reader_model!r}, log_site_code={self.log_site_code!r})"


# =============================================================
# Field Validation
# =============================================================
FIELD_MAX_LENGTHS: dict = {
    "SectorNo": 2, "PsSectorNo": 2, "DataSectorNo": 2,
    "DoorId": 2, "CardNo": 6, "GuestName": 8, "Cn": 2,
    "Nc": 4, "ReaderModel": 15, "ReaderPort": 10,
    "SystemPassword": 20, "PSW": 12,
    "LiftMax": 3, "BeginTime": 5, "EndTime": 5,
}


def validate_field(field_name: str, value: str,
                   max_len: Optional[int] = None) -> Optional[str]:
    """Validate a field value against max length.

    Returns None if valid, error string if invalid.
    """
    if not value:
        return None  # Optional fields
    max_len = max_len or FIELD_MAX_LENGTHS.get(field_name)
    if max_len and len(value) > max_len:
        display_name = field_name.replace("_", " ")
        return f"{display_name}: max {max_len} chars"
    return None


# =============================================================
# GodrejLockManager — Core lock management
# =============================================================
class GodrejLockManager:
    """Manages Godrej electronic door lock configuration.

    Supports simulation mode for testing without hardware.
    """

    def __init__(self, port: str = "COM1",
                 simulate: bool = True):
        self.port = port
        self.simulate = simulate
        self._connected = False
        self._configs: dict[str, LockConfig] = {}
        self._versions = {
            "reader_model": "RW-21",
            "firmware": "v2.1.5",
            "hardware": "Rev C",
        }

    @property
    def is_connected(self) -> bool:
        """Check if connected to lock device."""
        if self.simulate:
            return True
        return self._connected

    def connect(self) -> bool:
        """Connect to lock device."""
        if self.simulate:
            self._connected = True
            return True
        try:
            import serial
            self._serial = serial.Serial(self.port, 9600, timeout=1)
            self._connected = True
            return True
        except Exception as e:
            raise SerialConnectionError(f"Cannot connect to {self.port}: {e}")

    def disconnect(self):
        """Disconnect from lock device."""
        if hasattr(self, '_serial'):
            self._serial.close()
        self._connected = False

    def read_config(self, site_code: str) -> LockConfig:
        """Read lock configuration for a site."""
        if site_code in self._configs:
            return self._configs[site_code]
        # Return default config
        cfg = LockConfig(log_site_code=site_code)
        return cfg

    def write_config(self, config: LockConfig) -> bool:
        """Write lock configuration."""
        self._configs[config.log_site_code] = config
        return True

    def list_all_sites(self) -> list[str]:
        """List all configured site codes."""
        return list(self._configs.keys())

    def get_versions(self) -> dict:
        """Get reader firmware/hardware versions."""
        return dict(self._versions)

    def validate_card_data(self, card_no: str) -> bool:
        """Validate card data format."""
        if not card_no:
            return False
        return len(card_no) >= 4 and card_no.isdigit()


# =============================================================
# Utility functions
# =============================================================
def get_default_config() -> LockConfig:
    """Get default lock configuration."""
    return LockConfig()


def create_config(**kwargs) -> LockConfig:
    """Create a LockConfig with custom values."""
    return LockConfig(**kwargs)
