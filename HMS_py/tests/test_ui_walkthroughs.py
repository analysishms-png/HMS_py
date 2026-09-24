"""UI walkthrough regression tests (CI-ready).

Teeno manual walkthrough scripts (glass appearance, room status, main
window flow) ko ek pytest file me consolidate kiya hai. Offscreen Qt pe
chalte hain, DB ki zaroorat NAHI (fake data / offline-graceful).

Run:
    QT_QPA_PLATFORM=offscreen .venv/Scripts/python.exe -m pytest \
        tests/test_ui_walkthroughs.py -v

CI: koi bhi runner — env var `QT_QPA_PLATFORM=offscreen` set hota hai
conftest-level, koi display service (xvfb) ki zaroorat nahi.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

pytestmark = [pytest.mark.unit] if hasattr(pytest.mark, "unit") else []

# ---------------------------------------------------------------- qapp
_QAPP = None


def _qapp():
    global _QAPP
    if _QAPP is None:
        from PyQt6.QtWidgets import QApplication
        _QAPP = QApplication.instance() or QApplication([])
    return _QAPP


@pytest.fixture(autouse=True)
def _fresh_theme():
    """Har test se pehle/baad tokens + in-memory _active reset.

    Sirf QSettings clear karne se _active leak rehta hai — random test
    order (pytest-randomly) pe dark mode cancel/reset assertions fail
    karta tha.
    """
    from HMS_py.ui import theme
    theme.reset_tokens()
    theme._active = theme._resolve({})
    yield
    theme.reset_tokens()
    theme._active = theme._resolve({})


# =================================================================
# Appearance dialog walkthrough
# =================================================================
class TestAppearanceDialog:
    def test_dialog_opens_with_seeded_status_hues(self):
        from HMS_py.ui.glass import AppearanceDialog
        from HMS_py.ui import theme
        _qapp()
        # Saved tokens (pichle tests ka dark preset etc.) seed-pollute
        # karte hain — deterministic light-default check ke liye reset.
        theme.reset_tokens()
        d = AppearanceDialog()
        sdefs = theme.status_base_defaults(
            d._start.get("mode", "light"))  # dialog ke apne mode se
        assert d._swatches["success"]._color == sdefs["success"]
        assert d._swatches["neutral"]._color == sdefs["neutral"]
        d._cancel()

    def test_preset_live_preview_switches_modes(self):
        from HMS_py.ui.glass import AppearanceDialog
        from HMS_py.ui import theme
        _qapp()
        theme.apply_theme(_qapp())
        d = AppearanceDialog()
        for preset, mode in (("Midnight Glass", "dark"),
                             ("Emerald Breeze", "light"),
                             ("Graphite Pro", "dark")):
            d.cmbPreset.setCurrentText(preset)
            d._apply_preset()
            assert theme.current_theme() == mode, preset
        d._cancel()

    def test_sliders_update_tokens(self):
        from HMS_py.ui.glass import AppearanceDialog
        _qapp()
        d = AppearanceDialog()
        d.sldOpacity.setValue(85)
        d.sldRadius.setValue(4)
        assert d._tokens["glass_opacity"] == "0.85"
        assert d._tokens["radius"] == "4"
        d._cancel()

    def test_cancel_restores_saved_state(self):
        from HMS_py.ui.glass import AppearanceDialog
        from HMS_py.ui import theme
        _qapp()
        theme.apply_theme(_qapp())
        d = AppearanceDialog()
        d.cmbPreset.setCurrentText("Midnight Glass")
        d._apply_preset()
        assert theme.current_theme() == "dark"
        d._cancel()   # restore
        assert theme.current_theme() == "light"

    def test_save_persists_tokens(self):
        from HMS_py.ui.glass import AppearanceDialog
        from HMS_py.ui import theme
        _qapp()
        theme.apply_theme(_qapp())
        d = AppearanceDialog()
        d.cmbPreset.setCurrentText("Midnight Glass")
        d._apply_preset()
        d._save()
        saved = theme.load_tokens()
        assert saved.get("mode") == "dark"
        assert theme.current_theme() == "dark"

    def test_custom_status_hue_survives_preset_switch(self):
        from HMS_py.ui.glass import AppearanceDialog
        from HMS_py.ui import theme
        _qapp()
        theme.apply_theme(_qapp())
        d = AppearanceDialog()
        d._swatches["success"].set_color("#7c3aed")
        d._tokens["success"] = "#7c3aed"
        d.cmbPreset.setCurrentText("Midnight Glass")
        d._apply_preset()
        s = theme.status_colors()
        assert s["success"] == "#7c3aed"
        # bg derived purple-family (r > g)
        bg = s["success_bg"].lstrip("#")
        assert int(bg[0:2], 16) > int(bg[2:4], 16)
        d._cancel()

    def test_reset_hues_button_restores_defaults(self):
        from HMS_py.ui.glass import AppearanceDialog
        from HMS_py.ui import theme
        _qapp()
        theme.apply_theme(_qapp())
        d = AppearanceDialog()
        d._swatches["success"].set_color("#7c3aed")
        d._tokens["success"] = "#7c3aed"
        d._reset_status_hues()
        s = theme.status_colors()
        sdefs = theme.status_base_defaults("light")
        assert s["success"] == sdefs["success"]
        # explicit token prune hua — save pe default nahi jayega
        assert "success" not in d._tokens
        d._cancel()

    def test_no_widget_overflows_dialog(self):
        from HMS_py.ui.glass import AppearanceDialog
        _qapp()
        d = AppearanceDialog()
        d.show()
        _qapp().processEvents()
        dw, dh = d.width(), d.height()
        from PyQt6.QtWidgets import QWidget
        for child in d.findChildren(QWidget):
            if child.parent() is None:
                continue
            # popup widgets (combo dropdown QListView) dialog ke bahar
            # render hote hain — skip. Sirf layout-managed children check.
            if child.window() is not d:
                continue
            r = child.geometry()
            assert r.right() <= dw + 2, (child, r.right(), dw)
            assert r.bottom() <= dh + 2, (child, r.bottom(), dh)
        d._cancel()


# =================================================================
# Room status walkthrough (fake data, DB-free)
# =================================================================
FAKE_ROOMS = [
    {"roomno": "101", "name": "Deluxe", "cat": "DLX", "maid": "MS-1",
     "status": "Vacant", "folio": None, "guest": "", "dep": None,
     "chk_in": None},
    {"roomno": "102", "name": "Deluxe", "cat": "DLX", "maid": "MS-1",
     "status": "Occupied", "folio": 2101, "guest": "R. Sharma",
     "dep": "22/Sep/2026", "chk_in": "18/Sep/2026"},
    {"roomno": "103", "name": "Suite", "cat": "SUIT", "maid": "MS-2",
     "status": "Dirty", "folio": None, "guest": "", "dep": None,
     "chk_in": None},
    {"roomno": "104", "name": "Suite", "cat": "SUIT", "maid": "MS-2",
     "status": "Maintenance", "folio": None, "guest": "", "dep": None,
     "chk_in": None},
    {"roomno": "105", "name": "Std", "cat": "STD", "maid": "MS-3",
     "status": "Out of Order", "folio": None, "guest": "", "dep": None,
     "chk_in": None},
]


@pytest.fixture()
def room_status_form(monkeypatch):
    from HMS_py.ui import roomstatus_ui as rs
    from HMS_py.ui.roomstatus_ui import RoomStatusForm

    monkeypatch.setattr(rs.roomstatus, "room_rack",
                        lambda: [dict(r) for r in FAKE_ROOMS])
    monkeypatch.setattr(rs.roomstatus, "housekeeping_summary", lambda: {
        "total": 5, "occupied": 1, "vacant": 1, "dirty": 1,
        "maintenance": 2, "occ_pct": 20.0})

    w = RoomStatusForm()
    w.show()
    _qapp().processEvents()
    yield w
    w.close()


def _cell_bg(tbl, r, c):
    it = tbl.item(r, c)
    return it.background().color().name() if it else None


def _cell_fg(tbl, r, c):
    it = tbl.item(r, c)
    return it.foreground().color().name() if it else None


class TestRoomStatusScreen:
    def test_light_mode_status_cells(self, room_status_form):
        from HMS_py.ui import theme
        theme.apply_theme(_qapp())
        room_status_form.reload()
        s = theme.status_colors()
        tbl = room_status_form.tbl
        assert _cell_bg(tbl, 0, 0) == s["success_bg"]   # Vacant
        assert _cell_bg(tbl, 1, 0) == s["danger_bg"]    # Occupied
        assert _cell_bg(tbl, 2, 0) == s["warning_bg"]   # Dirty
        assert _cell_bg(tbl, 3, 0) == s["neutral_bg"]   # Maintenance
        assert _cell_bg(tbl, 4, 0) == s["neutral_bg"]   # Out of Order
        assert _cell_fg(tbl, 0, 0) == s["success_text"]

    def test_dark_mode_adapts_cells(self, room_status_form):
        from HMS_py.ui import theme
        theme.apply_tokens(_qapp(),
                           theme.preset_tokens("Midnight Glass"))
        room_status_form.reload()
        s = theme.status_colors()
        tbl = room_status_form.tbl
        bg = _cell_bg(tbl, 0, 0)
        assert bg == s["success_bg"]
        assert bg != "#dcf0ea"            # light value nahi
        assert _cell_fg(tbl, 0, 0) == s["success_text"]

    def test_custom_hue_derives_cell_colors(self, room_status_form):
        from HMS_py.ui import theme
        theme.apply_tokens(_qapp(), {"success": "#7c3aed"})
        room_status_form.reload()
        s = theme.status_colors()
        tbl = room_status_form.tbl
        assert _cell_bg(tbl, 0, 0) == s["success_bg"]
        bg = s["success_bg"].lstrip("#")
        assert int(bg[0:2], 16) > int(bg[2:4], 16)   # purple family

    def test_summary_labels_use_status_text(self, room_status_form):
        from HMS_py.ui import theme
        theme.apply_theme(_qapp())
        room_status_form.reload()
        # Occupied count > 0 -> danger_text style laga hoga
        assert "danger_text" or True  # text hai; style string check:
        sheet = room_status_form.lblOcc.styleSheet()
        assert theme.status_colors()["danger_text"] in sheet

    def test_hk_buttons_use_status_palette(self, room_status_form):
        from HMS_py.ui import theme
        theme.apply_theme(_qapp())
        s = theme.status_colors()
        assert s["success"] in room_status_form.btnVacant.styleSheet()
        assert s["warning"] in room_status_form.btnDirty.styleSheet()
        assert s["danger"] in room_status_form.btnOOO.styleSheet()


# =================================================================
# Main window flow walkthrough
# =================================================================
class TestMainWindowFlow:
    @pytest.fixture()
    def main_window(self, monkeypatch):
        from HMS_py.ui import shell
        from HMS_py.core import menu
        from HMS_py.ui.shell import MainWindow

        # DB offline-safe: menu model fake karo (User_Module table nahi)
        fake_modules = [
            {"code": "Mast", "name": "Main Setup", "srno": 41},
            {"code": "FrontDesk", "name": "Front Office", "srno": 216},
        ]
        fake_menubar = [{
            "name": "Masters",
            "items": [{"name": "Country Master", "children": []},
                      {"name": "Check In", "children": []}],
        }]
        monkeypatch.setattr(menu, "sidebar_modules",
                            lambda: list(fake_modules))
        monkeypatch.setattr(menu, "menubar_for",
                            lambda name, user: [dict(g) for g in fake_menubar])
        monkeypatch.setattr(
            "HMS_py.core.db.connect",
            lambda cfg=None: (_ for _ in ()).throw(OSError("offline")))

        # Modal auto-open guard: Main Setup / Reservation .exec() test pe
        # infinite block karta tha (QA pattern: spy_exec auto-close).
        from PyQt6.QtCore import QTimer
        from PyQt6.QtWidgets import QDialog
        _orig_exec = QDialog.exec

        def _spy_exec(self, *a, **k):
            if type(self).__name__ in ("MainSetupWorkbench",
                                       "PlanMasterForm"):
                QTimer.singleShot(0, self.close)
            return _orig_exec(self, *a, **k)

        monkeypatch.setattr(QDialog, "exec", _spy_exec)

        win = MainWindow("SA", {"name": "Test Resort", "short": "TR",
                                "year": "2025-26"})
        win.show()
        _qapp().processEvents()
        yield win
        win.close()

    def test_window_builds_with_aurora(self, main_window):
        assert hasattr(main_window, "aurora")
        assert main_window.windowTitle().startswith("Test Resort")

    def test_module_click_populates_menubar(self, main_window):
        win = main_window
        win._on_module({"name": "Main Setup", "srno": 41},
                       win._side_buttons[0])
        _qapp().processEvents()
        assert win.menuBar().actions(), "menubar khali na ho"
        assert "Main Setup" in win.windowTitle()

    def test_theme_toggle_flips_mode(self, main_window):
        from HMS_py.ui import theme
        win = main_window
        before = theme.current_theme()
        win._toggle_theme()
        after = theme.current_theme()
        assert after != before
        win._toggle_theme()          # wapas
        assert theme.current_theme() == before

    def test_resize_keeps_aurora_covered(self, main_window):
        win = main_window
        win.resize(900, 600)
        _qapp().processEvents()
        assert win.aurora.width() == win.centralWidget().width()
        assert win.aurora.height() == win.centralWidget().height()

    def test_sidebar_registry_has_core_masters(self, main_window):
        reg = main_window.registry
        for key in ("Main Setup", "Check In", "Reservation/Cancellation",
                    "Plan Master", "User Master"):
            assert key in reg, key


# =================================================================
# KOT state + table-map status sync (naye fixes)
# =================================================================
class TestKotAndTableMapSync:
    def test_kot_state_label_colors(self, monkeypatch):
        """Add/Edit -> accent tint, Idle -> neutral tint."""
        from HMS_py.ui import theme
        from HMS_py.ui.kot_entry import KOTEntryForm
        theme.apply_theme(_qapp())
        monkeypatch.setattr("HMS_py.core.db.connect",
                            lambda cfg=None: (_ for _ in ()).throw(
                                OSError("offline")))
        try:
            w = KOTEntryForm()
        except OSError:
            pytest.skip("KOT form DB ke bina nahi banta (lookups)")
        w.show()
        _qapp().processEvents()
        st = theme.status_colors()

        w.set_state(False)                      # Idle
        sheet = w.lbl_state.styleSheet()
        assert st["neutral_bg"] in sheet
        assert st["neutral_text"] in sheet

        w.edit_docid = None
        w.set_state(True)                       # Add
        sheet = w.lbl_state.styleSheet()
        t = theme.palette()
        assert t["accent_soft"] in sheet
        w.close()

    def test_pos_table_status_column_colors(self, monkeypatch):
        """Active=success, Inactive=neutral, Blocked=danger."""
        from PyQt6.QtWidgets import QTableWidgetItem
        from HMS_py.ui import theme
        from HMS_py.ui import pos_table_ui as ptu
        from HMS_py.ui.pos_table_ui import PosTableWindow
        theme.apply_theme(_qapp())
        monkeypatch.setattr(
            ptu.pos_table, "list_all",
            lambda cn=None, limit=500: [
                {"Code": "T1", "RoomName": "Hall", "RoomNo": "1",
                 "Type": "TB", "SeatingCapacity": 4, "Status": "Active"},
                {"Code": "T2", "RoomName": "Hall", "RoomNo": "2",
                 "Type": "TB", "SeatingCapacity": 2, "Status": "Inactive"},
                {"Code": "T3", "RoomName": "Hall", "RoomNo": "3",
                 "Type": "TB", "SeatingCapacity": 6, "Status": "Blocked"},
            ])
        w = PosTableWindow()
        w._load_data()
        st = theme.status_colors()
        assert _cell_bg(w.table, 0, 5) == st["success_bg"]    # Active
        assert _cell_bg(w.table, 1, 5) == st["neutral_bg"]    # Inactive
        assert _cell_bg(w.table, 2, 5) == st["danger_bg"]     # Blocked
        assert _cell_fg(w.table, 2, 5) == st["danger_text"]
        # non-status columns plain text
        assert _cell_fg(w.table, 0, 0) == theme.palette()["text"]
        w.close()
