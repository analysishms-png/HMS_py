"""Banquet Setup Masters UI (VB6: Main Setup -> Banquet / Hall).

Tables ported: VenueFeatures, CatalogMast, GroupProf.
VenueMast already in p2_masters.py -> open_venue.
EventsMast/BanquetMenuCategory/BanquetItemGroup/BanquetMenuItem do not
exist in this DB installation.

Run: python -m HMS_py.ui.banquet_masters_ui
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                             QVBoxLayout, QWidget)
from HMS_py.core.banquet_masters import VenFeatureAPI, CatalogAPI, GroupProfAPI, FuncTypeAPI
from HMS_py.ui.base_master import BaseMasterForm, Field, MasterConfig, make_delete_guard


# ── Venue Features ────────────────────────────────────────────
def venfeature_config() -> MasterConfig:
    return MasterConfig(
        title="Venue Features (Banquet Amenities) - HMS_py",
        columns=[("VenueCode","venue"),("Feature","feature")],
        fields=[
            Field("venue","Venue Code (FK->VenueMast)", max_len=5, required=True),
            Field("feature","Feature / Amenity", max_len=50, required=True),
        ],
        api=VenFeatureAPI,
        pk_key="code",   # composite 'VENUE|FEATURE'
        delete_guard=None,  # all rows deletable (no production guard needed)
    )


# ── Catalog Master ────────────────────────────────────────────
def catalog_config() -> MasterConfig:
    return MasterConfig(
        title="Catalog Master (Banquet Items) - HMS_py",
        columns=[("Code","code"),("Name","name"),("ItemCode","itemcode"),
                 ("Outlet","rest"),("Category","category")],
        fields=[
            Field("code","Catalog Code", max_len=6, required=True),
            Field("name","Catalog Name", max_len=50, required=True),
            Field("itemcode","Item Code (FK->ItemMast)", max_len=8),
            Field("rest","Outlet/RestCode (FK)", max_len=6),
            Field("itemcat","Item Category Code", max_len=6),
            Field("category","Category", max_len=30),
        ],
        api=CatalogAPI,
        delete_guard=make_delete_guard("PYT"),
    )


# ── Group Profile ─────────────────────────────────────────────
def groupprof_config() -> MasterConfig:
    return MasterConfig(
        title="Group Profile (Banquet / Reservation Groups) - HMS_py",
        columns=[("Code","code"),("Name","name"),("City","city"),
                 ("Contact","conname"),("Phone","phone"),("Type","gtype")],
        fields=[
            Field("code","Group Code", max_len=6, required=True),
            Field("name","Group Name", max_len=50, required=True),
            Field("add1","Address 1", max_len=50),
            Field("add2","Address 2", max_len=50),
            Field("city","City Code", max_len=6),
            Field("type","Type (India/Foreign)", max_len=7),
            Field("conname","Contact Person", max_len=40),
            Field("phone","Phone", max_len=35),
            Field("comments","Comments", max_len=100),
            Field("travel","Travel Agency", max_len=50),
            Field("mktseg","Market Segment", max_len=6),
            Field("bussrc","Business Source", max_len=6),
            Field("gtype","Group Type", max_len=20),
        ],
        api=GroupProfAPI,
        delete_guard=make_delete_guard("PYT"),
    )


# ── open helpers ──────────────────────────────────────────────
def _open(cfg_fn, parent=None):
    BaseMasterForm(cfg_fn(), parent).exec()

def open_venfeature(parent=None):  _open(venfeature_config, parent)
def open_catalog(parent=None):     _open(catalog_config, parent)
def open_groupprof(parent=None):   _open(groupprof_config, parent)
def open_func_type(parent=None):   _open(functype_config, parent)


# ── Function Type / Events Master ──────────────────────────────
def functype_config() -> MasterConfig:
    return MasterConfig(
        title="Function Type / Events Master - HMS_py",
        columns=[("Code","code"),("Name","name"),("Status","status")],
        fields=[
            Field("code","Function Code", max_len=6, required=True),
            Field("name","Function Name", max_len=50, required=True),
            Field("status","Status", max_len=10),
            Field("accode","A/C Code", max_len=10),
            Field("rate","Rate", default="0"),
        ],
        api=FuncTypeAPI,
        delete_guard=make_delete_guard("PYT"),
    )


# ── Standalone launcher ───────────────────────────────────────
class BanquetMastersLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HMS_py - Banquet Setup Masters")
        self.resize(340, 180)
        c = QWidget(); lay = QVBoxLayout(c)
        for lbl, fn in (
            ("Venue Features",           open_venfeature),
            ("Catalog Master",           open_catalog),
            ("Group Profile",            open_groupprof),
            ("Function Type / Events",   open_func_type),
        ):
            b = QPushButton(lbl); b.clicked.connect(fn); lay.addWidget(b)
        self.setCentralWidget(c)


def main() -> int:
    app = QApplication(sys.argv)
    w = BanquetMastersLauncher(); w.show()
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())
