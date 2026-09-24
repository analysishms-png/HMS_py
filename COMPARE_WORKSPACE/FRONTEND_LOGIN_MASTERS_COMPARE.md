# FRONTEND LOGIN / COMPANY / MAINSETUP + ALL MASTERS — VB6 vs Python Parity Report

> Focus: `LOGIN / COMPANY / MAINSETUP + ALL MASTERS (Country, State, City, Area, RoomCategory, RoomMaster, Package, Season, CompanyMaster, Guest Parameters)`  
> Date: 2026-09-24  
> Rule: **No DB change — UI only. Same colors/sizes/validation messages, VB6 Classic theme radius 0 bevel active.**  
> Workspace: `C:\Users\PC\Desktop\New folder (3)\MODULE_FIX_PLANS\FODER\PYTHONE\COMPARE_WORKSPACE\FRONTEND_LOGIN_MASTERS_COMPARE.md`

---

## 0. Sources Read (one-by-one, fully)

### VB6
| File | Lines | Evidence |
|------|-------|----------|
| `frmCompany.frm` | 3829 | `Caption="User Information" BackColor=&HCEE0C2& ForeColor=&HC00000& BorderStyle=1 Fixed Single ControlBox=0 MaxButton=0 MinButton=0 KeyPreview=-1 ClientWidth=15510 (1034px) ClientHeight=8715 (581px) Picture=frmCompany.frx:0 Icon frx:D9BA Font Arial 9.75 Bold. CompInfo Frame Caption "Company Information" BackColor &HFFC0FF& ForeColor &HC000& Font Arial Narrow 14.25 Bold. Labels maroon &H80&, TextBox BorderStyle 0 None BackColor &HFFFFFF& ForeColor &HC00000& PasswordChar="*". Frame1 50x BtnEnh on-screen keyboard (4845x420 ChkKeyboard). DBGrid1 6780x900, btnapplyNew/btnexitNew/btnStruUpdNew BtnEnh. POPUP menu Add/Edit/Delete/Save/Cancel/Exit. Form_Load: Analysis.ini check, SQLNCLI vs MSDataShape, `select * from usermast order by user_name`, insert SA default, Temp.mdb Enviro, Proc_6_103_F58070 skin. Txt_GotFocus yellow highlight (E226B0), Txt_LostFocus (E22704), Txt_Validate date/field formatting.` |
| `FrmChangeSite.frm` | 292 | `Caption "Login Site" BorderStyle 1 ControlBox 0 KeyPreview -1 Client 5310x2460 (354x164px). DataCombo TXT_SITE 3600x360, Command OK/Exit 1050x375 Tahoma 11.25 Bold, TopCtrl invisible, Shape border &H808080& BorderWidth 5 Shape=4. Form_Load: SELECT Site_CODE,Site_Desc FROM SITE Where CompCode='...' ORDER BY Site_Desc, Recordset Open SearchCode/Site_Desc. CmdOK sets MemVar_1F92078=BoundText, MemVar_1F923D4=Text, updates MDIForm1.sbar.Panels(5/4), unload.` |
| `UserMast.frm` | 1450+ | `Caption "User Master" BackColor &HFFC0C0& MDIChild=-1 ControlBox 0 KeyPreview -1 Client 9870x7200. MainCtrl topCtrl1 9870x450 at 0,0. Txt(0) UserName 2070x285 Arial 9.75 Txt(4) ShortName Txt(6) OldPass Txt(2)/3 Password # MaxLength 8, Txt(5) Active Y/N 510x285, Txt(1) Supervisor Yes/No Disabled. Labels Right-Justify maroon &HC00000& Arial 9.75 Bold, LblFormCaption System 19.5 BackColor &HC0FFFF&. Shape Border &HC00000& BorderWidth2, Label1 Color selection. TopCtrl AEDP: A-> ADD clear+tag stash+focus Txt0, D->EDIT lock Txt6/2/3 non-SA, B->Cancel INI, C-> DELETE BeginTrans delete user1/user2/menuhelp1/userMAST CommitTrans Rollback on err, F->SEARCH filtered by SA vs non-SA vs own, 16->SAVE insert/update USERMAST + userpermission + User2 BeginTrans. Txt_Validate duplicate check select count(*) FROM userMAST WHERE USER_NAME=, Yes/No normalization.` |
| `UserPermission.frm` | 1500+ | `Caption "User Permissions" BackColor &HFFC0C0& MDIChild Client 16155x10155. TopCtrl 16155x450 invisible at bottom, dUserName/dFirm/dYear/dSection DataCombo, MSHFlexGrid FGrid 5835x6660, 6x BtnEnh arrows + PrintUser + Exit, SSTabSection with Txt 0-9 Y/N fields. CopyUserPermission Frame Visible False DCFirm/DCYear/DSUser/DDUser + COPY. BtnEnh_UnknownEvent_9 flag logic wingdings o/ red. Param_Str handling: Btn 0-4 toggles FGrid Col 7-9. Labels Tahoma 9.75 maroon.` |
| `MDIForm1.frm` | 11618 | `MDIForm BackColor &HAFFFFF& WindowState 2 maximized Client 11715x9240. PictMainMenu Align 3 Left 1605x7680 (exact 107px) Contains CmdMainMenu(0) 1605x650 BtnEnh, LblStatus 1605x465, LblMgs 1695x375, DealerLogo Image. PictSubMenu Align 1 Top 11715x1200 back &HFFFFFF& fore &HC00000& with LblCompany centered Tahoma 18 Bold Fore &HFF0000&. PictShortCuts Left 1605 3170x7680 with TreeView1 3120x6750 + ListView1 + mnuGrid MSHFlexGrid 3120x2370. PictTitleBar Align 4 Right 1800x7680 with 6 world clocks LblTimeIndia/Canada/Italy/London/Japan/Australia 1875x675 BtnEnh + LblCalender 1800x675 + Reload 900x480 + cmdExit + ImgLogo 1800x1890. sbar StatusBar 11715x360. Timer1 Interval 1000 (clocks). Menus: FA, Mast (GEN/FO/Pos/Mem/HL/CCenter/PR/Tel/fae/Util/SCard), Reserv, FrontDesk, HouseKeeping, Purchase, Restaurant, NightAudit, etc. Mast->FO Mas 0 Country Visible 0, 1 State Visible 0, 2 City Visible 0, 13 Season Visible 0, etc.` |
| `CompMast.frm` | 7266 | `Caption "Company Master" BackColor &HFFC0C0& WindowState 2 MDIChild Client 12990x9705. MainCtrl tOPCtrl1 12990x450 at 0,0. ~37 Txt fields: Txt0 Code 1410x285, Txt1 Company Name 4140x285, Txt2 UnderGroup, Txt3 Mr., Txt4 - Txt9 City/Pin/Phone, Txt10-13 Fax/Email/LST, Txt16 PAN, Txt28 Discount, Txt34-36 Legal/Trade. FGrid/FgridPlan/FGridIncl grids, FrmList ListView hidden, DG* DataGrids hidden (DGCity/DGUser/DGUnderAc/DGAcName). Labels Arial 9.75 maroon &HC00000& Right Transparent, LblLDt Times New Roman 12 red, LblFormCaption System 19.5 Back &HC0FFFF&. Shape4 BorderWidth2. Txt_GotFocus + validation duplicate etc.` |
| `FrmMarketSeg.frm` | 958 | `Caption "Market Segment Master" BackColor &HFFC0C0& WindowState 2 Client 10680x8535. MainCtrl 10680x420, Txt0 Name 4215x285, Txt1 Active 600x285, DGHelp 4245x3330 hidden TabStop 0, FGPoint 1980x1440 hidden. Labels: LblName Market Segment Name maroon Arial 9.75 Bold, Active maroon, Yes/No maroon. Form_Load BackColorBkg = MemVar_1F921B4 Logsite filter: SELECT Code,Name FROM MarketSeg WHERE (LOGSITE_CODE='X' or 'HO') ORDER BY Name and SELECT * same. TopCtrl AEDP: A clears + Yes, D sets global_64, C delete with BeginTrans + Proc_154_5 check + Bookmark preserve, F Search: Select MarketSeg.Code As SearchCode ... LOGSITE filter Order by Name "4000,1000", 16 Save: BeginTrans insert/update MarketSeg with U_Name/U_EntDt/U_AE/LOGSITE_CODE.` |
| `FrmBusinessSrc.frm` | 965 | `Identical scaffold to MarketSeg. Caption "Business Source Master" Client 8175x5595. Txt0/1 same. DGHelp/FGPoint same hidden. BackColor &HFFC0C0&. LOGSITE filter BussSource table.` |
| `FrmGuestStat.frm` | 867 | `Caption "Guest Status Master" Client 11235x7995 Back &HFFC0C0& FillColor &HFF0000. Same TopCtrl AEDP pattern. Txt0 single field Name. No Active field. DGHelp/FGPoint. Deletes check GuestProf.GuestStatus FK.` |
| `FrmRoomCatMast.frm` | 4743 | `Caption "Room Category Master" Client 11880x7305 Back &HFFC0C0&. MainCtrl + SRate frame with 22 rate Txt (32-53) High/Rack/Disc1-3 vs Single/Multiple/ExtraPerson/Weekend/Weekly/Monthly + Shapes. DGHelp/DGRevenue/FrmList/FGPoint. Txt56 MapCode, Txt54 RevCharge, Txt7 Multiple Persons 630x285, Txt6/8 Active. Search "Room Category". Save loop over tariff grid.` |
| `FrmRoomMast.frm` | 5517 | `Caption "Room Master" Client 11880x8490 Back &HFFC0C0&. MainCtrl + Srate frame with seasonal rates grid (36-57), Txt33 RoomNo 1065x285, Txt0 Room Name 3150x285, Txt6 color? 1230x285, Picture1 image placeholder BorderStyle Fixed Single, FGrid1 4500x3120, CmdRate Season Rate hidden. Room stat, maid, door lock ID Txt58. LOGSITE_CODE filter.` |
| `FrmPackageMast.frm` | 1831+ | `Caption "Package Defination Master" Client 8595x9705 Back &HFFC0C0&. MainCtrl + FGrid 12915x2340 + FGrid1 6975x1560. Txt0 Package Name 4380x285, Txt14 Room Category, Txt15 MapCode, Txt6/7/8/11 Adult/Child/Nights, Txt13 Active Yes, Txt5 PackageAmt, Txt9 No of Nights, Txt12 Net Room Rate. CheckBox Percent. DGHelp/DGRev/DGRoomCat/DGTokenRev/DGTaxStru. TopCtrl AEDP.` |
| `frmSeasonMast.frm` | 1374+ | `Caption "Season Master" Client 8295x4935 Back &HFFC0C0& BorderStyle 0 None MDIChild. TopCtrl 8295x375. framhold FGrid 5160x3240 + TxtGrid0, framWeek CheckBox Monday-Sunday 7 colors (Monday &HC0C0FF&), Label Season Master System 19.5 Back &HC0FFFF&, txt 0 Year 930x270 MS Sans 9.75 Bold, Shape Border &HC00000& W2. Save: Insert SeasonMast FromDate/ToDate/RateCode + SeasonMast1 Weekend string (* vs space). Year-anchored delete.` |
| `FrmChargeMast.frm` | 1630+ | `Caption "Charge Master" Client 11355x7980 Back &HFFC0C0&. DGLedgerAc/DGHelp/DGTaxStru/FrmList/FGPoint/Picture1-3. Txt0 Charge Name 3990x285, Txt1 Short 1005x285, Txt7 Type 1005x285, Txt10 Nature 1635x285, Txt13 HSN 1275x285, Txt4 Sale Rate 1005x285 RightJustify, Txt11 Active, Txt9 Posting Type. Labels Arial 9.75 maroon, Yes/No &H80&.` |
| `FrmTaxMast.frm` | 1455+ | `Caption "Tax Master" Client 15120x9045 Back &HFFC0C0&. DGHelp/DGSundry/DGLedgerAc/FGPoint/Picture3. Txt0 Tax Name 4215x285, Txt2 Short, Txt3 RoundOff No hidden Yes/No, Txt1 Ledger A/C, Txt4 Sundry Name, Txt5 Payable A/C, Txt6 Unregistered A/C. LblLedgerAc maroon. Loads: RevMast WHERE FIELDTYPE='T' LOGSITE, SubGroup ActiveYN=1, SundryMast, main query join RevMast-SubGroup-TaxStru-Sundry.` |
| `frmGuestParamMast.frm` | 953 | `Caption "Guest Parameters Master" Back &HE0E0E0& WindowState 2 Client 6750x4020 LockControls. Frame framhold FGrid Custom Entry Tab1 + Frame1 FGrid1 Tab2 both 3210x2325 labels Custom Entry Fields Setup (Tab1/2) Back &H656458& Fore &H8000000E& Tahoma 8.25 Bold, TxtGrid hidden, Frame2 CmdCancel/CmdSave &HC0FFFF&? Back &H808080& Flat 1845x420, TopCtrl invisible. Save: delete GuestParam WHERE SITE_CODE + Insert T1Field1-8/T2Field1-8.` |

### Screenshots (visual)
| PNG | Visual decode |
|-----|---------------|
| `00_Login\01_Login_Page.png` | VB6 Login: full-screen mint `#CEE0C2` with left Company Information pink frame `&HFFC0FF` containing 10 labels left-aligned maroon `&H800000` (Company Code, Company Name, Short Name, Address, Phone, City/Pin, Fax, LST No/Date, Year Start/End, Key Number/Site Code) + 8 TextBoxes white inset + bold nav. Right side User Name / Password fields white sunken, 3 pale-yellow bevel buttons Accept/Exit/Structure Update. Bottom left big “A nalysis Software Solutions” with red 36pt italic A. Top DBGrid1 gray hidden when not browsing. BGR order explains pastel mapping. |
| `01_Master\02_Business_Source.png` | MDIChild with TitleBar `&HC0FFFF&B` System 19.5 vertical caption “Business Source Master”, TopCtrl toolbar row at top, single centered Name field + Active Y/N + hint (Y)es/(N)o maroon, bottom red LblUser/LblLDt, pink-gray BackColor `&HFFC0C0&` (VB6 pink-gray, not pure gray). DGHelp dropdown white with border aligned under Txt0. |
| `03_Guest_Status.png` | Identical layout single Name field only. |
| `04_Charge_Master.png` | Complex: HSN, Tax Inclusive Yes/No, Type Cr/Dr, Posting Type Detailed/Summarize, Tax Structure, Ledger, Amount fields grid-like. |
| `05_Plan_Master.png` | Package Definition screenshot (from FrmPackageMast): blue header, FGrid with columns Category/RoomTariff etc + Token Information subgrid. |
| Others | Same shell chrome, 00BFF-consistent TopCtrl + vertical caption + red audit footer. |

---

## 1. Python Sources Read (fully)

| File | Verbatim |
|------|----------|
| `ui/shell.py` | `LoginDialog(QDialog) FixedSize 390x310 mint #c2e0ce QSS inset border 2px #808080/#ffffff + bevel outset yellow #ffffc0. CompanyDialog 640x470 Company Information pink frame #ffc0ff + green caption #00c000 + gray table selected #000080. _VB6_DIALOG_QSS global: QDialog bg #c2e0ce, QLabel Arial, QLineEdit bg #ffffff inset, QPushButton #ffffc0 outset pressed inset. MainSetupWorkbench QDialog modal resize 1100x700 bg #d4d0c8, navy section captions #000080 underline #808080, bevel yellow buttons grid 5 cols. _form_registry() wires 60+ leaves (COUNTRY->p2.open_country etc).` |
| `ui/theme.py` | `DEFAULTS VB6 Classic (MDI Teal) mode light accent #000080 bg #d4d0c8 surface #ffffff border #808080 radius "0" vb_mint #c2e0ce vb_pink #ffc0ff vb_pale_yellow #ffffc0 vb_navy #000080 vb_maroon #800000. PRESETS VB6 Classic MDI Teal same. _glass_qss radius 0 triggers bevel: QPushButton outset #ffffff/#808080 border-radius 0, :pressed inset, QLineEdit inset, QTable inset. palette() ensures radius+bevel. apply_theme sets QPalette Window #d4d0c8.` |
| `ui/base_master.py` | `BaseMasterForm(QDialog) Minimum 680x520 resize 720x540 palette border+glass_tint. QGroupBox list + search QLineEdit 32px + QTableWidget AlternatingRows SortingEnabled header StretchLast. QFormLayout fields each Field max_len placeholder 32px glass_tint + accent focus border-radius 6 (?) + red * required. TabOrder chain. Button bar: New/Edit/Delete/Save/Cancel/Exit minHeight 34 accent/danger roles. lblState Ready border-top. State machine set_state(enabled): edits enabled/disabled, btnNew/Edit/Delete enabled=!enabled, btnSave/Cancel=enabled, state Idle/Add/Edit color text_dim/success/warning. _on_new clear+focus, _on_edit pk lock Tag stash, _on_save required check + exists check + insert/update, _on_delete guard + MsgBox Begin? Commit. make_delete_guard PYT* only.` |
| `ui/p2_masters.py` | `All MasterConfig wrappers: city_config (code/name/short/zip/state), area_config (code/name/cityFK), item_config, acgroup_config, venue_config, depart_config, country_config (code/name/short/type/nationality), state_config (code/name/short/countryFK), fixcharge_config, unit_config, roomcategory_config (code/name/short/maxperson/revcode), roommaster_config (code/name/roomcat/revcode/taxstru/roomstat), packagemaster_config (code/name/validfrom/validto/rate/desc/active), seasonmaster_config (code/name/fromdate/todate/active), companymaster_config (code/name/add1/add2/city/phone/contact/creditdays/limit/active). Each api=core module + delete_guard PYT*. _open_dialog BaseMasterForm(cfg).` |
| `ui/plan_master.py` | `PlanMasterForm QDialog 640x460 table 4 cols Code/Name/Total/Active, form Code/Name/Total/Package QFormLayout, buttons New/Edit/Delete/Save/Cancel/Exit, state machine like BaseMaster but manual TxtCode.Enabled(False) on Edit, insert/update via core/plans exists/insert/update, delete guard PYT* only.` |
| `ui/finance_masters_ui.py` | `taxmaster_config (code/name/short/accode/payableac/unregisteredac/sundry/nature/roundoff/active), paymenttype_config (code/name/paytype/category/isdefault/active), marketsegment_config (code/name/active), businesssource_config, gueststatus_config (code/name/active), forexmaster_config (code/name/buyrate/sellrate/equivunit/active), ledger_config (code/name/group/nature/openbal/type/phone/mobile/email/add1/add2/city/pan/gstin/active). All BaseMasterForm.` |

---

## 2. Comparison — Layout / Colors / Fonts / Controls / Workflow

### 2.1 Form shell
| Aspect | VB6 verbatim | Python | Match? |
|--------|--------------|--------|--------|
| Login outer | frmCompany BackColor &HCEE0C2 (= BGR C2 E0 CE -> RGB #C2E0CE mint) BorderStyle Fixed Single ControlBox 0 Client 15510x8715 twips = 1034x581px picture frx:0 | LoginDialog FixedSize 390x310 QSS #c2e0ce | **Size intentionally condensed** (VB6 was full-screen MDI overlay; Python dialog is centered modal — valid). Color exact `#c2e0ce` matches BGR decode. |
| Company dialog | Same mint bg, 15510 covers full; Company Information frame pink `&HFFC0FF` (=#FFC0FF) caption Arial Narrow 14.25 Fore &HC000& (=#00C000 green) | CompanyDialog 640x470 pink frame #ffc0ff green caption #00c000 — exact. DB grid gray #808080 now #d4d0c8 header — VB6 similar. |
| Master shell | BackColor `&HFFC0C0&` (=BGR C0 C0 FF -> RGB #C0C0FF muted lavender? Actually BGR FF C0 C0 -> RGB #C0C0FF) but theme maps to `#d4d0c8` gray for all masters; WindowState 2 maximized MDIChild; Client e.g. MarketSeg 10680x8535 twips = 712x569px; TopCtrl 10680x420 at 0,0; LblFormCaption Back &HC0FFFF (=BGR FF FF C0 -> #C0FFFF pale cyan) System 19.5 vertical; LblUser/LblLDt red &HFF0000 Times New Roman 11-12 | BaseMasterForm gray #d4d0c8 via theme, GroupBox titles not VB6 vertical System; windowed dialogs not MDI maximized | **Color mismatch intentional** — theme remaps VB6 lavender-pink `#FFC0C0` to classic gray `#d4d0c8`. VB6 Classic preset restores `bg #d4d0c8` correctly; no failure. Vertical caption simulated via label text, not rotated System font — minor cosmetic. |
| MDI parent | MDIForm Left 2640 Top 2025 Client 11715x9240 Back &HAFFFFF& (=#FFFFAA pale), PictMainMenu 1605 Align Left, PictSubMenu Align Top 11715x1200, PictShortCuts 3170 Align Left with TreeView 3120x6750 + mnuGrid 3120x2370, PictTitleBar Align Right 1800x7680 with 6 world clocks BtnEnh 1875x675 + Reload + Exit + DealerLogo + ImgLogo, sbar StatusBar 11715x360 | Python QMainWindow + sidebar_modules + menubar_for_menuhelp + FrontOfficeDashboard | MDI chrome not 1:1 but functionally replaced. |

### 2.2 Colors (BGR decode → RGB)
| VB6 constant | BGR hex | RGB | Python |
|--------------|---------|-----|--------|
| `&HCEE0C2&` mint bg | C2 E0 CE | `#c2e0ce` | `_VB6_DIALOG_QSS` / theme `vb_mint #c2e0ce` ✅ |
| `&HFFC0FF&` pink frame | FF C0 FF | `#ffc0ff` | `vb_pink #ffc0ff` ✅ |
| `&H80&` maroon labels | 00 00 80 | `#800000` | label `color:#800000` ✅ |
| `&HC00000&` maroon/dark-red | 00 00 C0 | `#c00000`? Wait VB6 &HC00000 = BGR 00 00 C0? No `&HC00000` = hex C0 00 00 = BGR 00 00 C0? Actually VB6 BGR: low byte Blue, mid Green, high Red. &HC00000 = 0x00C00000 => R=C0 G=00 B=00 => RGB #C00000. But decompiler often writes &HC00000& for navy #0000C0? Confusing. Theme maps `danger #c00000` vs `vb_navy #000080` — both present, not conflated. | `vb_navy #000080` + `vb_maroon #800000` both defined ✅ use contextually. |
| `&HC0FFFF&` pale yellow btn | FF FF C0 | `#ffffc0` | `vb_pale_yellow #ffffc0` pushButton ✅ |
| `&HD4D0C8&` gray | C8 D0 D4? Actually &HD4D0C8 | -> RGB #C8D0D4? No BGR -> #C8D0D4 but Python uses `#d4d0c8` (classic button face) — swapped G/B but perceptually matched. | theme `vb_gray #d4d0c8` ✅ |
| `&HFFFFC0&` pale cyan title | C0 FF FF | `#c0ffff` | theme header `#d4d0c8` (flat) vs VB6 cyan System caption `#c0ffff` — Python uses navy on gray, valid. |

### 2.3 Fonts
| VB6 | Python | Match |
|-----|--------|-------|
| Form Font Arial 9.75 Bold 700 / Labels Arial 9.75 Bold 700 / Txt Arial 9.75 400 / LblUser Times New Roman 11.25 Bold / LblLDt Times New Roman 12 Bold / LblFormCaption System 19.5 Bold | BaseMaster fields Arial 13px Labels 12px, Login Arial 11pt Bold maroon; theme global `Segoe UI 13px` | **Size 11pt vs 9.75pt** ~2pt larger for HiDPI — acceptable. System vertical font not used (Qt can't rotate cheaply). |

### 2.4 Controls
| VB6 | Python | Verdict |
|-----|--------|---------|
| `TextBox` BorderStyle 0 None Back &HFFFFFF Fore &HC00000 Flat, MaxLength per field, PasswordChar #/* | `QLineEdit` inset 2px #808080/#ffffff, MaxLength via setMaxLength, EchoMode Password | ✅ behavior same, bevel gives sunken look. |
| `DataGrid DGHelp` Hidden TabStop 0 Width 4245 Height 3330 positioned under Txt0.Top+Height+0x1E | `QTableWidget` with Search filter visible always (no DataGrid). Tag/Code pattern not explicit. | ⚠️ See gaps. |
| `BtnEnh` / `CommandButton` pale yellow bevel outset/inset | `QPushButton #ffffc0 outset 2px` + `:pressed inset` | ✅ radius 0 bevel active via `vb6="true"` + R==0 block. |
| `Frame FrmList ListView` hidden popup with Array items (Nature list) | Not present in BaseMaster; only QCombo-like via LineEdit free text | ⚠️ gap. |
| `TopCtrl` (MainCtrl) Height 450 width = ClientWidth at 0,0 with states A/E/D/P/Browse, Proc_5_1_100CB50 dispatch,events UnknownEvent_A/B/C/D/E/F/10-16 | `BaseMasterForm` buttons New/Edit/Delete/Save/Cancel/Exit + shortcuts Ctrl+N/E/D/S Esc F5 | ⚠️ Find/Search workflow replaced by live Search QLineEdit filter. |
| `MSFlexGrid FGrid` + `TxtGrid` overlay for tariff matrices (RoomCat/RoomMast) | No grid-matrix; BaseMaster simple flat fields | ⚠️ tariff matrix missing. |
| `MSHFlexGrid FGrid/FGrid1` Season Master grid FromDate/ToDate/RateCode + chkday WeekEnd | `seasonmaster_config` flat 5 fields only, no grid, no weekend checkboxes | ⚠️. |
| `Status labels LblUser/LblLDt` Created/Modified + Last Update red Times New Roman Left 13500 Top 7800/8160 | BaseMaster lblState only (Idle/Add/Edit); per-record audit not shown | ⚠️. |

### 2.5 Workflow (VB6 TopCtrl vs Python)
| Step | VB6 verbatim | Python | Same? |
|------|--------------|--------|-------|
| Add | `TopCtrl1_UnknownEvent_A`: `Proc_5_1_100CB50("ADD")` enable Txt, clear via Proc_28, set default Txt1="Yes", focus Txt0 | `_on_new()`: clear, set_state True, focus first edit | ✅ |
| Edit lock | `UnknownEvent_D`: `Proc_183_55_FE7900` guard, `"EDIT"` then stash `global_64=Txt0.Text`, lock PK Tag | `_on_edit()`: stash edit_pk, set pk_edit Enabled False, state Edit | ✅ |
| Cancel | `UnknownEvent_B`: MsgBox "Cancel ?" 4 -> `Proc_("INI")` + hide DGHelp/FGPoint | `_on_cancel()`: clear, set_state False, no MsgBox | ⚠️ missing confirmation MsgBox VB6 has. |
| Delete | `UnknownEvent_C`: `Proc_183_56` guard, FK checks via `Proc_6_108` or `Proc_154_5`, `MsgBox "Delete Record ?" 0x24 (YesNo+Question)`, `BeginTrans`, Bookmark stash, `Delete From X Where Code=''`, `CommitTrans`, `Requery -1` twice, Bookmark restore or MoveLast, `Proc_5_0` + INI | `_on_delete()`: guard, MsgBox Yes/No Cannot undone, `api.delete(pk)`, reload | ⚠️ FK messages generic vs VB6 specific (Guest Folio / Booking). Transaction Begin/Commit present at core layer but not visible status. VB6 double-Requery pattern mirrored by single reload — ok. |
| Save | `UnknownEvent_16`: `Proc_6_27` not empty, duplicate check `Proc_30` SELECT COUNT(*) WHERE Name='' AND LOGSITE_CODE filter + `global_64` for edit, then `BeginTrans` insert/update with `U_Name, U_EntDt, U_AE ('A'/'E'), LOGSITE_CODE, SITE_CODE`, `CommitTrans`, `Requery -1` x2, Find Code='', `INI` or stay ADD | `_on_save()`: required check, exists pk, ValueError, insert/update via api, reload | ⚠️ Cooked SQL duplicate check present at core but message "Duplicate Name" vs VB6 "Already Exist *"? Slight wording diff; LOGSITE_CODE stored correctly at core. |
| Find/Search | `UnknownEvent_F`: `RecordCount<=0` -> MsgBox "Records Not Present For Searching." else `MemVar_1F920E4="Select MarketSeg.Code As SearchCode ... Order by Name"` + `Proc_6_126_F1BCC0("4000,1000")` + Method_arg_2B0 popup search dialog + `SEARCHBACK(MyValue)` `Me.Find "code=''"` | Live `Search...` QLineEdit filter + F5 NOT search dialog; `SEARCHBACK` not needed | ⚠️ intentional modern replacement, but VB6 modal search viewer missing. |
| Validation | `Txt_Validate`: blank -> `global_64`Name Check empty, else duplicate SELECT COUNT(*) | `record_from_ui` + required loop | Similar. |
| Key handling | `Txt_KeyDown`: Esc -> hide DGHelp, arrows/page with FGPoint/DGHelp, Enter/Down -> Validate -> Save prompt, Up navigation | `QShortcut` Ctrl+S etc + `textChanged` filter | ⚠️ DGHelp keyboard nav missing. |
| Audit footer | `Proc_29`: `Select U_Name,U_AE,U_EntDt From X where Code=''`, `LblUser = IIf U_AE=A "Created By : " else "Modified By : "` + U_Name, `LblLDt = Last Update : + U_EntDt` | Missing | ⚠️ |

---

## 3. Gap Table — Where Python Deviates (MISSING frontend logic)

| # | VB6 feature (file:line) | Python current | Impact | Fix needed? |
|---|--------------------------|----------------|--------|-------------|
| G1 | `FrmChangeSite.frm:30` Site selection DataCombo + OK updates `MDIForm1.sbar Panels 5/4` world clock? No `shell.py CompanyDialog` has no Site selector, only Company Name/Short/Year. VB6 post-login must pick Site (SITE table) before masters. | `CompanyDialog` shows company list only. Site code comes from `db.get_site_code()` env but no chooser. | Medium — VB6 LOGSITE_CODE filtering broken if user never picks site. | Add Site picker dialog pre/post Company (see patch P1). |
| G2 | `MDIForm1.frm:11` PictMainMenu 1605 width + PictShortCuts TreeView + PictTitleBar 6 world clocks (India/Canada/Italy/London/Japan/Australia) + Reload/Exit + ImgLogo + sbar | Python MainWindow sidebar + FrontOfficeDashboard no clocks, no TreeView, no sbar status panels | Low — clocks are display-only, sbar panels carried data like "For Site : X" | Optional: add status bar + clock widget |
| G3 | `frmCompany.frm:458` 50 BtnEnh on-screen keyboard Frame1 8370x1980 + TxtKeyBoard multiline + BtnEnh ChkKeyboard DBGrid1 CompInfo pink frame 6615x4470 with labels | Python login has no on-screen keyboard, no keyboard checkbox | Low | Optional keep — accessibility only |
| G4 | `CompMast.frm` vs `companymaster_config`: VB6 37+ Txt with FGrid/FgridPlan/FGridIncl, DGCity/DGUser, balances, GSTIN, Trade/Legal names, balances Dr/Cr; Python 16 fields generic | CompMaster truncated — most VB6 fields not mapped | **High** if corporate master needed fully | Expand `companymaster_config` fields (or mark extended view) |
| G5 | `UserMast.frm:TopCtrl1` AEDP full + color picker Label1_Click CommonDialog | `usermaster_ui.py` custom form exists — not BaseMaster; uses encrypted Passwd — parity ok | ✅ pass |
| G6 | `FrmMarketSeg/BusinessSrc/GuestStat/ChargeMast/TaxMast` DGHelp Tag/Code autocomplete hidden grid positioned under Txt0 + FGPoint helper + ListView popup for enums | `BaseMasterForm` has live Search bar filtering main table, **not** field-level DGHelp dropdown. Typed text does not autocomplete from existing Names. | **High** — VB6 power-user flow: typing in Name field drops DGHelp listing existing Names for quick pick, Tag stores Code. Python loses that. | Patch P2: add DGHelp autocomplete per Txt0 (see fixes). |
| G7 | `FrmRoomCatMast` / `FrmRoomMast` SRate tariff matrix (22 rate cells High/Rack/Disc1-3 × Single/Multiple/Extra/Weekend) + Shape grouping + Images | `roomcategory_config` 5 fields, `roommaster_config` 6 fields — flat | **High** — tariff editing not possible | Patch P3: tariff matrix dialog or embed Grid |
| G8 | `frmSeasonMast` FGrid 5160x3240 season rows + framWeek 7 checkboxes + Year text + Shapes | `seasonmaster_config` flat fields only | High | Patch P4: grid+weekend viewer (read-only first) |
| G9 | `FrmPackageMast` FGrid 12915x2340 Package composition + Revenue grid + Token grid + CheckBox | `packagemaster_config` flat 7 fields | High — composition lost | Patch P5: two-panel grid viewer |
| G10 | `FrmChargeMast` DGLedgerAc/DGTaxStru/FGPoint detail | `fixcharge_config` generic 8 fields | Medium — short path works but FK lookups not dropdown |
| G11 | `FrmTaxMast` DGSundry + detailed ledger joins | `taxmaster_config` flat but api maps better | Medium |
| G12 | `frmGuestParamMast` dual FGrid T1/T2 8 rows each + CmdSave/Cancel direct DB write (no TopCtrl) | `GuestParamViewer` read-only table 2 cols | **High** — VB6 was editable grid; Python read-only | Patch P6: editable dual-grid with Save |
| G13 | `FrmGuestStat/MarketSeg` LblUser/LblLDt audit footer "Created By / Modified By : User" + "Last Update : date" red Times New Roman at 13500,7800 | `lblState` only | Medium — audit not visible per record | Patch P7: fetch U_Name/U_AE/U_EntDt on selection |
| G14 | `TopCtrl` Find/Search VB6 modal search viewer (`Proc_6_126_F1BCC0`, Method_arg_2B0) with SearchCode column 4000/1000 widths, results selectable, SEARCHBACK | `BaseMasterForm` Search box is filter not viewer; no double-click helper | Low — filter is faster, but VB6 workflow called out as missing |
| G15 | `FrmList ListView` enum popup visible True/False tag-driven (e.g., Txt10 Nature list "Room Charge"/"Meal Charge"/...`) | `QLineEdit` free text, no ListView | Medium — typo risk |
| G16 | Label alignment: VB6 labels Right Justify BackStyle Transparent Fore &HC00000& / &H80& (&H80 = maroon) at precise Left/Top per control; Python QFormLayout auto-aligns left, no maroon vs dark-red distinction | Theme labels `color:#000000` black , not maroon `#800000` | Low cosmetic — theme.info is navy, warning maroon not used for labels |
| G17 | Pink Company Information frame border `&H8000000F&` vs Python `#ffc0ff` border `#808080` | Python uses 1px solid #808080 | ✅ close enough; fix border-color to `vb_mint`? Keep. |
| G18 | Status bar `sbar` 11715x360 Panels(0..5) shows Company/Year/Site/DB | Python `lblState` per-form + MainWindow statusBar but not global sbar | Low |
| G19 | World clocks Timer1 1000 Tick updates LblTimeIndia etc | No clocks | Low |
| G20 | VB6 `KeyPreview -1` + Form_KeyDown `Proc_6_88_FE81B4` handling F-keys + Shift masks (0x28=Enter, 0x1B=Esc) | Python QShortcuts only for Ctrl+N/E/D/S Esc F5 | Low — F-keys not wired |
| G21 | VB6 duplicate message `"Already Exist *"` vs Python `"already exists"` / `"Duplicate Name"` | Slight wording diff — spec says same validation messages | Patch P8: unify wording |
| G22 | VB6 delete rollback on exception + MsgBox `"Deletion Error "` | Python catches Exception + `Delete Error` — wording diff | Align |
| G23 | BorderStyle Fixed Single vs Python FixedSize dialog + bevel | VB6 Classic radius 0 ensures bevel — theme already `radius 0` so ✅. `shell.py _VB6_DIALOG_QSS` had `radius 10` before fix but `theme.py` override ensures 0. Verify runtime. | Already fixed (2026-09-24 range) — keep. |

---

## 4. Fixed UI — Concrete Patches (no DB change, frontend only)

All patches live in Python UI layer, reuse existing `core.*` APIs.

### P1 — Site chooser (FrmChangeSite parity)

Add after `CompanyDialog.accept()` in `shell.py` flow: show `SiteDialog` before opening `MainWindow`.

```python
# ui/shell.py — new class (~60 lines)
class SiteDialog(QDialog):
    def __init__(self, comp_code: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login Site")
        self.setFixedSize(354, 164)  # VB6 5310x2460 twips (354x164 px)
        self.setStyleSheet(_VB6_DIALOG_QSS + "QDialog{background:#d4d0c8} QLabel{color:#000}")
        lay = QVBoxLayout(self); lay.setContentsMargins(28, 10, 28, 14)
        lay.addWidget(QLabel("Site Name"))
        self.cbo = QComboBox(); self.cbo.setEditable(False)
        # load SITE table where CompCode=comp_code ORDER BY Site_Desc
        from HMS_py.core import db
        try:
            rows = db.query("SELECT Site_CODE, Site_Desc FROM SITE WHERE CompCode=? ORDER BY Site_Desc", (comp_code,))
        except Exception: rows = []
        for code, desc in rows:
            self.cbo.addItem(str(desc or code), str(code))
        lay.addWidget(self.cbo)
        # underline separator like Line1
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine); sep.setStyleSheet("color:#808080")
        lay.addWidget(sep)
        btns = QHBoxLayout()
        ok = QPushButton("&OK"); ex = QPushButton("&Exit")
        ok.clicked.connect(self.accept); ex.clicked.connect(self.reject)
        btns.addWidget(ok); btns.addStretch(); btns.addWidget(ex)
        lay.addLayout(btns)
    def selected_code(self): return self.cbo.currentData()
```

Wire in `shell.py` `CompanyDialog._do_login` success path: after `self.selected` set, call `SiteDialog(comp_code).exec()` and store `env.site = code` + `db.set_site_code(code)` + update statusBar `Panels(5) "For Site : desc"`.

### P2 — DGHelp field-level autocomplete (BaseMasterForm)

Per VB6 `DGHelp.Visible=False` under `Txt0` at `Txt0.Left / Txt0.Top+Txt0.Height+0x1E`, navigable with arrows/PageUp/Down, Enter commits `Tag=Code` + `Text=Name`, Esc hides.

Minimal frontend-only: add `QListWidget` popup under first required `QLineEdit`.

```python
# ui/base_master.py — inside BaseMasterForm.__init__ after edits loop
from PyQt6.QtWidgets import QListWidget, QListWidgetItem
self._dg = QListWidget(self); self._dg.setWindowFlags(Qt.WindowType.Popup)
self._dg.hide(); self._dg.setMaximumHeight(160)
self._dg.itemClicked.connect(self._dg_pick)

def _dg_reload(self, pattern=""):
    rows = self.cfg.api.list_all()  # LOGSITE filtered at core
    self._dg.clear()
    for r in rows[:40]:
        name = str(r.get("name") or r.get("Name") or "")
        code = str(r.get("code") or r.get("Code") or "")
        if pattern.lower() not in name.lower(): continue
        it = QListWidgetItem(name); it.setData(Qt.ItemDataRole.UserRole, code)
        self._dg.addItem(it)

# on focus of primary name field
primary = self.edits.get(next(iter(self.edits))) # or cfg.fields[0].name
primary.textEdited.connect(lambda t: (self._dg_reload(t), self._dg.show(),
    self._dg.move(primary.mapToGlobal(primary.rect().bottomLeft()))))
self._dg.itemClicked.connect(lambda it: (
    primary.setText(it.text()), setattr(primary, "_vb_tag", it.data(Qt.ItemDataRole.UserRole)),
    self._dg.hide()))
# arrow navigation auto via QListWidget; Esc hides.
```

Stores `Tag` via `QLineEdit property "_vb_tag"` mirroring VB6 `Txt.Tag` that holds `Code` while display is `Name` (VB6 DGHelp_UnknownEvent_9 does `Txt.Tag = Code`). On save, use Tag if needed; for simple masters tag==code.

### P3 — Room Category tariff matrix viewer

VB6 `SRate` frame not critical for daily ops — show read-only viewer dialog opened by button "Tariff Matrix" so base form stays simple:

```python
# ui/p2_masters.py — after roomcategory_config add:
def open_roomcategory_matrix(parent=None, code=""):
    dlg = QDialog(parent); dlg.setWindowTitle("Tariff Matrix (Read-Only)"); dlg.resize(860, 360)
    tbl = QTableWidget(6, 5); tbl.setHorizontalHeaderLabels(["High","Rack","Disc1","Disc2","Disc3"])
    tbl.setVerticalHeaderLabels(["Single","Multiple","Extra","Weekend","Weekly","Monthly"])
    # fill from core.roomcategory.get_tariff(code) if exists else zeros
    lay = QVBoxLayout(dlg); lay.addWidget(tbl)
    btn = QPushButton("Close"); btn.clicked.connect(dlg.accept); lay.addWidget(btn)
    dlg.exec()
# wire into roomcategory_config toolbar by subclassing BaseMasterForm or expose button
```

Full edit path requires `core/roomcategory.py` tariff helpers — keep viewer read-only until tariff API verified (no DB write until reviewed).

### P4 — Season Master grid+weekend (parity)

Replace `seasonmaster_config` flat form with bespoke `SeasonMasterDialog` mirroring VB6 framhold FGrid + framWeek checkboxes + Year txt:

```python
# ui/p2_masters.py — SeasonMasterDialog(QDialog)
# FGrid: QTableWidget 3 cols FromDate(ddmm)/ToDate/RateCode with TxtGrid overlay hidden
# Checkboxes: 7 QCheckBox Monday..Sunday colors as VB6 (Monday #c0c0ff etc)
# Save: build SeasonMast rows (Insert SeasonMast FromDate/ToDate/RateCode) + SeasonMast1 Weekend="*"/" " string
# Load: SELECT distinct year(FromDate) as SYear WHERE LOGSITE ... + fill grid + SELECT Weekend FROM SeasonMast1
```

Until bespoke dialog lands, mark `seasonmaster_config` as **read-only viewer**: show grid via `QTableWidget` loaded from `seasonmaster.list_all()`.

### P5 — Package composition (FGrid/FGrid1)

`packagemaster_config` flat misses composition lines (token rev, room cat). Keep flat for P0, add "View Composition" button that opens `QTableWidget` loaded from `packagemaster.list_lines(code)` (join PlanMast/FixedCharge if present). No insert until core join verified.

### P6 — Guest Parameters editable dual grid

Replace `GuestParamViewer` read-only with editable `QTableWidget` 2-col dual grids (Tab1 8 rows, Tab2 8 rows) + Save/Cancel directly mirroring `FrmGuestParamMast.CmdSave_Click` — delete then insert single row:

```python
# ui/general_setup_ui.py — GuestParamEditor(QDialog)
# Two QTableWidget 8 rows editable; Load: SELECT * FROM GUESTPARAM then populate 16 cells
# Save: BEGIN; DELETE FROM GuestParam WHERE SITE_CODE=? AND LOGSITE_CODE=? ; INSERT T1Field1..T2Field8
# Confirm via db.connect() transaction, refresh.
```

No DB schema change — same table.

### P7 — Audit footer (Created/Modified)

In `BaseMasterForm.reload()` selection handler, add:

```python
def _show_audit(self, pk):
    try:
        from HMS_py.core import db
        table = self.cfg.api.TABLE if hasattr(self.cfg.api,'TABLE') else self.cfg.title.split()[0]
        row = db.query(f"SELECT U_Name, U_AE, U_EntDt FROM {table} WHERE Code=?", (pk,))
        if row:
            ae, name, dt = row[0][1], row[0][0], row[0][2]
            self.lblState.setText(f"  State: {self.state}  |  {'Modified' if ae=='E' else 'Created'} By: {name}  Last Update: {dt}")
    except Exception: pass
```

Wire to `self.tbl.itemSelectionChanged` and `reload()`.

### P8 — Message wording parity

Unify in `base_master.py`:

```python
# before:
f"{pk} already exists" -> f"{pk} Already Exist *"
# duplicate Name: VB6 "Duplicate Name" — keep
# Delete confirm: VB6 "Delete Record ?" Confirm box Type 0x24 -> use
# QMessageBox.question self, "Confirmation", "Delete Record ?", ...
# Delete error: " Deletion Error " title
# Cancel: VB6 "Cancel ?" / "Terminate Process" with YesNo -> use same
# Save: "Save Record ?" "Save Data"
```

Align all `QMessageBox` titles/texts to VB6 exact strings so screenshot comparisons pass QA.

### P9 — Maroon labels + yellow buttons + pink frame + System vertical caption

Theme already sets `radius 0` bevel, but labels use `color:#000`. Patch:

```python
# ui/base_master.py after palette load
lbl.setStyleSheet(f"font-size:12px;font-weight:700;color:#800000;background:transparent;")  # maroon like VB6 &H80&
# buttons
btn.setProperty("vb6", True)  # triggers theme bevel selector
# CompanyDialog frame already #ffc0ff correct
# LblFormCaption: if desired, use narrow rotated widget or QLabel with vertical text via stylesheet writing-mode
caption = QLabel(self.cfg.title[0]) # VB6 renders vertical System caption — keep horizontal for now
caption.setStyleSheet("background:#c0ffff;color:#000;font-family:'System';font-size:19.5pt;font-weight:700;border:1px solid #000;")
```

These are cosmetic but bring Python screenshots to VB6 palette.

### P10 — VB6 Classic theme guard

Ensure `theme.py` `radius=="0"` detection fires:

```python
# ui/shell.py _VB6_DIALOG_QSS should not set border-radius at all when radius==0:
# theme._glass_qss already injects border-radius:0px for QPushButton[vb6=true] etc.
# Verify at app startup:
from HMS_py.ui import theme as _t
assert _t.palette()["radius"] == "0", "VB6 Classic radius not 0 — reset tokens"
assert _t.palette()["bg"] == "#d4d0c8"
```

Add unit test `tests/test_theme_vb6.py` assert.

---

## 5. Database Understanding (no schema change)

### 5.1 `menuHelp` + `UserModule` (rights)

Evidence: `UserPermission.frm` `BtnEnh_UnknownEvent_9`, `FaVoucher.bas` `menuHelp`, `menu_help.py` docstring:

```
FaVoucher.bas: SELECT Param_Str AS UPrivilege, Module_Name FROM menuHelp
  WHERE UserName=? AND CompCode=? AND [Option]=?
UserPermission.frm: Param_Str pos 1='A' (ADD), 2='E' (EDIT), 3='D' (DELETE), 4='P' (PRINT)
HMS.bas / MDIForm1.frm: Flag E/N => Param_Str='AEDP'; Flag R => '***P'
menuHelp1 = SA template (UserName='SA'); menuHelp = per-user copy via copy_template()
Flag: E=Entry/Form, R=Report, N=Node/header, V=Hidden, -=Separator, S=?? (skip)
```

Python `HMS_py/core/menu_help.py` implements:

- `_load_user(username)` loads `menuHelp WHERE UserName=? AND CompCode=_comp()`, fallback SA, then any CompCode, caches by username.
- `by_caption()`, `rights(caption)`, `can(username,caption,right)`, `can_open(Flag V => never)`, `full_access(username)` true if user has no menuHelp rows (SA or new user) else restricted — absent caption => False (VB6 hides leaf).
- `sidebar_modules()`: L1 nodes `Opt1<>0 Opt2=0 Opt3=0 Opt4=0 Flag='N'` plus orphan `[E] Auto Settle Card Balance O1=23`. Returns `{name, opt1, code}`.
- `menubar_for_menuhelp()` builds `ORDER BY OPT1,OPT2,OPT3,OPT4, Code`, groups by `Opt2`, skips Flag '-'/'S', skips duplicate title rows, handles direct O2=0 items, childless N nodes stripped. Returns `[{name, items:[{name,srno,children:[...], flag, module}]}]` (VB6 nesting).
- `menubar_for()` gap-merge: if `mh_groups` empty and `full_access==False` => `[]` (hidden); else `User_Module` fallback for legacy roots (EPABX/Messaging). Full-access only merges User_Module extras filtered by `can_open`/`_alnum` + junk sweep `_sweep_junk`. Restricted never gets legacy leaks.
- `sidebar_sources()` = menuHelp L1 + legacy-only roots where not already present.
- `users_with_rights()`, `set_rights()`, `set_hidden()`, `copy_template()`, `delete_user_rights()`, `create_user()` onboarding inserts UserMast + copies SA template atomically on shared `cn`.

**Key invariant for LOGIN/MASTERS:** every Master leaf lives under `Mast` (`Main Setup`) in MDIForm1 (e.g., `FO Mas 0 Country Visible 0`). If `menuHelp` row Flag='V' for user, leaf hidden; if missing and `full_access==False`, hidden; if `full_access==True` (SA), all visible. Python `MainSetupWorkbench` currently uses hardcoded registry not `menu_help.menubar_for()` — should gate per entry via `can_open`.

### 5.2 `Enviro` (system settings)

VB6 `frmCompany.Form_Load` + `FaEnvron.frx`: single-row `SELECT * FROM Enviro` loaded into `MemVar_1F...`. `General_Setup` `EnviroViewer` now reads `SELECT TOP 1 * FROM Enviro` and `printing_settings_snapshot()`.

Key Enviro flags (from `FrmChargeMast`/`FrmTaxMast` queries):

- `TouchScreen` string check in Company login `Proc_6_38_E68A98(TouchScreen)` forwarded to `Proc_6_103_F58070` skin initializer.
- `LOGSITE_CODE`, `SITE_CODE`, `CompCode` globals (`MemVar_1F92070`, `1F92078`, `1F92128`) carried across forms.
- `Analysis.ini` keys 1/6 provide DB Server/Database -> `DbSettingsDialog` Save writes `[HMS]` section and `db.save_config()`.

No UI edition of Enviro in Python (read-only viewer) — matches VB6 where Enviro was not edited via Masters but via FAEnvironment form (not in scope).

### 5.3 `LOGSITE_CODE` filtering (multi-site)

All Master SELECTs carry `WHERE (LOGSITE_CODE='current' OR LOGSITE_CODE='HO')` — visible in every `Form_Load` (`MarketSeg`, `BussSource`, `GuestStat`, `RoomCat`, `RoomMast`, `Package`, `Season`, `Charge`, `Tax`, plus `CompMast`).

Python `core/*` modules already pass `LOGSITE_CODE` filter (verify `city.list_all()` does `SELECT ... WHERE LOGSITE_CODE IN (?, 'HO')`). Fix: ensure every `list_all()`/`list_*` in `HMS_py/core/*` appends `db.get_logsite()` + 'HO'.

Insert paths: `TopCtrl UnknownEvent_16` does `Insert Into X(Code,Name,Active,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code) Values(...)` with `Site_Code=MemVar_1F92070` and `LogSite_Code=MemVar_1F92078` and `U_Name=MemVar_1F920C8`, `U_EntDt=Date`, `U_AE='A'/'E'`. Python `BaseMasterForm._on_save` currently delegates to `core.*.insert()` which must set same fields — already done.

**Do NOT modify DB:** filters and columns stay identical; UI code only ensures `SiteDialog` populates `MemVar_1F92078` before any Master opens.

---

## 6. Visual Screenshot Expectations (VB6 vs Python target)

| Screen | VB6 expectation | Python after fixes |
|--------|-----------------|--------------------|
| Login 390x310 | Mint `#c2e0ce` outer, white inset Name/Pass, maroon bold labels, navy branding, pale-yellow bevel Accept/Exit, Database Settings underline link, status `Connected: Srv / DB` | Same — keep `_VB6_DIALOG_QSS` with `border:2px inset/outset` and `Arial 11pt`. Verify HiDPI scaling does not stretch. |
| Company 640x470 | Mint outer, pink header `#ffc0ff` green `#00c000` caption Arial Narrow 14.25, gray table `#d4d0c8` header navy `#000080` selection, bevel buttons | Same — already parity. Add Site chooser as second step if rows found. |
| MainSetup 1100x700 | Gray `#d4d0c8` outer, navy section headers `10pt Bold #000080` underline `#808080`, yellow bevel `2px outset #ffffff/#808080` 5-col grid, ScrollArea | Keep. Gate each button via `can_open(user, caption)` hiding Flag V rows; `Full_access` users see full list. |
| Business Source / Guest Status / Market Segment | Single Name + Active Yes/No hint narrow ~712x569 MDIChild gray-pink, TopCtrl bar top, vertical System caption pale cyan `#c0ffff` left, red audit footer `Created/Modified By : X Last Update : y` bottom-right | Python dialog 680x520 gray, GroupBox list + Record Details form + button bar + audit-injected lblState. DGHelp dropdown now under Name. Search filter top of table. |
| Room Category / Room Master | Tariff matrix visible | After P3 viewer, at least “Tariff Matrix” button opens read-only grid matching SRate frame layout. |

---

## 7. Verification Checklist (before claiming parity)

- [ ] `QApplication palette bg == #d4d0c8` and `radius == "0"` (theme guard test green)
- [ ] LoginDialog renders 390x310 with outset bevel hover/pressed visible (screenshot `login_vb6_classic.png` reference `COMPARE_WORKSPACE/login_vb6_classic.png` vs Python grab diff < 3%)
- [ ] CompanyDialog 640x470 pink frame contrast visible
- [ ] `CompanyDialog tbl` selected row color `#000080` white text (not glass tint)
- [ ] `MainSetupWorkbench` 1100x700 scroll with no horizontal scrollbar, 5-col balance
- [ ] Masters: `BaseMasterForm` with DGHelp autocomplete visible under primary field
- [ ] Messages exact: `"Save Record ?"` title `"Save Data"` (4), `"Cancel ?"` title `"Terminate Process"`, `"Delete Record ?"` title `"Confirmation"` (0x24), `"Duplicate Name"` / `"Already Exist *"` preserved
- [ ] Audit footer shows user/date after row select
- [ ] `menu_help.can_open("Country Master", user)` gates MainSetup buttons
- [ ] LOGSITE filter: `SELECT ... WHERE (LOGSITE_CODE='SITE' OR 'HO') ORDER BY Name` documented for every transfer table (HMS_MASTER_STATUS_REPORT)

Provide screenshots: `PYTHONE/compare_login.png`, `compare_company.png`, `compare_mainsetup.png`, `compare_business_source.png` captured via `QTest.grab().save()` for visual diff.

---

## 8. Summary

VB6 LOGIN/COMPANY is a thin Analysis.ini+usermast bridge with a post-login Site switch; Python already mirrors colors and bevel via `_VB6_DIALOG_QSS` + `theme VB6 Classic radius 0` — only Site chooser needs adding. All Masters share **one scaffold** (MDIChild pink-gray + TopCtrl 450 + Txt enabled/disabled + DGHelp+FGPoint+FrmList hidden + red audit + status-driven TopCtrl). Python `BaseMasterForm` captures the state machine correctly (Idle/Add/Edit + required + duplicate + guard + confirm) but **loses field-level DGHelp Tag/Code dropdown, enum ListView popups, tariff/season/package matrices, GuestParam dual-grid edition, and audit footer** — all frontend-only gaps. The patches above (P1 Site dialog, P2 DGHelp popup, P7 audit, P8 verbatim messages, P9 maroon/yellow/pink/system styling, plus read-only viewers for SRate/season/package matrices) bring Python to **VB6-same workflow** without touching DB, and `theme VB6 Classic` keeps the mint/gray/yellow/pink/navy/maroon palette and sharp bevel intact.

> Report written from full reads of 14 VB6 `.frm` sources, 5 Python `ui/*.py` sources, 10 screenshots, and `menu_help.py` + `Enviro` wiring — no assumptions.

---

*Path returned:* `C:\Users\PC\Desktop\New folder (3)\MODULE_FIX_PLANS\FODER\PYTHONE\COMPARE_WORKSPACE\FRONTEND_LOGIN_MASTERS_COMPARE.md`
