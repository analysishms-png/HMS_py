"""Quick Demo Entry - Module wise screenshots."""
import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt6.QtWidgets import QApplication
app = QApplication.instance() or QApplication(sys.argv)
from HMS_py.ui.theme import apply_theme
apply_theme(app, "dark")

SHOT_DIR = Path(__file__).parent / "demo_screenshots"
SHOT_DIR.mkdir(exist_ok=True)

def save(widget, name):
    path = str(SHOT_DIR / f"{name}.png")
    widget.grab().save(path)
    print(f"  SAVED: {name}.png ({os.path.getsize(path)//1024}KB)")

# 1. LOGIN
print("\n--- LOGIN ---")
from HMS_py.ui.shell import LoginDialog
login = LoginDialog()
login.resize(800, 480)
login.show(); app.processEvents()
save(login, "01_login")

# 2. COMPANY
from HMS_py.ui.shell import CompanyDialog
from HMS_py.core import company
comp = CompanyDialog("PYADMIN")
comp.resize(1000, 560)
comp.tbl.selectRow(0)
comp.show(); app.processEvents()
save(comp, "02_company")
comp.accept(); app.processEvents()

# 3. MAIN WINDOW
print("\n--- MAIN WINDOW ---")
from HMS_py.ui.shell import MainWindow
win = MainWindow("PYADMIN", {"name": "Moon and Mars Resorts", "short": "MMR", "year": company.current_year()})
win.resize(1200, 750)
win.show(); app.processEvents()
save(win, "03_main_window")

# 4. GUEST LOOKUP
print("\n--- GUEST LOOKUP ---")
from HMS_py.ui.guest_lookup_ui import GuestLookupWindow
gl = GuestLookupWindow()
gl.resize(900, 500)
gl.show(); app.processEvents()
save(gl, "04_guest_lookup")
gl.close()

# 5. REGISTRATION
print("\n--- REGISTRATION ---")
from HMS_py.ui.registration_entry_ui import RegistrationEntryWindow
reg = RegistrationEntryWindow()
reg.resize(950, 600)
reg.show(); app.processEvents()
save(reg, "05_registration")
reg.close()

# 6. SUNDRY MASTER
print("\n--- SUNDRY MASTER ---")
from HMS_py.ui.misc_sub_forms_ui import SundryMasterWindow
sw = SundryMasterWindow()
sw.resize(750, 450)
sw.show(); app.processEvents()
save(sw, "06_sundry_master")
sw.close()

# 7. NIGHT AUDIT REPORTS
print("\n--- NIGHT AUDIT ---")
from HMS_py.ui.nightaudit_reports_ui import NightAuditReportsWindow
nar = NightAuditReportsWindow()
nar.resize(800, 550)
nar.show(); app.processEvents()
save(nar, "07_night_audit_reports")
nar.close()

# 8. VOUCHER ENTRY
print("\n--- VOUCHER ---")
from HMS_py.ui.fa_voucher_ui import VoucherEntryDialog
fv = VoucherEntryDialog()
fv.resize(850, 550)
fv.show(); app.processEvents()
save(fv, "08_voucher_entry")
fv.close()

# 9. LEDGER ADJUSTMENT
print("\n--- ADJUSTMENT ---")
from HMS_py.ui.fa_sub_forms_ui import FaAdjustWindow
fa = FaAdjustWindow()
fa.resize(800, 500)
fa.show(); app.processEvents()
save(fa, "09_ledger_adjustment")
fa.close()

# 10. CHEQUE CLEARING
print("\n--- CHEQUE ---")
from HMS_py.ui.fa_sub_forms_ui import FaChqClearWindow
fc = FaChqClearWindow()
fc.resize(700, 400)
fc.show(); app.processEvents()
save(fc, "10_cheque_clearing")
fc.close()

# 11. TDS CERTIFICATE
print("\n--- TDS ---")
from HMS_py.ui.fa_sub_forms_ui import FaTDSCertificateWindow
ftds = FaTDSCertificateWindow()
ftds.resize(700, 400)
ftds.show(); app.processEvents()
save(ftds, "11_tds_certificate")
ftds.close()

# 12. KOT ENTRY
print("\n--- KOT ---")
from HMS_py.ui.kot_entry import KOTEntryForm
kot = KOTEntryForm()
kot.resize(900, 600)
kot.show(); app.processEvents()
save(kot, "12_kot_entry")
kot.close()

# 13. PURCHASE ORDER
print("\n--- PURCHASE ORDER ---")
from HMS_py.ui.purchase_order_ui import PurchaseOrderWindow
po = PurchaseOrderWindow()
po.resize(850, 550)
po.show(); app.processEvents()
save(po, "13_purchase_order")
po.close()

# 14. STOCK ISSUE
print("\n--- STOCK ISSUE ---")
from HMS_py.ui.stock_issue_ui import StockIssueWindow
si = StockIssueWindow()
si.resize(850, 550)
si.show(); app.processEvents()
save(si, "14_stock_issue")
si.close()

# 15. STOCK ADJUSTMENT
print("\n--- STOCK ADJUST ---")
from HMS_py.ui.stock_adjust_ui import StockAdjustWindow
sa = StockAdjustWindow()
sa.resize(850, 550)
sa.show(); app.processEvents()
save(sa, "15_stock_adjustment")
sa.close()

# 16. ROOM STATUS
print("\n--- ROOM STATUS ---")
from HMS_py.ui.roomstatus_ui import RoomStatusForm
rs = RoomStatusForm()
rs.resize(900, 550)
rs.show(); app.processEvents()
save(rs, "16_room_status")
rs.close()

# 17. TALLY EXPORT
print("\n--- TALLY ---")
from HMS_py.ui.tally_export_ui import TallyExportWindow
te = TallyExportWindow()
te.resize(650, 380)
te.show(); app.processEvents()
save(te, "17_tally_export")
te.close()

# 18. DB BACKUP
print("\n--- DB BACKUP ---")
from HMS_py.ui.db_backup_ui import DbBackupWindow
dbw = DbBackupWindow()
dbw.resize(650, 400)
dbw.show(); app.processEvents()
save(dbw, "18_db_backup")
dbw.close()

# 19. REVENUE BUDGET
print("\n--- REVENUE ---")
from HMS_py.ui.revenue_budget_ui import RevenueBudgetWindow
rb = RevenueBudgetWindow()
rb.resize(800, 500)
rb.show(); app.processEvents()
save(rb, "19_revenue_budget")
rb.close()

# 20. ACCOUNT MERGE
print("\n--- ACCOUNT MERGE ---")
from HMS_py.ui.account_merge_ui import AccountMergeWindow
am = AccountMergeWindow()
am.resize(700, 450)
am.show(); app.processEvents()
save(am, "20_account_merge")
am.close()

# 21. MAIN SETUP
print("\n--- MAIN SETUP ---")
from HMS_py.ui.shell import MainSetupWorkbench
ms = MainSetupWorkbench(user="PYADMIN")
ms.resize(1100, 700)
ms.show(); app.processEvents()
save(ms, "21_main_setup")
ms.close()

# 22. LIGHT MODE
print("\n--- LIGHT MODE ---")
from HMS_py.ui.theme import toggle_theme
toggle_theme(app)
app.processEvents()
save(win, "22_light_mode")

print("\n" + "=" * 50)
print("ALL DEMO SCREENSHOTS SAVED!")
files = sorted(SHOT_DIR.glob("*.png"))
for f in files:
    print(f"  {f.name:40s} {f.stat().st_size//1024:3d} KB")
print(f"\nTotal: {len(files)} screenshots")
