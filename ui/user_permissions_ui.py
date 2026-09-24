"""User Permissions UI - menuHelp Param_Str editor (VB6 UserPermission.frm port).

SA users hi khol sakte hain (VB6 MeUsers/UserPermission admin-only the).
- User select karo -> uska menuHelp tree (sidebar->group->leaf)
- Har leaf pe A / E / D / P checkboxes (Param_Str positions)
- Hide/V toggle (Flag V) + Leaf-absent toggle (restricted-user semantics)
- Save (DB update) / Revert (reload) / Copy from SA (template)
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (QComboBox, QDialog, QFormLayout, QGroupBox,
                             QHBoxLayout, QHeaderView, QLabel, QMessageBox,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QTreeWidget, QTreeWidgetItem, QVBoxLayout,
                             QWidget, QCheckBox, QLineEdit)

from HMS_py.core import menu_help as mh
from HMS_py.ui import theme as _theme


class UserPermissionsDialog(QDialog):
    """menuHelp rights editor: user -> tree -> AEDP checkboxes."""

    def __init__(self, parent=None, user: str = "SA"):
        super().__init__(parent)
        self.current_admin = user
        self.setWindowTitle("User Permissions (menuHelp Param_Str editor)")
        self.resize(980, 640)
        self._loading = False
        self._build_ui()
        self._load_users()

    # ------------------------------------------------------------ UI
    def _build_ui(self):
        p = _theme.palette()
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(10)

        # --- user selector + actions ---
        top = QFormLayout()
        self.cmb_user = QComboBox()
        self.cmb_user.setMinimumHeight(30)
        self.cmb_user.currentTextChanged.connect(self._on_user_changed)
        top.addRow("User:", self.cmb_user)

        acts = QHBoxLayout()
        self.btn_new_user = QPushButton("+ New User")
        self.btn_new_user.setToolTip(
            "UserMast login + menuHelp template copy (naya user onboarding)")
        self.btn_new_user.clicked.connect(self._on_new_user)
        self.btn_copy_sa = QPushButton("Copy from SA template")
        self.btn_copy_sa.setToolTip(
            "Is user ke menuHelp rows delete karke SA template copy karo")
        self.btn_copy_sa.clicked.connect(self._on_copy_from_sa)
        self.btn_clear = QPushButton("Clear all (full access)")
        self.btn_clear.setToolTip(
            "User ke saare menuHelp rows delete — full access (VB6 User1 pattern)")
        self.btn_clear.clicked.connect(self._on_clear_all)
        self.btn_revert = QPushButton("Revert")
        self.btn_revert.clicked.connect(self._on_user_changed_reload)
        self.btn_save = QPushButton("Save")
        self.btn_save.setDefault(True)
        self.btn_save.clicked.connect(self._on_save)
        for b in (self.btn_new_user, self.btn_copy_sa, self.btn_clear,
                  self.btn_revert, self.btn_save):
            b.setMinimumHeight(30)
            acts.addWidget(b)
        acts.addStretch()
        top.addRow(acts)
        root.addLayout(top)

        # --- search/filter (bade trees ke liye, 2026-09-23) ---
        srow = QHBoxLayout()
        srow.addWidget(QLabel("Search:"))
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText(
            "Leaf dhoondo... (substring, case-insensitive; Escape = clear)")
        self.txt_search.setClearButtonEnabled(True)
        self.txt_search.setMinimumHeight(30)
        self.txt_search.textChanged.connect(self._apply_filter)
        QShortcut(QKeySequence("Escape"), self.txt_search,
                  activated=self.txt_search.clear)
        srow.addWidget(self.txt_search, stretch=1)
        root.addLayout(srow)

        # --- bulk actions (2026-09-23) ---
        bulk = QHBoxLayout()
        bulk.addWidget(QLabel("Bulk:"))
        self.cmb_preset = QComboBox()
        self.cmb_preset.addItems([
            "AEDP — Full",
            "AE*P — No Delete",
            "A**P — Add+Print",
            "***P — Print-only",
            "**** — Deny",
            "REPORTS-ONLY — R=***P, E=****",
        ])
        self.cmb_preset.setToolTip(
            "Preset Param_Str. REPORTS-ONLY: reports print-only, "
            "forms denied (user sirf reports dekh sake).")
        self.btn_bulk_sel = QPushButton("Apply to selected group")
        self.btn_bulk_sel.setToolTip(
            "Tree me group/module row select karke dabao — us subtree ki "
            "sab leaves pe preset lagega (UI me; Save se persist)")
        self.btn_bulk_sel.clicked.connect(self._on_bulk_selected)
        self.btn_bulk_all = QPushButton("Apply to ALL leaves")
        self.btn_bulk_all.setToolTip(
            "Poore tree ki sab leaves pe preset (UI me; Save se persist)")
        self.btn_bulk_all.clicked.connect(self._on_bulk_all)
        for b in (self.btn_bulk_sel, self.btn_bulk_all):
            b.setMinimumHeight(30)
        bulk.addWidget(self.cmb_preset, stretch=1)
        bulk.addWidget(self.btn_bulk_sel)
        bulk.addWidget(self.btn_bulk_all)
        root.addLayout(bulk)

        # --- tree ---
        grp = QGroupBox("menuHelp tree (A=Add E=Edit D=Delete P=Print, "
                        "'*' = denied; V = leaf hidden)")
        lay = QVBoxLayout(grp)
        self.tree = QTreeWidget()
        self.tree.setColumnCount(6)
        self.tree.setHeaderLabels(
            ["Menu leaf", "Flag", "A", "E", "D", "P"])
        self.tree.header().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 6):
            self.tree.header().setSectionResizeMode(
                i, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.itemChanged.connect(self._on_item_changed)
        lay.addWidget(self.tree)
        root.addWidget(grp, stretch=1)

        # --- status ---
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet(f"color: {p.get('text_dim', p['text'])};")
        root.addWidget(self.lbl_status)

        self._style_check_cols()

    def _style_check_cols(self):
        p = _theme.palette()
        self.tree.setStyleSheet(
            f"QTreeWidget {{ background: {p['glass_tint']}; "
            f"color: {p['text']}; border: 1px solid {p['border']}; "
            f"border-radius: 6px; font-size: 13px; }}"
            f"QHeaderView::section {{ background: {p['surface_solid']}; "
            f"color: {p['text']}; padding: 4px; border: none; }}")

    # ------------------------------------------------------- data load
    def _load_users(self):
        self._loading = True
        try:
            self.cmb_user.clear()
            users = mh.users_with_rights()
            if self.current_admin.upper() != "SA":
                users = [u for u in users if u.upper() == "SA"]
            self.cmb_user.addItems(users)
        finally:
            self._loading = False
        if users:
            self._reload_tree()

    def _on_user_changed(self, _text):
        if self._loading:
            return
        self._reload_tree()

    def _on_user_changed_reload(self):
        self._reload_tree()

    def _reload_tree(self):
        user = self.cmb_user.currentText()
        self.tree.blockSignals(True)
        self.tree.clear()
        try:
            full = mh.full_access(user)
            self._base_status = (
                f"{user}: "
                + ("full access (menuHelp rows absent — SA-style)" if full
                   else f"{len(mh.entries(user))} menuHelp rows"))
            self.lbl_status.setText(self._base_status)
            side = mh.sidebar_sources(user)
            for mod in side:
                mitem = QTreeWidgetItem([mod["name"], "M", "", "", "", ""])
                mitem.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.tree.addTopLevelItem(mitem)
                for g in mh.menubar_for(mod["name"], user):
                    gitem = QTreeWidgetItem([g["name"], "G", "", "", "", ""])
                    gitem.setFlags(Qt.ItemFlag.ItemIsEnabled)
                    mitem.addChild(gitem)

                    def add_leaf(parent, it):
                        leaf = QTreeWidgetItem(
                            [it["name"], it.get("flag") or "N",
                             "", "", "", ""])
                        leaf.setFlags(
                            Qt.ItemFlag.ItemIsEnabled
                            | Qt.ItemFlag.ItemIsUserCheckable)
                        # FIX 2026-09-23: addChild PEHLE, setItemWidget
                        # baad me — warna widget-item association chutti
                        # (checks render hi nahi hote the)
                        parent.addChild(leaf)
                        self._set_checks(leaf, it["name"], user)
                        for ch in it.get("children") or []:
                            add_leaf(leaf, ch)

                    for it in g.get("items") or []:
                        add_leaf(gitem, it)
                mitem.setExpanded(True)
        finally:
            self.tree.blockSignals(False)
        # current search term dobara apply karo (reload ke baad)
        self._apply_filter()

    def _set_checks(self, item: QTreeWidgetItem, cap: str, user: str):
        """Param_Str + Flag V + absent-row state ko checkboxes me dalo."""
        row = mh.by_caption(user).get(mh._norm_caption(cap))
        present = row is not None
        if present:
            param = row["param"] or "AEDP"
            flag = row["flag"]
        else:
            param = "****" if not mh.full_access(user) else "AEDP"
            flag = "V" if not mh.full_access(user) else "-"
        hidden = flag == "V"

        # Leaf-presence checkbox: column 1 re-purposed via item data (tool tip)
        item.setToolTip(0, "Absent row = leaf user ko dikhti hi nahi "
                           "(restricted user). Tick = present.")
        item.setData(0, Qt.ItemDataRole.UserRole, {"cap": cap,
                                                   "present": present,
                                                   "hidden": hidden})
        marks = {"A": 2, "E": 3, "D": 4, "P": 5}
        for right, col in marks.items():
            c = QCheckBox()
            c.setChecked(right in (param or ""))
            c.setStyleSheet("QCheckBox { margin-left: 12px; }")
            self.tree.setItemWidget(item, col, c)
        # presence toggle column-1 me text se
        item.setText(1, ("V" if hidden else flag) if present
                     else "absent")

    def _read_checks(self, item: QTreeWidgetItem) -> tuple[str, str, bool, bool]:
        data = item.data(0, Qt.ItemDataRole.UserRole) or {}
        cap = data.get("cap", "")
        param = ""
        for col, right in ((2, "A"), (3, "E"), (4, "D"), (5, "P")):
            w = self.tree.itemWidget(item, col)
            if isinstance(w, QCheckBox) and w.isChecked():
                param += right
            else:
                param += "*"
        present = item.text(1) != "absent"
        hidden = item.text(1) == "V"
        return cap, param, present, hidden

    # -------------------------------------------------------- handlers
    def _apply_filter(self, *_):
        """Search term se tree filter karo (post-order visibility).

        - leaf: term empty => visible; warna caption contains term
        - module/group: own-name match => poora group visible;
          warna koi visible child ho to visible (+expand)
        - term empty => default state (modules expanded, groups collapsed)
        """
        if not hasattr(self, "txt_search"):
            return
        term = (self.txt_search.text() or "").strip().lower()
        stats = {"total": 0, "matched": 0}

        def walk(item):
            name = str(item.text(0) or "").lower()
            is_leaf = self.tree.itemWidget(item, 2) is not None
            if is_leaf:
                stats["total"] += 1
                ok = (not term) or (term in name)
                if ok:
                    stats["matched"] += 1
                item.setHidden(not ok)
                return
            any_child_visible = False
            for i in range(item.childCount()):
                walk(item.child(i))
                if not item.child(i).isHidden():
                    any_child_visible = True
            if term:
                visible = (term in name) or any_child_visible
                item.setHidden(not visible)
                item.setExpanded(visible)
            else:
                item.setHidden(False)
                # default: sirf top-level (modules) expanded
                item.setExpanded(item.parent() is None)

        for i in range(self.tree.topLevelItemCount()):
            walk(self.tree.topLevelItem(i))
        if term and hasattr(self, "_base_status"):
            self.lbl_status.setText(
                f"{self._base_status} · search '{term}': "
                f"{stats['matched']}/{stats['total']} leaves")
        elif hasattr(self, "_base_status"):
            self.lbl_status.setText(self._base_status)

    def _on_new_user(self):
        """Naya user onboarding: UserMast login + menuHelp template copy."""
        from PyQt6.QtWidgets import QLineEdit as _LE
        dlg = QDialog(self)
        dlg.setWindowTitle("New User (UserMast + menuHelp)")
        dlg.setMinimumWidth(380)
        form = QFormLayout(dlg)
        ed_user = _LE(); ed_user.setMaxLength(10)
        ed_user.setPlaceholderText("max 10 chars (USER_NAME)")
        ed_pass = _LE(); ed_pass.setEchoMode(_LE.EchoMode.Password)
        ed_pass2 = _LE(); ed_pass2.setEchoMode(_LE.EchoMode.Password)
        ed_label = _LE(); ed_label.setMaxLength(30)
        cmb_tmpl = QComboBox()
        for u in mh.users_with_rights():
            cmb_tmpl.addItem(u)
        if cmb_tmpl.findText("SA") >= 0:
            cmb_tmpl.setCurrentText("SA")
        form.addRow("Username*:", ed_user)
        form.addRow("Password*:", ed_pass)
        form.addRow("Password (again):", ed_pass2)
        form.addRow("Label:", ed_label)
        form.addRow("menuHelp template:", cmb_tmpl)
        btns = QHBoxLayout()
        btn_ok = QPushButton("Create")
        btn_ok.setDefault(True)
        btn_cancel = QPushButton("Cancel")
        btn_ok.clicked.connect(dlg.accept)
        btn_cancel.clicked.connect(dlg.reject)
        btns.addStretch(); btns.addWidget(btn_cancel); btns.addWidget(btn_ok)
        form.addRow(btns)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        uname = (ed_user.text() or "").strip()
        pw, pw2 = ed_pass.text() or "", ed_pass2.text() or ""
        if not uname or not pw:
            QMessageBox.warning(self, "New User",
                                "Username aur password zaroori hain")
            return
        if pw != pw2:
            QMessageBox.warning(self, "New User", "Passwords match nahi kar rahe")
            return
        try:
            res = mh.create_user(
                uname, pw, label=(ed_label.text() or uname).strip(),
                template_user=cmb_tmpl.currentText())
        except Exception as e:
            QMessageBox.critical(self, "New User", str(e))
            return
        self._loading = True
        try:
            self.cmb_user.addItem(res["username"])
            self.cmb_user.setCurrentText(res["username"])
        finally:
            self._loading = False
        self._reload_tree()
        QMessageBox.information(
            self, "New User",
            f"User '{res['username']}' bana: UserMast ok, "
            f"{res['menuhelp_rows']} menuHelp rows "
            f"({cmb_tmpl.currentText()} template se).")

    def _on_item_changed(self, *_):
        pass  # checkboxes itemWidget hain — itemChanged se kuch nahi

    # ---------------------------------------------------------- bulk
    _PRESET_PARAMS = {
        "AEDP": "AEDP", "AE*P": "AE*P", "A**P": "A**P",
        "***P": "***P", "****": "****",
    }

    def _preset_param_for(self, leaf_flag: str) -> str:
        """Selected preset -> Param_Str is leaf ke liye.

        REPORTS-ONLY: Flag R => ***P (print-only), E/N => **** (deny).
        """
        raw = (self.cmb_preset.currentText() or "").split(" ")[0].strip()
        if raw == "REPORTS-ONLY":
            return "***P" if leaf_flag == "R" else "****"
        return self._PRESET_PARAMS.get(raw, "AEDP")

    def _bulk_set_checks(self, item: QTreeWidgetItem, param: str):
        """Leaf ke checkboxes preset se set karo (UI-only)."""
        for col, right in ((2, "A"), (3, "E"), (4, "D"), (5, "P")):
            w = self.tree.itemWidget(item, col)
            if isinstance(w, QCheckBox):
                w.setChecked(right in param)

    def _bulk_guard(self) -> str | None:
        user = self.cmb_user.currentText()
        if not user:
            return None
        if user.upper() == "SA":
            QMessageBox.warning(self, "Bulk",
                                "SA template edit na karo (VB6 rule).")
            return None
        return user

    def _bulk_walk(self, item, param_fn, stats):
        """Subtree ke sab leaves pe preset UI-checks apply karo."""
        for i in range(item.childCount()):
            ch = item.child(i)
            if self.tree.itemWidget(ch, 2):  # leaf
                data = ch.data(0, Qt.ItemDataRole.UserRole) or {}
                if data.get("present"):
                    flag = str(ch.text(1) or "").strip()
                    self._bulk_set_checks(ch, param_fn(flag))
                    stats["n"] += 1
            self._bulk_walk(ch, param_fn, stats)

    def _bulk_apply(self, scope: str):
        user = self._bulk_guard()
        if not user:
            return
        raw = (self.cmb_preset.currentText() or "").split(" ")[0].strip()
        param_fn = self._preset_param_for
        roots = []
        if scope == "selected":
            cur = self.tree.currentItem()
            if cur is None:
                QMessageBox.information(
                    self, "Bulk",
                    "Pehle tree me group/module row select karo.")
                return
            roots = [cur]
        else:
            roots = [self.tree.topLevelItem(i)
                     for i in range(self.tree.topLevelItemCount())]
        stats = {"n": 0}
        for r in roots:
            self._bulk_walk(r, param_fn, stats)
        if stats["n"] == 0:
            QMessageBox.information(
                self, "Bulk",
                "Koi present leaf nahi mili (absent leaves skip hoti hain).")
            return
        self.lbl_status.setText(
            f"{self._base_status} · bulk '{raw}' ({scope}) -> "
            f"{stats['n']} leaves UI me set — persist karne ke liye Save dabao")

    def _on_bulk_selected(self):
        self._bulk_apply("selected")

    def _on_bulk_all(self):
        if QMessageBox.question(
                self, "Bulk ALL",
                "Poore tree ki sab leaves pe preset apply karein? "
                "(UI me — Save se DB me jayega)") \
                != QMessageBox.StandardButton.Yes:
            return
        self._bulk_apply("all")

    def _collect(self) -> list[tuple[str, str, bool, bool]]:
        out = []

        def walk(item):
            for i in range(item.childCount()):
                ch = item.child(i)
                if ch.childCount() or self.tree.itemWidget(ch, 2):
                    if self.tree.itemWidget(ch, 2):
                        out.append(self._read_checks(ch))
                    walk(ch)

        for i in range(self.tree.topLevelItemCount()):
            walk(self.tree.topLevelItem(i))
        return out

    def _on_save(self):
        user = self.cmb_user.currentText()
        if not user:
            return
        if user.upper() == "SA":
            QMessageBox.warning(self, "User Permissions",
                                "SA template edit na karo (VB6 rule). "
                                "Rights doosre user pe assign karo.")
            return
        changes = self._collect()
        n_rights = n_hidden = 0
        for cap, param, present, hidden in changes:
            if not cap:
                continue
            if not present:
                # absent leaf: kuch karne ki zaroorat nahi (already absent)
                continue
            if hidden:
                n_hidden += mh.set_hidden(user, cap, True)
            else:
                mh.set_rights(user, cap, param)
                n_rights += 1
        self._reload_tree()
        QMessageBox.information(
            self, "User Permissions",
            f"Saved: {n_rights} leaves ke rights, "
            f"{n_hidden} hidden toggles ({user}).")

    def _on_copy_from_sa(self):
        user = self.cmb_user.currentText()
        if user.upper() == "SA":
            return
        if QMessageBox.question(
                self, "Copy from SA",
                f"{user} ke saare menuHelp rows delete karke SA template "
                "copy karein?") != QMessageBox.StandardButton.Yes:
            return
        try:
            n = mh.copy_template("SA", user)
            self._reload_tree()
            QMessageBox.information(
                self, "Copy from SA", f"{n} rows copy hue ({user}).")
        except Exception as e:
            QMessageBox.critical(self, "Copy from SA", str(e))

    def _on_clear_all(self):
        user = self.cmb_user.currentText()
        if user.upper() == "SA":
            return
        if QMessageBox.question(
                self, "Clear all",
                f"{user} ke saare menuHelp rows delete karein? "
                "(User ko full access mil jayega)") \
                != QMessageBox.StandardButton.Yes:
            return
        try:
            mh.delete_user_rights(user)
            self._reload_tree()
        except Exception as e:
            QMessageBox.critical(self, "Clear all", str(e))


def open_user_permissions(parent=None, user: str = "SA"):
    """Registry opener (VB6 Permissions / User Permissions Advanced)."""
    dlg = UserPermissionsDialog(parent, user=user)
    dlg.exec()
