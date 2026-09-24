"""Misc small VB6 ports: Date Picker (FrmCalender/repTouchDate),
Touch Screen Keyboard (RsTouchScreenKeyBoard), Customer Information
(RsTouchOrderPersonDetails), FA Find (RsTouchScreenFAFind),
Key Massage banner (frmmessageKey)."""
from __future__ import annotations

import datetime as _dt

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import (QCalendarWidget, QDialog, QGridLayout,
                             QHBoxLayout, QLabel, QLineEdit, QListWidget,
                             QMenu, QPushButton, QVBoxLayout, QWidget)

_VB6_DIALOG_QSS = """
    QDialog { background: #d4d0c8; }
    QLabel { color: #000000; background: transparent;
             font-family: 'Arial'; }
    QPushButton {
        background: #ffffc0; color: #000000;
        font-family: 'Arial'; font-size: 11pt; font-weight: bold;
        border: 2px outset; border-color: #ffffff #808080 #808080 #ffffff;
        min-width: 44px; min-height: 36px; padding: 2px;
    }
    QPushButton:pressed { border-style: inset; }
"""


def pick_date(parent=None, title: str = "Calender") -> _dt.date | None:
    """VB6 FrmCalender/repTouchDate port: modal date picker.

    Returns selected date, or None on cancel. 'Calender' spelling is
    the VB6 caption (kept verbatim by callers that show it).
    """
    dlg = QDialog(parent)
    dlg.setWindowTitle(title)
    dlg.setStyleSheet(_VB6_DIALOG_QSS)

    lay = QVBoxLayout(dlg)
    lay.setContentsMargins(10, 10, 10, 10)

    cal = QCalendarWidget(dlg)
    cal.setSelectedDate(QDate.currentDate())
    lay.addWidget(cal)

    btns = QHBoxLayout()
    btns.addStretch()
    btn_ok = QPushButton("Ok")
    btn_cancel = QPushButton("Cancel")
    btns.addWidget(btn_ok)
    btns.addWidget(btn_cancel)
    btns.addStretch()
    lay.addLayout(btns)

    btn_ok.clicked.connect(dlg.accept)
    btn_cancel.clicked.connect(dlg.reject)
    cal.activated.connect(dlg.accept)

    if dlg.exec() != QDialog.DialogCode.Accepted:
        return None
    qd = cal.selectedDate()
    return _dt.date(qd.year(), qd.month(), qd.day())


class TouchKeyboardDialog(QDialog):
    """VB6 RsTouchScreenKeyBoard port: on-screen QWERTY for touch POS.

    feed(target_lineedit) se kisi bhi QLineEdit pe type karwa sakte ho
    (VB6 me TxtKeyBoard buffer hota tha jo Txt_<index> me jaata tha).
    """

    def __init__(self, parent=None, title: str = "Touch Screen KeyBoard",
                 initial: str = ""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setStyleSheet(_VB6_DIALOG_QSS)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 10, 10, 10)

        self.display = QLineEdit(initial)
        self.display.setMinimumHeight(40)
        lay.addWidget(self.display)

        rows = [
            list("1234567890"),
            list("QWERTYUIOP"),
            list("ASDFGHJKL"),
            list("ZXCVBNM"),
        ]
        grid_lay = QGridLayout()
        grid_lay.setSpacing(4)
        for r, keys in enumerate(rows):
            c = 0
            for k in keys:
                b = QPushButton(k)
                b.clicked.connect(lambda _, ch=k: self._key(ch))
                grid_lay.addWidget(b, r, c)
                c += 1
        # space + backspace last row
        b_sp = QPushButton("Space")
        b_sp.setMinimumWidth(140)
        b_sp.clicked.connect(lambda: self._key(" "))
        grid_lay.addWidget(b_sp, 4, 0, 1, 4)
        b_bs = QPushButton("<- Back")
        b_bs.setMinimumWidth(90)
        b_bs.clicked.connect(self._backspace)
        grid_lay.addWidget(b_bs, 4, 4, 1, 3)
        b_cl = QPushButton("Clear")
        b_cl.setMinimumWidth(80)
        b_cl.clicked.connect(lambda: self.display.clear())
        grid_lay.addWidget(b_cl, 4, 7, 1, 3)
        lay.addLayout(grid_lay)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_ok = QPushButton("Enter")
        btn_ok.setMinimumWidth(90)
        btn_cancel = QPushButton("Cancel")
        btns.addWidget(btn_ok)
        btns.addWidget(btn_cancel)
        btns.addStretch()
        lay.addLayout(btns)
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

    def _key(self, ch: str):
        self.display.insert(ch)

    def _backspace(self):
        self.display.backspace()

    def text(self) -> str:
        return self.display.text()


def get_touch_text(parent=None, title: str = "Touch Screen KeyBoard",
                   initial: str = "") -> str | None:
    """Modal convenience: text ya None (cancel)."""
    kb = TouchKeyboardDialog(parent, title=title, initial=initial)
    if kb.exec() != QDialog.DialogCode.Accepted:
        return None
    return kb.text()


# ------------------------------------------------------ customer information
class CustomerInfoDialog(QDialog):
    """VB6 RsTouchOrderPersonDetails port: touch 'Customer Information'.

    Fields walk karta hai: Enter -> next field (VB6 global_80 index 0..3),
    Finish -> values collect (VB6 SALEBILLENTRY me ParentForm.sPhoneNo/
    sCustName/sAddress1/sAddress2 set hoti thi), Cancel -> abort.
    """

    FIELDS = [("Phone No", "sPhoneNo"), ("Customer Name", "sCustName"),
              ("Address 1", "sAddress1"), ("Address 2", "sAddress2")]

    def __init__(self, parent=None, title: str = "Customer Information",
                 initial: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setStyleSheet(_VB6_DIALOG_QSS)
        self.result_data: dict = {}
        self._idx = 0  # VB6 global_80: active field index

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)

        cap = QLabel("Customer Information")
        cap.setStyleSheet("font-size: 13pt; font-weight: bold; color: #0000c0;")
        cap.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(cap)

        self.edits: dict[str, QLineEdit] = {}
        initial = initial or {}
        for label, key in self.FIELDS:
            row = QHBoxLayout()
            lbl = QLabel(f"{label}:")
            lbl.setMinimumWidth(130)
            ed = QLineEdit(str(initial.get(key, "")))
            ed.setMinimumHeight(38)
            ed.setStyleSheet("font-size: 12pt;")
            row.addWidget(lbl)
            row.addWidget(ed)
            lay.addLayout(row)
            self.edits[key] = ed
        self._apply_focus()

        btns = QHBoxLayout()
        btn_prev = QPushButton("< Back")
        btn_enter = QPushButton("Enter")
        btn_finish = QPushButton("Finish")
        btn_cancel = QPushButton("Cancel")
        for b in (btn_prev, btn_enter, btn_finish, btn_cancel):
            b.setMinimumHeight(44)
            btns.addWidget(b)
        lay.addLayout(btns)

        btn_prev.clicked.connect(self._back)
        btn_enter.clicked.connect(self._enter)
        btn_finish.clicked.connect(self._finish)
        btn_cancel.clicked.connect(self.reject)

    def _apply_focus(self):
        key = self.FIELDS[self._idx][1]
        self.edits[key].setFocus()

    def _back(self):
        self._idx = max(0, self._idx - 1)
        self._apply_focus()

    def _enter(self):
        """VB6 Enter: current Txt_ index aage badhta hai (field walk)."""
        self._idx = (self._idx + 1) % len(self.FIELDS)
        self._apply_focus()

    def _finish(self):
        self.result_data = {k: e.text().strip()
                            for k, e in self.edits.items()}
        self.accept()


def get_customer_info(parent=None, initial: dict | None = None) -> dict | None:
    """Modal convenience: fields dict ya None (cancel)."""
    dlg = CustomerInfoDialog(parent, initial=initial)
    if dlg.exec() != QDialog.DialogCode.Accepted:
        return None
    return dlg.result_data


# ------------------------------------------------------------------ FA find
class FAFindDialog(QDialog):
    """VB6 RsTouchScreenFAFind port: touch find-list (Up/Down/Select/Exit)
    + right-click menu: Filter Same / Filter Not Same / Remove Filter /
    Sort Ascending / Sort Descending."""

    def __init__(self, parent=None, items: list | None = None,
                 title: str = "Find"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setStyleSheet(_VB6_DIALOG_QSS)
        self.selected: str | None = None
        self._base = [str(i) for i in (items or [])]

        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 10, 10, 10)

        self.listw = QListWidget(self)
        self.listw.setStyleSheet("font-size: 12pt;")
        self.listw.itemDoubleClicked.connect(lambda _i: self.accept())
        lay.addWidget(self.listw)

        btns = QHBoxLayout()
        for cap, fn in (("Up", self._up), ("Down", self._down),
                        ("Select", self._select), ("Exit", self.reject)):
            b = QPushButton(cap)
            b.setMinimumSize(110, 46)
            b.clicked.connect(fn)
            btns.addWidget(b)
        lay.addLayout(btns)

        self.listw.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu)
        self.listw.customContextMenuRequested.connect(self._menu)
        self._reload()

    def _reload(self, items: list | None = None):
        self.listw.clear()
        self.listw.addItems(items if items is not None else self._base)
        if self.listw.count():
            self.listw.setCurrentRow(0)

    def _up(self):
        r = max(0, self.listw.currentRow() - 1)
        self.listw.setCurrentRow(r)

    def _down(self):
        r = min(self.listw.count() - 1, self.listw.currentRow() + 1)
        self.listw.setCurrentRow(r)

    def _select(self):
        it = self.listw.currentItem()
        if it:
            self.selected = it.text()
            self.accept()

    def _menu(self, pos):
        menu = QMenu(self)
        cur = self.listw.currentItem().text() if self.listw.currentItem() else ""
        menu.addAction("Filter Same Records",
                       lambda: self._reload([x for x in self._base if x == cur]))
        menu.addAction("Filter Not Same Records",
                       lambda: self._reload([x for x in self._base if x != cur]))
        menu.addAction("Remove Filter", lambda: self._reload())
        menu.addSeparator()
        menu.addAction("Sort Ascending",
                       lambda: self._reload(sorted(self._base)))
        menu.addAction("Sort Descending",
                       lambda: self._reload(sorted(self._base, reverse=True)))
        menu.exec(self.listw.mapToGlobal(pos))


def find_item(parent=None, items: list | None = None,
              title: str = "Find") -> str | None:
    """Modal convenience: selected item ya None."""
    dlg = FAFindDialog(parent, items=items, title=title)
    if dlg.exec() != QDialog.DialogCode.Accepted:
        return None
    return dlg.selected


# ------------------------------------------------------------- key massage
def show_message_key(parent=None, message: str = ""):
    """VB6 frmmessageKey port: frameless 'Key Massage' banner + OK.

    VB6 me borderless form (BtnEnh1 full-surface + lblOK) hota tha jo
    license/key notice dikha kar OK pe unload hota tha.
    """
    dlg = QDialog(parent)
    dlg.setWindowTitle("Key Massage")
    dlg.setWindowFlags(Qt.WindowType.FramelessWindowHint |
                       Qt.WindowType.Dialog)
    dlg.setStyleSheet(_VB6_DIALOG_QSS)
    dlg.setFixedWidth(780)

    lay = QVBoxLayout(dlg)
    lay.setContentsMargins(14, 14, 14, 14)
    body = QLabel(message or "Key Massage")
    body.setWordWrap(True)
    body.setStyleSheet("font-size: 12pt; font-weight: bold;")
    lay.addWidget(body)

    btn_ok = QPushButton("OK")
    btn_ok.setMinimumHeight(44)
    btn_ok.clicked.connect(dlg.accept)
    lay.addWidget(btn_ok, alignment=Qt.AlignmentFlag.AlignRight)
    dlg.exec()
