"""User Permissions UI: backend fns + offscreen smoke (no destructive DB)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from HMS_py.core import menu_help as mh


def test_backend_api_exists():
    for name in ("users_with_rights", "set_rights", "set_hidden",
                 "copy_template", "delete_user_rights", "has_row",
                 "full_access"):
        assert hasattr(mh, name), name
        assert callable(getattr(mh, name))


def test_users_with_rights_returns_list():
    users = mh.users_with_rights()
    assert isinstance(users, list)
    assert "SA" in [u.upper() for u in users]
    assert "admin" in [u.lower() for u in users]


def test_set_rights_roundtrip_synthetic():
    """set_rights logic synthetic cache se (no DB write)."""
    rows = [{"caption": "Voucher Entry", "param": "A**P", "flag": "E",
             "module": "FA", "opt1": "11", "opt2": "11", "opt3": "11",
             "opt4": "0", "code": 3}]
    orig = mh._load_user
    orig_fa = mh.full_access
    mh._CACHE.clear()
    mh._CACHE["RT"] = rows
    mh._load_user = lambda username: rows if username == "RT" else orig(username)
    mh.full_access = lambda username="SA": username.upper() == "SA"
    try:
        assert mh.rights("RT", "Voucher Entry") == "A**P"
        assert not mh.can("RT", "Voucher Entry", "D")
    finally:
        mh._load_user = orig
        mh.full_access = orig_fa
        mh.clear_cache()


def test_ui_smoke_offscreen():
    """Dialog build + user load + tree render (offscreen, read-only)."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError:
        import pytest
        pytest.skip("PyQt6 missing")
    from HMS_py.ui.user_permissions_ui import UserPermissionsDialog
    QApplication.instance() or QApplication(sys.argv)
    dlg = UserPermissionsDialog(user="SA")
    dlg.show()
    users = [dlg.cmb_user.itemText(i) for i in range(dlg.cmb_user.count())]
    assert users, "user combo populate hona chahiye"
    # pehla non-SA user select karke tree render
    non_sa = next((u for u in users if u.upper() != "SA"), None)
    if non_sa:
        dlg.cmb_user.setCurrentText(non_sa)
        assert dlg.tree.topLevelItemCount() > 0, "tree render hona chahiye"
    dlg.close()


def test_bulk_presets_and_checkboxes_render():
    """Bulk presets (A**P / REPORTS-ONLY) + checkbox-widget render fix."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
    except ImportError:
        import pytest
        pytest.skip("PyQt6 missing")
    from unittest.mock import patch
    from HMS_py.ui.user_permissions_ui import UserPermissionsDialog
    QApplication.instance() or QApplication(sys.argv)
    dlg = UserPermissionsDialog(user="SA")
    dlg.show()
    users = [dlg.cmb_user.itemText(i) for i in range(dlg.cmb_user.count())]
    non_sa = next((u for u in users if u.upper() != "SA"), None)
    assert non_sa, "kam se kam ek non-SA user chahiye"
    dlg.cmb_user.setCurrentText(non_sa)

    # checkbox widgets render honi chahiye (addChild-before-widget bug fixed)
    mod0 = dlg.tree.topLevelItem(0)
    assert mod0 is not None
    leaves = []

    def collect(item):
        for i in range(item.childCount()):
            ch = item.child(i)
            if dlg.tree.itemWidget(ch, 2):
                leaves.append(ch)
            collect(ch)

    collect(mod0)
    assert leaves, "module me leaves honi chahiye"
    assert all(dlg.tree.itemWidget(it, 2) is not None for it in leaves), \
        "har leaf pe A-checkbox widget hona chahiye"

    # bulk: poore module pe A**P
    dlg.tree.setCurrentItem(mod0)
    dlg.cmb_preset.setCurrentIndex(2)  # A**P
    with patch.object(QMessageBox, "information", lambda *a, **k: None):
        dlg._bulk_apply("selected")
    for it in leaves:
        checks = [dlg.tree.itemWidget(it, c).isChecked() for c in (2, 3, 4, 5)]
        assert checks == [True, False, False, True], f"{it.text(0)}: {checks}"

    # REPORTS-ONLY: R=***P, E=****
    dlg.cmb_preset.setCurrentIndex(5)
    with patch.object(QMessageBox, "information", lambda *a, **k: None):
        dlg._bulk_apply("selected")
    r_leaf = next((it for it in leaves if it.text(1) == "R"), None)
    e_leaf = next((it for it in leaves if it.text(1) == "E"), None)
    if r_leaf:
        checks = [dlg.tree.itemWidget(r_leaf, c).isChecked() for c in (2, 3, 4, 5)]
        assert checks == [False, False, False, True], f"R-leaf: {checks}"
    if e_leaf:
        checks = [dlg.tree.itemWidget(e_leaf, c).isChecked() for c in (2, 3, 4, 5)]
        assert checks == [False, False, False, False], f"E-leaf: {checks}"
    dlg.close()


def test_new_user_dialog_backend():
    """create_user backend (synthetic, no DB write): validation guards."""
    from HMS_py.core import menu_help as mh
    import pytest
    # empty username
    with pytest.raises(ValueError):
        mh.create_user("", "pw")
    # long username
    with pytest.raises(ValueError):
        mh.create_user("X" * 11, "pw")
