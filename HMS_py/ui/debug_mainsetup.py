# -*- coding: utf-8 -*-
"""Debug MainSetup comparison"""
import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from HMS_py.core import menu_help as _mh
from HMS_py.ui.shell import _form_registry, MainSetupWorkbench
from HMS_py.ui import sidebar_buttons as _sb

# VB6 MDI MainSetup groups from mdi_menu.json
vb6_menus = {
    "General Setup": [
        "Tax Master", "Tax Structure", "Payment Type", "Parameter",
        "Revenue Group Setting", "Printing Parameters", "Printing Setup",
        "Revenue Wise Budget Entry",
    ],
    "Front Office": [
        "Country Master", "State Master", "City Master", "Market Segment",
        "Business Source", "Guest Status", "Charge Master", "Fixed Charge",
        "Package Master", "Plan Master", "Season Master", "Room Features",
        "Room Category", "Room Master", "Company Master", "Forex Master",
        "Guest History", "Group Profile", "Room Display",
    ],
    "Point of Sale": [
        "Setup Outlet", "Outlet Bill Sundry Setting", "Server Master",
        "Table Master", "Item List", "Menu Group", "Menu Category",
        "Menu Item", "Menu Item Rate", "Rate Group Master", "Session Master",
        "Open Item Consumption", "Scheme Master", "Happy Hours",
        "Happy Hours [ Free Items ]", "Combo Pack", "NC Type",
        "Customer History", "Delivery Boy",
    ],
    "Members Mgmt": [
        "Category Master", "Member Master", "Corporate Member Master",
        "Revenue Master", "Facility Master", "Category wise Revenue",
        "Category wise Facility", "Member Bill Sundry Setting",
        "Environment Settings", "Member Age Wise Revenue",
        "Member Select Category",
    ],
    "Banquet": [
        "Events", "Venue Features", "Venue Master", "Menu Category",
        "Item Group", "Menu Item", "Catalog Master",
        "Banquet Bill Sundry Setting",
    ],
    "Inventory": [
        "Party Master", "Department", "Item Group", "Item Category",
        "Item Entry ", "Consumption Master", "Purchase Sundry Setting",
        "Location Master", "Opening Stock", "Item List", "Shift Master",
        "Enviro Inventry",
    ],
    "HR/Payroll": [
        "Designation Master", "Category  Master", "Holiday Master",
        "Employee Master",
    ],
    "EPABX": [
        "Com Port Properties", "Call Type Master", "Extension Master",
        "Call Codes Master", "Call Control Master",
        "Call Code", "Extension",
    ],
    "Finance": [
        "Group Accounts", "Ledger Accounts", "Narration Master",
        "T.D.S. Category", "FA Environment", "Voucher Environment",
        "Opening Balance Updation", "Year End Updation",
        "Current Balance Updation", "Country Master", "State Master",
        "City Master", "Delete Message", "Account Merging",
        "Voucher Serialisation",
    ],
    "Utility": [
        "User Master", "Permissions", "Update Database Nulls",
        "Backup Data", "Account Merging", "Guest Parameters Setting",
        "Sundry Master", "Voucher Wise Sundry Entry",
        "Sale MIS Customized", "Guest BirthDates/Anniversary",
        "Inconsistency Check", "Year End Updation", "Data Transfer",
        "Data Recieving", "Menu Item Copy", "POS Bill Deletion",
        "Guest LookUp", "Country Master", "State Master", "City Master",
        "Company Master", "Department", "Ledger Accounts",
        "Data Transfer (POS)", "PLU File (W.Scale)",
        "User Permissions (Advanced)", "POS Recycle", "Unit Master",
        "Task Scheduler",
    ],
}

print("=" * 70)
print("VB6 MDI vs _form_registry vs MainSetupWorkbench DEBUG")
print("=" * 70)

# Get registry keys - _form_registry() returns dict
try:
    _reg = _form_registry()
    registry_keys = set(_reg.keys())
except Exception:
    # If _form_registry fails, use known keys from shell.py
    registry_keys = {
        "Main Setup", "Guest Profile", "Check In", "Check-In", "Checkin",
        "KOT Entry", "POS Status", "Sales Register", "Item wise Sale", "Log",
        "Night Audit Log", "Daily Report", "Occupancy Analysis",
        "Guest Audit Ledger", "Plan Master",
        "City Master", "Country Master", "State Master", "Area Master",
        "Room Category", "Room Master", "Package Master", "Season Master",
        "Company Master", "Charge Master", "Fixed Charge", "Unit Master",
        "Item Master", "Sundry Master", "Narration Master", "Venue Master",
        "Department", "Department/Outlet", "Reservation/Cancellation",
        "User Master", "Permissions", "User Permissions (Advanced)",
        "Check Out", "Reverse Check Out", "Room Status",
        "House Keeping Screen", "Expense Entry", "Tax Master",
        "Payment Type", "Market Segment", "Business Source", "Guest Status",
        "Forex Master", "Ledger Accounts", "Group Accounts",
        "Session Master", "Scheme Master", "Delivery Boy",
        "Item List", "Menu Category", "Venue Features", "Catalog Master",
        "Group Profile", "NC Type", "Server / Waiter", "Shift Master",
        "Combo Pack", "Smart Card", "Function Type", "Call Type",
        "Call Code", "Extension", "Category Master", "Holiday Master",
        "Employee Master", "Designation", "Facility Master",
        "Revenue Master", "Room Features", "Godown Master",
        "Voucher Environment", "FA Environment", "Guest Parameters Setting",
        "Voucher Category", "Auto Settle Card Balance",
        "Indent", "Stock Summary", "Stock Register",
        "Stock Register Detailed", "GIN / Purchase Receipt",
        "Purchase Order", "Purchase Bill", "Stock Transfer",
        "eInvoice Config", "Kitchen Stock Report",
        "Stock Issue", "Stock Receive", "Stock Adjustment",
        "Purchase Register", "Folio Log", "Amend Departure",
        "Payment Receive Entry", "Receive Payment",
        "Tax Structure", "Printing Parameters", "Printing Setup",
        "Revenue Group Setting", "Guest History", "Room Display",
        "Update Database Nulls", "Booking Inquiry",
        "Location Facilities", "Reservation Status Report",
        "Advance Recd. Report", "M.I.S.",
        "Operations", "Reports", "Tourism Forms", "M.I.S.",
        "Tax Reports", "Complaint Master", "Complaint Clearance",
        "Lost / Found Entry", "Claim Entry", "Room Block",
        "Gravy Item Entry", "Indent", "Purchase Order", "M.R. Entry",
        "Purchase Bill", "Requisition Slip", "Stock Issue on Requisition",
        "Kitchen Closing Stock", "Stock Transfer",
        "Excise Invoice Cum Gate Pass", "Pending Indent",
        "Pending M.R.", "Pending Purchase Order",
        "Purchase Register", "Purchase Summary", "Cash/Credit Purchase",
        "Stock Register", "Stock Summary", "Stock In Hand",
        "Kitchen Stock Report I/R Basis", "Excess Consumption Report",
        "Restaurant Issue Report", "Store Issue Register",
        "Change Kitchen/Store", "Daily Store Issue Reports",
        "Purchase Ledger", "Issue CheckList", "Stock Summary P/S Basis",
        "ABC Analysis", "Production Report I/R Basis",
        "Store Issue Report", "Liquor Sale Report",
        "VAT Register", "VAT Register II", "VAT Register III",
        "Form24 Annexure-A", "Form III", "UPVAT XXIV",
        "Sales Register", "Stewardwise Sale", "Table wise Sale",
        "Settlement Summary", "KOT Wise Details",
        "Discount Register", "Cover Analysis", "Pending KOT",
        "Item wise Sale", "Deleted Unsettled Bill", "NC KOT Detail",
        "Sales Day Book", "Order Detail Report", "NC KOT Summary",
        "Daily DIET Report", "Not Delivered Order", "Group Wise Sale",
        "Denomination Detail", "Payment Receive Entry (POS)",
        "Collection Summary", "Open Item Sales", "KOT Change Report",
        "Monthwise Sales", "ABC Analysis", "Sale Summary",
        "Taxwise Details", "Group Pickup Report", "Group Arrival Report",
        "Arrival List", "23 Day Room Availability Forecast",
        "23 Day Room Type Availability Forecast",
        "Cover Analysis Report", "OutStanding Report",
        "Party wise OutStanding", "Bill Wise Outstanding Report For Debtors",
        "Excess Consumption Report", "Restaurant Issue Report",
        "Stock Summary P/S Basis", "ABC Analysis",
        "Production Report I/R Basis", "Issue CheckList",
        "Stock Summary ", "Stock Register ", "Stock In Hand ",
        "Kitchen Stock Report I/R Basis", "Change Kitchen/Store",
        "Form24 Annexure-A", "UPVAT XXIV", "Room Status Report",
        "Settlement  Report", "Banquet Taxwise Details",
        "Taxwise Details (Banquet)", "Charge Payment Detail",
        "Room Wise Plan Detail", "Bill Change Report",
        "Guest Extra Charges", "Sales Report", "Guest Payments",
        "FOM Tax Detail", "Tax Wise Charge Detail",
        "Tourism Form 1", "Tourism Form 2", "Tourism Form 5",
        "Tourism Form 6", "Tourism Form 4", "Monthly Return",
        "L.T. FORM II", "L.T. FORM IV", "Room Occupancy",
        "Attendance Report", "Form C", "F&&B Cost Statement",
        "Night Audit Process", "Night Audit Control Panel",
        "Reverse Night Audit", "Charges Posting", "Account Posting",
        "Bill Reprint", "Merge Room", "Bill Re-Settlement",
        "Look Up Rooms", "Look Up Room types", "POS Bill Reprint",
        "Split Sale Bill", "Table Change Entry", "KOT Transfer",
        "Room Change", "Ledger Adjustment", "Adjustment Deletion",
        "Cheque Clearing", "TDS Certificate", "Guest LookUp",
        "Registration Entry", "Guest Registration", "M.R. Entry",
        "Tally Export(XML)", "Tally Interface", "Opening Stock",
        "Scheme Master", "Happy Hours", "Happy Hours [ Free Items ]",
        "T.D.S. Category", "Adjustment Entry", "Bank Reconciliation",
        "T.D.S. Challan Entry", "T.D.S. Certificate Entry",
        "Expense Voucher", "Opening Balance Updation",
        "Year End Updation", "Current Balance Updation",
        "Balance Sheet", "Profit And Loss Account",
        "Trial Balance (Group)", "Trial Ledger", "Cash Flow",
        "Fund Flow", "Cash And Bank Books", "Trial Balance",
        "Interest Ledger", "Journal Books", "Bank Register",
        "Cheque Cleared Register", "Cheque Not Cleared Register",
        "Daily Transaction Summary", "Control Ledger",
        "Booking Operations", "Hall Booking", "HR Payroll",
        "Member Billing", "Guest Services", "Facility Billing",
        "POS Sales", "POS Stock", "POS Delivery", "POS Happy Hours",
        "POS Table", "POS Packing", "Finance Ledger", "Voucher Entry",
        "System Config", "Backup Data",
        "Reservation Status", "Reservation Status Arrival",
        "Reservation Status In-House", "Advance Recd.",
        "7-730 Days Forecast", "23 Day Room Availability Forecast",
        "Package Forecast ",
        "Occupancy Display", "Guest wise Analysis", "Company wise Analysis",
        "Guestwise Charges Detail", "Room Occupancy",
        "Room Type Occupancy", "Room Wise Room Revenue",
        "Occupancy Analysis", "Company wise Nights",
        "Revenue During the stay", "Room Type Occupancy Analysis",
        "Plan Report", "Business Source Occupancy Analysis",
        "Instant House Count ", "Room Inventory", "Guest In House",
        "House Keeping Report", "Arrival & Departure List",
        "Charge Payment Detail", "Payments By Cashier",
        "Cashier Report ", "Settlement Report", "Cancel Bill Details",
        "Room Change History", "Arrival And Departure Register",
        "FOM Sales Register", "Room Wise Plan Detail",
        "Expected Plan/Package F&&B Details", "Occupancy Report",
        "Bill Change Report", "Check Out Register", "Check In Register",
        "Expected Check Out", "Guest Bill Details", "Guest Extra Charges",
        "Checked In Guest Detail", "Room Rent Audit Report",
        "Sales Report", "Guest Payments", "Occupancy Report",
        "WalkIn CheckIn", "Room Status", "Expense Entry",
        "Forex Receive Entry", "Display Rack", "Travel Agency Posting",
        "Bill Reprint", "Reverse Check Out", "Merge Room",
        "Bill Re-Settlement", "Look Up Rooms", "Look Up Room types",
        "Plan Meal Tokens", "GRC Printing", "Blank GRC",
        "Add/Edit/Delete Group With Reservation ",
        "Reservation With History", "Advance Deposit",
        "Confirmation Letters", "Cancellation Letters",
        "Registration Card", "Reservation Status Screen",
        "Complaint Master", "Complaint Clearance",
        "Lost / Found Entry", "Claim Entry", "Room Block",
        "Item Issued On Cleaning", "Check Out Clearance Screen",
        "Changes Department", "Sale Bill Entry", "Settlement Entry",
        "Display Table", "Order Booking", "Bill Lookup",
        "Order Booking Advance", "Token Entry", "Assign Delivery",
        "Payment Receive", "Banquet Bill Sundry Setting",
        "Catalog Selection", "Chef Pre-Costing", "Banquet Billing",
        "Banquet Settlement", "Banquet Estimate Billing",
        "Banquet Booking Advance", "Member Master",
        "Corporate Member Master", "Category wise Revenue",
        "Category wise Facility", "Member Bill Sundry Setting",
        "Member Age Wise Revenue", "Member Select Category",
        "Outlet Bill Sundry Setting", "Table Master",
        "Menu Item Rate", "Rate Group Master", "Open Item Consumption",
        "Card Initialization", "Card Registration", "Card Recharge",
        "Card Refund", "Card Re-Issue", "User Collection",
        "Transfer (Offline)", "Transfer (Online)", "Door Locks",
        "Godrej Locks", "Cascade", "Tile Horizontal", "Tile Vertical",
        "Manage MDI", "Restaurant Change ", "Exit", "PlanPopup",
        "Sale Bill Modification", "Windows", "MDI", "-",
    }
    print(f"_form_registry() failed, using fallback registry ({len(registry_keys)} keys)")

if not registry_keys:
    registry_keys = set()

# All VB6 items
vb6_all = set()
for items in vb6_menus.values():
    for item in items:
        vb6_all.add(item.strip())

# Workbench items matching MainSetupWorkbench groups
wb_items = {
    "Tax Master", "Tax Structure", "Payment Type", "Parameter",
    "Revenue Group Setting", "Printing Parameters", "Printing Setup",
    "Revenue Wise Budget Entry",
    "Country Master", "State Master", "City Master", "Market Segment",
    "Business Source", "Guest Status", "Charge Master", "Fixed Charge",
    "Package Master", "Plan Master", "Season Master", "Room Features",
    "Room Category", "Room Master", "Company Master", "Forex Master",
    "Guest History", "Group Profile", "Room Display",
    "Setup Outlet", "Outlet Bill Sundry Setting", "Server Master",
    "Table Master", "Item List", "Menu Group", "Menu Category",
    "Menu Item", "Menu Item Rate", "Rate Group Master", "Session Master",
    "Open Item Consumption", "Scheme Master", "Happy Hours",
    "Happy Hours [ Free Items ]", "Combo Pack", "NC Type",
    "Customer History", "Delivery Boy",
    "Category Master", "Member Master", "Corporate Member Master",
    "Revenue Master", "Facility Master", "Category wise Revenue",
    "Category wise Facility", "Member Bill Sundry Setting",
    "Environment Settings", "Member Age Wise Revenue",
    "Member Select Category",
    "Events", "Venue Features", "Venue Master", "Menu Category",
    "Item Group", "Menu Item", "Catalog Master",
    "Banquet Bill Sundry Setting",
    "Party Master", "Department", "Item Group", "Item Category",
    "Item Entry", "Consumption Master", "Purchase Sundry Setting",
    "Location Master", "Opening Stock", "Item List", "Shift Master",
    "Enviro Inventry",
    "Designation Master", "Category  Master", "Holiday Master",
    "Employee Master",
    "Group Accounts", "Ledger Accounts", "Narration Master",
    "T.D.S. Category", "FA Environment", "Voucher Environment",
    "Opening Balance Updation", "Year End Updation",
    "Current Balance Updation", "Country Master", "State Master",
    "City Master", "Delete Message", "Account Merging",
    "Voucher Serialisation",
    "User Master", "Permissions", "Update Database Nulls",
    "Backup Data", "Account Merging", "Guest Parameters Setting",
    "Sundry Master", "Voucher Wise Sundry Entry",
    "Sale MIS Customized", "Guest BirthDates/Anniversary",
    "Inconsistency Check", "Year End Updation", "Data Transfer",
    "Data Recieving", "Menu Item Copy", "POS Bill Deletion",
    "Guest LookUp", "Country Master", "State Master", "City Master",
    "Company Master", "Department", "Ledger Accounts",
    "Data Transfer (POS)", "PLU File (W.Scale)",
    "User Permissions (Advanced)", "POS Recycle", "Unit Master",
    "Task Scheduler",
    # EPABX
    "Call Type Master", "Call Code", "Call Codes Master",
    "Call Control Master", "Com Port Properties",
    "Extension", "Extension Master",
}

# MISSING from registry (VB6 items not in registry)
print(f"\n--- VB6 MDI items NOT in _form_registry ---")
missing_reg = []
for item in sorted(vb6_all):
    found = any(item.lower().strip() == k.lower().strip() for k in registry_keys)
    if not found:
        missing_reg.append(item)
        print(f"  MISSING: {item}")
print(f"Total missing from registry: {len(missing_reg)}")

# MISSING from workbench
print(f"\n--- VB6 MDI items NOT in MainSetupWorkbench ---")
missing_wb = []
for item in sorted(vb6_all):
    if item not in wb_items:
        missing_wb.append(item)
        print(f"  MISSING: {item}")
print(f"Total missing from workbench: {len(missing_wb)}")

# EXTRA in workbench (not in VB6 MDI)
extra_wb = wb_items - vb6_all
print(f"\n--- MainSetupWorkbench items NOT in VB6 MDI ---")
for item in sorted(extra_wb):
    print(f"  EXTRA: {item}")
print(f"Total extra in workbench: {len(extra_wb)}")

# Registry items that are MainSetup related
print(f"\n--- Registry items NOT in VB6 MDI ---")
extra_reg = []
for k in sorted(registry_keys):
    if k not in vb6_all:
        extra_reg.append(k)
        if not any(kw in k.lower() for kw in ["report", "check", "bill", "sale", "pos", "sms", "email", "tax", "stock", "order", "purchase", "booking", "hall", "payroll", "member", "guest", "folio", "reservation", "room", "log", "export", "import", "backup", "config", "search", "notification", "appearance", "help", "settings", "global", "notification", "clock", "fullscreen", "caps", "num", "sidebar", "theme", "tool", "database", "db"]):
            print(f"  EXTRA_REG: {k}")
print(f"Total extra registry: {len(extra_reg)}")

# Auto-open check
print(f"\n--- _AUTO_OPEN ---")
print(f"sidebar_buttons.AUTO_OPEN: {_sb.AUTO_OPEN}")
print(f"MainWindow._AUTO_OPEN: {dict(_sb.AUTO_OPEN)}")

# Check specific key items
print(f"\n--- KEY ITEM CHECKS ---")
key_items = ["Tax Master", "Country Master", "Session Master", "Charge Master",
             "Unit Master", "Sundry Master", "Guest Profile", "Check In",
             "Room Category", "Room Master", "Package Master", "Plan Master",
             "Tax Structure", "Payment Type", "Parameter", "Printing Setup"]
for item in key_items:
    in_reg = any(item.lower().strip() == k.lower().strip() for k in registry_keys)
    in_wb = item in wb_items
    print(f"  {item:25} in_registry={in_reg} in_workbench={in_wb}")

print(f"\n{'=' * 70}")
print("DEBUG COMPLETE")
print("=" * 70)
