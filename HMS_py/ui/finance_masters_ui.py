"""Finance Masters UI - Ledger Accounts, Tax Master, Payment Type,
Market Segment, Business Source, Guest Status, Forex Master.

VB6 pattern: TopCtrl state-machine (BaseMasterForm engine use karo).
All MasterConfig-based except LedgerMast (extra search + group FK).

Run: python -m HMS_py.ui.finance_masters_ui
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                             QVBoxLayout, QWidget)

from HMS_py.core import (ledger, taxmaster, paymenttype, marketsegment,
                         businesssource, gueststatus, forexmaster)
from HMS_py.ui.base_master import BaseMasterForm, Field, MasterConfig, \
    make_delete_guard


# ---- MasterConfig definitions ----

def taxmaster_config() -> MasterConfig:
    # VB6 FrmTaxMast: flat RevMast FieldType='T' (Name/Short/Ledger/...).
    # P0 fix: pehle LIMITS["taxtype"] KeyError se app crash hota tha.
    return MasterConfig(
        title="Tax Master - HMS_py",
        columns=[("TaxCode", "code"), ("TaxName", "name"),
                 ("Short", "short"), ("Ledger", "accode"),
                 ("Nature", "nature"), ("Active", "active")],
        fields=[
            Field("code", "Tax Code", max_len=taxmaster.LIMITS["code"],
                  required=True),
            Field("name", "Tax Name", max_len=taxmaster.LIMITS["name"],
                  required=True),
            Field("short", "Short Name",
                  max_len=taxmaster.LIMITS["short"]),
            Field("accode", "Ledger A/C (FK->SubGroup)",
                  max_len=taxmaster.LIMITS["accode"]),
            Field("payableac", "Payable A/C",
                  max_len=taxmaster.LIMITS["payableac"]),
            Field("unregisteredac", "Unregistered A/C",
                  max_len=taxmaster.LIMITS["unregisteredac"]),
            Field("sundry", "Sundry Code",
                  max_len=taxmaster.LIMITS["sundry"]),
            Field("nature", "Nature",
                  max_len=taxmaster.LIMITS["nature"]),
            Field("roundoff", "Round Off (Yes/No)",
                  max_len=taxmaster.LIMITS["roundoff"], default="No"),
            Field("active", "Active Y/N", max_len=1, default="Y"),
        ],
        api=taxmaster,
        delete_guard=make_delete_guard("PYT"),
    )


def paymenttype_config() -> MasterConfig:
    return MasterConfig(
        title="Payment Type Master - HMS_py",
        columns=[("Code", "code"), ("Name", "name"),
                 ("Category", "category"), ("Default", "isdefault"),
                 ("Active", "active")],
        fields=[
            Field("code", "Pay Code", max_len=paymenttype.LIMITS.get("code", 6),
                  required=True),
            Field("name", "Pay Name", max_len=paymenttype.LIMITS.get("name", 50),
                  required=True),
            Field("paytype", "Pay Type",
                  max_len=paymenttype.LIMITS.get("paytype", 15)),
            Field("category", "Category (CASH/CARD/CHEQUE/ONLINE/CREDIT)",
                  max_len=15),
            Field("isdefault", "Is Default (Y/N)", max_len=1, default="N"),
            Field("active", "Active Y/N", max_len=1, default="Y"),
        ],
        api=paymenttype,
        delete_guard=make_delete_guard("PYT"),
    )


def marketsegment_config() -> MasterConfig:
    return MasterConfig(
        title="Market Segment Master - HMS_py",
        columns=[("Code", "code"), ("Name", "name"), ("Active", "active")],
        fields=[
            Field("code", "Mkt Code",
                  max_len=marketsegment.LIMITS.get("code", 5), required=True),
            Field("name", "Mkt Name",
                  max_len=marketsegment.LIMITS.get("name", 20), required=True),
            Field("active", "Active Y/N", max_len=1, default="Y"),
        ],
        api=marketsegment,
        delete_guard=make_delete_guard("PYT"),
    )


def businesssource_config() -> MasterConfig:
    return MasterConfig(
        title="Business Source Master - HMS_py",
        columns=[("Code", "code"), ("Name", "name"), ("Active", "active")],
        fields=[
            Field("code", "Bus Code",
                  max_len=businesssource.LIMITS.get("code", 5), required=True),
            Field("name", "Bus Name",
                  max_len=businesssource.LIMITS.get("name", 20), required=True),
            Field("active", "Active Y/N", max_len=1, default="Y"),
        ],
        api=businesssource,
        delete_guard=make_delete_guard("PYT"),
    )


def gueststatus_config() -> MasterConfig:
    return MasterConfig(
        title="Guest Status Master - HMS_py",
        columns=[("Code", "code"), ("Name", "name"), ("Active", "active")],
        fields=[
            Field("code", "Status Code",
                  max_len=gueststatus.LIMITS.get("code", 6), required=True),
            Field("name", "Status Name",
                  max_len=gueststatus.LIMITS.get("name", 30), required=True),
            Field("active", "Active Y/N", max_len=1, default="Y"),
        ],
        api=gueststatus,
        delete_guard=make_delete_guard("PYT"),
    )


def forexmaster_config() -> MasterConfig:
    return MasterConfig(
        title="Forex Master (Currency) - HMS_py",
        columns=[("Code", "code"), ("Name", "name"),
                 ("Buy Rate", "buyrate"), ("Sell Rate", "sellrate"),
                 ("Equiv Unit", "equivunit"), ("Active", "active")],
        fields=[
            Field("code", "Curr Code",
                  max_len=forexmaster.LIMITS.get("code", 6), required=True),
            Field("name", "Currency Name",
                  max_len=forexmaster.LIMITS.get("name", 30), required=True),
            Field("buyrate", "Buy Rate", default="0"),
            Field("sellrate", "Sell Rate", default="0"),
            Field("equivunit", "Equiv Unit (1 USD = ?)", default="1"),
            Field("active", "Active Y/N", max_len=1, default="Y"),
        ],
        api=forexmaster,
        delete_guard=make_delete_guard("PYT"),
    )


def ledger_config() -> MasterConfig:
    """Ledger Accounts - extended fields for Finance."""
    return MasterConfig(
        title="Ledger Accounts - HMS_py",
        columns=[("LedCode", "code"), ("LedName", "name"),
                 ("Group", "group"), ("Nature", "nature"),
                 ("OpenBal", "openbal"), ("Active", "active")],
        fields=[
            Field("code", "Led Code",
                  max_len=ledger.LIMITS.get("code", 8), required=True),
            Field("name", "Led Name",
                  max_len=ledger.LIMITS.get("name", 75), required=True),
            Field("group", "Group Code (FK->ACGROUP)",
                  max_len=ledger.LIMITS.get("group", 6)),
            Field("nature", "Nature (D/C)", max_len=1),
            Field("openbal", "Opening Balance", default="0"),
            Field("openbaltype", "Bal Type (Dr/Cr)",
                  max_len=2, default="Dr"),
            Field("phone", "Phone", max_len=ledger.LIMITS.get("phone", 35)),
            Field("mobile", "Mobile", max_len=ledger.LIMITS.get("mobile", 24)),
            Field("email", "Email", max_len=ledger.LIMITS.get("email", 50)),
            Field("add1", "Address 1", max_len=ledger.LIMITS.get("add1", 50)),
            Field("add2", "Address 2", max_len=ledger.LIMITS.get("add2", 50)),
            Field("city", "City", max_len=ledger.LIMITS.get("city", 6)),
            Field("pan", "PAN", max_len=ledger.LIMITS.get("pan", 20)),
            Field("gstin", "GSTIN", max_len=ledger.LIMITS.get("gstin", 30)),
            Field("active", "Active Y/N", max_len=1, default="Y"),
        ],
        api=ledger,
        delete_guard=_ledger_delete_guard,
    )


def _ledger_delete_guard(code: str) -> str | None:
    """System ledgers protected; only PYT* test ledgers deletable."""
    if code.upper().startswith("PYT"):
        return None
    return ("Safety: sirf PYT* test-ledgers delete ho sakte hain.\n"
            "System/production ledgers protected hain.")


# ---- open_* helpers ----
def _open(cfg_fn, parent=None):
    BaseMasterForm(cfg_fn(), parent).exec()


def open_taxmaster(parent=None):
    _open(taxmaster_config, parent)


def open_paymenttype(parent=None):
    _open(paymenttype_config, parent)


def open_marketsegment(parent=None):
    _open(marketsegment_config, parent)


def open_businesssource(parent=None):
    _open(businesssource_config, parent)


def open_gueststatus(parent=None):
    _open(gueststatus_config, parent)


def open_forexmaster(parent=None):
    _open(forexmaster_config, parent)


def open_ledger(parent=None):
    _open(ledger_config, parent)


# ---- standalone launcher ----
class FinanceMastersLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HMS_py - Finance & FO Masters")
        self.resize(380, 400)
        central = QWidget()
        lay = QVBoxLayout(central)
        for label, fn in (
            ("Tax Master", open_taxmaster),
            ("Payment Type Master", open_paymenttype),
            ("Market Segment Master", open_marketsegment),
            ("Business Source Master", open_businesssource),
            ("Guest Status Master", open_gueststatus),
            ("Forex Master (Currency)", open_forexmaster),
            ("Ledger Accounts", open_ledger),
        ):
            b = QPushButton(label)
            b.clicked.connect(fn)
            lay.addWidget(b)
        self.setCentralWidget(central)


def main() -> int:
    app = QApplication(sys.argv)
    w = FinanceMastersLauncher()
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
