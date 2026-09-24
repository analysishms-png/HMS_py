import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit,
    QLabel, QFormLayout, QMessageBox, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from HMS_py.core import hr_payroll
from HMS_py.ui import theme as _theme


class HrPayrollDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("HR Payroll Operations")
        self.resize(950, 650)
        self.current_mode = None
        self.current_row = -1
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self._build_salary_tab()
        self._build_attendance_tab()
        self._build_loan_tab()
        self._build_overtime_tab()

    @staticmethod
    def _dark_item(text):
        item = QTableWidgetItem(str(text))
        item.setForeground(QColor(_theme.palette()["text"]))
        return item

    def _clear_form(self, fields):
        for w in fields:
            if isinstance(w, QLineEdit):
                w.clear()

    _BTN_TOOLTIPS = {
        "New": "Add new record", "Edit": "Edit selected record",
        "Delete": "Delete selected record", "Save": "Save changes",
        "Cancel": "Cancel current operation", "Refresh": "Reload data from database",
    }

    def _make_btn(self, text, slot=None):
        btn = QPushButton(text)
        btn.setToolTip(self._BTN_TOOLTIPS.get(text, ""))
        if slot:
            btn.clicked.connect(slot)
        return btn

    def _btn_row(self, buttons):
        row = QHBoxLayout()
        for b in buttons:
            row.addWidget(b)
        return row

    def _set_form_enabled(self, fields, enabled):
        for w in fields:
            w.setEnabled(enabled)

    # ── SALARY TAB ──────────────────────────────────────────
    def _build_salary_tab(self):
        tab = QWidget()
        v = QVBoxLayout(tab)

        self.sal_table = QTableWidget(0, 8)
        self.sal_table.setHorizontalHeaderLabels(
            ["Emp_Code", "Mth_Year", "Basic", "DA", "HRA", "Gross", "Deductions", "Net"]
        )
        self.sal_table.setAlternatingRowColors(True)
        self.sal_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sal_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.sal_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.sal_table.itemSelectionChanged.connect(self._sal_select)
        v.addWidget(self.sal_table)

        form = QFormLayout()
        self.sal_mth = QLineEdit()
        self.sal_mth.setMaxLength(10)
        self.sal_mth.setPlaceholderText("e.g. 01/2026")
        self.sal_emp = QLineEdit()
        self.sal_emp.setMaxLength(10)
        self.sal_emp.setPlaceholderText("e.g. EMP001")
        self.sal_basic = QLineEdit()
        self.sal_basic.setMaxLength(12)
        self.sal_basic.setPlaceholderText("e.g. 25000")
        self.sal_da = QLineEdit()
        self.sal_da.setMaxLength(12)
        self.sal_da.setPlaceholderText("e.g. 5000")
        self.sal_hra = QLineEdit()
        self.sal_hra.setMaxLength(12)
        self.sal_hra.setPlaceholderText("e.g. 8000")
        self.sal_ded = QLineEdit()
        self.sal_ded.setMaxLength(12)
        self.sal_ded.setPlaceholderText("e.g. 2000")
        form.addRow("Mth_Year:", self.sal_mth)
        form.addRow("Emp_Code:", self.sal_emp)
        form.addRow("Basic:", self.sal_basic)
        form.addRow("DA:", self.sal_da)
        form.addRow("HRA:", self.sal_hra)
        form.addRow("Deductions:", self.sal_ded)
        v.addLayout(form)

        self._sal_fields = [self.sal_mth, self.sal_emp, self.sal_basic,
                            self.sal_da, self.sal_hra, self.sal_ded]

        btn_new = self._make_btn("New", self._sal_new)
        btn_edit = self._make_btn("Edit", self._sal_edit)
        btn_del = self._make_btn("Delete", self._sal_delete)
        btn_save = self._make_btn("Save", self._sal_save)
        btn_cancel = self._make_btn("Cancel", self._sal_cancel)
        btn_refresh = self._make_btn("Refresh", self._sal_refresh)
        v.addLayout(self._btn_row([btn_new, btn_edit, btn_del, btn_save, btn_cancel, btn_refresh]))

        self.tabs.addTab(tab, "Salary")
        self._sal_refresh()

    def _sal_refresh(self):
        try:
            rows = hr_payroll.list_salary()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        self.sal_table.setRowCount(0)
        if not rows:
            return
        self.sal_table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            vals = ([r.get("mth_year", ""), r.get("emp_code", ""),
                     r.get("basic", 0), r.get("da", 0), r.get("hra", 0),
                     (r.get("basic", 0) or 0) + (r.get("da", 0) or 0) +
                     (r.get("hra", 0) or 0), "", r.get("net_salary", 0)]
                    if isinstance(r, dict) else list(r))
            for j, val in enumerate(vals):
                self.sal_table.setItem(i, j, self._dark_item(val))

    def _sal_select(self):
        sel = self.sal_table.selectionModel().selectedRows()
        if not sel:
            return
        row = sel[0].row()
        self.current_row = row
        self.sal_mth.setText(self.sal_table.item(row, 0).text())
        self.sal_emp.setText(self.sal_table.item(row, 1).text())
        self.sal_basic.setText(self.sal_table.item(row, 2).text())
        self.sal_da.setText(self.sal_table.item(row, 3).text())
        self.sal_hra.setText(self.sal_table.item(row, 4).text())
        self.sal_ded.setText(self.sal_table.item(row, 6).text())

    def _sal_new(self):
        self.current_mode = "new"
        self._clear_form(self._sal_fields)
        self._set_form_enabled(self._sal_fields, True)
        self.sal_emp.setFocus()

    def _sal_edit(self):
        if self.current_row < 0:
            QMessageBox.information(self, "Info", "Select a row first.")
            return
        self.current_mode = "edit"
        self._set_form_enabled(self._sal_fields, True)
        self.sal_emp.setReadOnly(True)

    def _sal_delete(self):
        if self.current_row < 0:
            QMessageBox.information(self, "Info", "Select a row first.")
            return
        mth = self.sal_mth.text().strip()
        emp = self.sal_emp.text().strip()
        reply = QMessageBox.question(self, "Confirm", f"Delete salary for {emp}/{mth}?")
        if reply == QMessageBox.StandardButton.Yes:
            try:
                hr_payroll.delete_salary(mth, emp)
                self._sal_refresh()
                self._clear_form(self._sal_fields)
                self.current_row = -1
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _sal_save(self):
        mth = self.sal_mth.text().strip()
        emp = self.sal_emp.text().strip()
        if not mth or not emp:
            QMessageBox.warning(self, "Warning", "Mth_Year and Emp_Code required.")
            return
        rec = {
            "mth_year": mth,
            "emp_code": emp,
            "basic": self.sal_basic.text().strip() or 0,
            "da": self.sal_da.text().strip() or 0,
            "hra": self.sal_hra.text().strip() or 0,
        }
        try:
            if self.current_mode == "new":
                hr_payroll.insert_salary(rec)
            elif self.current_mode == "edit":
                hr_payroll.update_salary(mth, emp, rec)
            self._sal_refresh()
            self._clear_form(self._sal_fields)
            self.current_mode = None
            self.current_row = -1
            self._set_form_enabled(self._sal_fields, False)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _sal_cancel(self):
        self.current_mode = None
        self.current_row = -1
        self._clear_form(self._sal_fields)
        self._set_form_enabled(self._sal_fields, False)

    # ── ATTENDANCE TAB ──────────────────────────────────────
    def _build_attendance_tab(self):
        tab = QWidget()
        v = QVBoxLayout(tab)

        self.att_table = QTableWidget(0, 5)
        self.att_table.setHorizontalHeaderLabels(
            ["Emp_Code", "Date", "InTime", "OutTime", "Status"]
        )
        self.att_table.setAlternatingRowColors(True)
        self.att_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.att_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.att_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.att_table.itemSelectionChanged.connect(self._att_select)
        v.addWidget(self.att_table)

        form = QFormLayout()
        self.att_emp = QLineEdit()
        self.att_emp.setMaxLength(10)
        self.att_emp.setPlaceholderText("e.g. EMP001")
        self.att_date = QLineEdit()
        self.att_date.setMaxLength(12)
        self.att_date.setPlaceholderText("YYYY-MM-DD")
        self.att_in = QLineEdit()
        self.att_in.setMaxLength(8)
        self.att_in.setPlaceholderText("HH:MM")
        self.att_out = QLineEdit()
        self.att_out.setMaxLength(8)
        self.att_out.setPlaceholderText("HH:MM")
        self.att_status = QLineEdit()
        self.att_status.setMaxLength(10)
        self.att_status.setPlaceholderText("e.g. Present")
        form.addRow("Emp_Code:", self.att_emp)
        form.addRow("Date:", self.att_date)
        form.addRow("InTime:", self.att_in)
        form.addRow("OutTime:", self.att_out)
        form.addRow("Status:", self.att_status)
        v.addLayout(form)

        self._att_fields = [self.att_emp, self.att_date, self.att_in,
                            self.att_out, self.att_status]

        btn_new = self._make_btn("New", self._att_new)
        btn_edit = self._make_btn("Edit", self._att_edit)
        btn_del = self._make_btn("Delete", self._att_delete)
        btn_save = self._make_btn("Save", self._att_save)
        btn_cancel = self._make_btn("Cancel", self._att_cancel)
        btn_refresh = self._make_btn("Refresh", self._att_refresh)
        v.addLayout(self._btn_row([btn_new, btn_edit, btn_del, btn_save, btn_cancel, btn_refresh]))

        self.tabs.addTab(tab, "Attendance")
        self._att_refresh()

    def _att_refresh(self):
        try:
            rows = hr_payroll.list_attendence()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        self.att_table.setRowCount(0)
        if not rows:
            return
        self.att_table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            attn = str(r.get("attn_str", "") if isinstance(r, dict)
                       else (r[2] if len(r) > 2 else "")) or "-"
            parts = attn.split("-")
            vals = [r.get("emp_code", "") if isinstance(r, dict) else r[1],
                    str(r.get("mth_year", "") if isinstance(r, dict) else r[0]),
                    parts[0] if len(parts) > 0 else "",
                    parts[1] if len(parts) > 1 else "",
                    parts[2] if len(parts) > 2 else ""]
            for j, val in enumerate(vals):
                self.att_table.setItem(i, j, self._dark_item(val))

    def _att_select(self):
        sel = self.att_table.selectionModel().selectedRows()
        if not sel:
            return
        row = sel[0].row()
        self.current_row = row
        self.att_emp.setText(self.att_table.item(row, 0).text())
        self.att_date.setText(self.att_table.item(row, 1).text())
        self.att_in.setText(self.att_table.item(row, 2).text())
        self.att_out.setText(self.att_table.item(row, 3).text())
        self.att_status.setText(self.att_table.item(row, 4).text())

    def _att_new(self):
        self.current_mode = "new"
        self._clear_form(self._att_fields)
        self._set_form_enabled(self._att_fields, True)
        self.att_emp.setFocus()

    def _att_edit(self):
        if self.current_row < 0:
            QMessageBox.information(self, "Info", "Select a row first.")
            return
        self.current_mode = "edit"
        self._set_form_enabled(self._att_fields, True)
        self.att_emp.setReadOnly(True)

    def _att_delete(self):
        if self.current_row < 0:
            QMessageBox.information(self, "Info", "Select a row first.")
            return
        emp = self.att_emp.text().strip()
        dt = self.att_date.text().strip()
        reply = QMessageBox.question(self, "Confirm", f"Delete attendance for {emp} on {dt}?")
        if reply == QMessageBox.StandardButton.Yes:
            try:
                hr_payroll.delete_attendence(emp, dt)
                self._att_refresh()
                self._clear_form(self._att_fields)
                self.current_row = -1
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _att_save(self):
        emp = self.att_emp.text().strip()
        dt = self.att_date.text().strip()
        if not emp or not dt:
            QMessageBox.warning(self, "Warning", "Emp_Code and Date required.")
            return
        rec = {
            "emp_code": emp,
            "intime": self.att_in.text().strip(),
            "outtime": self.att_out.text().strip(),
            "status": self.att_status.text().strip(),
        }
        try:
            if self.current_mode == "new":
                hr_payroll.insert_attendence(rec)
            elif self.current_mode == "edit":
                hr_payroll.update_attendence(emp, dt, rec)
            self._att_refresh()
            self._clear_form(self._att_fields)
            self.current_mode = None
            self.current_row = -1
            self._set_form_enabled(self._att_fields, False)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _att_cancel(self):
        self.current_mode = None
        self.current_row = -1
        self._clear_form(self._att_fields)
        self._set_form_enabled(self._att_fields, False)

    # ── LOAN TAB ────────────────────────────────────────────
    def _build_loan_tab(self):
        tab = QWidget()
        v = QVBoxLayout(tab)

        self.loan_table = QTableWidget(0, 5)
        self.loan_table.setHorizontalHeaderLabels(
            ["Emp_Code", "Sr_No", "LoanAmt", "Installment", "Balance"]
        )
        self.loan_table.setAlternatingRowColors(True)
        self.loan_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.loan_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.loan_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.loan_table.itemSelectionChanged.connect(self._loan_select)
        v.addWidget(self.loan_table)

        form = QFormLayout()
        self.loan_emp = QLineEdit()
        self.loan_emp.setMaxLength(10)
        self.loan_emp.setPlaceholderText("e.g. EMP001")
        self.loan_sr = QLineEdit()
        self.loan_sr.setMaxLength(5)
        self.loan_sr.setPlaceholderText("1")
        self.loan_amt = QLineEdit()
        self.loan_amt.setMaxLength(12)
        self.loan_amt.setPlaceholderText("e.g. 50000")
        self.loan_inst = QLineEdit()
        self.loan_inst.setMaxLength(12)
        self.loan_inst.setPlaceholderText("e.g. 2000")
        self.loan_bal = QLineEdit()
        self.loan_bal.setMaxLength(12)
        self.loan_bal.setPlaceholderText("e.g. 30000")
        form.addRow("Emp_Code:", self.loan_emp)
        form.addRow("Sr_No:", self.loan_sr)
        form.addRow("LoanAmt:", self.loan_amt)
        form.addRow("Installment:", self.loan_inst)
        form.addRow("Balance:", self.loan_bal)
        v.addLayout(form)

        self._loan_fields = [self.loan_emp, self.loan_sr, self.loan_amt,
                             self.loan_inst, self.loan_bal]

        btn_new = self._make_btn("New", self._loan_new)
        btn_edit = self._make_btn("Edit", self._loan_edit)
        btn_del = self._make_btn("Delete", self._loan_delete)
        btn_save = self._make_btn("Save", self._loan_save)
        btn_cancel = self._make_btn("Cancel", self._loan_cancel)
        btn_refresh = self._make_btn("Refresh", self._loan_refresh)
        v.addLayout(self._btn_row([btn_new, btn_edit, btn_del, btn_save, btn_cancel, btn_refresh]))

        self.tabs.addTab(tab, "Loan")
        self._loan_refresh()

    def _loan_refresh(self):
        try:
            rows = hr_payroll.list_loan()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        self.loan_table.setRowCount(0)
        if not rows:
            return
        self.loan_table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            vals = ([r.get("emp_code", ""), r.get("sr_no", ""),
                     r.get("amount", 0), r.get("installment", 0),
                     (r.get("amount", 0) or 0) - (r.get("installment", 0) or 0)]
                    if isinstance(r, dict) else list(r))
            for j, val in enumerate(vals):
                self.loan_table.setItem(i, j, self._dark_item(val))

    def _loan_select(self):
        sel = self.loan_table.selectionModel().selectedRows()
        if not sel:
            return
        row = sel[0].row()
        self.current_row = row
        self.loan_emp.setText(self.loan_table.item(row, 0).text())
        self.loan_sr.setText(self.loan_table.item(row, 1).text())
        self.loan_amt.setText(self.loan_table.item(row, 2).text())
        self.loan_inst.setText(self.loan_table.item(row, 3).text())
        self.loan_bal.setText(self.loan_table.item(row, 4).text())

    def _loan_new(self):
        self.current_mode = "new"
        self._clear_form(self._loan_fields)
        self._set_form_enabled(self._loan_fields, True)
        self.loan_emp.setFocus()

    def _loan_edit(self):
        if self.current_row < 0:
            QMessageBox.information(self, "Info", "Select a row first.")
            return
        self.current_mode = "edit"
        self._set_form_enabled(self._loan_fields, True)
        self.loan_emp.setReadOnly(True)

    def _loan_delete(self):
        if self.current_row < 0:
            QMessageBox.information(self, "Info", "Select a row first.")
            return
        emp = self.loan_emp.text().strip()
        sr = self.loan_sr.text().strip()
        reply = QMessageBox.question(self, "Confirm", f"Delete loan {sr} for {emp}?")
        if reply == QMessageBox.StandardButton.Yes:
            try:
                hr_payroll.delete_loan(emp, sr)
                self._loan_refresh()
                self._clear_form(self._loan_fields)
                self.current_row = -1
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _loan_save(self):
        emp = self.loan_emp.text().strip()
        sr = self.loan_sr.text().strip()
        if not emp or not sr:
            QMessageBox.warning(self, "Warning", "Emp_Code and Sr_No required.")
            return
        rec = {
            "emp_code": emp,
            "sr_no": sr,
            "amount": self.loan_amt.text().strip() or 0,
            "installment": self.loan_inst.text().strip() or 0,
        }
        try:
            if self.current_mode == "new":
                hr_payroll.insert_loan(rec)
            elif self.current_mode == "edit":
                hr_payroll.update_loan(emp, sr, rec)
            self._loan_refresh()
            self._clear_form(self._loan_fields)
            self.current_mode = None
            self.current_row = -1
            self._set_form_enabled(self._loan_fields, False)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _loan_cancel(self):
        self.current_mode = None
        self.current_row = -1
        self._clear_form(self._loan_fields)
        self._set_form_enabled(self._loan_fields, False)

    # ── OVERTIME TAB ────────────────────────────────────────
    def _build_overtime_tab(self):
        tab = QWidget()
        v = QVBoxLayout(tab)

        self.ot_table = QTableWidget(0, 5)
        self.ot_table.setHorizontalHeaderLabels(
            ["Emp_Code", "Date", "Hours", "Rate", "Amount"]
        )
        self.ot_table.setAlternatingRowColors(True)
        self.ot_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ot_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.ot_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.ot_table.itemSelectionChanged.connect(self._ot_select)
        v.addWidget(self.ot_table)

        form = QFormLayout()
        self.ot_emp = QLineEdit()
        self.ot_emp.setMaxLength(10)
        self.ot_emp.setPlaceholderText("e.g. EMP001")
        self.ot_date = QLineEdit()
        self.ot_date.setMaxLength(12)
        self.ot_date.setPlaceholderText("YYYY-MM-DD")
        self.ot_hours = QLineEdit()
        self.ot_hours.setMaxLength(6)
        self.ot_hours.setPlaceholderText("e.g. 4")
        self.ot_rate = QLineEdit()
        self.ot_rate.setMaxLength(10)
        self.ot_rate.setPlaceholderText("e.g. 150")
        self.ot_amt = QLineEdit()
        self.ot_amt.setMaxLength(12)
        self.ot_amt.setPlaceholderText("e.g. 600")
        form.addRow("Emp_Code:", self.ot_emp)
        form.addRow("Date:", self.ot_date)
        form.addRow("Hours:", self.ot_hours)
        form.addRow("Rate:", self.ot_rate)
        form.addRow("Amount:", self.ot_amt)
        v.addLayout(form)

        self._ot_fields = [self.ot_emp, self.ot_date, self.ot_hours,
                           self.ot_rate, self.ot_amt]

        btn_new = self._make_btn("New", self._ot_new)
        btn_edit = self._make_btn("Edit", self._ot_edit)
        btn_del = self._make_btn("Delete", self._ot_delete)
        btn_save = self._make_btn("Save", self._ot_save)
        btn_cancel = self._make_btn("Cancel", self._ot_cancel)
        btn_refresh = self._make_btn("Refresh", self._ot_refresh)
        v.addLayout(self._btn_row([btn_new, btn_edit, btn_del, btn_save, btn_cancel, btn_refresh]))

        self.tabs.addTab(tab, "Overtime")
        self._ot_refresh()

    def _ot_refresh(self):
        try:
            rows = hr_payroll.list_overtime()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        self.ot_table.setRowCount(0)
        if not rows:
            return
        self.ot_table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            vals = ([r.get("empcode", ""), str(r.get("otdate", "")),
                     r.get("otime", 0), r.get("otrate", 0), r.get("amount", 0)]
                    if isinstance(r, dict) else list(r))
            for j, val in enumerate(vals):
                self.ot_table.setItem(i, j, self._dark_item(val))

    def _ot_select(self):
        sel = self.ot_table.selectionModel().selectedRows()
        if not sel:
            return
        row = sel[0].row()
        self.current_row = row
        self.ot_emp.setText(self.ot_table.item(row, 0).text())
        self.ot_date.setText(self.ot_table.item(row, 1).text())
        self.ot_hours.setText(self.ot_table.item(row, 2).text())
        self.ot_rate.setText(self.ot_table.item(row, 3).text())
        self.ot_amt.setText(self.ot_table.item(row, 4).text())

    def _ot_new(self):
        self.current_mode = "new"
        self._clear_form(self._ot_fields)
        self._set_form_enabled(self._ot_fields, True)
        self.ot_emp.setFocus()

    def _ot_edit(self):
        if self.current_row < 0:
            QMessageBox.information(self, "Info", "Select a row first.")
            return
        self.current_mode = "edit"
        self._set_form_enabled(self._ot_fields, True)
        self.ot_emp.setReadOnly(True)

    def _ot_delete(self):
        if self.current_row < 0:
            QMessageBox.information(self, "Info", "Select a row first.")
            return
        emp = self.ot_emp.text().strip()
        dt = self.ot_date.text().strip()
        reply = QMessageBox.question(self, "Confirm", f"Delete overtime for {emp} on {dt}?")
        if reply == QMessageBox.StandardButton.Yes:
            try:
                hr_payroll.delete_overtime(emp, dt)
                self._ot_refresh()
                self._clear_form(self._ot_fields)
                self.current_row = -1
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _ot_save(self):
        emp = self.ot_emp.text().strip()
        dt = self.ot_date.text().strip()
        if not emp or not dt:
            QMessageBox.warning(self, "Warning", "Emp_Code and Date required.")
            return
        rec = {
            "empcode": emp,
            "otime": self.ot_hours.text().strip() or 0,
            "otrate": self.ot_rate.text().strip() or 0,
            "amount": self.ot_amt.text().strip() or 0,
        }
        try:
            if self.current_mode == "new":
                hr_payroll.insert_overtime(rec)
            elif self.current_mode == "edit":
                hr_payroll.update_overtime(emp, dt, rec)
            self._ot_refresh()
            self._clear_form(self._ot_fields)
            self.current_mode = None
            self.current_row = -1
            self._set_form_enabled(self._ot_fields, False)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _ot_cancel(self):
        self.current_mode = None
        self.current_row = -1
        self._clear_form(self._ot_fields)
        self._set_form_enabled(self._ot_fields, False)


def open_hr_payroll(parent=None):
    dlg = HrPayrollDialog(parent)
    dlg.exec()
    return dlg
