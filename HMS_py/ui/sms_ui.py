"""SMS UI - SMS Composition, Send, History (VB6 MemberSMS.frm port).

Provides:
- SMSSendDialog: Compose and send SMS
- SMSHistoryDialog: View SMS log/history
- SMSTemplateDialog: Manage SMS templates

Follows existing UI patterns: theme.py, design.py,
shell.py _form_registry conventions.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QKeySequence, QShortcut
from PyQt6.QtWidgets import (QDialog, QFormLayout, QHBoxLayout,
                             QLabel, QLineEdit, QMessageBox,
                             QPushButton, QTableWidget,
                             QTableWidgetItem, QVBoxLayout,
                             QWidget, QTabWidget, QGroupBox,
                             QTextEdit, QComboBox, QSpinBox,
                             QAbstractItemView, QHeaderView,
                             QFrame, QSplitter)

from HMS_py.core import db
from HMS_py.core.sms_http import (SMSEngine, SMSMessage,
                                   format_phone, validate_phone,
                                   SMSResponse)
import logging
logger = logging.getLogger(__name__)

SITE_CODE = db.get_site_code()

from HMS_py.core.sms_enviro import smsenviro_get
from HMS_py.ui import theme as _theme
from HMS_py.ui.design import (DS, Spacing, Size, Font,
                               styled_button, make_card_v2,
                               make_form_row, make_line_edit,
                               make_combo_box, make_text_edit,
                               setup_table, status_badge,
                               make_button_bar, Layout)
from HMS_py.ui.base_master import BaseMasterForm, Field, MasterConfig


class SMSSendDialog(QDialog):
    """SMS Composition dialog (VB6 MemberSMS.frm port).

    Allows composing SMS with template selection,
    recipient entry, send with retry, and status display.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SMS Send - HMS_py")
        self.resize(720, 560)
        self.setModal(True)
        self._engine = SMSEngine(mock_mode=True)
        self._sending = False

        self._build_ui()
        self._load_templates()
        self._refresh_queues()
        QTimer.singleShot(0, self._refresh_queues)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(Spacing.XL, Layout.CARD[1],
                                Spacing.XL, Layout.CARD[3])
        root.setSpacing(Spacing.MD)

        # --- Template selection card ---
        tmpl_card = make_card_v2("Message Template", parent=self)
        tmpl_lay = QFormLayout()
        tmpl_lay.setSpacing(Spacing.SM)

        self.cmb_template = make_combo_box(
            items=[], placeholder="Select template...",
            tooltip="Choose a predefined SMS template")
        self.cmb_template.currentIndexChanged.connect(self._on_template)
        tmpl_lay.addRow("Template:", self.cmb_template)

        self.txt_sender = make_line_edit(
            placeholder="Sender Name", tooltip="SMS Sender ID")
        tmpl_lay.addRow("Sender:", self.txt_sender)

        self.txt_msg = make_text_edit(
            placeholder="Type your message here...",
            min_height=100, tooltip="SMS message body")
        tmpl_lay.addRow("Message:", self.txt_msg)

        tmpl_card.layout().addLayout(tmpl_lay)
        root.addWidget(tmpl_card)

        # --- Recipient card ---
        recv_card = make_card_v2("Recipient", parent=self)
        recv_lay = QFormLayout()
        recv_lay.setSpacing(Spacing.SM)

        self.txt_phone = make_line_edit(
            placeholder="+91XXXXXXXXXX", min_width=200,
            tooltip="Mobile number (India format)")
        self.txt_phone.textChanged.connect(self._validate_phone)
        recv_lay.addRow("Mobile No:", self.txt_phone)

        self.lbl_phone_status = QLabel("")
        self.lbl_phone_status.setStyleSheet(
            "font-size: 11px; font-weight: 500;")
        recv_lay.addRow("", self.lbl_phone_status)

        self.spn_count = DS.make_spin_box(
            minimum=1, maximum=100, suffix="",
            tooltip="Number of recipients (bulk)")
        recv_lay.addRow("Count:", self.spn_count)

        recv_card.layout().addLayout(recv_lay)
        root.addWidget(recv_card)

        # --- Queue/History tab ---
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(
            f"QTabWidget::pane {{ border: 1px solid {_theme.palette()['border']}; "
            f"border-radius: {Size.RADIUS}px; }}")

        # Outbox tab
        self.tbl_outbox = QTableWidget()
        setup_table(self.tbl_outbox,
                     ["Date", "Mobile", "Message", "Status"],
                     read_only=True)
        self.tbl_outbox.setMaximumHeight(180)
        self._load_outbox()

        # Sent tab
        self.tbl_sent = QTableWidget()
        setup_table(self.tbl_sent,
                     ["Date", "Mobile", "Message", "Status"],
                     read_only=True)
        self.tbl_sent.setMaximumHeight(180)
        self._load_sent()

        out_frame = QFrame()
        out_lay = QVBoxLayout(out_frame)
        out_lay.addWidget(QLabel("OutBox (Pending)"))
        out_lay.addWidget(self.tbl_outbox)

        sent_frame = QFrame()
        sent_lay = QVBoxLayout(sent_frame)
        sent_lay.addWidget(QLabel("InBox (Sent)"))
        sent_lay.addWidget(self.tbl_sent)

        self.tabs.addTab(out_frame, "OutBox")
        self.tabs.addTab(sent_frame, "InBox")
        root.addWidget(self.tabs, stretch=1)

        # --- Status bar ---
        self.lbl_status = QLabel("Ready")
        self.lbl_status.setStyleSheet(
            f"font-size: {Font.SM}px; font-weight: 500; "
            f"color: {_theme.palette()['text_dim']}; padding: 4px;")
        root.addWidget(self.lbl_status)

        # --- Button bar ---
        self.btn_send = styled_button("Send SMS", role="primary",
                                       tooltip="Send SMS to recipient")
        self.btn_send.clicked.connect(self._do_send)
        self.btn_bulk = styled_button("Bulk Send", role="success",
                                       tooltip="Send to all recipients")
        self.btn_bulk.clicked.connect(self._do_bulk)
        self.btn_refresh = styled_button("Refresh",
                                          tooltip="Refresh queues")
        self.btn_refresh.clicked.connect(self._refresh_queues)
        self.btn_close = styled_button("Close", role="danger",
                                        tooltip="Close dialog")
        self.btn_close.clicked.connect(self.reject)

        bar = DS.make_button_bar([
            (self.btn_send, "primary"),
            (self.btn_bulk, "success"),
            (self.btn_refresh, "default"),
            (self.btn_close, "danger"),
        ], add_stretch=True)
        root.addWidget(bar)

        QShortcut(QKeySequence("Ctrl+Enter"), self,
                  activated=self._do_send)
        QShortcut(QKeySequence("F5"), self,
                  activated=self._refresh_queues)

    def _load_templates(self):
        """Populate template combo from SMSEnviro."""
        try:
            env = smsenviro_get()
            items = []
            for k in ["CheckInMsg", "CheckOutMsg", "ReservationMsg",
                       "ReservationCancelMsg", "OutStandingMsg",
                       "CashReceiptMsg", "BankReceiptMsg",
                       "MemberBillMsg", "GuestRegistrationMsg",
                       "RewardPointMsg", "RedeemPointMsg",
                       "POSBillMsg", "AssignDeliveryMsg"]:
                val = env.get(k.lower(), "")
                if val:
                    items.append((k, k))
            self.cmb_template.clear()
            self.cmb_template.addItem("<Custom Message>", "")
            for key, display in items:
                self.cmb_template.addItem(display, key)
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
            self.cmb_template.addItem("<No templates>", "")

    def _on_template(self, index: int):
        """Load template text when template selected."""
        if index <= 0:
            return
        key = self.cmb_template.currentData()
        if not key:
            return
        text = self._engine.get_template(key)
        if text:
            self.txt_msg.setPlainText(text)

    def _validate_phone(self, text: str):
        """Update phone validation status label."""
        phone = text.strip()
        if not phone:
            self.lbl_phone_status.setText("")
            return
        if validate_phone(phone):
            self.lbl_phone_status.setText(
                status_badge("Valid", "success"))
        else:
            self.lbl_phone_status.setText(
                status_badge("Invalid", "danger"))

    def _get_messages(self) -> list[SMSMessage]:
        """Build SMSMessage list from UI inputs."""
        msg_text = self.txt_msg.toPlainText().strip()
        sender = self.txt_sender.text().strip()
        phone = self.txt_phone.text().strip()
        count = int(self.spn_count.value())
        msgs = []
        if phone:
            msgs.append(SMSMessage(
                recipient=phone, message_text=msg_text,
                sender_name=sender or SITE_CODE))
        for i in range(1, count):
            msgs.append(SMSMessage(
                recipient=phone, message_text=msg_text,
                sender_name=sender or SITE_CODE))
        return msgs

    def _do_send(self):
        """Send single SMS."""
        if self._sending:
            return
        phone = self.txt_phone.text().strip()
        msg_text = self.txt_msg.toPlainText().strip()
        if not phone:
            QMessageBox.warning(self, "SMS", "Recipient mobile number required")
            return
        if not msg_text:
            QMessageBox.warning(self, "SMS", "Message text required")
            return
        if not validate_phone(phone):
            QMessageBox.warning(self, "SMS", f"Invalid phone: {phone}")
            return
        self._sending = True
        self.btn_send.setEnabled(False)
        self.lbl_status.setText("Sending...")
        engine = SMSEngine(mock_mode=self._engine.mock_mode)
        resp = engine.send(SMSMessage(
            recipient=phone, message_text=msg_text,
            sender_name=self.txt_sender.text().strip()))
        self._sending = False
        self.btn_send.setEnabled(True)
        if resp.success:
            self.lbl_status.setText(
                f"Sent OK: {resp.message_id}")
            self._refresh_queues()
        else:
            self.lbl_status.setText(
                f"Failed: {resp.error}")
            QMessageBox.critical(self, "SMS Send Failed",
                                  f"Error: {resp.error}\n"
                                  f"Retry count: {resp.retry_count}")

    def _do_bulk(self):
        """Send bulk SMS."""
        if self._sending:
            return
        phone = self.txt_phone.text().strip()
        msg_text = self.txt_msg.toPlainText().strip()
        if not phone or not msg_text:
            QMessageBox.warning(self, "SMS",
                                 "Phone and message required")
            return
        self._sending = True
        self.btn_bulk.setEnabled(False)
        self.lbl_status.setText("Bulk sending...")
        engine = SMSEngine(mock_mode=self._engine.mock_mode)
        msgs = self._get_messages()
        results = engine.send_bulk(msgs)
        success = sum(1 for r in results if r.success)
        self._sending = False
        self.btn_bulk.setEnabled(True)
        self.lbl_status.setText(
            f"Bulk complete: {success}/{len(results)} sent")
        self._refresh_queues()

    def _load_outbox(self):
        """Load pending SMS into outbox table."""
        from HMS_py.core.sms_http import SMSLogViewer
        viewer = SMSLogViewer()
        rows = viewer.get_outbox(limit=50)
        self.tbl_outbox.setRowCount(len(rows))
        for r, rec in enumerate(rows):
            self.tbl_outbox.setItem(r, 0,
                QTableWidgetItem(str(rec.get("date", ""))))
            self.tbl_outbox.setItem(r, 1,
                QTableWidgetItem(str(rec.get("mobile", ""))))
            self.tbl_outbox.setItem(r, 2,
                QTableWidgetItem(str(rec.get("message", ""))))
            self.tbl_outbox.setItem(r, 3,
                QTableWidgetItem("Pending"))
            self.tbl_outbox.item(r, 3).setForeground(
                QColor(_theme.palette()["warning"]))

    def _load_sent(self):
        """Load sent SMS into inbox table."""
        from HMS_py.core.sms_http import SMSLogViewer
        viewer = SMSLogViewer()
        rows = viewer.get_inbox(limit=50)
        self.tbl_sent.setRowCount(len(rows))
        for r, rec in enumerate(rows):
            self.tbl_sent.setItem(r, 0,
                QTableWidgetItem(str(rec.get("date", ""))))
            self.tbl_sent.setItem(r, 1,
                QTableWidgetItem(str(rec.get("mobile", ""))))
            self.tbl_sent.setItem(r, 2,
                QTableWidgetItem(str(rec.get("message", ""))))
            self.tbl_sent.setItem(r, 3,
                QTableWidgetItem("Sent"))
            self.tbl_sent.item(r, 3).setForeground(
                QColor(_theme.palette()["success"]))

    def _refresh_queues(self):
        """Refresh both outbox and inbox tables."""
        self._load_outbox()
        self._load_sent()


class SMSHistoryDialog(QDialog):
    """SMS History/Log viewer (VB6 InBox/OutBox port).

    Shows full SMS history from DBSendSMS with filters.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SMS History - HMS_py")
        self.resize(800, 600)
        self.setModal(True)

        self._build_ui()
        self._load_history()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(Spacing.XL, Layout.CARD[1],
                                Spacing.XL, Layout.CARD[3])
        root.setSpacing(Spacing.MD)

        # Filter bar
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(Spacing.SM)
        self.lbl_filter = QLabel("Filter:")
        self.cmb_filter = make_combo_box(
            items=["All", "Sent", "Pending"],
            placeholder="Status", tooltip="Filter by status")
        self.cmb_filter.currentIndexChanged.connect(self._load_history)
        filter_bar.addWidget(self.lbl_filter)
        filter_bar.addWidget(self.cmb_filter)
        filter_bar.addStretch()
        self.btn_export = styled_button("Export",
                                         tooltip="Export SMS log")
        self.btn_export.clicked.connect(self._export)
        filter_bar.addWidget(self.btn_export)
        root.addLayout(filter_bar)

        # History table
        self.tbl = QTableWidget()
        setup_table(self.tbl,
                     ["Date", "Mobile", "Message",
                      "Sender", "Status", "DocId"],
                     sortable=True, read_only=True)
        self.tbl.setMinimumHeight(350)
        root.addWidget(self.tbl, stretch=1)

        # Summary
        self.lbl_summary = QLabel("")
        self.lbl_summary.setStyleSheet(
            f"font-size: {Font.SM}px; font-weight: 500; "
            f"color: {_theme.palette()['text_dim']}; padding: 4px;")
        root.addWidget(self.lbl_summary)

        # Close
        btn_close = styled_button("Close", role="danger")
        btn_close.clicked.connect(self.reject)
        root.addWidget(btn_close)

    def _load_history(self):
        """Load SMS history from DB."""
        from HMS_py.core.sms_http import SMSLogViewer
        viewer = SMSLogViewer()
        filter_type = self.cmb_filter.currentText()
        rows = viewer.get_history(limit=200)

        filtered = rows
        if filter_type == "Sent":
            filtered = [r for r in rows if r.get("sent")]
        elif filter_type == "Pending":
            filtered = [r for r in rows if not r.get("sent")]

        self.tbl.setRowCount(len(filtered))
        for r, rec in enumerate(filtered):
            self.tbl.setItem(r, 0,
                QTableWidgetItem(str(rec.get("date", ""))))
            self.tbl.setItem(r, 1,
                QTableWidgetItem(str(rec.get("mobile", ""))))
            self.tbl.setItem(r, 2,
                QTableWidgetItem(str(rec.get("message", ""))))
            self.tbl.setItem(r, 3,
                QTableWidgetItem(str(rec.get("sender", ""))))
            status_item = QTableWidgetItem(
                "Sent" if rec.get("sent") else "Pending")
            status_item.setForeground(
                QColor(_theme.palette()["success"]
                       if rec.get("sent") else "warning"))
            self.tbl.setItem(r, 4, status_item)
            self.tbl.setItem(r, 5,
                QTableWidgetItem(str(rec.get("docid", ""))))

        self.lbl_summary.setText(
            f"Showing {len(filtered)} of {len(rows)} SMS records")

    def _export(self):
        """Export SMS history to text file."""
        from HMS_py.core.sms_http import SMSLogViewer
        viewer = SMSLogViewer()
        rows = viewer.get_history(limit=500)
        if not rows:
            QMessageBox.information(self, "Export", "No records to export")
            return
        path = os.path.join(os.path.dirname(__file__),
                             "..", "sms_export.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write("Date,Mobile,Message,Sender,Status,DocId\n")
            for rec in rows:
                f.write(
                    f"{rec.get('date','')},"
                    f"{rec.get('mobile','')},"
                    f'"{rec.get("message","")}",'
                    f"{rec.get('sender','')},"
                    f"{'Sent' if rec.get('sent') else 'Pending'},"
                    f"{rec.get('docid','')}\n")
        QMessageBox.information(
            self, "Export", f"Exported {len(rows)} records to {path}")


class SMSTemplateDialog(QDialog):
    """SMS Template Manager (VB6 SMS Center Settings port).

    Allows viewing and editing SMS templates stored in SMSEnviro.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SMS Templates - HMS_py")
        self.resize(700, 500)
        self.setModal(True)
        self._engine = SMSEngine()

        self._build_ui()
        self._load_templates()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(Spacing.XL, Layout.CARD[1],
                                Spacing.XL, Layout.CARD[3])
        root.setSpacing(Spacing.MD)

        # Template list
        self.lbl_title = QLabel("SMS Templates")
        self.lbl_title.setProperty("glassTitle", True)
        root.addWidget(self.lbl_title)

        self.tbl = QTableWidget()
        setup_table(self.tbl, ["Template Key", "Message Content"],
                     sortable=True, read_only=False)
        self.tbl.setMinimumHeight(250)
        root.addWidget(self.tbl, stretch=1)

        # Buttons
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(Spacing.SM)
        self.btn_save = styled_button("Save Templates",
                                       role="primary",
                                       tooltip="Save all templates")
        self.btn_save.clicked.connect(self._save_templates)
        btn_bar.addWidget(self.btn_save)
        btn_bar.addStretch()
        self.btn_close = styled_button("Close", role="danger")
        self.btn_close.clicked.connect(self.reject)
        btn_bar.addWidget(self.btn_close)
        root.addLayout(btn_bar)

    def _load_templates(self):
        """Load all templates into table."""
        from HMS_py.core.sms_http import SMS_TEMPLATES
        templates = self._engine.get_all_templates()
        self.tbl.setRowCount(len(SMS_TEMPLATES))
        for i, key in enumerate(SMS_TEMPLATES):
            self.tbl.setItem(i, 0, QTableWidgetItem(key))
            val = templates.get(key, "")
            self.tbl.setItem(i, 1, QTableWidgetItem(val))

    def _save_templates(self):
        """Save all templates from table back to SMSEnviro."""
        rows = self.tbl.rowCount()
        saved = 0
        for i in range(rows):
            key_item = self.tbl.item(i, 0)
            val_item = self.tbl.item(i, 1)
            if key_item and val_item:
                key = key_item.text()
                val = val_item.text()
                self._engine.set_template(key, val)
                saved += 1
        QMessageBox.information(
            self, "Templates Saved",
            f"{saved} templates updated.")
        self._load_templates()


def open_sms_send(w=None):
    """Open SMS Send dialog."""
    dlg = SMSSendDialog(w)
    dlg.exec()


def open_sms_history(w=None):
    """Open SMS History dialog."""
    dlg = SMSHistoryDialog(w)
    dlg.exec()


def open_sms_templates(w=None):
    """Open SMS Template dialog."""
    dlg = SMSTemplateDialog(w)
    dlg.exec()


class SMSEnviroSettings(QDialog):
    """SMS Environment Settings (VB6 SMS Environment port).

    Configure SMS Center credentials and settings.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SMS Environment Settings")
        self.resize(750, 600)
        self.setModal(True)
        self._build_ui()
        self._load_settings()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(Spacing.XL, Layout.CARD[1],
                                Spacing.XL, Layout.CARD[3])
        root.setSpacing(Spacing.MD)

        # Card with settings
        card = make_card_v2("SMS Center Configuration", parent=self)
        form = QFormLayout()
        form.setSpacing(Spacing.SM)

        self.txt_user = make_line_edit(placeholder="SMS Center Username")
        form.addRow("Username:", self.txt_user)

        self.txt_pass = make_line_edit(placeholder="SMS Center Password")
        self.txt_pass.setText("")
        form.addRow("Password:", self.txt_pass)

        self.txt_url = make_line_edit(placeholder="SMS API URL")
        form.addRow("SMS URL:", self.txt_url)

        self.txt_display = make_line_edit(placeholder="Display Name")
        form.addRow("Display Name:", self.txt_display)

        self.txt_purchase = make_line_edit(placeholder="Purchase URL")
        form.addRow("Purchase URL:", self.txt_purchase)

        self.txt_bal = make_line_edit(placeholder="Balance URL")
        form.addRow("Balance URL:", self.txt_bal)

        self.cmb_mock = make_combo_box(
            items=["Yes", "No"], placeholder="Mock Mode")
        form.addRow("Mock Mode:", self.cmb_mock)

        card.layout().addLayout(form)
        root.addWidget(card)

        # Buttons
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(Spacing.SM)
        self.btn_save = styled_button("Save Settings",
                                       role="primary")
        self.btn_save.clicked.connect(self._save)
        btn_bar.addWidget(self.btn_save)
        btn_bar.addStretch()
        self.btn_test = styled_button("Test Connection",
                                       tooltip="Test SMS API connection")
        self.btn_test.clicked.connect(self._test)
        btn_bar.addWidget(self.btn_test)
        btn_bar.addWidget(styled_button("Close", role="danger")
                          .clicked.connect(self.reject))
        root.addLayout(btn_bar)

    def _load_settings(self):
        """Load current SMS settings."""
        try:
            env = smsenviro_get()
            self.txt_user.setText(env.get("smsscenterusername", ""))
            self.txt_pass.setText(env.get("smsscenterpassword", ""))
            self.txt_url.setText(env.get("smsurl", ""))
            self.txt_display.setText(env.get("smsdisplayname", ""))
            self.txt_purchase.setText(env.get("smspurchase", ""))
            self.txt_bal.setText(env.get("smsbal", ""))
        except Exception:
            pass

    def _save(self):
        """Save SMS settings."""
        from HMS_py.core.sms_enviro import smsenviro_update
        changes = {}
        if self.txt_user.text().strip():
            changes["SmsCenterUserName"] = self.txt_user.text().strip()
        if self.txt_pass.text().strip():
            changes["SmsCenterPassword"] = self.txt_pass.text().strip()
        if self.txt_url.text().strip():
            changes["SmsURL"] = self.txt_url.text().strip()
        if self.txt_display.text().strip():
            changes["SmsDisplayName"] = self.txt_display.text().strip()
        if self.txt_purchase.text().strip():
            changes["SmsPurchase"] = self.txt_purchase.text().strip()
        if self.txt_bal.text().strip():
            changes["SmsBal"] = self.txt_bal.text().strip()
        if changes:
            smsenviro_update(changes)
            QMessageBox.information(self, "Settings",
                                     "SMS settings saved.")

    def _test(self):
        """Test SMS API connection."""
        try:
            engine = SMSEngine(mock_mode=False)
            resp = engine.send(SMSMessage(
                recipient="+919999999999",
                message_text="HMS Test Message"))
            if resp.success:
                QMessageBox.information(
                    self, "Test", f"SMS sent! ID: {resp.message_id}")
            else:
                QMessageBox.warning(
                    self, "Test",
                    f"SMS failed: {resp.error}")
        except Exception as e:
            QMessageBox.critical(self, "Test", str(e))
