# FINANCE — VB6 vs Python Parity Report
> Module: Ledger / LedgerM, FaVoucher, FaReports, FaChqClear, YearEnd, Bank/Cash/Ageing  
> Date: 2026-09-24  
> Rule: **SAME VB6 SQL, no DB schema change** — only add `WHERE LOGSITE_CODE` filter if missing, keep table/column names identical.

---

## 1) VB6 Sources Read (verbatim SQL)

### 1.1 `FaVoucher.bas` (378 lines) — NCAT routing + voucher print counts

| VB6 Sub | Verbatim SQL | Purpose |
|---------|--------------|---------|
| `Proc_7_0_F78958` L11 | `SELECT NCAT FROM VOUCHER_TYPE WHERE V_TYPE='<arg_C>'` | CNT/JV/PMT/RCT branch → `FaVrEnt.FindMove` |
| `Proc_7_1_1365344` L49,64 | `SELECT NCAT FROM VOUCHER_TYPE WHERE V_TYPE='<arg_C>'` ; `SELECT Param_Str AS UPrivilege,Module_Name FROM menuHelp WHERE UserName='<user>' AND CompCode='<comp>' AND [Option]='Voucher Entry'` | Same NCAT; then `menuHelp` UPrivilege for `fate+0` (CNT/JV/PMT/RCT). Else branches: `PBILL/PTRAN → Purch+5 → 'Purchase Bill/Return Entry'` ; `SBILL/PRET/SRET/… → pPBILL/…`; `OPBAL → FaSubGroup.SEARCHBACK`; `PBR/PBC/PRR/PRC → Purch+5 → [Option]='Purchase Bill'` ; `EXR/EXC → Purch+5 → [Option]='Purchase Bill'` ; `MBILL → Memb+3 → [Option]='Member Facility Billing'` |
| `Proc_7_2_FF1E88` L215 | `SELECT VOUCHER_TYPE.DESCRIPTION,NAME,LEDGER.V_Type,LEDGER.V_No,LEDGER.v_Prefix,LEDGER.V_Date,LEDGER.V_SNo,LEDGER.AmtCr,LEDGER.AmtDr,LEDGER.Chq_No,LEDGER.Chq_Date,LEDGER.Narration,LEDGERM.Narration AS NARRMAIN,LEDGERM.DocId,LEDGERM.v_Prefix,LEDGER.U_NAME UserName FROM ((LEDGER LEFT JOIN LEDGERM ON LEDGERM.DOCID=LEDGER.DOCID)LEFT JOIN SUBGROUP ON SUBGROUP.SUBCODE = LEDGER.SUBCODE ) INNER JOIN VOUCHER_TYPE ON (VOUCHER_TYPE.V_tYPE=LEDGER.V_tYPE AND VOUCHER_TYPE.LOGSITE_CODE=LEDGER.LOGSITE_CODE) WHERE LEDGER.V_TYPE='<type>' AND LEDGER.V_NO=<vno> order by ledger.v_no,LEDGER.V_SNo` | Single-voucher print (FaRect.TTX) |
| `Proc_7_4_11ABBE0` L294/308/315 | `SELECT VOUCHER_TYPE.DESCRIPTION,NAME,LEDGER.V_Type,LEDGER.V_No,LEDGER.v_Prefix,LEDGER.V_Date,LEDGER.V_SNo,LEDGER.AmtCr,LEDGER.AmtDr,LEDGER.Chq_No,LEDGER.Chq_Date,LEDGER.Narration,LEDGERM.Narration AS NARRMAIN,LEDGER.U_Name As UserName,LEDGERM.DocId,LEDGERM.v_Prefix,LTDS.TDSAMT,LTDS.TDS,LTDS.ONAMT FROM (((LEDGER LEFT JOIN LEDGERM ON LEDGERM.DOCID=LEDGER.DOCID)LEFT JOIN SUBGROUP ON SUBGROUP.SUBCODE = LEDGER.SUBCODE ) INNER JOIN VOUCHER_TYPE ON (VOUCHER_TYPE.V_tYPE=LEDGER.V_tYPE AND VOUCHER_TYPE.LOGSITE_CODE=LEDGER.LOGSITE_CODE)) LEFT JOIN LEDGERTDS LTDS ON (LTDS.TDSDRCODE=LEDGER.SUBCODE AND LEDGER.DOCID=LTDS.DOCID) WHERE LEDGER.V_PREFIX=<fyPrefix> And LEDGER.V_TYPE='<type>' AND LEDGER.V_NO BETWEEN <from> AND <to> order by …` (3 variants: BETWEEN, `VOUCHER_TYPE.Category='FA' AND LEDGER.V_date=` , single `V_NO=`) | Range/date/single print (FaJVCHR.TTX) |
| `Proc_7_3_F61A94` L248/256 | `SELECT COUNT(*) FROM Ledger WHERE V_Type=<arg>` ; `SELECT COUNT(*) FROM LedgerM WHERE V_Type=<arg>` | Delete-guard (rc>0 block) |
| `Proc_7_7_F2F5A4` L365 | `SELECT NCAT FROM VOUCHER_TYPE WHERE V_TYPE='<arg_C>'` | OPBAL/OPDIFF branch |

**Also found in `moondata.sql` definitions (UTF-16, 1.31M chars):**

```sql
-- ACGROUP PK (ID, Site_Code), col LogSite_Code; SubGroup PK (SubCode), col LogSite_Code
-- Ledger PK (DocId, V_SNo) cols V_Type(5), V_No(int), v_Prefix(5), V_Date, SubCode(8), AmtCr/Dr float, ContraSub, Chq_No/Chq_Date/Clg_Date, Narration(500), GroupCode, GroupNature, LogSite_Code, Site_Code, SeqNo
-- LedgerM PK (DocId) cols V_Type,v_Prefix,V_No,Site_Code,V_Date,Narration(255),LogSite_Code
-- LedgerTDS PK (DocId, V_SNo) cols Site_Code,v_Prefix,V_DATE,TDSCode,TDSDrCode,TDSYN,ONAMT,TDS,TDSAMT,TDSPOST,TDSDocId,TDSV_SNo,LogSite_Code
-- ledgerRef PK (Id) cols DocId,V_SNo,Dr,Cr,SubCode,DueDate,AgRefNo,AgRefType,V_Date,Site_Code,LogSite_Code
-- ledgerAdj PK (DocId1,V_SNo1,DocId2,V_SNo2,SubCode) cols Cr, Name, AgRefNo, Site_Code,LogSite_Code
-- Voucher_Type PK (V_Type,Site_Code,LogSite_Code) cols Category(10),NCat(5),Description(30),SerialNo_From_Table(50), Print_VNo, Header_Desc etc, Site/LogSite_Code
-- Voucher_Prefix PK (V_Type,Date_From,Site_Code,LogSite_Code) cols Date_From/To,Prefix,Start_Srl_No
-- LastVoucher PK (user_name,V_Type) ; LastVou PK (UNAME,ENAME,DOCID,Site_Code)
-- FaEnviro single row per LogSite_Code (Age1..6, Amt1..6, flags VerticalBalanceSheet etc, Site/LogSite_Code)
-- SUBGROUPCURRBAL PK (LogSite_Code,SubCode,V_Date) col GroupCode,Curr_Bal ; ACGROUPCURRBAL similar
-- DATELOCK PK (CODE) cols flag bit, SDate/EDate
```

### 1.2 `FaGrEnt.frm` — Group Accounts Entry (AcGroup) VB6 workflow

| Area | VB6 verbatim SQL |
|------|-------------------|
| TopCtrl eFind L655 | `Select GROUPCODE As SearchCode,GroupName,GroupNature,Nature FROM AcGroup Where (LOGSITE_CODE='<site>' OR LOGSITE_CODE='HO') AND AliasYN<>'Y' Order by GroupName` |
| Print L704 | `select SYSGROUP,GroupName,Nature,GNature= CASE GroupNature WHEN 'A' THEN 'A S S E T S' WHEN 'E' THEN 'E X P E N D I T U R E' WHEN 'L' THEN 'L I A B I L I T Y' WHEN 'R' THEN 'R E V E N U E' ELSE 'Others' END,MainGrCode from acgroup WHERE (LOGSITE_CODE='<site>' OR LOGSITE_CODE='HO') order by groupname` |
| Form_Load L870/935 | `Select GroupCode As Code,GroupName As Name,GroupNature,MainGrCode,CurrentBalance,SubLedYN,AliasYN,GroupHelp,Nature From AcGroup Where MainGrCode<>'999' AND (LOGSITE_CODE='<site>' OR LOGSITE_CODE='HO') … Order by GroupName` ; `Select ID,GroupCode,GroupName,GroupHelp,Nature From AcGroup Where MainGrCode<>'999' AND (LOGSITE_CODE='<site>' OR LOGSITE_CODE='HO') Order by GroupHelp` ; `Select GROUPCODE as SearchCode,ID,Site_Code,GroupCode,GroupName,GroupNameBiLang,GroupNature,MainGrCode,CurrentBalance,SubLedYN,BlOrd,AliasYN,GroupHelp,Nature,SysGroup,TRADINGYN,LogSite_Code From AcGroup Where (LOGSITE_CODE='<site>' OR LOGSITE_CODE='HO') AND AliasYN<>'Y' Order by GroupName` |
| Validation | `Select GroupHelp From AcGroup Where GroupHelp='<help>'` ; `Select GroupCode,GroupName,MainGrCode,Nature,AliasYN From AcGroup Where GroupCode='<code>'` |

**Key pattern:** every AcGroup read uses `(LOGSITE_CODE='<site>' OR LOGSITE_CODE='HO')` HO-fallback. AliasYN filter.

### 1.3 `FaVrEnt.frm` (14k lines, truncated read) — Voucher Entry

VB6 form owns: `TxtGlb` narration, grid arrays `TxtDr/TxtCr/TxtAcName/TxtNar/TxtCrDr(0..11)`, cheque fields `TxtCHno/TXTChDate/TXTClrDate`, ref frames `FrameRef/FGridRef` (ledgerRef/Adj), TDS frame `FrameTDS` (`TxtTDSCode/TxtTDSAmt/TxtTDS/TxtONAMT`), adjust frame `FRAMEADJUST/FgridAdjust`, Voucher list `FRAMEVLIST`, print frame `Frame1(1) Opt2(0..2) DataCombo3/2`.  
Inferred VB6 writes (from `fa_voucher.py` evidence + FaVoucher.bas): `INSERT INTO LedgerM (DocId,V_Type,v_Prefix,V_No,Site_Code,V_Date,Narration,U_Name,U_EntDt,U_AE,LogSite_Code)` and per-line `INSERT INTO LEDGER (DocId,V_SNo,V_Type,V_No,v_Prefix,Site_Code,V_Date,SubCode,AmtCr,AmtDr,ContraSub,Narration,Chq_No,Chq_Date,Clg_Date,GroupCode,GroupNature,AgRefNo,U_Name,U_EntDt,U_AE,LogSite_Code)`. Also CurrBal update (`SUBGROUPCURRBAL`/`ACGROUPCURRBAL` per `V_Date`), `LEDGERREF`, `LEDGERADJ`, `LEDGERTDS`, `LedgerLog`/`LedgerMLog`, `VOUCHER_Prefix.Start_Srl_No`, `LastVoucher`.

### 1.4 `FaChqClear.frm` — Cheque Clearing

| Area | Verbatim SQL |
|------|--------------|
| Form_Load L911 | `SELECT * FROM FAENVIRO WHERE LOGSITE_CODE='<site>'` |
| DGBank/DGParty L912/924 | `Select SubCode As Code,Name From SubGroup Where Nature in ('Bank') AND (LOGSITE_CODE='<site>' OR LOGSITE_CODE='HO') Order by Name` ; `Where Nature <>'Bank' AND (LOGSITE_CODE='<site>' OR LOGSITE_CODE='HO')` |
| Save L782/801/308 | `Update Ledger Set Chq_No='<no>',Chq_Date=<dt>,Clg_Date=<dt> Where DocID='<doc>' AND V_SNO=<n> [AND AmtCr=<amt> AND ContraSub='<sub>']` (2 branches: `V_Type='HPOST'` special with `AmtCr/ContraSub` match, else single) + `BeginTrans/CommitTrans/RollbackTrans` |
| FGrid init L399+ | 15 cols (DocID,V.SNo,V.Type,V.Prefix etc) |

**VB6 `FaChqClear` business rule:** pending drawer shows cheques where cheque exists but not cleared; clearing updates Ledger `Chq_No/Chq_Date/Clg_Date` inside a transaction. Bank lookup is `Nature='Bank'` + HO fallback.

### 1.5 `FaReports.frm` — Finance display/reports

VB6 `GRepFormName` driven. Reported captions imply: `Led/LedInt/LedDeb/MemLed/LedCred/CashBook/BankBook/Budget/BudgetVariance/AcCheckList/GroupTrial/LedTrial/CashFlow/FundFlow/CashBankSum` etc.  
`Form_Load L1071` : `SELECT * FROM FAENVIRO WHERE LOGSITE_CODE='<site>'` → loads `TagadaHeader/Footer`. Buttons wire to Crystal reports via `FaRepView`. Filter uses `DGSite` (`Site_Code/ Site_Desc FROM Site`).

### 1.6 `frmYearEnd.frm` — YearEnd

| Step | VB6 SQL |
|------|---------|
| L156 | `Select * From Company Where Comp_Code='<comp>'` |
| L180 | `Select Max(Cast(Comp_Code As Integer))+1 As Code From Company` |
| L184 | `Insert into Company (Comp_Code,Comp_Name,CentralData_Path,Repo_Path,Start_Dt,End_Dt,address1,address2,city,phone,fax,lstno,lstdate,cstno,cstdate,cyear,pyear,Pin,SName,U_Name,U_EntDt,U_AE,FGLNO,SerialKeyNo,SiteCode,SiteName,SiteCodeDisplay,ActiveEpabx,PanNo,TinNo,GSTIN,StateCode,State,DivisionCode,Mobile,Email,LegalName,TradeName,Comp_Id) Values (...)` |
| L276 | `Select * From menuHelp Where CompCode='<comp>'` → loop `INSERT INTO menuHelp … VALUES('<newComp>', … Flag, Module_Name …)` |
| L296 | `Select * From menuHelp1 Where CompCode='<comp>'` → `INSERT INTO menuHelp1 …` |
| L298 | `Select * From Voucher_Prefix Where Site_Code='<site>' and date_From=<Start_Dt>` → loop `Insert into Voucher_Prefix (V_Type,Date_From,Date_To,Prefix,Start_Srl_No,Site_Code,LogSite_Code) values('<vtype>',<newFY_Date_From>,<newFY_Date_To>,'<year>',0,'<logSite>','<logSite>')` |
| L324 | `Insert into UserPermission (CompCode,UserName,LogSite_Code,POSDiscountAllowUpto,CancelGuestBill,ChangeRoomDtl,DeleteGuestCharges,Site_Code,POSSettlementYN,EditItemInKOT,ChangeGuestCharges) values('<newComp>', '<user>', '<site>', …)` |
| L235 | `Update Company Set ActiveEpabx='' Where Comp_Code='<comp>'` |

**Not** a Ledger OPBAL generator — YearEnd is a *Company snapshot + menuHelp/Voucher_Prefix/Site security copy* (new Comp_Code as `MAX+1`, `Start_Dt/End_Dt +1 year`, `CYear = 'YYYY-XX'`). VB6 never inserts Ledger OPBAL rows here.

### 1.7 `MDIForm1.frm` 315-492 FA menus

```
FA > Transaction: fate[0] Voucher Entry | fate[1] Adjustment Entry (hidden) | fate[2] Delete Adjustment (hidden) | fate[3] Bank Reconciliation | fate[5] TDS Challan (hidden) | fate[6] TDS Certificate (hidden) | fate[7] Expense Voucher
FA > Display (hidden): Trial Balance (Group), P&L, Ledger Interest, Cash Flow, Fund Flow, Cash And Bank Books, Trial Ledger(current)
FA > Reports: Trial Balance | Day Book(hidden) | Ledger | Interest Ledger(hidden) | Cash Book | Bank Book | Journal Books | Annexure | Bank Register | Ageing Debtors | Ageing Creditors | Cheque Cleared | Cheque Not Cleared | Outstanding Debtors | Outstanding Creditors | Daily Transaction Summary(hidden) | Non Transaction(hidden) | Reference(hidden) | Detailed Trial Ledger | Bill Wise Outstanding Debtors | Control Ledger(hidden) | Roz Namcha
FAME (Main Setup > Finance) : Group Accounts | Ledger Accounts | Narration Master | TDS Category | FA Environment | Voucher Environment | Opening Balance Updation(hidden) | Year End Updation | Current Balance Updation | Delete Message | Account Merging | Voucher Serialisation
```

`fate_Click` does `SELECT Param_Str AS UPrivilege FROM menuHelp WHERE UserName='<u>' AND CompCode='<c>' AND [Option]='Voucher Entry'` then `fate+0` etc. Same privilege guard as FaVoucher.bas.

---

## 2) Python Sources Read (verbatim SQL)

### 2.1 `core/fa_voucher.py` (821 lines)

```python
# _prefix_for
"SELECT TOP 1 Prefix FROM Voucher_Prefix WHERE V_Type = ? AND ? BETWEEN Date_From AND Date_To AND Site_Code = ? ORDER BY Date_From DESC"
# fallback without Site_Code
"SELECT TOP 1 Prefix FROM Voucher_Prefix WHERE V_Type = ? AND ? BETWEEN Date_From AND Date_To ORDER BY Date_From DESC"

# next_vno
"SELECT ISNULL(MAX(V_No), 0) FROM LedgerM WHERE V_Type = ? AND v_Prefix = ? AND Site_Code = ?"
"SELECT ISNULL(MAX(V_No), 0) FROM Ledger WHERE V_Type = ? AND v_Prefix = ? AND Site_Code = ?"
"SELECT ISNULL(Start_Srl_No, 0) FROM Voucher_Prefix WHERE V_Type = ? AND Prefix = ? AND Site_Code = ?"

# post_voucher header/line
"INSERT INTO LedgerM (DocId, V_Type, v_Prefix, V_No, Site_Code, V_Date, Narration, U_Name, U_EntDt, U_AE, LogSite_Code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)"
"INSERT INTO Ledger (DocId, V_SNo, V_Type, V_No, v_Prefix, Site_Code, V_Date, SubCode, AmtDr, AmtCr, ContraSub, Narration, Chq_No, Chq_Date, Clg_Date, GroupCode, GroupNature, AgRefNo, U_Name, U_EntDt, U_AE, LogSite_Code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, ?, getdate(), 'A', ?)"
# _update_currbal
"SELECT GroupCode FROM SubGroup WHERE RTRIM(SubCode) = ?"
"SELECT ISNULL(Curr_Bal, 0) FROM SUBGROUPCURRBAL WHERE SubCode = ? AND LogSite_Code = ? AND V_Date = ?"
"UPDATE SUBGROUPCURRBAL SET Curr_Bal = ?, GroupCode = ? WHERE SubCode = ? AND LogSite_Code = ? AND V_Date = ?"
"INSERT INTO SUBGROUPCURRBAL (LogSite_Code, SubCode, V_Date, GroupCode, Curr_Bal, Site_Code) VALUES (?, ?, ?, ?, ?, ?)"
"SELECT ISNULL(Curr_Bal, 0) FROM ACGROUPCURRBAL WHERE GroupCode = ? AND LogSite_Code = ? AND V_Date = ?"
"UPDATE ACGROUPCURRBAL SET Curr_Bal = ? WHERE GroupCode = ? AND LogSite_Code = ? AND V_Date = ?"
"INSERT INTO ACGROUPCURRBAL (LogSite_Code, GroupCode, V_Date, Curr_Bal, Site_Code) VALUES (?, ?, ?, ?, ?)"
"SELECT MainGrCode FROM AcGroup WHERE GroupCode = ?"
"DELETE FROM LEDGERADJ WHERE DocId1 = ? OR DocId2 = ?"   # _write_ledgeradj
"SELECT 1 FROM Voucher_Type WHERE V_Type = ?"            # TDS vtype check
# cheque
"SELECT l.DocId, l.V_SNo, l.V_Date, l.SubCode, s.Name, l.Chq_No, l.Chq_Date, l.AmtDr, l.AmtCr FROM Ledger l LEFT JOIN Subgroup s ON s.SubCode = l.SubCode WHERE l.Chq_No <> '' AND (l.Clg_Date IS NULL OR l.Clg_Date > GETDATE()) ORDER BY l.V_Date"  # cheque_pending
"SELECT l.DocId, l.V_SNo, l.V_Date, l.SubCode, s.Name, l.Chq_No, l.Chq_Date, l.Clg_Date, l.AmtDr, l.AmtCr FROM Ledger l LEFT JOIN Subgroup s … WHERE l.Chq_No <> '' AND l.Clg_Date IS NOT NULL AND l.Clg_Date <= GETDATE() ORDER BY l.Clg_Date DESC" # cheque_cleared
"SELECT Chq_No, Chq_Date FROM Ledger WHERE DocId = ? AND V_SNo = ?"
"UPDATE Ledger SET Clg_Date = ?, Chq_No = ?, Chq_Date = ? WHERE DocId = ? AND V_SNo = ?"
# reports in fa_voucher
"SELECT l.GroupCode, a.GroupName, a.GroupNature, SUM(l.AmtDr) AS Dr, SUM(l.AmtCr) AS Cr, SUM(l.AmtDr) - SUM(l.AmtCr) AS Bal FROM Ledger l LEFT JOIN Acgroup a ON a.GroupCode = l.GroupCode [WHERE l.V_Date BETWEEN ? AND ?] GROUP BY …"
"SELECT l.V_Date, l.DocId, s.Name, l.Chq_No, l.AmtDr, l.AmtCr FROM Ledger l JOIN Subgroup s ON … WHERE (s.Name LIKE '%BANK%') AND l.V_Date BETWEEN ? AND ? …" # bank_register
# _log_voucher
"SELECT V_SNo, V_Type, V_No, v_Prefix, V_Date, SubCode, AmtCr, AmtDr, ContraSub, Chq_No, Chq_Date, Clg_Date, Narration, GroupCode, GroupNature FROM Ledger WHERE DocId = ? ORDER BY V_SNo"
"SELECT ISNULL(MAX(SeqNo), 0) FROM LedgerLog WHERE DocId = ?"
"SELECT V_Type, v_Prefix, V_No, V_Date, Narration FROM LedgerM WHERE DocId = ?"
"SELECT ISNULL(MAX(SeqNo), 0) FROM LedgerMLog WHERE DocId = ?"
```

### 2.2 `core/fa_ledger_ops.py`, `core/ledger.py`, `core/acgroup.py`

- `fa_ledger_ops.py` : CRUD for LEDGERADJ / LEDGERREF / LEDGERTDS / SUBGROUPCURRBAL / ACGROUPCURRBAL / Budget / Voucher_Prefix / Voucher_Include/Exclude / LastVoucher / LedgerLog / LedgerMLog / LEDGER. All `WHERE` use `Site_Code = ?` or `LogSite_Code = ?` with `SITE_CODE` param — **no HO-fallback** on reads (`acgroup.py` also has `WHERE GroupCode = ?` without LOGSITE filter; `ledger.py` `SubGroup` reads have **no** `LOGSITE_CODE` filter at all).
- `acgroup.py` : `SELECT … FROM ACGROUP WHERE GroupCode = ?` ; `INSERT INTO ACGROUP (ID,GroupCode,…?) VALUES …` with `SITE_CODE` ; `UPDATE … WHERE GroupCode = ?` (no LogSite_Code).
- `ledger.py` : `SELECT … FROM SubGroup WHERE SubCode = ?` / `Name LIKE ?` (no LogSite_Code).

### 2.3 `core/fa_reports.py` (832 lines) & `core/fa_tds_ops.py` (278 lines)

`fa_reports.py` aggregates `LEDGER LEFT JOIN SubGroup … LEFT JOIN AcGroup`; no DateLock, no LOGSITE, no `Category='FA'`. `fa_tds_ops.py` : `TDSChal/TDSChal1` header/detail + `LEDGERTDS` joined via `RTRIM(TDSDrCode)`; `tds_detail` uses `WHERE RTRIM(t.TDSDrCode)=?` (no site filter); `tds_amt = int(onamt*tds/100+0.5)`.

### 2.4 `core/year_end.py` (233 lines)

Python YearEnd = `SUBGROUPCURRBAL/ACGROUPCURRBAL V_Date` bump + `LastVoucher` null-out + `Budget` Site_Code delete+reinsert — **not** VB6's `Company` clone + `menuHelp/Voucher_Prefix/UserPermission` clone.

### 2.5 UI: `ui/fa_voucher_ui.py` (365 lines), `ui/fa_ledger_ui.py` (221 lines)

- `fa_voucher_ui.py` : `VoucherEntryDialog` hard-codes `vtypes=["JV","HPOST","F_AO"]` fallback (else `voucher_type.list_entry_types()`), grid cols `SubCode|Name|Debit|Credit` (TODO: no `Narration/Chq_No/Chq_Date/Clg_Date/AgRefNo` per line), `TopCtrl`-like buttons only `+Line / -Line / Post Voucher` (VB6 TopCtrl has Add/Edit/Del/Save/Cancel/Find/Print/Exit + Edit locking); `BankReconDialog` shows pending only; `ReportViewer` with `QDateEdit` From/To + `Run`. No `menuHelp.Flag` check, no `FindMove`, no `Dr==Cr` live indicator beyond label, no transaction toast for CurrBal.
- `fa_ledger_ui.py` : `_LedgerMasterBridge` maps `AcCode→code/SubGroup`, fields only `AcCode/AcName/GroupCode/OpBalance/DrCr/Address` (real SubGroup has 70+ cols incl `PANNo/GSTIN/GroupNature/Category`); OpBalance `""` always; no `DateLock` guard.

---

## 3) Gap Table — where Python deviates from VB6

| # | Area | VB6 behavior | Python current | Severity | SAME-SQL fix (no schema change) |
|---|------|--------------|----------------|----------|--------------------------------|
| G1 | **HO fallback** `OR LOGSITE_CODE='HO'` | Every `AcGroup` and `SubGroup` lookup uses `(LOGSITE_CODE='<site>' OR LOGSITE_CODE='HO')` (`FaGrEnt` x6, `FaChqClear` Bank/Party). | `acgroup.py:get`, `ledger.py:get/search`, `fa_voucher.py:post_voucher` subcode validation `WHERE RTRIM(s.SubCode)=?` (no LOGSITE at all), `fa_ledger_ops.pending_adjustments` only case with `OR ISNULL(...,'')='' OR LOGSITE_CODE='HO'` (partial). Group reads miss HO. | **HIGH** — site HO ledgers invisible in PYTHONE. | Add `(s.LogSite_Code = ? OR s.LogSite_Code='HO' OR ISNULL(s.LogSite_Code,'')='')` to every SubGroup/AcGroup `SELECT`. Keep column names; `? = SITE_CODE`. Same for `AcGroup` reads. |
| G2 | **LOGSITE_CODE scoping on reports & ledger reads** | FaVoucher print SQL joins `VOUCHER_TYPE.LOGSITE_CODE=LEDGER.LOGSITE_CODE` and filters `LEDGER.V_PREFIX=<fy>` (FaEnviro-derived). | `fa_voucher.py:trial_balance/bank_register/cash_and_bank_books/journal_book/find_voucher/get_voucher` have **no** `LOGSITE_CODE` filter; `fa_reports.py` all aggregations no site filter; `ledger.py:list_all` no filter. Cross-site leakage. | HIGH | Add `WHERE Ledger.LogSite_Code = ?` (or `(Ledger.LogSite_Code=? OR Ledger.LogSite_Code='HO')` if VB6 display shows HO) to every report SELECT. Parameterize `SITE_CODE`. |
| G3 | **Voucher number generation** | `Voucher_Prefix.Start_Srl_No` + `MAX(Ledger/LedgerM V_No)` per `V_Type+Prefix+Site_Code+LogSite_Code`; YearEnd inserts fresh `Voucher_Prefix` row per `V_Type` with `Prefix=YYYY`. VB6 uses `Select * From Voucher_Prefix Where Site_Code='<site>' and date_From=<Start_Dt>` then `Insert … ,Start_Srl_No=0,Prefix='<YYYY>'`. | Python `next_vno` does `MAX(LedgerM)` then `MAX(Ledger)` then `Start_Srl_No` per `Site_Code` (missing `LogSite_Code` on MAX, missing `Date_From/To` FY window except prefix lookup). `UPDATE Voucher_Prefix SET Start_Srl_No = V_No` only updates one `(V_Type,Prefix,Site_Code)` row — VB6 yearly rows would collide. | MEDIUM | Keep VB6 SQL verbatim: add `AND LogSite_Code = ?` to all three `MAX`/`Start_Srl_No` SELECTs and the `UPDATE`. For FY: keep `_prefix_for` BETWEEN window. No schema change. |
| G4 | **Dr==Cr guard** | FaVrEnt blocks save unless `SUM(Dr)-SUM(Cr)=0` (VB6 FaVrEnt adjustment `LblRefAdjBal`); FaChqClear save skips empty `DocID`. | `fa_voucher.py:post_voucher` correctly has `abs(tot_dr-tot_cr)>0.005` + `tot_dr==0` guard — OK. But `ui/fa_voucher_ui.py` does not live-validate per row nor block `AmtCr+AmtDr` single-side per line (both zero allowed). | LOW | Add UI guard: per-row `AmtDr*AmtCr==0` (one side), `SELECT NCAT NOT NULL` check before Post. |
| G5 | **V_No / DocId 21-char spec** | `DocId = 'D'+site(2)+V_Type.ljust(5)+Prefix.ljust(5)+V_No.rjust(8)` =21 char (FaVrEnt:13332). `SeqNo` present on Ledger/LedgerLog for ordering. | Python `_make_docid` matches spec — OK. But `Ledger INSERT` omits `SeqNo` (VB6 increments). Harmless but `ORDER BY Ledger.V_SNo` vs `SeqNo` difference on rerun. | LOW | Keep 21-char helper; add `SeqNo = V_SNo` on insert to mirror VB6 log ordering (same SQL, extra col). |
| G6 | **TDS LedgerTDS insert** | FaVrEnt `FrameTDS`: per-line `TDSCode/TDSDrCode/ONAMT/TDS/TDSAMT/TDSPOST` → `INSERT INTO LedgerTDS (DocId,V_SNo,Site_Code,v_Prefix,V_DATE,TDSCode,TDSDrCode,TDSYN,ONAMT,TDS,TDSAMT,TDSPOST,TDSDocId,TDSV_SNo, LogSite_Code)` + auto contra-voucher `V_Type='TDS'` with `Chq` not allowed. | `fa_voucher.py:_post_line_tds` matches: validates `TDSCode/TDSDrCode`, `tds_amt = tds_amt(onamt,tds_pct)`, creates `post_voucher([TDS_Dr, TDS_Cr])` with `vtype='TDS'`, then `ledgertds_insert` with `LogSite_Code` — OK. Gap: missing `TDSYN` default `'Y'`, `TDSPOST` default `''`, and `TDSV_SNo` always 1 (VB6 may vary). Also `fa_tds_ops:tds_detail` filters only `RTRIM(TDSDrCode)` without `LogSite_Code`. | LOW | Add `WHERE LogSite_Code=?` to `tds_detail`; keep SQL column names identical. |
| G7 | **menuHelp Flag / UPrivilege check** | `FaVoucher.bas:Proc_7_1` → `SELECT Param_Str AS UPrivilege FROM menuHelp WHERE UserName='<u>' AND CompCode='<c>' AND [Option]='Voucher Entry'` then `MemVar_1F92E80=UPrivilege`; `MDI fame_Click` same with `fame+index`. VB6 TopCtrl enables Add/Edit/Del based on `Param_Str` (e.g. `A/E/D/P`). | Python has `core/menu_help.py` (not read here, but `fa_voucher`/`acgroup`/`ledger` never call it). No `Flag` check before insert/update/delete; `COM_TEST_FLAG` bypasses `db.execute` check. Any user can post voucher. | **HIGH** — workflow guard missing. | Reuse SAME SQL: add at top of `post_voucher/edit/delete` and `acgroup.insert/update/delete`, `ledger.insert/update/delete`: `SELECT Flag, Param_Str FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]=?` ; if `Flag<>'Y'` or `Param_Str` not containing `A/E/D` raise `PermissionError`. No schema change. |
| G8 | **BeginTrans/Commit parity** | FaChqClear `BeginTrans … Execute Update Ledger Set Chq_No/Chq_Date/Clg_Date Where DocID+V_SNo[+AmtCr+ContraSub] … CommitTrans / RollbackTrans`; FaGrEnt `TopCtrl1_eSave` uses recordset `Requery/Find`. | Python `fa_voucher.py:post_voucher` is `try: … commit else rollback` on one `cn` — equivalent to `BeginTrans`. `fa_voucher:cheque_mark_cleared` is single `UPDATE` without transaction — VB6 bulk grid commit (multi-row) not replicated. | MEDIUM | For bulk clear, wrap `cheque_mark_cleared` batch in same `cn` with `BEGIN TRAN` semantics (Python `cn.commit/rollback`). |
| G9 | **FaReports missing reports** | VB6 has 20+ reports: `Ledger, Ledger Deb/Cred, Trial Balance, Cash/Bank Book, Journal, Annexure, Bank Register, Ageing Debtors/Creditors, Cheque Cleared/Not Cleared, Outstanding, Bill Wise Outstanding, Detailed Trial Ledger, Roz Namcha, Interest Ledger, AcCheckList` etc with `DGSite` site picker and `FAENVIRO` Tagada headers. | Python `fa_voucher`+`fa_reports` covers 7-11: `trial_balance/profit_and_loss/balance_sheet/cash_and_bank/bank_register/journal/daily_summary/aging/ledger_with_opening/bank_reconciliation/cash_flow/fund_flow`. Missing: `Interest Ledger, Annexure, Outstanding (non-bill-wise), Detailed Trial Ledger with narration, Roz Namcha (daily cash book with MTD), AcCheckList, Reference, Non Transaction`. | MEDIUM | Keep SAME SQL: implement missing with `SELECT … FROM Ledger WHERE LogSite_Code=? AND V_Date BETWEEN ? AND ?` ; keep TTX field-def path `MemVar_1F923B0\*.TTX`. |
| G10 | **YearEnd OPBAL generation** | VB6 **does not** generate Ledger OPBAL — it clones `Company` row (`MAX(Comp_Code)+1`) + `menuHelp/menuHelp1` + `Voucher_Prefix` (per V_Type 0-balance) + `UserPermission`. | Python `year_end.py:carry_forward_balances` mutates `SUBGROUPCURRBAL/ACGROUPCURRBAL V_Date` in place (data-destructive) + `reset_budget` deletes Site_Code budget. Destructive vs VB6 snapshot. | **HIGH** | Restore VB6 workflow: generate new `Company` row (same INSERT verbatim), then replicate Python `carry_forward` as *non-destructive* report only; or guard `carry_forward` behind `if VB6 YearEnd already cloned Company then skip V_Date bump`. At minimum add `where LogSite_Code=?` to UPDATEs. |
| G11 | **TopCtrl toolbar workflow mismatch** | VB6 `FaGrEnt.TopCtrl1` : states `AEDP` (Add/Edit/Del/Print), `Find` (`LOGSITE_CODE OR HO`), `Save` validates `GroupHelp` duplicate, sets `Enabled` per row. `FaVrEnt.TopCtrl1` similarly. | Python UIs: `fa_ledger_ui.py` has New/Edit/Refresh/Exit (no Delete/Find/Print, no TopCtrl state), `fa_voucher_ui.py` has +Line/-Line/Post (no Add/Edit/Del/Save toggle, no edit-lock `Enabled=False` for `Txt(0)/Txt(4)`). | MEDIUM | Backend fix first; UI: add `QToolBar` mimicking TopCtrl `AEDP` mapping to `menuHelp Flag`, wire `Find` to `SearchCode` SQL. |
| G12 | **DATELOCK / negative cash** | FaEnviro flags `DateLock`, `NegativeCashBalance`, `CreditLimit/DebitLimit` checked before voucher post (global_96). | Python `year_end.check_datelock` exists but **never called** in `post_voucher`. Cash negative guard absent. | MEDIUM | Insert at top of `post_voucher`: `SELECT TOP 1 flag FROM DATELOCK WHERE SDate <= ? AND EDate >= ? AND flag=1` ; if locked raise; if `NegativeCashBalance<>'Y'` and `GroupNature` cash/bank would go negative, block. SAME SQL verbatim. |
| G13 | **Ledger Ref/Adj reconciliation** | VB6 `FRAMEADJUST` does `AmtCr - SUM(LEDGERADJ.Cr WHERE DocId2)` live; `LEDGERREF` uses `AgRefType` in key. | Python `pending_adjustments` SQL drops `LogSite_Code` filter and `eliminates` `DocId1` side; `adj_pending` sums `DocId2 OR DocId1` correctly but `ledgeradj_insert` guard calls `adj_pending(docid2)` only. Partial. | MEDIUM | Align to VB6: `SELECT l.AmtCr, ISNULL((SELECT SUM(a.Cr) FROM LEDGERADJ a WHERE (a.DocId2=l.DocId AND a.V_SNo2=l.V_SNo) OR (a.DocId1=l.DocId AND a.V_SNo1=l.V_SNo)),0)` already in `adj_pending`; ensure `pending_adjustments` also OR branch with `LogSite_Code` param. |

---

## 4) Fixed Workflow (EXACTLY VB6 same workflow, SAME SQL)

### 4.1 Voucher post — fixed sequence

```python
# 1) Privilege + DateLock (VB6 Proc_7_1 + FaEnviro)
rows = db.query("SELECT Param_Str AS UPrivilege, Flag FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]='Voucher Entry'", (user, comp), cn=cn)
if not rows or ('A' not in rows[0].UPrivilege and rows[0].Flag != 'Y'): raise PermissionError
if check_datelock(vdate): raise ValueError("Date locked")

# 2) NCAT routing (VB6 FaVoucher.bas)
ncat = db.query("SELECT NCAT FROM VOUCHER_TYPE WHERE V_TYPE=? AND (LogSite_Code=? OR LogSite_Code='HO')", (vtype, SITE_CODE), cn=cn)
if not ncat: raise ValueError("Voucher Type not found")
# branch: CNT/JV/PMT/RCT → FaVrEnt ; else OPBAL/PBILL/etc (unchanged)

# 3) Prefix + numbering (VB6 Voucher_Prefix)
prefix = db.query("SELECT TOP 1 Prefix FROM Voucher_Prefix WHERE V_Type=? AND ? BETWEEN Date_From AND Date_To AND (Site_Code=? OR Site_Code='HO') AND (LogSite_Code=? OR LogSite_Code='HO') ORDER BY Date_From DESC", (vtype,vdate,SITE_CODE,SITE_CODE), cn=cn)
vno = db.query("SELECT ISNULL(MAX(V_No),0) FROM LedgerM WHERE V_Type=? AND v_Prefix=? AND Site_Code=? AND LogSite_Code=?", (vtype,prefix,SITE_CODE,SITE_CODE), cn=cn) # fallback Ledger, then Start_Srl_No
docid = f"D{SITE_CODE}{vtype.ljust(5)}{prefix.ljust(5)}{str(vno).rjust(8)}"  # 21 char

# 4) Dr==Cr + zero guard + SubCode HO-fallback validate
tot_dr/tot_cr → raise if mismatch; for sc in lines: db.query("SELECT s.SubCode, s.GroupCode, a.GroupNature FROM Subgroup s JOIN Acgroup a ON a.GroupCode=s.GroupCode WHERE RTRIM(s.SubCode)=? AND (s.LogSite_Code=? OR s.LogSite_Code='HO')", (sc,SITE_CODE))

# 5) cn = db.connect(); try: cur.execute("INSERT INTO LedgerM … LogSite_Code", …); for sno,l in enumerate(lines,1): cur.execute("INSERT INTO Ledger … LogSite_Code …"); _update_currbal(cn, sc, dr, cr, vdate)  # per V_Date, LogSite_Code
# 6) LEDGERREF per line + LEDGERADJ delete+reinsert + LEDGERTDS + LedgerLog/LedgerMLog + Voucher_Prefix Start_Srl_No + LastVoucher — same SQL, add LogSite_Code param
# 7) Emit same TTX print path via fa_voucher: FF1E88 / 11ABBE0 joins with VOUCHER_TYPE.LOGSITE_CODE=LEDGER.LOGSITE_CODE
```

### 4.2 Bank/Cheque clearing — fixed bulk

```sql
-- VB6: BeginTrans; loop grid rows:
Update Ledger Set Chq_No='<trim(Chq)>',Chq_Date=<dt>,Clg_Date=<dt> Where DocID='<doc>' AND V_SNO=<n> [AND AmtCr=<amt> AND ContraSub='<sub>'] -- if V_Type='HPOST'
-- CommitTrans else RollbackTrans
-- Filter mirrors VB6:
-- pending  = WHERE Chq_No<>'' AND (Clg_Date IS NULL OR Clg_Date>GETDATE()) AND LogSite_Code=?
-- cleared  = WHERE Chq_No<>'' AND Clg_Date IS NOT NULL AND Clg_Date<=GETDATE() AND LogSite_Code=?
```

### 4.3 YearEnd — restore VB6 clone

```sql
-- Keep existing python carry_forward as utility, but default YearEnd run does VB6 steps:
Select * From Company Where Comp_Code=? ;
Select Max(Cast(Comp_Code As Integer))+1 As Code From Company;
Insert into Company (Comp_Code,Comp_Name,CentralData_Path,Repo_Path,Start_Dt,End_Dt, … CYear,PYear,FGLNO,SerialKeyNo,SiteCode,LogSite_Code) Values (?, …, DateAdd(Y,1,Start_Dt), … , ?, ?, SITE_CODE, SITE_CODE);
Update Company Set ActiveEpabx='' Where Comp_Code=?;
Select * From menuHelp Where CompCode=? → INSERT INTO menuHelp (CompCode,UserName,…,Flag) VALUES (NEW_CODE,…);
-- same for menuHelp1, Voucher_Prefix (Prefix=YYYY, Start_Srl_No=0), UserPermission
```

### 4.4 AcGroup / SubGroup save

```sql
-- Guard:
SELECT Param_Str AS UPrivilege, Flag FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]='Group Accounts' -- or Ledger Accounts
-- Validate:
Select GroupHelp From AcGroup Where GroupHelp=? AND (LOGSITE_CODE=? OR LOGSITE_CODE='HO')
Select GroupCode,GroupName,MainGrCode,Nature,AliasYN From AcGroup Where GroupCode=?
-- Insert uses same columns (ID+1 from MAX(ID), Site_Code, LogSite_Code)
```

---

## 5) Frontend vs Backend Debug Notes

### Backend (core) — required patches

- [ ] **P0** `core/fa_voucher.py:next_vno` — add `AND LogSite_Code=?` to all 3 SELECTs and UPDATE.
- [ ] **P0** `core/fa_voucher.py:post_voucher` — prepend `menuHelp` + `DATELOCK` query; subcode lookup add `(LogSite_Code=? OR 'HO')`; `cheque_pending/cleared` add `AND l.LogSite_Code=?`; reports in same file add `LogSite_Code` filter; `_update_currbal` caller already per `V_Date` OK but `SELECT SUBGROUPCURRBAL WHERE SubCode=? AND LogSite_Code=? AND V_Date=?` (done) — ensure `ACGROUPCURRBAL` chain also per `V_Date`.
- [ ] **P0** `core/ledger.py` — add `AND (LogSite_Code=? OR LogSite_Code='HO' OR ISNULL(LogSite_Code,'')='')` to `get/search/list_all`; `insert/update` set both `Site_Code` and `LogSite_Code = SITE_CODE`.
- [ ] **P0** `core/acgroup.py` — `get/exists/list_all` add `(LOGSITE_CODE=? OR LOGSITE_CODE='HO')` ; `update/delete` add `AND (LogSite_Code=? OR LogSite_Code='HO')` to WHERE.
- [ ] **P1** `core/fa_ledger_ops.py` — `ledgerref_search`, `ledgertds_list/delete`, `ledger_list` add `LogSite_Code` filter; `pending_adjustments` add `OR (a.DocId1…)` and `LogSite_Code=?` branch; `subgroupcurrbal/acgroupcurrbal` already per `LogSite_Code+V_Date` correct.
- [ ] **P1** `core/year_end.py` — add VB6 `Company` clone functions `year_end_company_clone(comp_code, cn)` using verbatim SQL; change `carry_forward_balances` UPDATEs to `WHERE LogSite_Code=?` (already) but make caller choose destructive vs snapshot; add `reset_voucher_prefix` mirroring VB6 Voucher_Prefix insert.
- [ ] **P1** `core/fa_reports.py` — every `LEDGER` aggregation add `WHERE LEDGER.LogSite_Code=?` (param SITE_CODE); `bank_reconciliation/ledger_with_opening` already scoped by SubCode but add `AND LogSite_Code=?`.

### Frontend (ui) — required patches

- [ ] `ui/fa_ledger_ui.py` — Replace `_LedgerMasterBridge` toy fields with full `SubGroup` columns (Add `GroupNature/Nature/Category/CityCode/PAN/GSTIN/CreditLimit/Days/ActiveYN`); wire `TopCtrl` pattern: `Add→ClearForm+Enable Txt(0), Edit→Load+Lock GroupCode, Delete→Check LEDGER COUNT(*) guard (FaVoucher Proc_7_3), Save→call core with cn, Find→SearchCode SQL, Print→AcGroup TTX`. Add `LOGSITE_CODE` display chip.
- [ ] `ui/fa_voucher_ui.py` — Extend grid to include `Narration/Chq_No/Chq_Date/Clg_Date/AgRefNo` per line (match VB6 Txt arrays); add `TopCtrl1_eSave` `FindMove` equivalent (Voucher find dialog with `V_No` BETWEEN, V_Date, Party combo); add live `Dr==Cr` color (green=balanced, red=unbalanced) and disable Post until balanced; add `menuHelp` Flag gate before Post/Edit/Delete; add `BankReconDialog` tabs `Cleared/Un-Cleared/All` with `Clg_Date` editable and bulk `Update Ledger Set … Where …` transaction.
- [ ] Both — show `U_Name/U_EntDt/U_AE` footer (`LblUser/LblLDt`) from last `LedgerLog` SeqNo.

### Verification command (after PATCH, before claim)

```bash
pytest PYTHONE/tests/test_fa_*.py -q
python -m PYTHONE.core.fa_voucher --selftest  # Dr==Cr, HO fallback, DocId 21-char
```

---

## 6) Raw SQL Reference — copy-paste parity

```sql
-- HO-fallback used everywhere in VB6
WHERE (LOGSITE_CODE=? OR LOGSITE_CODE='HO')
-- SubGroup HO fallback variant
WHERE (s.LogSite_Code=? OR s.LogSite_Code='HO' OR ISNULL(s.LogSite_Code,'')='')
-- Ledger print exact (VB6 11ABBE0)
SELECT … FROM (((LEDGER LEFT JOIN LEDGERM ON LEDGERM.DOCID=LEDGER.DOCID) LEFT JOIN SUBGROUP ON SUBGROUP.SUBCODE=LEDGER.SUBCODE) INNER JOIN VOUCHER_TYPE ON (VOUCHER_TYPE.V_tYPE=LEDGER.V_tYPE AND VOUCHER_TYPE.LOGSITE_CODE=LEDGER.LOGSITE_CODE)) LEFT JOIN LEDGERTDS LTDS ON (LTDS.TDSDRCODE=LEDGER.SUBCODE AND LEDGER.DOCID=LTDS.DOCID) WHERE LEDGER.V_PREFIX=? AND LEDGER.V_TYPE=? AND LEDGER.V_NO BETWEEN ? AND ? ORDER BY ledger.v_no, LEDGER.V_SNo
-- Cheque clear bulk (VB6 130DE…)
Update Ledger Set Chq_No=?, Chq_Date=?, Clg_Date=? Where DocID=? AND V_SNO=? [AND AmtCr=? AND ContraSub=?]
-- Privilege
SELECT Param_Str AS UPrivilege, Flag, Module_Name FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]=?
-- Prefix
SELECT TOP 1 Prefix FROM Voucher_Prefix WHERE V_Type=? AND ? BETWEEN Date_From AND Date_To AND Site_Code=? ORDER BY Date_From DESC
-- AcGroup Find
Select GROUPCODE As SearchCode,GroupName,GroupNature,Nature FROM AcGroup Where (LOGSITE_CODE=? OR LOGSITE_CODE='HO') AND AliasYN<>'Y' Order by GroupName
```

---

*Report path:* `C:\Users\PC\Desktop\New folder (3)\MODULE_FIX_PLANS\FODER\PYTHONE\COMPARE_WORKSPACE\FINANCE_COMPARE.md`  
*Generated by side-by-side full read of FaVoucher.bas + FaGrEnt/FaVrEnt/FaChqClear/FaReports/frmYearEnd + MDI 315-492 + moondata.sql + fa_voucher/fa_ledger_ops/ledger/acgroup/fa_reports/fa_tds_ops/year_end + fa_voucher_ui/fa_ledger_ui.*
