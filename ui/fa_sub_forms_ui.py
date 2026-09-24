"""Finance Sub-Forms UI (VB6: FaAdjust, FaAdjustDel, FaChqClear, FaTDSCertificate port)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel,
    QComboBox, QMessageBox, QGroupBox, QFormLayout, QDateEdit, QTabWidget)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QFont
from core import fa_ledger_ops as falo
from core import fa_tds_ops as tds
from core import fa_voucher as fv
from ui.theme import palette


class FaAdjustWindow(QMainWindow):
    """Ledger Adjustment Entry (VB6: FaAdjust)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ledger Adjustment Entry")
        self.resize(800, 500)
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        title = QLabel("Ledger Adjustment (Bill-wise)")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form = QGroupBox("Adjustment Details")
        form_lay = QFormLayout(form)
        self.txt_docid1 = QLineEdit(); self.txt_docid1.setPlaceholderText("Debit DocId")
        self.txt_sno1 = QLineEdit(); self.txt_sno1.setPlaceholderText("Debit SNo")
        self.txt_docid2 = QLineEdit(); self.txt_docid2.setPlaceholderText("Credit DocId")
        self.txt_sno2 = QLineEdit(); self.txt_sno2.setPlaceholderText("Credit SNo")
        self.txt_amt = QLineEdit(); self.txt_amt.setPlaceholderText("Amount")
        self.txt_subcode = QLineEdit(); self.txt_subcode.setPlaceholderText("SubCode")
        self.txt_agref = QLineEdit(); self.txt_agref.setPlaceholderText("Adjustment Reference")
        form_lay.addRow("Debit DocId:", self.txt_docid1)
        form_lay.addRow("Debit SNo:", self.txt_sno1)
        form_lay.addRow("Credit DocId:", self.txt_docid2)
        form_lay.addRow("Credit SNo:", self.txt_sno2)
        form_lay.addRow("Amount:", self.txt_amt)
        form_lay.addRow("SubCode:", self.txt_subcode)
        form_lay.addRow("AgRefNo:", self.txt_agref)
        layout.addWidget(form)

        btn_lay = QHBoxLayout()
        self.btn_save = QPushButton("Save Adjustment")
        self.btn_save.setProperty("success", True)
        self.btn_save.setToolTip("Save the ledger adjustment entry")
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setToolTip("Close this window")
        self.btn_save.clicked.connect(self._save)
        self.btn_exit.clicked.connect(self.close)
        btn_lay.addWidget(self.btn_save); btn_lay.addWidget(self.btn_exit)
        layout.addLayout(btn_lay)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["DocId1", "SNo1", "DocId2", "SNo2", "Amount", "SubCode"])
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def _load_data(self):
        try:
            rows = falo.ledgeradj_list()
            self.table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                for j, v in enumerate([r["docid1"], str(r["v_sno1"]), r["docid2"],
                                       str(r["v_sno2"]), str(r["cr"]), r["subcode"]]):
                    it = QTableWidgetItem(str(v))
                    it.setForeground(QColor(palette()["text"]))
                    self.table.setItem(i, j, it)
        except Exception: pass

    def _save(self):
        try:
            falo.ledgeradj_insert({
                "docid1": self.txt_docid1.text().strip(),
                "v_sno1": int(self.txt_sno1.text() or 0),
                "docid2": self.txt_docid2.text().strip(),
                "v_sno2": int(self.txt_sno2.text() or 0),
                "cr": float(self.txt_amt.text() or 0),
                "subcode": self.txt_subcode.text().strip(),
                "agrefno": self.txt_agref.text().strip(),
            })
            QMessageBox.information(self, "Saved", "Adjustment saved!")
            self._load_data()
        except ValueError as e:
            QMessageBox.warning(self, "Adjustment", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class FaChqClearWindow(QMainWindow):
    """Cheque Clearing Entry (VB6: FaChqClear)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cheque Clearing")
        self.resize(700, 400)
        self._build_ui()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        title = QLabel("Cheque Clearing")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form = QGroupBox("Cheque Details")
        form_lay = QFormLayout(form)
        self.txt_docid = QLineEdit(); self.txt_docid.setPlaceholderText("Voucher DocId")
        self.txt_sno = QLineEdit(); self.txt_sno.setPlaceholderText("Line SNo")
        self.dt_clg = QDateEdit(); self.dt_clg.setCalendarPopup(True)
        self.dt_clg.setDate(QDate.currentDate())
        self.txt_chq = QLineEdit(); self.txt_chq.setPlaceholderText("Cheque Number")
        self.dt_chq = QDateEdit(); self.dt_chq.setCalendarPopup(True)
        self.dt_chq.setDate(QDate.currentDate())
        form_lay.addRow("DocId:", self.txt_docid)
        form_lay.addRow("SNo:", self.txt_sno)
        form_lay.addRow("Clearing Date:", self.dt_clg)
        form_lay.addRow("Cheque No:", self.txt_chq)
        form_lay.addRow("Cheque Date:", self.dt_chq)
        layout.addWidget(form)

        btn_lay = QHBoxLayout()
        self.btn_save = QPushButton("Mark Cleared")
        self.btn_save.setProperty("success", True)
        self.btn_save.setToolTip("Mark the cheque as cleared with the selected date")
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setToolTip("Close this window")
        self.btn_save.clicked.connect(self._save)
        self.btn_exit.clicked.connect(self.close)
        btn_lay.addWidget(self.btn_save); btn_lay.addWidget(self.btn_exit)
        layout.addLayout(btn_lay)

    def _save(self):
        docid = self.txt_docid.text().strip()
        sno = int(self.txt_sno.text() or 0)
        clg_date = self.dt_clg.date().toPyDate()
        if not docid:
            QMessageBox.warning(self, "Input", "DocId zaroori hai"); return
        try:
            chq = self.txt_chq.text().strip()
            fv.cheque_mark_cleared(
                docid, sno, clg_date,
                chq_no=chq if chq else None,
                chq_date=self.dt_chq.date().toPyDate())
            QMessageBox.information(self, "Saved", "Cheque marked as cleared!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class FaTDSCertificateWindow(QMainWindow):
    """TDS Certificate (VB6: FaTDSCertificate)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("TDS Certificate")
        self.resize(700, 400)
        self._build_ui()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        title = QLabel("TDS Certificate Generation")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form = QGroupBox("Certificate Details")
        form_lay = QFormLayout(form)
        self.txt_subcode = QLineEdit(); self.txt_subcode.setPlaceholderText("SubCode (Party)")
        self.txt_finyear = QLineEdit(); self.txt_finyear.setPlaceholderText("2025-26")
        self.dt_from = QDateEdit(); self.dt_from.setCalendarPopup(True)
        self.dt_from.setDate(QDate(2025, 4, 1))
        self.dt_to = QDateEdit(); self.dt_to.setCalendarPopup(True)
        self.dt_to.setDate(QDate(2026, 3, 31))
        form_lay.addRow("Party SubCode:", self.txt_subcode)
        form_lay.addRow("Financial Year:", self.txt_finyear)
        form_lay.addRow("From:", self.dt_from)
        form_lay.addRow("To:", self.dt_to)
        layout.addWidget(form)

        btn_lay = QHBoxLayout()
        self.btn_gen = QPushButton("Generate Certificate")
        self.btn_gen.setProperty("success", True)
        self.btn_gen.setToolTip("Generate TDS certificate for the selected party and period")
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setToolTip("Close this window")
        self.btn_gen.clicked.connect(self._generate)
        self.btn_exit.clicked.connect(self.close)
        btn_lay.addWidget(self.btn_gen); btn_lay.addWidget(self.btn_exit)
        layout.addLayout(btn_lay)

    def _generate(self):
        subcode = self.txt_subcode.text().strip()
        if not subcode:
            QMessageBox.warning(self, "Input", "SubCode zaroori hai"); return
        try:
            rows = tds.tds_detail(subcode)
            total_tds = sum(float(r.get("tds_amt", 0)) for r in rows)
            QMessageBox.information(self, "TDS Certificate",
                f"Party: {subcode}\nTotal TDS: {total_tds:,.2f}\n"
                f"Entries: {len(rows)}\n\n(Crystal Report se print karo)")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


def open_fa_adjust(parent=None):
    w = FaAdjustWindow(parent); w.show(); return w

def open_fa_chq_clear(parent=None):
    w = FaChqClearWindow(parent); w.show(); return w

def open_fa_tds_cert(parent=None):
    w = FaTDSCertificateWindow(parent); w.show(); return w
