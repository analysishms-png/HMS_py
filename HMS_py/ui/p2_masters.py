"""P2 masters: Sundry + Narration + all Main Setup masters - BaseMasterForm config.

Run: python -m HMS_py.ui.p2_masters
Offscreen screenshot: HMS_POC_SHOT=<path> env var.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from PyQt6.QtWidgets import (QApplication, QHBoxLayout, QMainWindow,
                             QPushButton, QVBoxLayout, QWidget)

from HMS_py.core import (acgroup, area, city, country, depart, fixcharge,
                         item, narr, state, sundry, unit, venue)
# New Main Setup masters (P2-complete)
from HMS_py.core import (roomcategory, roommaster, packagemaster,
                         seasonmaster, companymaster, usermaster)
from HMS_py.ui.base_master import (BaseMasterForm, Field, MasterConfig,
                                   make_delete_guard)


def sundry_config() -> MasterConfig:
    return MasterConfig(
        title="Sundry Master (P2) - HMS_py",
        columns=[("Code", "code"), ("Name", "name"), ("Nature", "nature"),
                 ("Calc", "calc"), ("Sys", "sysyn")],
        fields=[
            Field("code", "Code", max_len=sundry.LIMITS["code"],
                  required=True),
            Field("name", "Name", max_len=sundry.LIMITS["name"],
                  required=True),
            Field("nature", "Nature", max_len=sundry.LIMITS["nature"],
                  required=True),
            Field("calc", "Calc +/-", max_len=sundry.LIMITS["calc"]),
        ],
        api=sundry,
        delete_guard=make_delete_guard("PYT"),
    )


def narr_config() -> MasterConfig:
    return MasterConfig(
        title="Narration Master (P2) - HMS_py",
        columns=[("Code", "code"), ("Name", "name")],
        fields=[
            Field("code", "Code", max_len=narr.LIMITS["code"],
                  required=True),
            Field("name", "Narration", max_len=narr.LIMITS["name"],
                  required=True),
        ],
        api=narr,
        delete_guard=make_delete_guard("PYT"),
    )


def city_config() -> MasterConfig:
    return MasterConfig(
        title="City Master (P2) - HMS_py",
        columns=[("CityCode", "code"), ("CityName", "name"),
                 ("Short", "short"), ("Zip", "zip"), ("State", "state")],
        fields=[
            Field("code", "CityCode", max_len=city.LIMITS["code"],
                  required=True),
            Field("name", "CityName", max_len=city.LIMITS["name"],
                  required=True),
            Field("short", "Short Name", max_len=city.LIMITS["short"]),
            Field("zip", "Zip Code", max_len=city.LIMITS["zip"]),
            Field("state", "State Code", max_len=city.LIMITS["state"]),
        ],
        api=city,
        delete_guard=make_delete_guard("PYT"),
    )


def area_config() -> MasterConfig:
    return MasterConfig(
        title="Area Master (P2) - HMS_py",
        columns=[("AreaCode", "code"), ("AreaName", "name"),
                 ("CityCode", "city")],
        fields=[
            Field("code", "AreaCODE", max_len=area.LIMITS["code"],
                  required=True),
            Field("name", "AreaNAME", max_len=area.LIMITS["name"],
                  required=True),
            Field("city", "CityCode (FK)", max_len=area.LIMITS["city"],
                  required=True),
        ],
        api=area,
        delete_guard=make_delete_guard("PYT"),
    )


def item_config() -> MasterConfig:
    return MasterConfig(
        title="Item Master (P2, F&B) - HMS_py",
        columns=[("Code", "code"), ("Name", "name"), ("Unit", "unit"),
                 ("Type", "type"), ("Rate", "rate")],
        fields=[
            Field("code", "Code", max_len=item.LIMITS["code"],
                  required=True),
            Field("name", "Name", max_len=item.LIMITS["name"],
                  required=True),
            Field("unit", "Unit", max_len=item.LIMITS["unit"]),
            Field("type", "Type", max_len=item.LIMITS["type"]),
            Field("group", "ItemGroup", max_len=item.LIMITS["group"]),
            Field("rate", "SaleRate", default="0"),
        ],
        api=item,
        delete_guard=make_delete_guard("PYT"),
    )


def acgroup_config() -> MasterConfig:
    return MasterConfig(
        title="Account Group Master (P2) - HMS_py",
        columns=[("GroupCode", "code"), ("GroupName", "name"),
                 ("A/L", "gnature"), ("Nature", "nature"),
                 ("ID", "id")],
        fields=[
            Field("code", "GroupCode", max_len=acgroup.LIMITS["code"],
                  required=True),
            Field("name", "GroupName", max_len=acgroup.LIMITS["name"],
                  required=True),
            Field("gnature", "GroupNature A/L", max_len=1),
            Field("nature", "Nature", max_len=acgroup.LIMITS["type"]),
        ],
        api=acgroup,
        delete_guard=make_delete_guard("PYT"),
    )


def venue_config() -> MasterConfig:
    return MasterConfig(
        title="Venue Master (P2, Banquet) - HMS_py",
        columns=[("Code", "code"), ("Name", "name"),
                 ("Capacity", "capacity"), ("Seating", "seating"),
                 ("Status", "status")],
        fields=[
            Field("code", "Code", max_len=venue.LIMITS["code"],
                  required=True),
            Field("name", "Name", max_len=venue.LIMITS["name"],
                  required=True),
            Field("short", "ShortName", max_len=venue.LIMITS["short"]),
            Field("capacity", "Capacity", max_len=venue.LIMITS["capacity"]),
            Field("seating", "Seating", default="0"),
            Field("floating", "Floating", default="0"),
            Field("status", "Status", max_len=venue.LIMITS["status"]),
        ],
        api=venue,
        delete_guard=make_delete_guard("PYT"),
    )


def depart_config() -> MasterConfig:
    return MasterConfig(
        title="Department/Outlet Master (P2, F&B) - HMS_py",
        columns=[("Code", "code"), ("Name", "name"),
                 ("KOT", "kotyn"), ("POS", "pos")],
        fields=[
            Field("code", "Code", max_len=depart.LIMITS["code"],
                  required=True),
            Field("name", "Name", max_len=depart.LIMITS["name"],
                  required=True),
            Field("kotyn", "KOT Y/N", max_len=1),
            Field("pos", "POS Y/N", max_len=1),
            Field("phone", "Phone", max_len=depart.LIMITS["phone"]),
        ],
        api=depart,
        delete_guard=make_delete_guard("PYT"),
    )


# ---- Main Setup completion (P2-c): Country/State/Charge/Unit ----

def country_config() -> MasterConfig:
    return MasterConfig(
        title="Country Master (P2-c) - HMS_py",
        columns=[("Code", "code"), ("Name", "name"), ("Short", "short"),
                 ("Type", "type"), ("Nationality", "nationality")],
        fields=[
            Field("code", "Code", max_len=country.LIMITS["code"],
                  required=True),
            Field("name", "Name", max_len=country.LIMITS["name"],
                  required=True),
            Field("short", "ShortName", max_len=country.LIMITS["short"]),
            Field("type", "Type (India/Foreign)",
                  max_len=country.LIMITS["type"]),
            Field("nationality", "Nationality",
                  max_len=country.LIMITS["nationality"]),
        ],
        api=country,
        delete_guard=make_delete_guard("PYT"),
    )


def state_config() -> MasterConfig:
    return MasterConfig(
        title="State Master (P2-c) - HMS_py",
        columns=[("Code", "code"), ("Name", "name"), ("Short", "short"),
                 ("Country", "country")],
        fields=[
            Field("code", "Code", max_len=state.LIMITS["code"],
                  required=True),
            Field("name", "Name", max_len=state.LIMITS["name"],
                  required=True),
            Field("short", "State No (Short)",
                  max_len=state.LIMITS["short"]),
            Field("country", "Country Code (FK)",
                  max_len=state.LIMITS["country"]),
        ],
        api=state,
        delete_guard=make_delete_guard("PYT"),
    )


def fixcharge_config() -> MasterConfig:
    return MasterConfig(
        title="Charge Master / Fixed Charge (P2-c) - HMS_py",
        columns=[("Code", "code"), ("Name", "name"), ("Rev", "revcode"),
                 ("TaxInc", "taxinc"), ("Rate", "flatrate")],
        fields=[
            Field("code", "Code", max_len=fixcharge.LIMITS["code"],
                  required=True),
            Field("name", "Name", max_len=fixcharge.LIMITS["name"],
                  required=True),
            Field("sname", "Short", max_len=fixcharge.LIMITS["sname"]),
            Field("revcode", "RevCode", max_len=fixcharge.LIMITS["revcode"]),
            Field("taxinc", "TaxInc Y/N", max_len=fixcharge.LIMITS["taxinc"]),
            Field("taxstru", "TaxStru", max_len=fixcharge.LIMITS["taxstru"]),
            Field("chargetype", "ChargeType",
                  max_len=fixcharge.LIMITS["chargetype"]),
            Field("flatrate", "FlatRate", default="0"),
        ],
        api=fixcharge,
        delete_guard=make_delete_guard("PYT"),
    )


def unit_config() -> MasterConfig:
    return MasterConfig(
        title="Unit Master (P2-c, POS) - HMS_py",
        columns=[("Unit", "code"), ("PriceType", "pricetype"),
                 ("Status", "status")],
        fields=[
            Field("code", "Unit Name", max_len=unit.LIMITS["code"],
                  required=True),
            Field("pricetype", "PriceType (0/1)", default="0"),
            Field("status", "Status", max_len=unit.LIMITS["status"]),
        ],
        api=unit,
        delete_guard=make_delete_guard("PYT"),
    )


# ---- shell.py registry helpers: ek-ek master dialog ke roop me kholo ----
def _open_dialog(cfg_fn, parent=None):
    BaseMasterForm(cfg_fn(), parent).exec()


def open_sundry(parent=None):
    _open_dialog(sundry_config, parent)


def open_narr(parent=None):
    _open_dialog(narr_config, parent)


def open_city(parent=None):
    _open_dialog(city_config, parent)


def open_area(parent=None):
    _open_dialog(area_config, parent)


def open_item(parent=None):
    _open_dialog(item_config, parent)


def open_acgroup(parent=None):
    _open_dialog(acgroup_config, parent)


def open_venue(parent=None):
    _open_dialog(venue_config, parent)


def open_depart(parent=None):
    _open_dialog(depart_config, parent)


def open_country(parent=None):
    _open_dialog(country_config, parent)


def open_state(parent=None):
    _open_dialog(state_config, parent)


def open_fixcharge(parent=None):
    _open_dialog(fixcharge_config, parent)


def open_unit(parent=None):
    _open_dialog(unit_config, parent)


# ---- Main Setup COMPLETE (P2-complete): Room Cat/Master, Package,
#      Season, Company Master, User Master ----

def roomcategory_config() -> MasterConfig:
    return MasterConfig(
        title="Room Category Master - HMS_py",
        columns=[("Code", "code"), ("Name", "name"), ("Short", "short"),
                 ("MaxPerson", "maxperson"), ("RevCode", "revcode")],
        fields=[
            Field("code", "CatCode", max_len=roomcategory.LIMITS["code"],
                  required=True),
            Field("name", "Category Name", max_len=roomcategory.LIMITS["name"],
                  required=True),
            Field("short", "Short Name", max_len=roomcategory.LIMITS["short"]),
            Field("maxperson", "Max Person", default="2"),
            Field("revcode", "Revenue Code",
                  max_len=roomcategory.LIMITS["revcode"]),
        ],
        api=roomcategory,
        delete_guard=make_delete_guard("PYT"),
    )


def roommaster_config() -> MasterConfig:
    return MasterConfig(
        title="Room Master - HMS_py",
        columns=[("RoomNo", "code"), ("Name", "name"), ("Category", "roomcat"),
                 ("RevCode", "revcode"), ("RoomStat", "roomstat")],
        fields=[
            Field("code", "Room No", max_len=roommaster.LIMITS["code"],
                  required=True),
            Field("name", "Room Name", max_len=roommaster.LIMITS["name"],
                  required=True),
            Field("roomcat", "Category Code (FK RoomCat)",
                  max_len=roommaster.LIMITS["roomcat"]),
            Field("revcode", "Revenue Code",
                  max_len=roommaster.LIMITS["revcode"]),
            Field("taxstru", "Tax Structure",
                  max_len=roommaster.LIMITS["taxstru"]),
            Field("roomstat", "Room Stat",
                  max_len=1, default=""),
        ],
        api=roommaster,
        delete_guard=make_delete_guard("PYT"),
    )


def packagemaster_config() -> MasterConfig:
    return MasterConfig(
        title="Package Master - HMS_py",
        columns=[("Code", "code"), ("Name", "name"),
                 ("Rate", "rate"), ("Active", "active")],
        fields=[
            Field("code", "Pack Code", max_len=packagemaster.LIMITS.get("code", 5),
                  required=True),
            Field("name", "Pack Name", max_len=packagemaster.LIMITS.get("name", 25),
                  required=True),
            Field("validfrom", "Valid From (YYYY-MM-DD)"),
            Field("validto", "Valid To (YYYY-MM-DD)"),
            Field("rate", "Rate", default="0"),
            Field("desc", "Description", max_len=255),
            Field("active", "Active Y/N", max_len=1, default="Y"),
        ],
        api=packagemaster,
        delete_guard=make_delete_guard("PYT"),
    )


def seasonmaster_config() -> MasterConfig:
    return MasterConfig(
        title="Season Master - HMS_py",
        columns=[("Code", "code"), ("Name", "name"),
                 ("From", "fromdate"), ("To", "todate"), ("Active", "active")],
        fields=[
            Field("code", "Season Code",
                  max_len=seasonmaster.LIMITS.get("ratecode", 2),
                  required=True),
            Field("name", "Season Name", max_len=30),
            Field("fromdate", "From Date (YYYY-MM-DD)"),
            Field("todate", "To Date (YYYY-MM-DD)"),
            Field("active", "Active Y/N", max_len=1, default="Y"),
        ],
        api=seasonmaster,
        delete_guard=make_delete_guard("PYT"),
    )


def companymaster_config() -> MasterConfig:
    return MasterConfig(
        title="Company Master (Corporate Clients) - HMS_py",
        columns=[("Code", "code"), ("Name", "name"), ("City", "city"),
                 ("Phone", "phone"), ("Contact", "contact"),
                 ("Active", "active")],
        fields=[
            Field("code", "Comp Code", max_len=companymaster.LIMITS.get("code", 8),
                  required=True),
            Field("name", "Company Name", max_len=companymaster.LIMITS.get("name", 50),
                  required=True),
            Field("add1", "Address 1", max_len=companymaster.LIMITS.get("add1", 50)),
            Field("add2", "Address 2", max_len=companymaster.LIMITS.get("add2", 50)),
            Field("city", "City Code", max_len=companymaster.LIMITS.get("city", 6)),
            Field("phone", "Phone", max_len=companymaster.LIMITS.get("phone", 35)),
            Field("contact", "Contact Person",
                  max_len=companymaster.LIMITS.get("contact", 35)),
            Field("creditdays", "Credit Days", default="0"),
            Field("creditlimit", "Credit Limit", default="0"),
            Field("active", "Active Y/N", max_len=1, default="Y"),
        ],
        api=companymaster,
        delete_guard=make_delete_guard("PYT"),
    )


def open_roomcategory(parent=None):
    _open_dialog(roomcategory_config, parent)


def open_roommaster(parent=None):
    _open_dialog(roommaster_config, parent)


def open_packagemaster(parent=None):
    _open_dialog(packagemaster_config, parent)


def open_seasonmaster(parent=None):
    _open_dialog(seasonmaster_config, parent)


def open_companymaster(parent=None):
    _open_dialog(companymaster_config, parent)


def open_usermaster(parent=None, current_user: str = "SA"):
    """User Master - special UI (password field hai)."""
    from HMS_py.ui.usermaster_ui import UserMasterForm
    UserMasterForm(parent, current_user=current_user).exec()


class P2Launcher(QMainWindow):
    """Sab masters ek window se - VB6 menu jaisa."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HMS_py - All Masters")
        self.resize(440, 600)
        central = QWidget()
        lay = QVBoxLayout(central)
        for label, fn in (
            ("Sundry Master", open_sundry),
            ("Narration Master", open_narr),
            ("City Master", open_city),
            ("Area Master", open_area),
            ("Item Master (F&B)", open_item),
            ("Account Group Master", open_acgroup),
            ("Venue Master (Banquet)", open_venue),
            ("Department/Outlet (F&B)", open_depart),
            ("Country Master", open_country),
            ("State Master", open_state),
            ("Charge Master (Fixed)", open_fixcharge),
            ("Unit Master (POS)", open_unit),
            # Main Setup Complete (P2-complete):
            ("Room Category Master", open_roomcategory),
            ("Room Master", open_roommaster),
            ("Package Master", open_packagemaster),
            ("Season Master", open_seasonmaster),
            ("Company Master (Corporate)", open_companymaster),
            ("User Master", open_usermaster),
        ):
            b = QPushButton(label)
            b.clicked.connect(fn)
            lay.addWidget(b)
        self.setCentralWidget(central)


def main() -> int:
    app = QApplication(sys.argv)
    win = P2Launcher()
    win.show()
    shot = os.environ.get("HMS_POC_SHOT")
    if shot:
        from PyQt6.QtTest import QTest
        QTest.qWait(500)
        win.grab().save(os.path.splitext(shot)[0] + "_launcher.png")
        for tag, cfg_fn in (("sundry", sundry_config),
                            ("city", city_config),
                            ("item", item_config),
                            ("acgroup", acgroup_config),
                            ("venue", venue_config),
                            ("depart", depart_config)):
            f = BaseMasterForm(cfg_fn())
            f.show()
            QTest.qWait(500)
            p2 = os.path.splitext(shot)[0] + "_" + tag + ".png"
            f.grab().save(p2)
            print("screenshot:", p2, "| rows:", f.tbl.rowCount())
        return 0
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
