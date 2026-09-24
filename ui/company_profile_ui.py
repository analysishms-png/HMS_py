"""Company Profile UI (VB6 salmarCompProfile port).

VB6 form: FGrid (FieldName | FieldValue), Picture1 (image preview for
PicturePath row), buttons &Report / &Save/Exit / &Cancel.
IniGrid fill-query aur CmdSave per-row UPDATE core/company_profile me
port kiye gaye hain (parity recipe step 2/3).
"""
from __future__ import annotations

import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (QDialog, QFileDialog, QHBoxLayout, QLabel,
                             QMessageBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QVBoxLayout)

from HMS_py.core.company_profile import profile_fields, save_profile


def open_company_profile(parent=None):
    dlg = QDialog(parent)
    dlg.setWindowTitle("Company Profile")
    dlg.resize(620, 520)
    dlg.setStyleSheet("""
        QDialog { background: #d4d0c8; }
        QLabel { color: #000080; font-family: 'Arial'; }
        QTableWidget {
            background: #ffffff; color: #000000;
            gridline-color: #808080; font-family: 'Arial'; font-size: 10pt;
        }
        QHeaderView::section {
            background: #d4d0c8; color: #000000;
            border: 1px solid #808080; font-weight: bold; padding: 3px;
        }
        QPushButton {
            background: #ffffc0; color: #000000;
            font-family: 'Arial'; font-size: 10pt; font-weight: bold;
            border: 2px outset; border-color: #ffffff #808080 #808080 #ffffff;
            padding: 4px 16px;
        }
        QPushButton:pressed { border-style: inset; }
    """)

    lay = QVBoxLayout(dlg)
    lay.setContentsMargins(12, 10, 12, 10)
    lay.setSpacing(8)

    title = QLabel("Company Profile")
    title.setStyleSheet("font-size: 13pt; font-weight: bold;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lay.addWidget(title)

    rows = profile_fields()
    tw = QTableWidget(len(rows) if rows else 1, 2)
    tw.setHorizontalHeaderLabels(["FieldName", "FieldValue"])
    tw.verticalHeader().setVisible(False)
    tw.setColumnWidth(0, 220)
    tw.horizontalHeader().setStretchLastSection(True)
    lay.addWidget(tw, stretch=1)

    pic_label = QLabel()
    pic_label.setVisible(False)
    lay.addWidget(pic_label)

    def _load_rows():
        for r, rec in enumerate(rows):
            tw.setItem(r, 0, QTableWidgetItem(rec["field"]))
            tw.setItem(r, 1, QTableWidgetItem(rec["value"]))

    if rows:
        _load_rows()
        # PicturePath row -> image preview (VB6 LoadPicture behaviour)
        for r, rec in enumerate(rows):
            if rec["field"].strip().lower() == "picturepath" and rec["value"]:
                pm = QPixmap(rec["value"])
                if not pm.isNull():
                    pic_label.setPixmap(
                        pm.scaled(200, 120,
                                  Qt.AspectRatioMode.KeepAspectRatio,
                                  Qt.TransformationMode.SmoothTransformation))
                    pic_label.setVisible(True)
                break

    def _browse():
        r = tw.currentRow()
        if r < 0 or not (tw.item(r, 0) and tw.item(r, 0).text().strip()
                         .lower() == "picturepath"):
            QMessageBox.information(
                dlg, "Company Profile", "PicturePath row select karo")
            return
        path, _ = QFileDialog.getOpenFileName(
            dlg, "Select Picture", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if path:
            tw.setItem(r, 1, QTableWidgetItem(path))

    def _save_exit():
        # VB6 CmdSave: har grid row ka UPDATE (core audit-columns ke saath)
        values = {}
        for r in range(tw.rowCount()):
            f_it, v_it = tw.item(r, 0), tw.item(r, 1)
            if f_it and f_it.text().strip():
                values[f_it.text().strip()] = v_it.text() if v_it else ""
        try:
            n = save_profile(values)
            QMessageBox.information(
                dlg, "Company Profile", f"Saved ({n} fields updated).")
            dlg.accept()
        except Exception as e:
            QMessageBox.critical(dlg, "Company Profile", f"Save fail: {e}")

    btns = QHBoxLayout()
    btn_rpt = QPushButton("&Report")
    btn_rpt.setToolTip("VB6: profile report print (preview stub)")
    btn_rpt.clicked.connect(
        lambda: QMessageBox.information(
            dlg, "Company Profile Report",
            "Profile fields report — print preview (VB6 DataReport "
            "ka read-only viewer port pending)."))
    btn_browse = QPushButton("Browse...")
    btn_browse.setToolTip("PicturePath ke liye image choose karo")
    btn_browse.clicked.connect(_browse)
    btn_save = QPushButton("&Save/Exit")
    btn_save.clicked.connect(_save_exit)
    btn_cancel = QPushButton("&Cancel")
    btn_cancel.clicked.connect(dlg.reject)
    btns.addWidget(btn_rpt)
    btns.addWidget(btn_browse)
    btns.addStretch()
    btns.addWidget(btn_save)
    btns.addWidget(btn_cancel)
    lay.addLayout(btns)

    if not rows:
        QMessageBox.information(
            dlg, "Company Profile",
            "No Company Profile Fields Are Defined! First Specify Them")
    dlg.exec()
