"""PlanMast master form - VB6 TopCtrl state-machine pattern par.

States (original app jaisa):
  Idle  : fields disabled, buttons [New] [Edit] [Delete] [Exit]
  Add   : fields enabled,  buttons [Save] [Cancel]
  Edit  : fields enabled,  buttons [Save] [Cancel]

Evidence: CompMast.frm Proc_22_78_F5F2C4(arg_C) -> Txt(i).Enabled = arg_C
DB writes: core/plans.py (audit U_Name/U_EntDt/U_AE VB6 pattern).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from PyQt6.QtWidgets import (QApplication, QDialog, QFormLayout, QHBoxLayout,
                             QInputDialog, QLabel, QLineEdit, QMessageBox,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QWidget)
from PyQt6.QtCore import Qt

from HMS_py.core import plans


class PlanMasterForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Plan Master (CompMast port) - HMS_py")
        self.resize(640, 460)
        self.state = "Idle"          # Idle | Add | Edit
        self.edit_code = None

        root = QVBoxLayout(self)

        # ---- grid (readonly list) ----
        self.tbl = QTableWidget(0, 4)
        self.tbl.setHorizontalHeaderLabels(["Code", "Name", "Total", "Active"])
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        self.tbl.cellDoubleClicked.connect(self._on_row_dbl)
        root.addWidget(self.tbl)

        # ---- fields ----
        form = QFormLayout()
        self.txtCode = QLineEdit()
        self.txtCode.setMaxLength(plans.LIMITS["code"])
        self.txtName = QLineEdit()
        self.txtName.setMaxLength(plans.LIMITS["name"])
        self.txtTotal = QLineEdit("0")
        self.txtPackage = QLineEdit()
        self.txtPackage.setMaxLength(plans.LIMITS["package"])
        form.addRow("Code", self.txtCode)
        form.addRow("Name", self.txtName)
        form.addRow("Total", self.txtTotal)
        form.addRow("Package", self.txtPackage)
        root.addLayout(form)

        # ---- TopCtrl-style buttons ----
        btns = QHBoxLayout()
        self.btnNew = QPushButton("New")
        self.btnEdit = QPushButton("Edit")
        self.btnDelete = QPushButton("Delete")
        self.btnSave = QPushButton("Save")
        self.btnCancel = QPushButton("Cancel")
        self.btnExit = QPushButton("Exit")
        for b in (self.btnNew, self.btnEdit, self.btnDelete, self.btnSave,
                  self.btnCancel, self.btnExit):
            btns.addWidget(b)
        root.addLayout(btns)

        self.lblState = QLabel("State: Idle")
        root.addWidget(self.lblState)

        self.btnNew.clicked.connect(self._on_new)
        self.btnEdit.clicked.connect(self._on_edit)
        self.btnDelete.clicked.connect(self._on_delete)
        self.btnSave.clicked.connect(self._on_save)
        self.btnCancel.clicked.connect(self._on_cancel)
        self.btnExit.clicked.connect(self.reject)

        self.set_state(False)   # original: form Idle me khulta hai
        self.reload()

    # ---------- state machine (TopCtrl pattern) ----------
    def set_state(self, enabled: bool):
        """Proc_22_78 pattern: sab fields enable/disable."""
        for w in (self.txtCode, self.txtName, self.txtTotal,
                  self.txtPackage):
            w.setEnabled(enabled)
        self.btnNew.setEnabled(not enabled)
        self.btnEdit.setEnabled(not enabled)
        self.btnDelete.setEnabled(not enabled)
        self.btnSave.setEnabled(enabled)
        self.btnCancel.setEnabled(enabled)
        self.state = "Add" if enabled and self.edit_code is None else (
            "Edit" if enabled else "Idle")
        self.lblState.setText(f"State: {self.state}")

    def _clear_fields(self):
        for w in (self.txtCode, self.txtName, self.txtTotal,
                  self.txtPackage):
            w.clear()
        self.txtTotal.setText("0")

    # ---------- data ----------
    def reload(self):
        rows = plans.list_plans()
        self.tbl.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate((row.Code, row.Name,
                                     f"{row.Total:.2f}", row.ActiveYN)):
                it = QTableWidgetItem(str(val))
                it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tbl.setItem(r, c, it)

    def _selected_code(self):
        r = self.tbl.currentRow()
        if r < 0:
            return None
        return self.tbl.item(r, 0).text()

    # ---------- handlers ----------
    def _on_new(self):
        self.edit_code = None
        self._clear_fields()
        self.set_state(True)
        self.txtCode.setFocus()

    def _on_edit(self):
        code = self._selected_code()
        if not code:
            QMessageBox.information(self, "Edit", "Pehle row select karo")
            return
        row = plans.get(code)
        if not row:
            return
        self.edit_code = code
        self.txtCode.setText(row.Code)
        self.txtCode.setEnabled(False)   # PK edit nahi hota
        self.txtName.setText(row.Name or "")
        self.txtTotal.setText(str(row.Total or 0))
        self.txtPackage.setText(row.Plan_Package or "")
        self.set_state(True)
        self.state = "Edit"
        self.lblState.setText("State: Edit")

    def _on_row_dbl(self, *_):
        self._on_edit()

    def _on_save(self):
        try:
            code = self.txtCode.text().strip()
            name = self.txtName.text().strip()
            if not code or not name:
                QMessageBox.warning(self, "Save",
                                    "Code aur Name zaroori hain")
                return
            total = float(self.txtTotal.text() or 0)
            pkg = self.txtPackage.text().strip()
            if self.state == "Add":
                if plans.exists(code):
                    QMessageBox.warning(self, "Save",
                                        f"Code {code} pehle se maujood hai")
                    return
                plans.insert(code, name, total, pkg)
            else:
                plans.update(self.edit_code, name, total, pkg)
        except ValueError as e:
            QMessageBox.warning(self, "Save", str(e))
            return
        except Exception as e:
            QMessageBox.critical(self, "Save", f"DB error: {e}")
            return
        self.set_state(False)
        self.reload()

    def _on_cancel(self):
        self.edit_code = None
        self._clear_fields()
        self.set_state(False)

    def _on_delete(self):
        code = self._selected_code()
        if not code:
            QMessageBox.information(self, "Delete", "Pehle row select karo")
            return
        # safety: test-code only delete (production data safe)
        if not code.upper().startswith("PYT"):
            QMessageBox.warning(self, "Delete",
                                "Safety: sirf PYT* test-records delete ho "
                                "sakte hain (production data protected)")
            return
        if QMessageBox.question(self, "Delete", f"{code} delete karein?") \
                == QMessageBox.StandardButton.Yes:
            plans.delete(code)
            self.reload()


def main() -> int:
    app = QApplication(sys.argv)
    f = PlanMasterForm()
    f.show()
    shot = os.environ.get("HMS_POC_SHOT")
    if shot:
        from PyQt6.QtTest import QTest
        QTest.qWait(800)
        f.grab().save(shot)
        print("screenshot:", shot)
        return 0
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
