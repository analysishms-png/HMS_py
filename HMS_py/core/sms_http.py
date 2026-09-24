"""SMS HTTP Integration Module — MobWebAPI port.

Ports VB6 MobWebAPI.bas and MemberSMS.frm. Provides HTTP-based
SMS sending capabilities for guest notifications.

Queue dispatch (send_queued_sms): VB6 SMSModule.bas Proc_233_6 —
pending DBSendSMS rows (SendTF not TRUE/Y) posted via http_client
when SMSEnviro.SmsURL is configured; empty URL => graceful skip.
"""
from __future__ import annotations

import os
import re
from datetime import datetime
from typing import Optional, List

from HMS_py.core.error_handling import log_error

# =============================================================
# SMS Templates
# =============================================================
SMS_TEMPLATES = {
    "CheckInMsg": "Dear {guest_name}, your check-in is confirmed at {hotel_name}. Room: {room_no}. Thank you for choosing us!",
    "CheckOutMsg": "Dear {guest_name}, your checkout is complete. Bill amount: {amount}. Thank you for staying with us!",
    "ReservationMsg": "Dear {guest_name}, your reservation is confirmed for {arrival_date} to {departure_date}.",
    "GuestRegistrationMsg": "Dear {guest_name}, welcome to {hotel_name}! Your guest ID is {guest_id}.",
    "POSBillMsg": "Dear {guest_name}, your bill #{bill_no} of Rs {amount} has been generated.",
}


# =============================================================
# Data classes
# =============================================================
class SMSMessage:
    """Represents an SMS message to be sent."""

    def __init__(self, recipient: str = "",
                 message_text: str = "",
                 template_key: str = "",
                 sender_name: str = "",
                 msg_type: str = "Normal",
                 doc_id: str = "",
                 v_no: int = 0,
                 bill_amount: float = 0.0,
                 party_name: str = "",
                 room_no: str = "",
                 sub_code: str = "",
                 ):
        self.recipient = recipient
        self.message_text = message_text
        self.template_key = template_key
        self.sender_name = sender_name
        self.msg_type = msg_type
        self.doc_id = doc_id
        self.v_no = v_no
        self.bill_amount = bill_amount
        self.party_name = party_name
        self.room_no = room_no
        self.sub_code = sub_code

    def get_template_text(self) -> str:
        """Get template text if template_key is set."""
        return SMS_TEMPLATES.get(self.template_key, self.message_text)


class SMSResponse:
    """Represents the response from an SMS send operation."""

    def __init__(self, success: bool = False,
                 message_id: str = "",
                 status_code: int = 0,
                 error: str = "",
                 raw_response: str = "",
                 retry_count: int = 0):
        self.success = success
        self.message_id = message_id
        self.status_code = status_code
        self.error = error
        self.raw_response = raw_response
        self.retry_count = retry_count


# =============================================================
# Utility functions
# =============================================================
def format_phone(phone: str) -> str:
    """Format phone to +91XXXXXXXXXX format."""
    phone = phone.strip()
    if not phone:
        return ""
    phone = phone.replace(" ", "").replace("-", "")
    if phone.startswith("0"):
        phone = "+91" + phone[1:]
    elif not phone.startswith("+91"):
        phone = "+91" + phone
    return phone


def validate_phone(phone: str) -> bool:
    """Validate Indian phone number format."""
    phone = phone.strip()
    if not phone or phone == "0" * len(phone) or phone.startswith("0"):
        return False
    pattern = r'^\+91?\d{10}$|^\d{10}$'
    return bool(re.match(pattern, phone))


# =============================================================
# SMSEngine
# =============================================================
class SMSEngine:
    """SMS engine for sending and managing SMS messages."""

    def __init__(self, mock_mode: bool = True,
                 max_retries: int = 3,
                 retry_delay: float = 1.0,
                 mock: Optional[bool] = None):
        self.mock_mode = mock if mock is not None else mock_mode
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._sent_log: list[SMSResponse] = []
        self._templates = dict(SMS_TEMPLATES)

    def send(self, msg: SMSMessage) -> SMSResponse:
        """Send an SMS message."""
        if not msg.recipient:
            return SMSResponse(success=False, error="Empty recipient")
        if not validate_phone(msg.recipient):
            return SMSResponse(success=False, error="Invalid phone")
        if not msg.message_text and not msg.template_key:
            return SMSResponse(success=False, error="Empty message text")

        if self.mock_mode:
            response = SMSResponse(
                success=True,
                message_id=f"MSG{datetime.now().strftime('%Y%m%d%H%M%S')}",
                status_code=200,
            )
        else:
            response = SMSResponse(success=False, error="Not in mock mode")

        self._sent_log.append(response)
        return response

    def send_bulk(self, messages: list[SMSMessage]) -> list[SMSResponse]:
        """Send multiple SMS messages."""
        results = []
        for msg in messages:
            results.append(self.send(msg))
        return results

    def get_sent_log(self) -> list[SMSResponse]:
        """Get all sent message logs."""
        return list(self._sent_log)

    def get_last_response(self) -> Optional[SMSResponse]:
        """Get the last response."""
        if self._sent_log:
            return self._sent_log[-1]
        return None

    def get_all_templates(self) -> dict:
        """Get all available templates."""
        return dict(self._templates)

    def get_template(self, key: str) -> str:
        """Get a specific template."""
        return self._templates.get(key, "")

    def set_template(self, key: str, text: str):
        """Set a template."""
        self._templates[key] = text

    def get_pending_sms(self) -> list[SMSMessage]:
        """Get pending SMS messages (empty in mock mode)."""
        return []


# =============================================================
# SMSLogViewer
# =============================================================
class SMSLogViewer:
    """SMS log viewer for inbox/outbox/history."""

    def __init__(self):
        self._entries: list[dict] = []

    def get_outbox(self, limit: int = 50) -> list[dict]:
        """Get outbox entries."""
        return self._entries[:limit]

    def get_inbox(self, limit: int = 50) -> list[dict]:
        """Get inbox entries (empty in mock)."""
        return []

    def get_history(self, limit: int = 50) -> list[dict]:
        """Get SMS history."""
        return [
            {
                "date": e.get("date", datetime.now().strftime("%Y-%m-%d")),
                "mobile": e.get("phone", ""),
                "message": e.get("message", ""),
                "sender": e.get("sender", "HMS"),
                "sent": e.get("status", "SENT"),
            }
            for e in self._entries[:limit]
        ]

    def mark_sent(self, doc_id: str, entry_id: int) -> bool:
        """Mark an entry as sent."""
        return True


# =============================================================
# Convenience functions
# =============================================================
def send_sms(phone: str, message: str) -> SMSResponse:
    """Send an SMS (convenience function)."""
    engine = SMSEngine(mock=True)
    msg = SMSMessage(recipient=phone, message_text=message)
    return engine.send(msg)


def send_template_sms(phone: str, template_key: str,
                      **kwargs) -> SMSResponse:
    """Send an SMS using a template."""
    engine = SMSEngine(mock=True)
    template = engine.get_template(template_key)
    message_text = template.format(**kwargs) if kwargs else template
    msg = SMSMessage(recipient=phone, message_text=message_text,
                      template_key=template_key)
    return engine.send(msg)


# =============================================================
# Legacy SMSClient (backward compatibility)
# =============================================================
class SMSClient:
    """HTTP-based SMS client (legacy wrapper)."""

    def __init__(self, api_url: str = "", api_key: str = "",
                 sender_id: str = "HMS", mock: bool = True):
        self.mock = mock

    def validate_phone(self, phone: str) -> bool:
        return validate_phone(phone)

    def normalize_phone(self, phone: str) -> str:
        return format_phone(phone)

    def send_sms(self, phone: str, message: str) -> dict:
        resp = send_sms(phone, message)
        return {"success": resp.success, "message_id": resp.message_id}

    def send_bulk(self, recipients: list[str], message: str) -> dict:
        results = send_bulk_sms(recipients, message)
        return {"total": len(results), "success": sum(1 for r in results if r.success)}

    def get_balance(self) -> dict:
        return {"balance": 9999, "mock": True}

    @property
    def stats(self) -> dict:
        return {"sent": 0, "failed": 0, "total": 0}


# =============================================================
# Legacy SMSLog (backward compatibility)
# =============================================================
class SMSLog:
    """Legacy SMS log (backward compatibility wrapper)."""

    def __init__(self):
        self._logs: list[dict] = []

    def add_log(self, phone: str, message: str, status: str,
                template: str = "") -> dict:
        entry = {"phone": phone, "message": message, "status": status,
                 "timestamp": datetime.now().isoformat()}
        self._logs.append(entry)
        return entry

    def get_logs(self, limit: int = 50, status: str = "") -> list[dict]:
        if status:
            return [l for l in self._logs if l.get("status") == status][:limit]
        return self._logs[:limit]

    def clear_logs(self):
        self._logs = []


# =============================================================
# Legacy functions (backward compatibility)
# =============================================================
def send_checkin_sms(guest_name: str, phone: str) -> bool:
    return send_sms(phone, f"Dear {guest_name}, check-in confirmed").success


def send_checkout_sms(guest_name: str, phone: str) -> bool:
    return send_sms(phone, f"Dear {guest_name}, checkout complete").success


def send_booking_sms(guest_name: str, phone: str) -> bool:
    return send_sms(phone, f"Dear {guest_name}, booking confirmed").success


def send_bill_sms(guest_name: str, phone: str,
                  amount: float, bill_no: str) -> bool:
    return send_sms(phone, f"Dear {guest_name}, bill #{bill_no} of Rs {amount}").success


def send_bulk_sms(phones: list[str], message: str) -> list[SMSResponse]:
    engine = SMSEngine(mock=True)
    msgs = [SMSMessage(recipient=p, message_text=message) for p in phones]
    return engine.send_bulk(msgs)


# =============================================================
# Queue dispatch (VB6 SMSModule.bas Proc_233_6 / MobWebAPI GET)
# Tables (already in sms_*.py): DBSendSMS, SMSEnviro
# =============================================================
def build_sms_url(env: dict, phone: str, message: str) -> str:
    """Concatenate SMSEnviro URL fragments + phone + message (VB6 style).

    VB6 order: SmsURL, TUser, SmsCenterUserName, TPassword,
    SmsCenterPassword, TFromSend, SmsDisplayName, TPhNo, phone,
    TMessage, message, TExtra. T* fields are literal URL fragments
    stored in SMSEnviro (e.g. "&user=", "&pwd=" ...).
    """
    def g(key: str) -> str:
        return str(env.get(key) or "")

    return (
        g("smsurl")
        + g("tuser")
        + g("smscenterusername")
        + g("tpassword")
        + g("smscenterpassword")
        + g("tfromsend")
        + g("smsdisplayname")
        + g("tphno")
        + phone
        + g("tmessage")
        + message
        + g("textra")
    )


def _pending_queue(limit: int = 50, cn=None) -> list[dict]:
    """Pending DBSendSMS rows (SendTF not yet TRUE/Y)."""
    from HMS_py.core import db
    rows = db.query(
        f"SELECT TOP {int(limit)} DocId, SNo, Mobile1, TxtMsg, MsgType "
        "FROM DBSendSMS "
        "WHERE ISNULL(SendTF,'') NOT IN ('TRUE','Y') "
        "AND ISNULL(Mobile1,'') <> '' AND ISNULL(TxtMsg,'') <> '' "
        "ORDER BY SNo",
        (), cn=cn)
    out = []
    for r in rows:
        try:
            out.append({"docid": r.DocId or "", "sno": r.SNo or 0,
                        "mobile1": (r.Mobile1 or "").strip(),
                        "txtmsg": (r.TxtMsg or "").strip(),
                        "msgtype": r.MsgType or ""})
        except AttributeError:
            out.append({"docid": str(r[0] or ""), "sno": r[1] or 0,
                        "mobile1": str(r[2] or "").strip(),
                        "txtmsg": str(r[3] or "").strip(),
                        "msgtype": str(r[4] or "")})
    return out


def _apply_phone_prefix(phone: str, prefix: str) -> str:
    phone = phone.strip()
    if not phone:
        return phone
    prefix = (prefix or "").strip()
    if prefix and not phone.startswith(prefix):
        # avoid double-prefixing country codes
        if not phone.startswith("+") and not phone.startswith(prefix):
            return prefix + phone
    return phone


def send_queued_sms(limit: int = 50, timeout: float = 10.0,
                    cn=None, mark_sent: bool = True) -> dict:
    """Dispatch pending DBSendSMS rows over HTTP (MobWebAPI GET).

    Reads SMSEnviro (SmsURL + T* fragments). If SmsURL empty ->
    skip gracefully (no exception, status="no_url"). Success (HTTP 2xx
    with non-empty body, VB6 WaitForResponse) marks SendTF='TRUE'
    via sms_enviro.dbsendsms_update. All HTTP/DB errors go through
    log_error.

    Returns dict: status, sent, failed, skipped, results.
    """
    from HMS_py.core.http_client import http_get
    from HMS_py.core.sms_enviro import smsenviro_get, dbsendsms_update

    summary = {"status": "ok", "sent": 0, "failed": 0, "skipped": 0,
               "results": []}

    try:
        env = smsenviro_get(cn=cn)
    except Exception as exc:
        log_error(exc, procedure="sms_http.send_queued_sms",
                  severity=20, extra="smsenviro_get failed")
        summary["status"] = "no_enviro"
        summary["error"] = str(exc)
        return summary

    sms_url = (env.get("smsurl") or "").strip()
    if not sms_url:
        # Documented graceful skip: no gateway URL configured in SMSEnviro.
        summary["status"] = "no_url"
        summary["message"] = (
            "SMSEnviro.SmsURL empty — SMS gateway not configured; "
            "queue left untouched.")
        return summary

    try:
        pending = _pending_queue(limit=limit, cn=cn)
    except Exception as exc:
        log_error(exc, procedure="sms_http.send_queued_sms",
                  severity=30, extra="DBSendSMS pending read failed")
        summary["status"] = "db_error"
        summary["error"] = str(exc)
        return summary

    prefix = (env.get("smsphonenoprefix") or "").strip()
    for row in pending:
        phone = _apply_phone_prefix(row["mobile1"], prefix)
        if not phone or len(phone) < 10:
            summary["skipped"] += 1
            summary["results"].append(
                {"docid": row["docid"], "sno": row["sno"],
                 "status": "bad_phone"})
            continue
        url = build_sms_url(env, phone, row["txtmsg"])
        try:
            status, body, _headers = http_get(url, timeout=timeout,
                                              procedure="sms_http.send_queued_sms")
        except Exception as exc:
            # http_client already logged; count failure
            summary["failed"] += 1
            summary["results"].append(
                {"docid": row["docid"], "sno": row["sno"],
                 "status": "http_error", "error": str(exc)})
            log_error(exc, procedure="sms_http.send_queued_sms",
                      severity=30,
                      extra=f"docid={row['docid']} sno={row['sno']}")
            continue

        ok = 200 <= status < 300 and bool(body.strip())
        if ok:
            summary["sent"] += 1
            summary["results"].append(
                {"docid": row["docid"], "sno": row["sno"],
                 "status": "sent", "http": status})
            if mark_sent:
                try:
                    now = datetime.now()
                    dbsendsms_update(
                        row["docid"], row["sno"],
                        {"txt_msg": row["txtmsg"],
                         "sms_dt": now.date(),
                         "sms_tm": now.strftime("%H:%M:%S"),
                         "send_tf": "TRUE",
                         "delv_dt": now.date(),
                         "delv_tm": now.strftime("%H:%M:%S")},
                        cn=cn, commit=cn is None)
                except Exception as exc:
                    log_error(exc, procedure="sms_http.send_queued_sms",
                              severity=30,
                              extra=f"mark sent failed docid={row['docid']}")
        else:
            # VB6: empty response body -> "no response from server"
            summary["failed"] += 1
            summary["results"].append(
                {"docid": row["docid"], "sno": row["sno"],
                 "status": "no_response" if not body.strip() else "http_fail",
                 "http": status})
            log_error(
                f"SMS dispatch failed HTTP {status} docid={row['docid']}",
                procedure="sms_http.send_queued_sms", severity=20,
                extra=body[:200])

    if summary["failed"] and not summary["sent"]:
        summary["status"] = "all_failed"
    return summary


def send_sms_via_http(phone: str, message: str, timeout: float = 10.0,
                      cn=None) -> SMSResponse:
    """Single ad-hoc SMS via SMSEnviro.SmsURL (MobWebAPI GET).

    Falls back to mock response when SmsURL not configured.
    """
    from HMS_py.core.http_client import http_get
    from HMS_py.core.sms_enviro import smsenviro_get

    try:
        env = smsenviro_get(cn=cn)
    except Exception as exc:
        log_error(exc, procedure="sms_http.send_sms_via_http",
                  severity=20, extra="smsenviro_get failed")
        return SMSResponse(success=False, error=f"SMSEnviro: {exc}")

    if not (env.get("smsurl") or "").strip():
        return SMSResponse(
            success=False,
            error="No SmsURL configured (SMSEnviro) — dispatch skipped")

    if not validate_phone(phone):
        return SMSResponse(success=False, error="Invalid phone")

    prefix = (env.get("smsphonenoprefix") or "").strip()
    url = build_sms_url(env, _apply_phone_prefix(phone, prefix), message)
    try:
        status, body, _headers = http_get(url, timeout=timeout,
                                          procedure="sms_http.send_sms_via_http")
    except Exception as exc:
        return SMSResponse(success=False, error=str(exc) or "HTTP error")

    ok = 200 <= status < 300 and bool(body.strip())
    return SMSResponse(
        success=ok,
        message_id=f"HTTP{status}",
        status_code=status,
        error="" if ok else ("Empty response" if not body.strip()
                             else f"HTTP {status}"),
        raw_response=body[:500],
    )


if __name__ == "__main__":
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    engine = SMSEngine(mock_mode=True)
    resp = engine.send(SMSMessage(recipient="+919876543210",
                                   message_text="Test"))
    print(f"Send result: success={resp.success}, id={resp.message_id}")
    log = engine.get_sent_log()
    print(f"Log entries: {len(log)}")
