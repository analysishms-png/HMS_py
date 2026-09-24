"""General Setup (VB6: Main Setup -> General Setup).

Database evidence (live HMS):
- Voucher_Type: Voucher type master - EXISTS (37 cols)
  Used as: Payment Type config + voucher series setup
  Key cols: V_Type varchar(10) PK, Category varchar(10), Description varchar(50),
  Number_Method varchar(20), Start_No int, Site_Code, U_NAME, U_EntDt, U_AE
- Enviro: System environment settings - EXISTS
  Key cols: Cash_Ac, DiscountAc, RoundOffAc, etc. (single-row config)
- RoomFeature: Room amenity features - EXISTS
  Schema: Code varchar(6) PK, Name varchar(30),
  Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code
- GodownMast: Inventory locations (used in General Setup Utility) - EXISTS
  Schema: Code varchar(6) PK, Name varchar(30), ShortName varchar(6),
  DepartCode varchar(6), SysYn varchar(1),
  Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code

NOTE: Parameter/HMSParam/RevGroup/PrintParam/RevenueGroup tables do NOT
exist in this DB. GuestParam exists as a configuration table.
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()

# ============================================================
# Enviro allowlist - editable operational flags only
# Financial fields are READ-ONLY (protected)
# ============================================================
ENVIRO_EDITABLE_FIELDS = frozenset({
    # Printing / KOT / POS operational flags
    "KOTPrinting", "KOTAtNightAudit", "POSBillAtNightAudit", "KOTOutletSelection",
    "KOTPrintEdited", "AutoPrintKOTYN", "AutoFillItemInKitchenClosingYN",
    "TOKENPrint", "RcptPrinting", "ReservationPrinting",
    "BillPrintingSummerised", "FomBillCopies",
    "POSSaleBillModification", "POSSaleBillEditLog", "POSBillCalcType",
    "POSSaleRevenueBifercation", "PostPOSDiscSeparately",
    "HideSettledBillsOnSaleBillYN", "ReprintingOnSaleBillYN",
    # Checkout / Settlement flags
    "Checkout", "CheckoutVar", "Variation", "VariationBefore",
    "RoomCheckOutClearanceYN", "RoomCheckInClearanceYN",
    "AllowRoomSettlement", "SplitYN", "PostComplimentaryBills",
    "PostNilLT", "AllowBillOnHoldSettlement",
    "PostRoomDiscSeparately", "IncCashPurchInFOCC",
    "RoomRentBefChkOut", "RoomRentChkOutPost",
    # Room rate editable flags
    "RoomRateEditable", "RoomIncTaxEditable", "RoomServiceChargeEditable",
    "RateEditableInPO", "RateEditableInStockIssue",
    # Tax / VAT settings
    "PurchaseTaxVAT", "SaleTaxVAT", "ExciseInvoiceTaxStru",
    "PostPOSDiscSeparately",
    # KOT / Kitchen settings
    "FreeItemInKOT", "NCKOTPercentage", "ResetTokenAtNightAudit",
    "KOTHeader1", "KOTHeader2", "KOTHeader3", "KOTHeader4",
    # Banquet / Catering
    "OutDoorCatering", "BanquetKitchen",
    # Display / UI settings
    "DisplayRackRow", "DisplayRackCol", "DisplayRackFontSize",
    "DisplayPort", "DisplayMode", "menuX", "menuY", "menuDISP",
    "ShowTitleBar", "ShowMenuBar", "ShowSubMenuBar", "ShowShortCutsBar",
    # Reservation settings
    "ArrDateTimeEdit", "ReservationExpandOnSaveYN",
    "IncReservationInBlankGRC", "SeperateReservationLetterAsPerStatusYN",
    "NewTarrifForOldGuest", "BlockInvalidTarrifIncTaxYN",
    "ResInstruction1", "ResInstruction2", "ResInstruction3", "ResInstruction4",
    "ResInstruction5", "ResInstruction6", "ResInstruction7", "ResInstruction8",
    "ResInstruction9", "ResInstruction10", "ResInstruction11", "ResInstruction12",
    # Guest / Mobile settings
    "SMSMessaging", "SMSOption", "MobileNo", "MobileSet", "SMSMessage",
    "MobileInfoMandatoryYN", "CoversMandatory", "MobileNoMandatory",
    "PANNOMandatoryYN",
    # Purchase / Stock settings
    "ImportOptionInPurchase", "ReqCompWise", "BarCodeFeatureInPurchase",
    "SmartPurchaseOrder", "NegativeStockAllowYN",
    "PurchaseGodown", "StockRecGodown",
    # Cash Card settings
    "CashCardApplYN", "CashCardInfoMandatoryYN", "CashCardDebitAc",
    "CashCardCreditAc", "CashCardSecurityAc",
    # Smart Card
    "SMARTCARDRECIEPTPrintingDW",
    # Other operational
    "Editopen", "AcFieldAlterable", "AddModifyEntryInBackDate",
    "PlanSelectionBasedOn", "PlanTariffNarration",
    "GuestChargesDeleteLog", "FOMBillReprintAutoRefresh",
    "UserWiseShowOutletYN",
})


ENVIRO_FINANCE_FIELDS = frozenset({
    # All financial account codes - READ ONLY
    "Cash_Ac", "DiscountAc", "RoundOffAc", "CommAC", "SALARY_AC",
    "Loan_AC", "AdvanceAc", "WagesAc", "LessFreightAc",
    "OutletDiscAc", "OutletRoundAc", "CommissionAc",
    "RoomChrgDueAc", "RoomTaxDueAc", "HallDiscAC", "HallRoundOff",
    "CashPurchAc", "CancellationAC", "BookingPartyAc",
    "CashPayType", "RoomPayType", "OutletDiscAc", "OutletRoundAc",
    "OutdoorSaleAC", "IndoorSaleAC", "OutdoorPartyAC", "IndoorPartyAC",
    "DummyTravelAc", "CatalogLimit", "BookingPartyAc",
    "CashCardDebitAc", "CashCardCreditAc", "CashCardSecurityAc",
    # Payroll / HR
    "PF_LIMIT", "PF_EMPLOYEE", "PF_EMPLOYER", "ESI_LIMIT",
    "esi_employee", "ESIBasic", "ESIDA", "ESIHRA", "ESIConvey",
    "ESIOther", "ESILTA",
    # Tax / VAT structure
    "TaxSummary", "SaleTaxVAT", "PurchaseTaxVAT",
    "ExciseInvoiceTaxStru",
    # Advance / Imprest
    "ImprestAmount", "AdvanceRRoomRent",
    # General ledger
    "Postingtype", "calcMethod", "NCUR",
    "SiteCode", "GAppCompYear", "GMonthConsidered",
    "GWorkingDaysInAMonth", "GDaysSalary",
    "AttendType", "PlanMastType", "PlanCalc", "PlanTariffNarration",
    "PlanSelectionBasedOn",
    # System
    "LogSite_Code", "U_AE_FOMBillSetE",
    "DTCPETakeEffectHeadToSite",
    "HTWCurDateEdit",
    "ServiceTaxOnServiceChargeYN",
    "CreditCardInfoMandatoryYN",
    "ExpMfdDateInMR",
    "BarCodeFeatureInPurchase",
    "RevenueGroupModule", "MemberShipModule",
    "HotelLogo", "PurchaseAdd1", "PurchaseDed1", "PurchaseAdd2", "PurchaseDed2",
    "SundryPassword", "Rate1", "Rate2", "Rate3", "Rate4", "Rate5",
    "DefCompGroup", "DefaultCrAc", "DefaultDrAc",
})


# ============================================================
# Room Feature Master (Main Setup -> FO -> Room Features)
# ============================================================
ROOMFEAT_LIMITS = {"code": 5, "name": 25}
ROOMFEAT_COLS = "Code, Name, U_Name, U_EntDt, U_AE"


def _map_roomfeat(r) -> dict:
    try:
        return {"code": r.Code, "name": (r.Name or "").strip(),
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        c, n, un, _, uae = r
        return {"code": c, "name": (n or "").strip(),
                "u_name": un or "", "u_ae": uae or ""}


def roomfeat_list(cn=None) -> list[dict]:
    return [_map_roomfeat(r) for r in db.query(
        f"SELECT {ROOMFEAT_COLS} FROM RoomFeature ORDER BY Code", cn=cn)]


def roomfeat_get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {ROOMFEAT_COLS} FROM RoomFeature WHERE Code = ?", (code,), cn=cn)
    return _map_roomfeat(rows[0]) if rows else None


def roomfeat_exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM RoomFeature WHERE Code = ?", (code,), cn=cn))


def roomfeat_insert(rec: dict, cn=None, commit=True) -> int:
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    db.require_absent("RoomFeature", "Code", rec["code"], "Room Feature Code")
    return db.execute(
        "INSERT INTO RoomFeature (Code, Name, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"], SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def roomfeat_update(code: str, rec: dict, cn=None, commit=True) -> int:
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "UPDATE RoomFeature SET Name = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec["name"], USER, code), cn=cn, commit=commit)


def roomfeat_delete(code: str, cn=None, commit=True) -> int:
    return db.execute(
        "DELETE FROM RoomFeature WHERE Code = ?", (code,), cn=cn, commit=commit)


class _RoomFeatAPI:
    LIMITS = ROOMFEAT_LIMITS

    @staticmethod
    def list_all(cn=None): return roomfeat_list(cn)

    @staticmethod
    def get(code, cn=None): return roomfeat_get(code, cn)

    @staticmethod
    def exists(code, cn=None): return roomfeat_exists(code, cn)

    @staticmethod
    def insert(rec, cn=None, commit=True): return roomfeat_insert(rec, cn, commit)

    @staticmethod
    def update(code, rec, cn=None, commit=True): return roomfeat_update(code, rec, cn, commit)

    @staticmethod
    def delete(code, cn=None, commit=True): return roomfeat_delete(code, cn, commit)


RoomFeatAPI = _RoomFeatAPI()


# ============================================================
# Godown / Location Master (Inventory locations)
# ============================================================
GODOWN_LIMITS = {"code": 6, "name": 30, "short": 6, "dept": 6}
GODOWN_COLS = "Code, Name, ShortName, DepartCode, SysYn, U_Name, U_EntDt, U_AE"


def _map_godown(r) -> dict:
    try:
        return {"code": r.Code, "name": (r.Name or "").strip(),
                "short": (r.ShortName or "").strip(),
                "dept": r.DepartCode or "", "sysyn": r.SysYn or "N",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        c, n, sn, dc, sy, un, _, uae = r
        return {"code": c, "name": (n or "").strip(), "short": (sn or "").strip(),
                "dept": dc or "", "sysyn": sy or "N",
                "u_name": un or "", "u_ae": uae or ""}


def godown_list(cn=None) -> list[dict]:
    return [_map_godown(r) for r in db.query(
        f"SELECT {GODOWN_COLS} FROM GodownMast ORDER BY Code", cn=cn)]


def godown_get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {GODOWN_COLS} FROM GodownMast WHERE Code = ?", (code,), cn=cn)
    return _map_godown(rows[0]) if rows else None


def godown_exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM GodownMast WHERE Code = ?", (code,), cn=cn))


def godown_insert(rec: dict, cn=None, commit=True) -> int:
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    db.require_absent("GodownMast", "Code", rec["code"], "Godown Code")
    return db.execute(
        "INSERT INTO GodownMast (Code, Name, ShortName, DepartCode, SysYn, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"], rec.get("short", ""),
         rec.get("dept", ""), rec.get("sysyn", "N"),
         SITE_CODE, USER, SITE_CODE), cn=cn, commit=commit)


def godown_update(code: str, rec: dict, cn=None, commit=True) -> int:
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    return db.execute(
        "UPDATE GodownMast SET Name = ?, ShortName = ?, DepartCode = ?, "
        "SysYn = ?, U_Name = ?, U_EntDt = getdate(), U_AE = 'E' "
        "WHERE Code = ?",
        (rec["name"], rec.get("short", ""), rec.get("dept", ""),
         rec.get("sysyn", "N"), USER, code), cn=cn, commit=commit)


def godown_delete(code: str, cn=None, commit=True) -> int:
    rows = db.query("SELECT SysYn FROM GodownMast WHERE Code = ?", (code,), cn=cn)
    if rows and str(rows[0][0] or "").upper() == "Y":
        raise ValueError(f"'{code}' system godown hai - delete nahi hota")
    return db.execute(
        "DELETE FROM GodownMast WHERE Code = ?", (code,), cn=cn, commit=commit)


class _GodownAPI:
    LIMITS = GODOWN_LIMITS

    @staticmethod
    def list_all(cn=None): return godown_list(cn)

    @staticmethod
    def get(code, cn=None): return godown_get(code, cn)

    @staticmethod
    def exists(code, cn=None): return godown_exists(code, cn)

    @staticmethod
    def insert(rec, cn=None, commit=True): return godown_insert(rec, cn, commit)

    @staticmethod
    def update(code, rec, cn=None, commit=True): return godown_update(code, rec, cn, commit)

    @staticmethod
    def delete(code, cn=None, commit=True): return godown_delete(code, cn, commit)


GodownAPI = _GodownAPI()


# ============================================================
# Voucher Type browser (read-only - config table, no user edits)
# ============================================================
def voucher_type_list(cn=None) -> list[dict]:
    """Voucher_Type table browse (VB6 General Setup -> Voucher Environment)."""
    rows = db.query(
        "SELECT V_Type, Category, Description, Number_Method, Start_No, "
        "Short_Name, Site_Code, U_NAME, U_EntDt, U_AE "
        "FROM Voucher_Type ORDER BY Category, V_Type", cn=cn)
    out = []
    for r in rows:
        try:
            out.append({
                "vtype": r.V_Type or "", "category": r.Category or "",
                "desc": (r.Description or "").strip(),
                "method": r.Number_Method or "",
                "startno": r.Start_No or 1,
                "short": (r.Short_Name or "").strip(),
                "u_name": r.U_NAME or "", "u_ae": r.U_AE or "",
            })
        except AttributeError:
            vt, cat, desc, mth, sno, sh, _, un, _, uae = r
            out.append({
                "vtype": vt or "", "category": cat or "",
                "desc": (desc or "").strip(), "method": mth or "",
                "startno": sno or 1, "short": (sh or "").strip(),
                "u_name": un or "", "u_ae": uae or "",
            })
    return out


def printing_settings_snapshot(cn=None) -> dict:
    """VB6-style printing settings snapshot for Main Setup -> Printing Setup.

    Source of truth:
    - Analysis.ini keys 2/3/4 = Reports/Temp/Printer path
    - Enviro row = operational flags like KOTPrinting, RcptPrinting,
      ReservationPrinting, etc.
    """
    cfg = db.load_config()
    keys = (
        "Bill_Header", "Bill_Footer", "KOTPrinting", "KOTPrintEdited",
        "TOKENPrint", "RcptPrinting", "ReservationPrinting",
        "KOTOutletSelection", "TaxSummary", "BillPrintingSummerised",
        "FomBillCopies", "POSBillAtNightAudit", "KOTAtNightAudit",
        "NoShowAtNightAudit", "Checkout", "CheckoutVar", "Variation",
        "AllowRoomSettlement", "SplitYN", "RoomRateEditable"
    )
    env = {}
    for k in keys:
        try:
            rows = db.query(
                f"SELECT [{k}] FROM Enviro WHERE LogSite_Code = ? OR LogSite_Code = 'HO'",
                (SITE_CODE,), cn=cn
            )
            if rows:
                env[k] = rows[0][0]
            else:
                env[k] = None
        except Exception:
            env[k] = None
    return {
        "reports": cfg.get("reports") or "",
        "temp": cfg.get("temp") or "",
        "printer": cfg.get("printer") or "Prn",
        "site": cfg.get("site") or SITE_CODE,
        "company": cfg.get("company") or "KK",
        "enviro": env,
    }


def enviro_update(field: str, value: str, cn=None, commit: bool = True) -> int:
    """Update a single Enviro field (operational flags only)."""
    if field not in ENVIRO_EDITABLE_FIELDS:
        raise ValueError(f"Field '{field}' is not editable (protected finance field)")
    return db.execute(
        f"UPDATE Enviro SET [{field}] = ?, U_Name = ?, U_EntDt = getdate(), U_AE = 'E' "
        f"WHERE LogSite_Code = ? OR LogSite_Code = 'HO'",
        (value, USER, SITE_CODE), cn=cn, commit=commit)


def enviro_get(field: str, cn=None) -> str | None:
    """Get a single Enviro field value."""
    try:
        rows = db.query(
            f"SELECT [{field}] FROM Enviro WHERE LogSite_Code = ? OR LogSite_Code = 'HO'",
            (SITE_CODE,), cn=cn
        )
        return rows[0][0] if rows else None
    except Exception:
        return None


# ============================================================
# Voucher Category Master
# Table: VoucherCat - Category varchar PK, NCat varchar,
#        Site_Code, LogSite_Code (NO audit cols: no U_Name/U_EntDt/U_AE)
# ============================================================
VOUCHCAT_LIMITS = {"category": 10, "ncat": 10}
VOUCHCAT_COLS = "Category, NCat, Site_Code"


def _map_vouchcat(r) -> dict:
    try:
        return {"category": r.Category, "ncat": (r.NCat or "").strip(),
                "site": r.Site_Code or ""}
    except AttributeError:
        c, nc, sc = r
        return {"category": c, "ncat": (nc or "").strip(),
                "site": sc or ""}


def vouchcat_list(cn=None) -> list[dict]:
    return [_map_vouchcat(r) for r in db.query(
        f"SELECT {VOUCHCAT_COLS} FROM VoucherCat ORDER BY Category", cn=cn)]


def vouchcat_get(code: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {VOUCHCAT_COLS} FROM VoucherCat WHERE Category = ?",
        (code,), cn=cn)
    return _map_vouchcat(rows[0]) if rows else None


def vouchcat_exists(code: str, cn=None) -> bool:
    return bool(db.query(
        "SELECT 1 FROM VoucherCat WHERE Category = ?", (code,), cn=cn))


def vouchcat_insert(rec: dict, cn=None, commit=True) -> int:
    if not rec.get("category", "").strip():
        raise ValueError("Category zaroori hai")
    db.require_absent("VoucherCat", "Category", rec["category"], "Voucher Category")
    return db.execute(
        "INSERT INTO VoucherCat (Category, NCat, Site_Code, LogSite_Code) "
        "VALUES (?, ?, ?, ?)",
        (rec["category"], rec.get("ncat", ""),
         SITE_CODE, SITE_CODE), cn=cn, commit=commit)


def vouchcat_update(code: str, rec: dict, cn=None, commit=True) -> int:
    return db.execute(
        "UPDATE VoucherCat SET NCat = ? WHERE Category = ?",
        (rec.get("ncat", ""), code), cn=cn, commit=commit)


def vouchcat_delete(code: str, cn=None, commit=True) -> int:
    return db.execute(
        "DELETE FROM VoucherCat WHERE Category = ?", (code,),
        cn=cn, commit=commit)


class _VouchCatAPI:
    LIMITS = VOUCHCAT_LIMITS
    @staticmethod
    def list_all(cn=None): return vouchcat_list(cn)
    @staticmethod
    def get(code, cn=None): return vouchcat_get(code, cn)
    @staticmethod
    def exists(code, cn=None): return vouchcat_exists(code, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return vouchcat_insert(rec, cn, commit)
    @staticmethod
    def update(code, rec, cn=None, commit=True): return vouchcat_update(code, rec, cn, commit)
    @staticmethod
    def delete(code, cn=None, commit=True): return vouchcat_delete(code, cn, commit)

VouchCatAPI = _VouchCatAPI()