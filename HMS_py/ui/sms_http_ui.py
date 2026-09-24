"""SMS HTTP UI Module."""
from __future__ import annotations

import os
from datetime import datetime
from typing import Optional


def open_sms_compose(parent=None) -> dict:
    """Open SMS compose interface."""
    from HMS_py.core.sms_http import SMSClient
    client = SMSClient(mock=True)
    return {"status": "compose_open", "client": client, "mock": True}


def send_sms(phone: str, message: str) -> dict:
    """Send SMS."""
    from HMS_py.core.sms_http import SMSClient
    client = SMSClient(mock=True)
    return client.send_sms(phone, message)


if __name__ == "__main__":
    import sys
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    result = send_sms("+919876543210", "Test from HMS")
    print(result)
