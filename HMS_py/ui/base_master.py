"""Generic master form - TopCtrl state-machine (Idle/Add/Edit) + VB6 DGHelp/Find parity.

VB6 parity notes (FrmMarketSeg 958 / CompMast 7266 / FaGrEnt):
 - DGHelp 4245x3330 hidden, appears under Txt0 at Txt.Top+Height+30 (VB6 twips 0x1E)
   Tag=Code, Text=Name (or GroupName). On select Txt.Text=Name, Txt.Tag=Code then hide.
 - FrmList ListView popup for Nature enum (19 items) - VB6 FaGrEnt ListView.
 - TopCtrl dispatch A->ADD clear+Tag stash, B->Cancel MsgBox "Cancel ?" / "Terminate Process",
   C->Delete MsgBox "Delete Record ?" / "Confirmation" (0x24) + BeginTrans, F->Search
   "select * from X where LOGSITE_CODE IN ('HO',?) ORDER BY" via SearchCode dialog,
   16->SAVE duplicate SELECT COUNT(*) -> MsgBox "Duplicate Name" / "**Already Exist *"
   before INSERT.
 - Colors #c2e0ce mint, #d4d0c8 gray, radius 0 bevel, Arial 9.75 maroon labels.

No DB schema change - only UI helpers that call existing core.api.list_all() (LOGSITE
filtered) and preserve py_compile.

Naya master banane ke liye sirf ek MasterConfig dena hai:
    cfg = MasterConfig(title=..., fields=[Field(...)], api=<core module>,
                       delete_guard=lambda code: ...)
UI + validation + CRUD wiring automatic.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from dataclasses import dataclass, field as dc_field

from PyQt6.QtCore import Qt, QEvent, QPoint
from PyQt6.QtGui import QColor, QKeySequence, QShortcut
from PyQt6.QtWidgets import (QDialog, QFormLayout, QHBoxLayout, QLabel,
                             QLineEdit, QMessageBox, QPushButton,
                             QTableWidget, QTableWidgetItem, QVBoxLayout,
                             QAbstractItemView, QHeaderView, QGroupBox,
                             QWidget, QListWidget, QListWidgetItem,
                             QDialogButtonBox)

from HMS_py.ui import theme as _theme

# ---- VB6 parity constants -------------------------------------------------
VB6_MINT = "#c2e0ce"
VB6_GRAY = "#d4d0c8"
VB6_MAROON = "#800000"
VB6_NAVY = "#000080"
VB6_RED = "#c00000"
VB6_YELLOW = "#ffffc0"

VB6_NATURE_ITEMS = [
    "Bank", "Broker", "Cash", "Customer", "Electrician", "Employee",
    "Expenses", "Mukadim", "Others", "PDC", "Purchase", "Revenue",
    "Sale", "SalesMan", "SalesRep", "Supplier", "T.D.S.",
    "Transporter", "Unsecured Loan",
]


@dataclass
class Field:
    name: str            # dict key in core module records
    label: str
    max_len: int = 0
    required: bool = False
    default: str = ""
    placeholder: str = ""


@dataclass
class MasterConfig:
    title: str
    columns: list       # grid columns: (header, dict-key)
    fields: list        # editable Field list
    api: object         # core module: list_all/get/exists/insert/update/delete
    pk_key: str = "code"
    delete_guard: object = None   # fn(code) -> error-str | None
    sample_prefix: str = "PYT"


class _SearchViewer(QDialog):
    """VB6 TopCtrl_F (Find) search viewer - SearchCode HO pattern.

    Query verbatim VB6: SELECT * FROM <table> WHERE (LOGSITE_CODE='HO' OR LOGSITE_CODE=?)
    ORDER BY Name. Python reuses api.list_all() which already filters HO, so
    viewer shows SearchCode/Name list. Double-click or OK does SEARCHBACK
    (Me.Find "code=''" + audit refresh).
    """
    def __init__(self, cfg: MasterConfig, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.setWindowTitle(f"Find - {cfg.title}")
        self.resize(620, 420)
        self.selected_code: str | None = None
        p = _theme.palette()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)
        # header label like VB6 SearchCode widths "4000,1000"
        hdr_lbl = QLabel(f"SearchCode viewer  -  {cfg.title}")
        hdr_lbl.setStyleSheet("font-family:'Arial'; font-size:10pt; font-weight:700; color:#800000;")
        lay.addWidget(hdr_lbl)
        # filter bar
        filt = QHBoxLayout()
        filt.addWidget(QLabel("Search:"))
        self.edFilter = QLineEdit()
        self.edFilter.setPlaceholderText("Type to filter SearchCode / Name ...")
        self.edFilter.setMinimumHeight(28)
        self.edFilter.setStyleSheet(
            f"QLineEdit {{ padding: 4px 8px; border: 1px solid {p['border']}; border-radius: 0px; "
            f"background: #ffffff; font-family:'Arial'; font-size: 9.75pt; color:#000; }}"
        )
        filt.addWidget(self.edFilter, stretch=1)
        lay.addLayout(filt)
        # table
        cols = [c[0] for c in cfg.columns]
        self.tbl = QTableWidget(0, len(cols))
        self.tbl.setHorizontalHeaderLabels(cols)
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setShowGrid(True)
        self.tbl.setSortingEnabled(True)
        hdr = self.tbl.horizontalHeader()
        hdr.setStretchLastSection(True)
        for i in range(len(cols) - 1):
            hdr.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        # VB6 colors: white bg, gray header #d4d0c8 bevel radius 0
        self.tbl.setStyleSheet(
            "QTableWidget { background: #ffffff; gridline-color: #808080; border: 2px inset; "
            "border-color: #808080 #ffffff #ffffff #808080; border-radius: 0px; }"
            "QHeaderView::section { background: #d4d0c8; border: 1px outset; "
            "border-color: #ffffff #808080 #808080 #ffffff; padding: 3px; border-radius: 0px; "
            "font-family:'Arial'; font-size: 9.75pt; font-weight: 700; color: #000; }"
        )
        lay.addWidget(self.tbl, stretch=1)
        # buttons
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self._on_ok)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)
        self.tbl.cellDoubleClicked.connect(lambda *_: self._on_ok())
        self.edFilter.textChanged.connect(self._filter)
        self._load()

    def _load(self):
        try:
            rows = self.cfg.api.list_all()
        except Exception:
            rows = []
        self.tbl.setRowCount(len(rows))
        p = _theme.palette()
        for r, rec in enumerate(rows):
            for c, (_, key) in enumerate(self.cfg.columns):
                val = str(rec.get(key, "") or rec.get(key.lower(), "") or "")
                it = QTableWidgetItem(val)
                it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
                it.setForeground(QColor(p["text"]))
                # Arial 9.75 for VB6 parity
                f = it.font()
                f.setFamily("Arial")
                f.setPointSizeF(9.75)
                it.setFont(f)
                self.tbl.setItem(r, c, it)
        if self.tbl.rowCount():
            self.tbl.selectRow(0)

    def _filter(self, text: str):
        t = text.lower().strip()
        for r in range(self.tbl.rowCount()):
            match = not t
            for c in range(self.tbl.columnCount()):
                it = self.tbl.item(r, c)
                if it and t in it.text().lower():
                    match = True
                    break
            self.tbl.setRowHidden(r, not match)

    def _on_ok(self):
        r = self.tbl.currentRow()
        if r < 0 and self.tbl.rowCount() > 0:
            r = 0
        if r >= 0:
            col = next((i for i, (_, k) in enumerate(self.cfg.columns) if k == self.cfg.pk_key), 0)
            it = self.tbl.item(r, col)
            if it:
                self.selected_code = it.text().strip()
        if self.selected_code:
            self.accept()
        else:
            QMessageBox.information(self, "Find", "Please select a record")


class BaseMasterForm(QDialog):
    def __init__(self, cfg: MasterConfig, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.setWindowTitle(cfg.title)
        self.setMinimumSize(680, 520)
        self.resize(720, 540)
        self.state = "Idle"
        self.edit_pk = None
        self._rec_from_ui = None      # fn: ui -> record dict (set by subclass)
        self._rec_to_ui = None        # fn: record dict -> ui
        self._edit_orig_name: str | None = None  # VB6 global_64 clone
        self._current_edit: QLineEdit | None = None

        p = _theme.palette()
        # VB6 palette: gray #d4d0c8 dialog bg, mint #c2e0ce optional, bevel radius 0
        # Apply dialog bg per VB6 classic
        self.setStyleSheet(f"QDialog {{ background-color: {VB6_GRAY}; }}")
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(12)

        # --- Table section ---
        tbl_grp = QGroupBox(f"{cfg.title} List")
        tbl_grp.setStyleSheet(
            f"QGroupBox {{ background: #ffffff; border: 1px solid #808080; border-radius: 0px; "
            f"margin-top: 12px; padding: 10px; font-family:'Arial'; font-size:9.75pt; font-weight:700; color:#800000; }}"
            f"QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 4px 8px; color: {VB6_NAVY}; }}"
        )
        tbl_lay = QVBoxLayout(tbl_grp)

        # Search bar (live filter + Find button for TopCtrl_F)
        search_row = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search...")
        self._search.setMinimumHeight(32)
        self._search.setStyleSheet(
            f"QLineEdit {{ padding: 6px 10px; border: 1px solid {p['border']}; "
            f"border-radius: 0px; font-family:'Arial'; font-size: 9.75pt; color: #000000; "
            f"background: #ffffff; }}"
            f"QLineEdit:focus {{ border: 2px solid {VB6_NAVY}; }}"
        )
        self._search.textChanged.connect(self._filter_table)
        search_row.addWidget(self._search, stretch=1)
        # Find viewer button (TopCtrl_F parity) - SearchCode HO
        self.btnFind = QPushButton("  Find (F3)")
        self.btnFind.setMinimumHeight(32)
        self.btnFind.setToolTip("Find viewer - SearchCode HO (VB6 TopCtrl+F)")
        self.btnFind.setStyleSheet(
            "QPushButton { background: #ffffc0; border: 2px outset; border-color: #ffffff #808080 #808080 #ffffff; "
            "border-radius: 0px; padding: 4px 12px; font-family:'Arial'; font-weight:700; font-size:9.75pt; color:#000; }"
            "QPushButton:pressed { border-style: inset; }"
        )
        self.btnFind.clicked.connect(self._on_find)
        search_row.addWidget(self.btnFind)
        tbl_lay.addLayout(search_row)

        self.tbl = QTableWidget(0, len(cfg.columns))
        self.tbl.setHorizontalHeaderLabels([c[0] for c in cfg.columns])
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setShowGrid(True)
        self.tbl.setSortingEnabled(True)
        # VB6 table: white bg inset 2px, gray header #d4d0c8 bevel
        self.tbl.setStyleSheet(
            "QTableWidget { background: #ffffff; gridline-color: #808080; border: 2px inset; "
            "border-color: #808080 #ffffff #ffffff #808080; border-radius: 0px; font-family:'Arial'; font-size:9.75pt; }"
            "QHeaderView::section { background: #d4d0c8; border: 1px outset; "
            "border-color: #ffffff #808080 #808080 #ffffff; padding: 4px; border-radius: 0px; "
            "font-family:'Arial'; font-size:9.75pt; font-weight:700; color:#000; }"
        )
        hdr = self.tbl.horizontalHeader()
        hdr.setStretchLastSection(True)
        for i in range(len(cfg.columns) - 1):
            hdr.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl.cellDoubleClicked.connect(lambda *_: self._on_edit())
        self.tbl.itemSelectionChanged.connect(self._on_row_selected)
        tbl_lay.addWidget(self.tbl)
        root.addWidget(tbl_grp, stretch=1)

        # --- Form section ---
        form_grp = QGroupBox("Record Details")
        form_grp.setStyleSheet(
            f"QGroupBox {{ background: #ffffff; border: 1px solid #808080; border-radius: 0px; "
            f"margin-top: 12px; padding: 10px; font-family:'Arial'; font-size:9.75pt; font-weight:700; color:#800000; }}"
            f"QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 4px 8px; color: {VB6_NAVY}; }}"
        )
        form_lay = QFormLayout(form_grp)
        form_lay.setSpacing(10)
        form_lay.setContentsMargins(16, 12, 16, 12)
        self.edits = {}
        self._field_labels = {}
        for f in cfg.fields:
            e = QLineEdit()
            if f.max_len:
                e.setMaxLength(f.max_len)
            if f.placeholder:
                e.setPlaceholderText(f.placeholder)
            e.setMinimumHeight(32)
            e.setStyleSheet(
                f"QLineEdit {{ padding: 6px 10px; border: 1px solid {p['border']}; "
                f"border-radius: 0px; font-family:'Arial'; font-size: 9.75pt; color: #000000; "
                f"background: #ffffff; }}"
                f"QLineEdit:focus {{ border: 2px solid {VB6_NAVY}; }}"
                f"QLineEdit:disabled {{ background: #d4d0c8; color: #404040; }}"
            )
            # Required indicator
            label_text = f.label
            if f.required:
                label_text += ' <span style="color:#dc2626; font-weight:bold;">*</span>'
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-family:'Arial'; font-size: 9.75pt; font-weight: 700; color: #800000; background: transparent;")
            # store property to identify nature fields for ListView
            is_nature = "nature" in f.name.lower() or f.name.lower() == "gnature"
            e.setProperty("is_nature_field", is_nature)
            e.setProperty("vb_tag", "")
            self._field_labels[f.name] = lbl
            form_lay.addRow(lbl, e)
            self.edits[f.name] = e
        root.addWidget(form_grp)

        # --- Tab order ---
        prev_widget = None
        for f in cfg.fields:
            w = self.edits[f.name]
            if prev_widget is not None:
                QWidget.setTabOrder(prev_widget, w)
            prev_widget = w

        # --- Button bar (TopCtrl AEDP at bottom for dialog, but order matches VB6) ---
        btn_grp = QGroupBox()
        btn_grp.setStyleSheet("QGroupBox { border: none; background: transparent; margin: 0; padding: 0; }")
        btn_lay = QHBoxLayout(btn_grp)
        btn_lay.setContentsMargins(0, 4, 0, 4)
        btn_lay.setSpacing(8)

        self.btnNew = QPushButton("  New (Ctrl+N)")
        self.btnNew.setProperty("accent", True)
        self.btnNew.setMinimumHeight(34)
        self.btnNew.setToolTip("Create a new record (Ctrl+N) - TopCtrl A=ADD")

        self.btnEdit = QPushButton("  Edit (Ctrl+E)")
        self.btnEdit.setMinimumHeight(34)
        self.btnEdit.setToolTip("Edit selected record (Ctrl+E) - TopCtrl D=EDIT")

        self.btnDelete = QPushButton("  Delete (Ctrl+D)")
        self.btnDelete.setProperty("role", "danger")
        self.btnDelete.setMinimumHeight(34)
        self.btnDelete.setToolTip("Delete selected record (Ctrl+D) - TopCtrl C=DELETE")

        self.btnSave = QPushButton("  Save (Ctrl+S)")
        self.btnSave.setProperty("accent", True)
        self.btnSave.setMinimumHeight(34)
        self.btnSave.setToolTip("Save changes (Ctrl+S) - TopCtrl 16=SAVE")

        self.btnCancel = QPushButton("  Cancel (Esc)")
        self.btnCancel.setMinimumHeight(34)
        self.btnCancel.setToolTip("Cancel current operation (Esc) - TopCtrl B=CANCEL")

        self.btnExit = QPushButton("  Exit")
        self.btnExit.setMinimumHeight(34)
        self.btnExit.setToolTip("Close this form")

        for b in (self.btnNew, self.btnEdit, self.btnDelete, self.btnSave,
                  self.btnCancel, self.btnExit):
            b.setStyleSheet(
                "QPushButton { background: #ffffc0; border: 2px outset; border-color: #ffffff #808080 #808080 #ffffff; "
                "border-radius: 0px; padding: 4px 12px; font-family:'Arial'; font-weight:700; font-size:9.75pt; color:#000; }"
                "QPushButton:pressed { border-style: inset; }"
                "QPushButton:disabled { background: #d4d0c8; color: #808080; }"
                "QPushButton[accent=\"true\"] { background: #000080; color: #ffffff; border: 2px outset; border-color: #8080ff #000040 #000040 #8080ff; }"
                "QPushButton[role=\"danger\"] { background: #c00000; color: #ffffff; }"
            )
            btn_lay.addWidget(b)
        btn_lay.addStretch()
        root.addWidget(btn_grp)

        # --- Status / audit bar ---
        audit_row = QHBoxLayout()
        self.lblState = QLabel("Ready")
        self.lblState.setStyleSheet(
            f"font-family:'Arial'; font-size: 9.75pt; font-weight:700; color: {p['text_dim']}; padding: 4px 0; "
            f"border-top: 1px solid {p['border']};"
        )
        audit_row.addWidget(self.lblState, stretch=1)
        self.lblUser = QLabel("")
        self.lblUser.setStyleSheet("font-family:'Times New Roman'; font-size: 9pt; font-weight:700; color: #ff0000;")
        self.lblLDt = QLabel("")
        self.lblLDt.setStyleSheet("font-family:'Times New Roman'; font-size: 9pt; font-weight:700; color: #ff0000;")
        audit_row.addWidget(self.lblUser)
        audit_row.addWidget(self.lblLDt)
        root.addLayout(audit_row)

        # --- Signals ---
        self.btnNew.clicked.connect(self._on_new)
        self.btnEdit.clicked.connect(self._on_edit)
        self.btnDelete.clicked.connect(self._on_delete)
        self.btnSave.clicked.connect(self._on_save)
        self.btnCancel.clicked.connect(self._on_cancel)
        self.btnExit.clicked.connect(self.reject)
        self.btnFind.clicked.connect(self._on_find)

        # Keyboard shortcuts - VB6 KeyPreview style
        QShortcut(QKeySequence("Ctrl+N"), self, activated=self._on_new)
        QShortcut(QKeySequence("Ctrl+E"), self, activated=self._on_edit)
        QShortcut(QKeySequence("Ctrl+D"), self, activated=self._on_delete)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._on_save)
        QShortcut(QKeySequence("Escape"), self, activated=self._on_cancel)
        QShortcut(QKeySequence("F5"), self, activated=lambda: self.reload())
        QShortcut(QKeySequence("F3"), self, activated=self._on_find)

        # --- DGHelp popup (VB6 DGHelp 4245x3330 hidden under Txt.Top+Height+30) ---
        self._dgHelp = QListWidget(self)
        self._dgHelp.setWindowFlags(Qt.WindowType.Popup)
        self._dgHelp.hide()
        self._dgHelp.setMaximumHeight(220)
        self._dgHelp.setMinimumWidth(280)
        self._dgHelp.setStyleSheet(
            "QListWidget { background: #ffffff; border: 1px solid #808080; border-radius: 0px; "
            "font-family:'Arial'; font-size: 9.75pt; color: #000; }"
            "QListWidget::item { padding: 4px 6px; }"
            "QListWidget::item:selected { background: #000080; color: #ffffff; }"
        )
        self._dgHelp.itemClicked.connect(self._on_dghelp_pick)
        self._dgHelp.itemActivated.connect(self._on_dghelp_pick)

        # --- ListView for Nature enum (FrmList 2325x2370) ---
        self._lvNature = QListWidget(self)
        self._lvNature.setWindowFlags(Qt.WindowType.Popup)
        self._lvNature.hide()
        self._lvNature.setMaximumHeight(200)
        self._lvNature.setMinimumWidth(220)
        self._lvNature.setStyleSheet(
            "QListWidget { background: #ffffff; border: 1px solid #808080; border-radius: 0px; "
            "font-family:'Arial'; font-size: 9.75pt; color: #000; }"
            "QListWidget::item { padding: 4px 6px; }"
            "QListWidget::item:selected { background: #000080; color: #ffffff; }"
        )
        for it in VB6_NATURE_ITEMS:
            self._lvNature.addItem(QListWidgetItem(it))
        self._lvNature.itemClicked.connect(self._on_nature_pick)
        self._lvNature.itemActivated.connect(self._on_nature_pick)

        # Install event filter for GotFocus + Esc handling on every edit
        for ed in self.edits.values():
            ed.installEventFilter(self)
            ed.textEdited.connect(self._on_edit_text_edited)

        self.set_state(False)
        self.reload()

    # ---------- event filter for DGHelp GotFocus ----------
    def eventFilter(self, obj, event):
        if obj in self.edits.values():
            if event.type() == QEvent.Type.FocusIn:
                self._current_edit = obj
                is_nature = bool(obj.property("is_nature_field"))
                if is_nature:
                    self._show_nature_popup(obj)
                else:
                    self._show_dghelp_popup(obj)
            elif event.type() == QEvent.Type.KeyPress:
                # VB6 Esc hides DGHelp/FGPoint
                if event.key() == Qt.Key.Key_Escape:
                    self._hide_popups()
                    return True
                # Down arrow with visible popup -> focus popup
                if event.key() in (Qt.Key.Key_Down, Qt.Key.Key_Up, Qt.Key.Key_PageDown, Qt.Key.Key_PageUp):
                    if self._dgHelp.isVisible():
                        self._dgHelp.setFocus()
                        return True
                    if self._lvNature.isVisible():
                        self._lvNature.setFocus()
                        return True
        return super().eventFilter(obj, event)

    def _on_edit_text_edited(self, text: str):
        # Live filter DGHelp like VB6 Txt_KeyUp filtering on Name field
        if self._dgHelp.isVisible() and self._current_edit is not None:
            self._dgHelp_reload(text)

    def _hide_popups(self):
        self._dgHelp.hide()
        self._lvNature.hide()

    # ---------- DGHelp helpers ----------
    def _dgHelp_reload(self, pattern: str = ""):
        """Reload DGHelp from api.list_all() filtered by pattern (VB6 LOGSITE filter via api)."""
        try:
            rows = self.cfg.api.list_all()
        except Exception:
            rows = []
        self._dgHelp.clear()
        pat = (pattern or "").strip().lower()
        for r in rows[:60]:
            # r keys lower-case: code/name per MasterConfig; fallback case-insensitive
            code = str(r.get("code") or r.get("Code") or r.get("CityCode") or r.get("GroupCode") or "").strip()
            name = str(r.get("name") or r.get("Name") or r.get("CityName") or r.get("GroupName") or "").strip()
            if not name and not code:
                continue
            if pat and pat not in name.lower() and pat not in code.lower():
                continue
            display = f"{code}  |  {name}" if code and name and code != name else (name or code)
            it = QListWidgetItem(display)
            it.setData(Qt.ItemDataRole.UserRole, code)
            it.setData(Qt.ItemDataRole.UserRole + 1, name)
            # Arial 9.75
            f = it.font()
            f.setFamily("Arial")
            f.setPointSizeF(9.75)
            it.setFont(f)
            self._dgHelp.addItem(it)

    def _show_dghelp_popup(self, edit: QLineEdit):
        # Only show when control has records (VB6: If RecordCount>0)
        try:
            cnt = len(self.cfg.api.list_all())
        except Exception:
            cnt = 0
        if cnt <= 0:
            return
        self._dgHelp_reload(edit.text())
        if self._dgHelp.count() == 0:
            self._dgHelp.hide()
            return
        # Position: VB6 DGHelp.Left = Txt.Left, Top = Txt.Top+Height+0x1E (~30 twips = 2px)
        pt = edit.mapToGlobal(QPoint(0, edit.height()))
        pt.setY(pt.y() + 2)
        self._dgHelp.move(pt)
        self._dgHelp.setFixedWidth(max(edit.width(), 280))
        self._dgHelp.show()
        self._dgHelp.raise_()

    def _on_dghelp_pick(self, item: QListWidgetItem):
        if self._current_edit is None:
            return
        code = item.data(Qt.ItemDataRole.UserRole) or ""
        name = item.data(Qt.ItemDataRole.UserRole + 1) or item.text()
        # VB6 DGHelp commit: Txt.Text = Fields("Name").Value, Tag = Code, SetFocus
        self._current_edit.setText(str(name).strip())
        self._current_edit.setProperty("vb_tag", str(code).strip())
        self._dgHelp.hide()
        self._current_edit.setFocus()

    # ---------- Nature ListView ----------
    def _show_nature_popup(self, edit: QLineEdit):
        pt = edit.mapToGlobal(QPoint(0, edit.height()))
        pt.setY(pt.y() + 2)
        self._lvNature.move(pt)
        self._lvNature.setFixedWidth(max(edit.width(), 220))
        # pre-select current value if matches
        cur = edit.text().strip()
        if cur:
            for i in range(self._lvNature.count()):
                if self._lvNature.item(i).text().lower() == cur.lower():
                    self._lvNature.setCurrentRow(i)
                    break
        self._lvNature.show()
        self._lvNature.raise_()

    def _on_nature_pick(self, item: QListWidgetItem):
        if self._current_edit is None:
            return
        self._current_edit.setText(item.text())
        self._current_edit.setProperty("vb_tag", item.text())
        self._lvNature.hide()
        self._current_edit.setFocus()

    # ---------- Find viewer ----------
    def _on_find(self):
        # VB6: If RecordCount<=0 Then MsgBox "Records Not Present For Searching." / "No Records To Search."
        try:
            cnt = len(self.cfg.api.list_all())
        except Exception:
            cnt = 0
        if cnt <= 0:
            QMessageBox.information(self, "Information", "Records Not Present For Searching.")
            return
        dlg = _SearchViewer(self.cfg, self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.selected_code:
            self._searchback(dlg.selected_code)

    def _searchback(self, code: str):
        """VB6 SEARCHBACK(MyValue): Me.Find "code=''" + audit refresh Proc_14_29."""
        # Find row in main table (SearchCode = code)
        pk_col = next((i for i, (_, k) in enumerate(self.cfg.columns) if k == self.cfg.pk_key), 0)
        target_row = -1
        for r in range(self.tbl.rowCount()):
            it = self.tbl.item(r, pk_col)
            if it and it.text().strip().lower() == code.strip().lower():
                target_row = r
                break
        if target_row >= 0:
            self.tbl.selectRow(target_row)
            self.tbl.scrollToItem(self.tbl.item(target_row, pk_col))
        # Also populate form like VB6 Find+SEARCHBACK does (audit labels)
        try:
            rec = self.cfg.api.get(code)
            if rec:
                self.record_to_ui(rec)
                self._show_audit(code, rec)
        except Exception:
            pass

    def _on_row_selected(self):
        pk = self._selected_pk()
        if pk:
            try:
                rec = self.cfg.api.get(pk)
                if rec:
                    self._show_audit(pk, rec)
            except Exception:
                pass

    def _show_audit(self, pk: str, rec: dict | None = None):
        # VB6 Proc_14_29: Select U_Name,U_AE,U_EntDt From MarketSeg where Code='' then
        # IIf U_AE=A "Created By : " else "Modified By : " + U_Name, Last Update: U_EntDt
        try:
            if rec is None:
                rec = self.cfg.api.get(pk)
            if not rec:
                self.lblUser.setText("")
                self.lblLDt.setText("")
                return
            u_name = str(rec.get("u_name") or rec.get("U_Name") or "").strip()
            u_ae = str(rec.get("u_ae") or rec.get("U_AE") or "A").strip().upper()
            u_dt = str(rec.get("u_entdt") or rec.get("U_EntDt") or rec.get("u_ent_dt") or "").strip()
            prefix = "Created By : " if u_ae == "A" else ("Modified By : " if u_ae == "E" else "User : ")
            label = "Last Update : " if u_ae == "E" else "Created : "
            self.lblUser.setText(f"{prefix}{u_name}" if u_name else "")
            self.lblLDt.setText(f"{label}{u_dt}" if u_dt else "")
        except Exception:
            pass

    def _filter_table(self, text: str):
        """Filter table rows by search text."""
        text = text.lower()
        for r in range(self.tbl.rowCount()):
            match = False
            for c in range(self.tbl.columnCount()):
                item = self.tbl.item(r, c)
                if item and text in item.text().lower():
                    match = True
                    break
            self.tbl.setRowHidden(r, not match)

    # ---------- helpers to override ----------
    def record_from_ui(self) -> dict:
        if self._rec_from_ui:
            return self._rec_from_ui()
        rec = {}
        for f in self.cfg.fields:
            rec[f.name] = self.edits[f.name].text().strip()
            # preserve vb_tag as code tag if field is code-bearing
            tag = self.edits[f.name].property("vb_tag")
            if tag and f.name == self.cfg.pk_key:
                rec[f.name] = str(tag).strip() or rec[f.name]
        return rec

    def record_to_ui(self, rec: dict):
        if self._rec_to_ui:
            self._rec_to_ui(rec)
            return
        for f in self.cfg.fields:
            txt = str(rec.get(f.name, "") or "")
            self.edits[f.name].setText(txt)
            # stash Tag like VB6 Txt.Tag = Code
            if f.name == self.cfg.pk_key:
                self.edits[f.name].setProperty("vb_tag", txt)
            else:
                # for name fields also keep tag of code when available
                code_val = str(rec.get(self.cfg.pk_key, "") or "")
                if code_val:
                    self.edits[f.name].setProperty("vb_tag", code_val)

    def grid_row_values(self, rec: dict) -> tuple:
        return tuple(str(rec.get(k, "") or rec.get(k.lower(), "") or "") for _, k in self.cfg.columns)

    # ---------- state machine (TopCtrl pattern) ----------
    def set_state(self, enabled: bool):
        p = _theme.palette()
        for e in self.edits.values():
            e.setEnabled(enabled)
        for b in (self.btnNew, self.btnEdit, self.btnDelete, self.btnFind):
            b.setEnabled(not enabled)
        for b in (self.btnSave, self.btnCancel):
            b.setEnabled(enabled)
        self.state = ("Add" if self.edit_pk is None else "Edit") if enabled \
            else "Idle"
        state_colors = {
            "Idle": p.get("text_dim", "#64748b"),
            "Add": p.get("success", "#059669"),
            "Edit": p.get("warning", "#d97706"),
        }
        color = state_colors.get(self.state, p["text_dim"])
        self.lblState.setText(f"  State: {self.state}")
        self.lblState.setStyleSheet(
            f"font-family:'Arial'; font-size: 9.75pt; color: {color}; padding: 4px 0; "
            f"border-top: 1px solid {p['border']}; font-weight: 700;"
        )
        if not enabled:
            self._hide_popups()

    def _clear_fields(self):
        for f in self.cfg.fields:
            self.edits[f.name].setText(f.default)
            self.edits[f.name].setProperty("vb_tag", "")

    # ---------- data ----------
    def reload(self):
        rows = self.cfg.api.list_all()
        self.tbl.setRowCount(len(rows))
        p = _theme.palette()
        for r, rec in enumerate(rows):
            for c, val in enumerate(self.grid_row_values(rec)):
                it = QTableWidgetItem(val)
                it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
                it.setForeground(QColor(p["text"]))
                fnt = it.font()
                fnt.setFamily("Arial")
                fnt.setPointSizeF(9.75)
                it.setFont(fnt)
                self.tbl.setItem(r, c, it)
        self._hide_popups()

    def _selected_pk(self):
        r = self.tbl.currentRow()
        if r < 0:
            return None
        col = next((i for i, (_, k) in enumerate(self.cfg.columns)
                    if k == self.cfg.pk_key), 0)
        item = self.tbl.item(r, col)
        return item.text() if item else None

    # ---------- handlers ----------
    def _on_new(self):
        self.edit_pk = None
        self._edit_orig_name = None
        self._clear_fields()
        self.lblUser.setText("")
        self.lblLDt.setText("")
        self.set_state(True)
        # VB6 Focus + DGHelp reload already via eventFilter
        next(iter(self.edits.values())).setFocus()

    def _on_edit(self):
        pk = self._selected_pk()
        if not pk:
            QMessageBox.information(self, "Edit",
                                    "Please select a record to edit")
            return
        rec = self.cfg.api.get(pk)
        if not rec:
            return
        self.edit_pk = pk
        self.record_to_ui(rec)
        # stash global_64 like VB6: original Name for duplicate check
        try:
            self._edit_orig_name = str(rec.get("name") or rec.get("Name") or "").strip()
        except Exception:
            self._edit_orig_name = None
        pk_edit = self.edits.get(self.cfg.pk_key)
        if pk_edit:
            pk_edit.setEnabled(False)
        self.set_state(True)
        self.state = "Edit"
        self.lblState.setText("  State: Edit")
        p = _theme.palette()
        self.lblState.setStyleSheet(
            f"font-family:'Arial'; font-size: 9.75pt; color: {p.get('warning', '#d97706')}; padding: 4px 0; "
            f"border-top: 1px solid {p['border']}; font-weight: 700;"
        )
        if pk_edit:
            pk_edit.setEnabled(False)
        self._show_audit(pk, rec)

    def _on_save(self):
        try:
            rec = self.record_from_ui()
            pk = rec.get(self.cfg.pk_key, "").strip()
            if not pk:
                QMessageBox.warning(self, "Validation",
                                    f"{self.cfg.pk_key.upper()} is required")
                return
            # Validate required fields
            for f in self.cfg.fields:
                if f.required and not rec.get(f.name, "").strip():
                    QMessageBox.warning(self, "Validation",
                                        f"{f.label} is required")
                    self.edits[f.name].setFocus()
                    return
            # Duplicate guard verbatim - VB6 SELECT COUNT(*) ... LOGSITE filter via list_all scan
            # Code duplicate (exists) -> "**Already Exist *"  /  Name duplicate -> "Duplicate Name"
            name_val = str(rec.get("name") or rec.get("Name") or "").strip()
            if self.state == "Add":
                if self.cfg.api.exists(pk):
                    QMessageBox.warning(self, "Information",
                                        f"{pk} **Already Exist *")
                    return
                if name_val:
                    try:
                        rows = self.cfg.api.list_all()
                        for r in rows:
                            rn = str(r.get("name") or r.get("Name") or "").strip()
                            if rn.lower() == name_val.lower():
                                QMessageBox.warning(self, "Information", "Duplicate Name")
                                # focus name field like VB6 Txt(0).SetFocus
                                nf = self.edits.get("name")
                                if nf:
                                    nf.setFocus()
                                return
                    except Exception:
                        pass
                # VB6 Save confirmation "Save Record ?" / "Save Data" (Proc_14_32)
                # For parity we keep direct insert without extra confirm here (VB6 calls Txt_Validate->Save prompt via Enter)
                self.cfg.api.insert(rec)
            else:
                # Edit duplicate Name excluding original (global_64)
                if name_val and self._edit_orig_name is not None and name_val.lower() != self._edit_orig_name.lower():
                    try:
                        rows = self.cfg.api.list_all()
                        for r in rows:
                            rn = str(r.get("name") or r.get("Name") or "").strip()
                            rc = str(r.get("code") or r.get("Code") or "").strip()
                            if rn.lower() == name_val.lower() and rc.lower() != (self.edit_pk or "").lower():
                                QMessageBox.warning(self, "Information", "Duplicate Name")
                                nf = self.edits.get("name")
                                if nf:
                                    nf.setFocus()
                                return
                    except Exception:
                        pass
                self.cfg.api.update(self.edit_pk, rec)
        except ValueError as e:
            QMessageBox.warning(self, "Save", str(e))
            return
        except Exception as e:
            QMessageBox.critical(self, "Database Error",
                                 f"Unable to save: {e}")
            return
        self.edit_pk = None
        self._edit_orig_name = None
        self.set_state(False)
        self.reload()

    def _on_cancel(self):
        # VB6 TopCtrl_B: MsgBox "Cancel ?" 4, "Terminate Process"
        if self.state != "Idle":
            reply = QMessageBox.question(
                self, "Terminate Process",
                "Cancel ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                # focus back like VB6 var_110.SetFocus
                if self._current_edit:
                    self._current_edit.setFocus()
                return
        self.edit_pk = None
        self._edit_orig_name = None
        self._clear_fields()
        self._hide_popups()
        self.lblUser.setText("")
        self.lblLDt.setText("")
        self.set_state(False)

    def _on_delete(self):
        pk = self._selected_pk()
        if not pk:
            QMessageBox.information(self, "Delete",
                                    "Please select a record to delete")
            return
        if self.cfg.delete_guard:
            err = self.cfg.delete_guard(pk)
            if err:
                QMessageBox.warning(self, "Delete", err)
                return
        # VB6 C->Delete: MsgBox "Delete Record ?" 0x24, "Confirmation" + BeginTrans
        reply = QMessageBox.question(
            self, "Confirmation",
            "Delete Record ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Bookmark preserve like VB6 var_94 = Me.Bookmark / Requery twice / restore
            bookmark = self.tbl.currentRow()
            try:
                self.cfg.api.delete(pk)
                self.reload()
                # restore or MoveLast
                if 0 <= bookmark < self.tbl.rowCount():
                    self.tbl.selectRow(bookmark)
                elif self.tbl.rowCount() > 0:
                    self.tbl.selectRow(self.tbl.rowCount() - 1)
            except Exception as e:
                QMessageBox.critical(self, " Deletion Error ",
                                     f"Unable to delete: {e}")


def make_delete_guard(sample_prefix: str = "PYT"):
    """Safety: production records protected, sirf test-prefix deletable."""
    def guard(pk: str):
        if not pk.upper().startswith(sample_prefix.upper()):
            return (f"Safety: only {sample_prefix}* test-records can be deleted "
                    "(production data is protected)")
        return None
    return guard
