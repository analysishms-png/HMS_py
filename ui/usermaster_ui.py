"""User Master UI (VB6: Utility -> User Master / Permissions).

VB6 pattern: TopCtrl state-machine (Idle/Add/Edit).
Special: Password field (EchoMode.Password), Change Password button.
Safety: SA user delete nahi hota, sirf PYT* users delete allowed.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from PyQt6.QtWidgets import (QApplication, QDialog, QFormLayout, QHBoxLayout,
                             QLabel, QLineEdit, QMessageBox, QPushButton,
                             QTableWidget, QTableWidgetItem, QVBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from HMS_py.core import usermaster
from HMS_py.ui import theme as _theme


class UserMasterForm(QDialog):
    """VB6 UserMast form ka port - CRUD + password change."""

    def __init__(self, parent=None, current_user: str = "SA"):
        super().__init__(parent)
        self.current_user = current_user
        self.setWindowTitle("User Master - HMS_py")
        self.resize(700, 520)
        self.state = "Idle"
        self.edit_pk = None

        root = QVBoxLayout(self)

        # Grid
        self.tbl = QTableWidget(0, 5)
        self.tbl.setHorizontalHeaderLabels(
            ["Username", "Full Name", "Short Name", "Active", "Last Edit"])
        self.tbl.setAlternatingRowColors(True)
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        self.tbl.cellDoubleClicked.connect(lambda *_: self._on_edit())
        root.addWidget(self.tbl)

        # Form fields
        form = QFormLayout()
        self.edUser = QLineEdit()
        self.edUser.setMaxLength(usermaster.LIMITS["username"])
        self.edUser.setPlaceholderText("Max 10 chars, UPPERCASE stored")
        self.edLabel = QLineEdit()
        self.edLabel.setMaxLength(usermaster.LIMITS["label"])
        self.edLabel.setPlaceholderText("Full display name")
        self.edShort = QLineEdit()
        self.edShort.setMaxLength(usermaster.LIMITS["short"])
        self.edPass = QLineEdit()
        self.edPass.setEchoMode(QLineEdit.EchoMode.Password)
        self.edPass.setPlaceholderText(
            "New password (Edit: blank = keep current)")
        self.edActive = QLineEdit("Y")
        self.edActive.setMaxLength(1)
        self.edActive.setPlaceholderText("Y or N")
        form.addRow("Username *", self.edUser)
        form.addRow("Full Name (LABEL)", self.edLabel)
        form.addRow("Short Name", self.edShort)
        form.addRow("Password", self.edPass)
        form.addRow("Active (Y/N)", self.edActive)
        root.addLayout(form)

        # Buttons
        btns = QHBoxLayout()
        self.btnNew = QPushButton("&New")
        self.btnNew.setToolTip("Add new user (Ctrl+N)")
        self.btnEdit = QPushButton("&Edit")
        self.btnEdit.setToolTip("Edit selected user (Ctrl+E)")
        self.btnDelete = QPushButton("&Delete")
        self.btnDelete.setToolTip("Delete selected user (PYT* only)")
        self.btnSave = QPushButton("&Save")
        self.btnSave.setToolTip("Save changes (Ctrl+S)")
        self.btnCancel = QPushButton("&Cancel")
        self.btnCancel.setToolTip("Cancel current operation (Esc)")
        self.btnChgPwd = QPushButton("Change &Password")
        self.btnChgPwd.setToolTip("Change password for selected user")
        self.btnExit = QPushButton("E&xit")
        self.btnExit.setToolTip("Close this window")
        for b in (self.btnNew, self.btnEdit, self.btnDelete, self.btnSave,
                  self.btnCancel, self.btnChgPwd, self.btnExit):
            btns.addWidget(b)
        root.addLayout(btns)

        self.lblState = QLabel("State: Idle")
        root.addWidget(self.lblState)

        self.btnNew.clicked.connect(self._on_new)
        self.btnEdit.clicked.connect(self._on_edit)
        self.btnDelete.clicked.connect(self._on_delete)
        self.btnSave.clicked.connect(self._on_save)
        self.btnCancel.clicked.connect(self._on_cancel)
        self.btnChgPwd.clicked.connect(self._on_change_pwd)
        self.btnExit.clicked.connect(self.reject)

        from PyQt6.QtGui import QShortcut, QKeySequence
        QShortcut(QKeySequence("Ctrl+N"), self, activated=self._on_new)
        QShortcut(QKeySequence("Ctrl+E"), self, activated=self._on_edit)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._on_save)
        QShortcut(QKeySequence("Escape"), self, activated=self._on_cancel)
        QShortcut(QKeySequence("F5"), self, activated=self.reload)

        self._set_state(False)
        self.reload()

    # ---- state machine ----
    def _set_state(self, enabled: bool):
        for e in (self.edUser, self.edLabel, self.edShort,
                  self.edPass, self.edActive):
            e.setEnabled(enabled)
        for b in (self.btnNew, self.btnEdit, self.btnDelete, self.btnChgPwd):
            b.setEnabled(not enabled)
        for b in (self.btnSave, self.btnCancel):
            b.setEnabled(enabled)
        self.state = ("Add" if enabled and self.edit_pk is None
                      else ("Edit" if enabled else "Idle"))
        self.lblState.setText(f"State: {self.state}")

    def _clear(self):
        for e in (self.edUser, self.edLabel, self.edShort, self.edPass):
            e.clear()
        self.edActive.setText("Y")

    # ---- data ----
    def reload(self):
        rows = usermaster.list_all()
        self.tbl.setRowCount(len(rows))
        for r, rec in enumerate(rows):
            vals = [rec["username"], rec["label"], rec.get("short", ""),
                    rec["active"], rec.get("u_ae", "")]
            for c, v in enumerate(vals):
                it = QTableWidgetItem(str(v or ""))
                it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
                it.setForeground(QColor(_theme.palette()["text"]))
                self.tbl.setItem(r, c, it)
        if rows:
            self.tbl.selectRow(0)

    def _selected_user(self) -> str | None:
        r = self.tbl.currentRow()
        if r < 0:
            return None
        return self.tbl.item(r, 0).text()

    # ---- handlers ----
    def _on_new(self):
        self.edit_pk = None
        self._clear()
        self._set_state(True)
        self.edUser.setFocus()

    def _on_edit(self):
        uname = self._selected_user()
        if not uname:
            QMessageBox.information(self, "Edit", "Pehle row select karo")
            return
        rec = usermaster.get(uname)
        if not rec:
            return
        self.edit_pk = uname
        self.edUser.setText(rec["username"])
        self.edUser.setEnabled(False)   # PK change nahi hoti
        self.edLabel.setText(rec["label"])
        self.edShort.setText(rec["short"])
        self.edPass.clear()
        self.edPass.setPlaceholderText("Blank rakho = password nahi badlega")
        self.edActive.setText(rec["active"])
        self._set_state(True)
        self.state = "Edit"
        self.lblState.setText("State: Edit")
        self.edUser.setEnabled(False)

    def _on_save(self):
        uname = self.edUser.text().strip().upper()
        if not uname:
            QMessageBox.warning(self, "Save", "Username zaroori hai")
            return
        rec = {
            "username": uname,
            "label": self.edLabel.text().strip(),
            "short": self.edShort.text().strip(),
            "active": (self.edActive.text().strip().upper() or "Y"),
        }
        pwd = self.edPass.text()  # blank = keep (edit mode)
        try:
            if self.state == "Add":
                if usermaster.exists(uname):
                    QMessageBox.warning(self, "Save",
                                        f"User '{uname}' pehle se hai")
                    return
                usermaster.insert(rec, plain_password=pwd)
            else:
                # Edit: password sirf tab update jab user ne kuch type kiya
                usermaster.update(
                    self.edit_pk, rec,
                    plain_password=pwd if pwd else None)
        except ValueError as e:
            QMessageBox.warning(self, "Save", str(e))
            return
        except Exception as e:
            QMessageBox.critical(self, "Save", f"DB error: {e}")
            return
        self.edit_pk = None
        self._set_state(False)
        self.reload()

    def _on_cancel(self):
        self.edit_pk = None
        self._clear()
        self._set_state(False)

    def _on_delete(self):
        uname = self._selected_user()
        if not uname:
            QMessageBox.information(self, "Delete", "Pehle row select karo")
            return
        # SA aur current user delete nahi hote
        if uname.upper() in ("SA",):
            QMessageBox.warning(self, "Delete",
                                "SA user delete nahi ho sakta (system user)")
            return
        if uname.upper() == self.current_user.upper():
            QMessageBox.warning(self, "Delete",
                                "Aap khud ko delete nahi kar sakte")
            return
        # PYT* safety guard
        if not uname.upper().startswith("PYT"):
            QMessageBox.warning(
                self, "Delete",
                "Safety: sirf PYT* test-users delete ho sakte hain\n"
                "(production users protected)")
            return
        if QMessageBox.question(
                self, "Delete",
                f"User '{uname}' delete karein?") == \
                QMessageBox.StandardButton.Yes:
            try:
                usermaster.delete(uname)
            except Exception as e:
                QMessageBox.critical(self, "Delete", f"DB error: {e}")
                return
            self.reload()

    def _on_change_pwd(self):
        """VB6 password-change dialog (Idle mode - grid se user select)."""
        uname = self._selected_user()
        if not uname:
            QMessageBox.information(self, "Change Password",
                                    "Pehle grid mein user select karo")
            return
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Change Password - {uname}")
        dlg.setModal(True)
        form = QFormLayout()
        ed_new = QLineEdit()
        ed_new.setEchoMode(QLineEdit.EchoMode.Password)
        ed_new.setPlaceholderText("Naya password")
        ed_conf = QLineEdit()
        ed_conf.setEchoMode(QLineEdit.EchoMode.Password)
        ed_conf.setPlaceholderText("Confirm password")
        form.addRow("New Password", ed_new)
        form.addRow("Confirm", ed_conf)
        lay = QVBoxLayout(dlg)
        lay.addLayout(form)
        brow = QHBoxLayout()
        ok = QPushButton("Change")
        cancel = QPushButton("Cancel")
        brow.addStretch()
        brow.addWidget(ok)
        brow.addWidget(cancel)
        lay.addLayout(brow)
        ok.clicked.connect(dlg.accept)
        cancel.clicked.connect(dlg.reject)
        ok.setDefault(True)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        new_pwd = ed_new.text()
        if new_pwd != ed_conf.text():
            QMessageBox.warning(self, "Change Password",
                                "Passwords match nahi karte")
            return
        try:
            usermaster.set_password(uname, new_pwd)
        except Exception as e:
            QMessageBox.critical(self, "Change Password", f"DB error: {e}")
            return
        QMessageBox.information(self, "Change Password",
                                f"'{uname}' ka password change ho gaya")


def open_usermaster(parent=None, current_user: str = "SA"):
    UserMasterForm(parent, current_user=current_user).exec()


def main() -> int:
    app = QApplication(sys.argv)
    f = UserMasterForm()
    f.show()
    shot = os.environ.get("HMS_POC_SHOT")
    if shot:
        from PyQt6.QtTest import QTest
        QTest.qWait(600)
        f.grab().save(shot)
        print("screenshot:", shot)
        return 0
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
