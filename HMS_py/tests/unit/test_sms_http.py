"""SMS HTTP module unit tests.

Tests core/sms_http.py: SMSEngine, SMSMessage, SMSResponse,
format_phone, validate_phone, SMSLogViewer, template management.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest


# ============================================================ imports
from HMS_py.core.sms_http import (
    SMSEngine, SMSMessage, SMSResponse,
    format_phone, validate_phone, SMSLogViewer,
    send_sms, send_template_sms, SMS_TEMPLATES,
)


# ============================================================ format_phone
class TestFormatPhone:
    def test_valid_10_digit(self):
        assert format_phone("9876543210") == "+919876543210"

    def test_valid_with_country_code(self):
        assert format_phone("+919876543210") == "+919876543210"

    def test_valid_with_spaces(self):
        assert format_phone("+91 98765 43210") == "+919876543210"

    def test_valid_with_dashes(self):
        assert format_phone("+91-98765-43210") == "+919876543210"

    def test_already_formatted(self):
        assert format_phone("+919876543210") == "+919876543210"

    def test_empty_returns_empty(self):
        assert format_phone("") == ""

    def test_13_digit_starts_with_plus91(self):
        assert format_phone("+919876543210") == "+919876543210"


# ============================================================ validate_phone
class TestValidatePhone:
    def test_valid_mobile(self):
        assert validate_phone("9876543210") is True

    def test_valid_with_country(self):
        assert validate_phone("+919876543210") is True

    def test_invalid_short(self):
        assert validate_phone("98765") is False

    def test_invalid_zeros(self):
        assert validate_phone("0000000000") is False

    def test_invalid_empty(self):
        assert validate_phone("") is False

    def test_starts_with_zero(self):
        assert validate_phone("0987654321") is False


# ============================================================ SMSMessage
class TestSMSMessage:
    def test_default_values(self):
        msg = SMSMessage(recipient="+919876543210")
        assert msg.recipient == "+919876543210"
        assert msg.template_key == ""
        assert msg.message_text == ""
        assert msg.sender_name == ""
        assert msg.msg_type == "Normal"
        assert msg.doc_id == ""
        assert msg.v_no == 0
        assert msg.bill_amount == 0.0

    def test_all_fields(self):
        msg = SMSMessage(
            recipient="+919876543210",
            template_key="CheckInMsg",
            message_text="Welcome",
            sender_name="HMS",
            msg_type="Transactional",
            doc_id="DOC001",
            sub_code="SUB1",
            v_no=5,
            bill_amount=1500.0,
            party_name="Test Party",
            room_no="101",
        )
        assert msg.recipient == "+919876543210"
        assert msg.template_key == "CheckInMsg"
        assert msg.message_text == "Welcome"
        assert msg.sender_name == "HMS"
        assert msg.msg_type == "Transactional"
        assert msg.doc_id == "DOC001"
        assert msg.v_no == 5
        assert msg.bill_amount == 1500.0
        assert msg.party_name == "Test Party"
        assert msg.room_no == "101"


# ============================================================ SMSResponse
class TestSMSResponse:
    def test_success_response(self):
        resp = SMSResponse(success=True, message_id="MSG001")
        assert resp.success is True
        assert resp.message_id == "MSG001"
        assert resp.error == ""
        assert resp.status_code == 0
        assert resp.retry_count == 0

    def test_error_response(self):
        resp = SMSResponse(success=False, error="Timeout")
        assert resp.success is False
        assert resp.error == "Timeout"

    def test_full_response(self):
        resp = SMSResponse(
            success=True, message_id="MSG002",
            status_code=200, error="",
            raw_response='{"id":"MSG002"}',
            retry_count=2)
        assert resp.success is True
        assert resp.status_code == 200
        assert resp.raw_response == '{"id":"MSG002"}'
        assert resp.retry_count == 2


# ============================================================ SMSEngine mock
class TestSMSEngineMock:
    def test_default_mock_mode(self):
        engine = SMSEngine(mock_mode=True)
        assert engine.mock_mode is True
        assert engine.max_retries == 3
        assert engine.retry_delay == 1.0

    def test_custom_retries(self):
        engine = SMSEngine(mock_mode=True, max_retries=5, retry_delay=2.0)
        assert engine.max_retries == 5
        assert engine.retry_delay == 2.0

    def test_send_valid_phone(self):
        engine = SMSEngine(mock_mode=True)
        resp = engine.send(SMSMessage(
            recipient="+919876543210",
            message_text="Test message"))
        assert resp.success is True
        assert resp.message_id != ""
        assert resp.status_code == 200

    def test_send_invalid_phone(self):
        engine = SMSEngine(mock_mode=True)
        resp = engine.send(SMSMessage(
            recipient="invalid",
            message_text="Test"))
        assert resp.success is False
        assert "Invalid phone" in resp.error

    def test_send_empty_recipient(self):
        engine = SMSEngine(mock_mode=True)
        resp = engine.send(SMSMessage(
            recipient="",
            message_text="Test"))
        assert resp.success is False
        assert "Empty recipient" in resp.error

    def test_send_empty_message(self):
        engine = SMSEngine(mock_mode=True)
        resp = engine.send(SMSMessage(
            recipient="+919876543210",
            message_text=""))
        assert resp.success is False
        assert "Empty message text" in resp.error

    def test_send_bulk(self):
        engine = SMSEngine(mock_mode=True)
        msgs = [
            SMSMessage(recipient="+919876543210",
                        message_text=f"Msg {i}")
            for i in range(3)
        ]
        results = engine.send_bulk(msgs)
        assert len(results) == 3
        assert all(r.success for r in results)

    def test_get_sent_log(self):
        engine = SMSEngine(mock_mode=True)
        engine.send(SMSMessage(
            recipient="+919876543210",
            message_text="Test"))
        log = engine.get_sent_log()
        assert len(log) == 1
        assert log[0].success is True

    def test_get_last_response(self):
        engine = SMSEngine(mock_mode=True)
        resp = engine.send(SMSMessage(
            recipient="+919876543210",
            message_text="Test"))
        last = engine.get_last_response()
        assert last is not None
        assert last.success is True
        assert last.message_id == resp.message_id

    def test_get_all_templates(self):
        engine = SMSEngine(mock_mode=True)
        templates = engine.get_all_templates()
        assert isinstance(templates, dict)
        for key in ["CheckInMsg", "CheckOutMsg", "ReservationMsg"]:
            assert key in templates

    def test_get_template(self):
        engine = SMSEngine(mock_mode=True)
        template = engine.get_template("CheckInMsg")
        assert isinstance(template, str)

    def test_set_template(self):
        engine = SMSEngine(mock_mode=True)
        engine.set_template("CustomKey", "Custom text")
        assert engine.get_template("CustomKey") == "Custom text"

    def test_get_pending_sms(self):
        engine = SMSEngine(mock_mode=True)
        pending = engine.get_pending_sms()
        assert isinstance(pending, list)


# ============================================================ send_sms convenience
class TestConvenienceFunctions:
    def test_send_sms_returns_response(self):
        resp = send_sms("+919876543210", "Hello")
        assert isinstance(resp, SMSResponse)
        assert resp.success is True

    def test_send_sms_invalid(self):
        resp = send_sms("invalid", "Hello")
        assert resp.success is False

    def test_send_template_sms(self):
        resp = send_template_sms("+919876543210", "CheckInMsg")
        assert isinstance(resp, SMSResponse)


# ============================================================ SMSLogViewer
class TestSMSLogViewer:
    def test_get_outbox_returns_list(self):
        viewer = SMSLogViewer()
        outbox = viewer.get_outbox(limit=10)
        assert isinstance(outbox, list)

    def test_get_inbox_returns_list(self):
        viewer = SMSLogViewer()
        inbox = viewer.get_inbox(limit=10)
        assert isinstance(inbox, list)

    def test_get_history_returns_list(self):
        viewer = SMSLogViewer()
        history = viewer.get_history(limit=10)
        assert isinstance(history, list)

    def test_history_entries_have_required_keys(self):
        viewer = SMSLogViewer()
        history = viewer.get_history(limit=5)
        for entry in history:
            assert "date" in entry
            assert "mobile" in entry
            assert "message" in entry
            assert "sender" in entry
            assert "sent" in entry

    def test_mark_sent_returns_bool(self):
        viewer = SMSLogViewer()
        result = viewer.mark_sent("DOC001", 1)
        assert isinstance(result, bool)


# ============================================================ SMS_TEMPLATES constant
class TestSMSTemplatesConstant:
    def test_templates_list_not_empty(self):
        assert len(SMS_TEMPLATES) > 0

    def test_contains_expected_keys(self):
        expected = ["CheckInMsg", "CheckOutMsg", "ReservationMsg",
                     "GuestRegistrationMsg", "POSBillMsg"]
        for key in expected:
            assert key in SMS_TEMPLATES

    def test_all_strings(self):
        assert all(isinstance(t, str) for t in SMS_TEMPLATES)