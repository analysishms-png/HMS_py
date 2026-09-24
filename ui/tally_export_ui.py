"""Tally Export UI (VB6: TallyExportXML - generates XML from LEDGER for Tally import)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QDateEdit, QMessageBox, QFileDialog, QGroupBox,
    QFormLayout)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from core import db
import xml.etree.ElementTree as ET
from xml.dom import minidom


class TallyExportWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tally Export (XML)")
        self.resize(600, 350)
        self._build_ui()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        title = QLabel("Tally Export (XML)")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form = QGroupBox("Export Period")
        fl = QFormLayout(form)
        self.dt_from = QDateEdit(); self.dt_from.setCalendarPopup(True)
        self.dt_from.setDate(QDate(2026, 4, 1))
        self.dt_to = QDateEdit(); self.dt_to.setCalendarPopup(True)
        self.dt_to.setDate(QDate.currentDate())
        fl.addRow("From:", self.dt_from)
        fl.addRow("To:", self.dt_to)
        layout.addWidget(form)

        info = QLabel("LEDGER data ko Tally-compatible XML format me export karega.\n"
                      "File select karke Save karo.")
        info.setWordWrap(True); layout.addWidget(info)

        btn_lay = QHBoxLayout()
        self.btn_export = QPushButton("Export to XML")
        self.btn_export.setProperty("success", True)
        self.btn_export.setToolTip("Export LEDGER data to Tally-compatible XML")
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setToolTip("Close this window")
        self.btn_export.clicked.connect(self._export)
        self.btn_exit.clicked.connect(self.close)
        btn_lay.addWidget(self.btn_export); btn_lay.addWidget(self.btn_exit)
        layout.addLayout(btn_lay)

    def _export(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Tally XML", "", "XML Files (*.xml)")
        if not path: return
        try:
            rows = db.query(
                "SELECT L.DocId, L.V_Type, L.V_Date, L.SubCode, L.Chq_No, "
                "L.Narration, L.AmtDr, L.AmtCr, L.Clg_Date, "
                "ISNULL(S.Name,'') as SubName "
                "FROM LEDGER L LEFT JOIN SubGroup S ON L.SubCode = S.SubCode "
                "WHERE L.V_Date BETWEEN ? AND ? "
                "ORDER BY L.V_Date, L.DocId",
                (self.dt_from.date().toPyDate(), self.dt_to.date().toPyDate()))

            root = ET.Element("ENVELOPE")
            header = ET.SubElement(root, "HEADER")
            ET.SubElement(header, "TALLYREQUEST").text = "Import Data"
            body = ET.SubElement(root, "BODY")
            imp = ET.SubElement(body, "IMPORTDATA")
            req = ET.SubElement(imp, "REQUESTDESC")
            ET.SubElement(req, "REPORTNAME").text = "Vouchers"
            rlist = ET.SubElement(req, "STATICVARIABLES")
            ET.SubElement(rlist, "SVCURRENTCOMPANY").text = "HMS Hotel"
            data = ET.SubElement(imp, "REQUESTDATA")

            for r in rows:
                vch = ET.SubElement(data, "TALLYMESSAGE", attrib={"OBJECT": "Voucher"})
                ET.SubElement(vch, "VOUCHERTYPENAME").text = str(r["V_Type"] or "Journal")
                ET.SubElement(vch, "VOUCHERDATE").text = str(r["V_Date"] or "")
                ET.SubElement(vch, "REFERENCE").text = str(r["DocId"] or "")
                ET.SubElement(vch, "NARRATION").text = str(r["Narration"] or "")
                ledger = ET.SubElement(vch, "LEDGERENTRIES.LIST")
                ent = ET.SubElement(ledger, "LEDGERENTRIES")
                ET.SubElement(ent, "LEDGERNAME").text = str(r["SubName"] or "")
                dr = float(r["AmtDr"] or 0)
                cr = float(r["AmtCr"] or 0)
                if dr > 0:
                    ET.SubElement(ent, "DEBIT").text = f"{dr:.2f}"
                elif cr > 0:
                    ET.SubElement(ent, "CREDIT").text = f"{cr:.2f}"

            xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
            with open(path, "w", encoding="utf-8") as f:
                f.write(xml_str)
            QMessageBox.information(self, "Exported",
                f"{len(rows)} vouchers exported to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


def open_tally_export(parent=None):
    w = TallyExportWindow(parent); w.show(); return w
