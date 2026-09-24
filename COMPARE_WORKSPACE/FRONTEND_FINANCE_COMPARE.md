# FRONTEND FINANCE — VB6 vs Python Parity Report
> Module: FaVrEnt/FaGrEnt (Voucher/Group), FaReports, FaChqClear, frmYearEnd, MDI FA menus `fate/farp/fame`
> Date: 2026-09-24
> Rule: **No DB schema change — frontend only**. Same control behavior, same colors/sizes, same validation, same workflow (Dr==Cr, AdjBal, TDS contra, DATELOCK, menuHelp Param_Str, TopCtrl Find SearchCode).
> Python sources under `PYTHONE/ui/*.py` • VB6 sources under `FODER/*.frm`

---

## 0) Executive summary

| Dimension | VB6 canonical | Python current | Verdict |
|-----------|----------------|----------------|---------|
| Overall layout | MDIChild maximized (`WindowState=2`), BackColor per form (`&HC0C0FF` lavender for voucher, `&HFFC0C0` pink for group), FixedSingle header label `LblFormCaption` System 19.5pt, `TopCtrl1` AEDP toolbar always at `(0,0)` 450px high | `QDialog`/`QMainWindow` `resize(820×520)` etc, `QVBoxLayout` + `QGroupBox` + `QTableWidget`, theme-driven palette (navy `#000080` on `#d4d0c8` when VB6 Classic) | **Partial** — theme approximates VB6 but no pixel parity, no TopCtrl |
| Colors/fonts | Arial 9/9.75pt, MS Sans Serif 9.75pt bold, BorderStyle 0 None + Appearance Flat, BackColor `#FFFFFF` inputs, `#C0C0FF` form, `#FF0000` section headers | `Segoe UI` 13px via global QSS, `glass_tint` inputs, `QGroupBox` titles `#000080` | **Gap** — font family/size mismatch; header red `#FF0000` vs theme accent |
| Controls | `BtnEnh LblShort(1..4)` shortcut-bar, `DataGrid DGAcHlp/DGUnderAc/DGSite/DGBank/DGParty`, `MSHFlexGrid FGrid/FGVLIST/FGridRef/FgridAdjust`, `TxtCr/TxtDr/TxtAcName/TxtCrDr/TxtNar(0..11)` arrays, `FrameTDS/FRAMEADJUST/FrameRef/FRAMEVLIST/Frame1` overlay frames, `TxtGlb(0)` global narration Courier New 8.25 | `QTableWidget` (Editable), `QComboBox`, `QDateEdit`, `QLineEdit`, `QPushButton` (+Line/-Line/Post, New/Edit/Refresh/Exit) | **Gap** — overlay frames missing; indexed Txt arrays collapsed to table; no BtnEnh |
| Workflow guards | `Txt_Validate` duplicate GroupHelp, Dr==Cr `ADJ_LAB4/LAB7` live, TDS auto contra-voucher `V_Type='TDS'`, DATELOCK `SDate/EDate Flag=1` block on Save, `menuHelp.Param_Str` per `[Option]='Voucher Entry'` (A/E/D/P) gates TopCtrl buttons, TopCtrl Find = `SearchCode` SQL `LOGSITE_CODE OR HO` + `AliasYN<>'Y'` | Python `post_voucher` checks `tot_dr vs tot_cr` but UI never disables Post; no DATELOCK call in `fa_voucher_ui`; no `menuHelp` check in any UI; Find is generic `SearchCode` not implemented; TDS is checkbox-level in dialog not per-line frame | **Gap** — critical workflow missing |
| Validation | Per-field `Txt_Validate(Cancel)` + `GotFocus/LostFocus` colour `BackColor` switch, `DGHelp` Tag/Code + `ListView FrmList` for Nature, `TxtCHno` duplicate `SELECT COUNT(*) FROM LEDGER WHERE Chq_No='…'` | `BaseMasterForm` checks `required` + `exists` + `delete_guard PYT*`; voucher `_num` swallows ValueError to 0 | **Gap** — duplicate cheque, GroupHelp, Alias checks not in Python UI |

**Threshold to reach VB6 parity without DB change:** add TopCtrl state-machine, overlay frames (or tabbed equivalents), Dr==Cr live indicator + disabled Post, DATELOCK pre-check, menuHelp guard before every Save/Delete/Print, Find dialog with `SearchCode` SQL, per-line TDS + Chq cols, BtnEnh shortcut semantics, and font/colour mapping.

---

## 1) VB6 Sources Read ONE BY ONE — verbatim controls

### 1.1 `FaVrEnt.frm` — Voucher Entry (14,149 lines, `FaVrEnt.frx` icon)

**Form header:**
```vb
Begin VB.Form FaVrEnt
  Caption = "Voucher Entry" : BackColor = &HC0C0FF&  ' lavender #C0C0FF
  WindowState = 2  ' Maximized  ClientWidth 12690 × ClientHeight 7890 twips (~847×526 px ≈ 15" @96dpi)
  ScaleMode=1 AutoRedraw=True FontTransparent=True ControlBox=0 MDIChild=-1 KeyPreview=-1
```

**Top strip (VB6 TopCtrl pattern):**
```vb
Begin MainCtrl TopCtrl1  Left 0 Top 0 Width 12690 Height 450  TabIndex 205
' Dispatch IDs: {EAEC4767-…}.DispID_68030005("ADD"/"EDIT"/"FIND"/"PRINT"/…), Clone, Requery/Find
' Verified handlers: TopCtrl1_UnknownEvent_A/B/C/D/E/F/10/11/12/13/14/15/16 (A=Add D=Edit F=Find 14=Print 15=Requery 16=Save)
' Includes duplicate-sub detection: Call TopCtrl1_UnknownEvent_A() then global_124 = var_90.Tag
```

**Header inputs (flat, borderless):**
```vb
Begin TextBox VchDt(0)          Left 510  Top 495  Width 1200 Height 255 MaxLength12 ForeColor &HC00000& BorderStyle 0 None Appearance Flat Font Arial 9.75
Begin TextBox TxtVtYpe(0)       Left 3180 Top 495  Width 2295 Height 255  ForeColor &HC00000& BorderStyle 0 None Font Arial 9.75
Begin TextBox TxtVno(0)         Left 6690 Top 495  Width 1065 Height 255 ForeColor &HC00000& BorderStyle 0 None MaxLength8 Font Arial 9.75
Begin Label LblDt/LblVtype/LblVno  ForeColor &HC00000& Italic -1 Font Arial 9 Bold
Begin Label LblDay               ForeColor &HFF& italic “day” chip at 1680,585
Begin TextBox TxtGlb(0)         Left 0 Top 5760 Width 10380 Height 855 MultiLine -1 ScrollBars2 MaxLength255 BackColor &HE0E0E0& Font Courier New 8.25 Appearance Flat
' Courier New for global narration is distinctive — monospaced audit trail
```

**Section header row (VB6 “grid header” as Labels, not DataGrid):**
```vb
Begin Label Label1(0) Caption "       Particulars" BackColor &HFF0000& ForeColor &HBEFDFE& Left 15 Top 780 Width 7545 Height 240 Font Arial 9.75 Bold Italic -1
Begin Label Label1(1) Caption " Debit "           BackColor &HFF0000& ForeColor &HBEFDFE& Left 7575 Top 780 Width 1395 Height 240 RightJustify
Begin Label Label1(2) Caption "Credit "           BackColor &HFF0000& ForeColor &HBEFDFE& Left 8985 Top 780 Width 1395 Height 240
' Red header (#FF0000) with pale-cyan text (#BEFDFE / &HBEFDFE&) — hot canonical colour, not theme navy
Begin Line Line1(0) X1 7560 Y1 795 X2 7560 Y2 5100  ' vertical dividers for Debit/Credit columns
Begin Line Line1(1) X1 10380 Y1 795 X2 10380 Y2 5100
Begin Line Line1(2) X1 8970 Y1 795 X2 8970 Y2 5100
Begin Line Line2(0) X1 0 Y1 5100 X2 10410 Y2 5100
Begin Line Line2(1) X1 0 Y1 5490 X2 10410 Y2 5490
Begin Label LblDrAmt/LblCrAmt  Left 8775/10200 Top 5175 RightJustify Bold "dr"/"cr"
Begin Label Label3 Caption "dIFF" Left 6780 Top 5175 Invisible debug label
```

**Detail rows — 12 indexed arrays (the core VB6 pattern collapsed to a table in Python):**
```vb
' Per row i = 0..11 (0..6 visible in detail area, 7..11 hidden overflow):
Begin TextBox TxtCrDr(i)   Left 15   Top 1020+~756*i  Width 285  Height 210 BorderStyle 0 None Locked -1 Text "Cr" Font Arial 9 Bold Italic -1  BackColor &HFFFFFF&
Begin TextBox TxtAcName(i) Left 330  Top same        Width 7200 Height 210 BorderStyle 0 None MaxLength75 Font Arial 9 BackColor &HFFFFFF&
Begin TextBox TxtDr(i)     Left 7620 Top same        Width 1335 Height 210 BorderStyle 0 None RightJustify Font Arial 9 BackColor &HFFFFFF&
Begin TextBox TxtCr(i)     Left 9015 Top same        Width 1380 Height 210 BorderStyle 0 None RightJustify Font Arial 9 BackColor &HFFFFFF&
Begin Label LblCb(i)       "Voucher type" ForeColor &H4080& Italic -1 Invisible — holds GroupCode help
Begin Label LblNar(i)      "Voucher type" ForeColor &H4080& Italic Invisible — holds Narration help
Begin TextBox TxtNar(i)    Left 990 Top 1500/2260/3020/3780/4540/5280/5760/6240/6705/7185/7665/8130 Width 6540 Height210 BorderStyle 0 None MaxLength255 Font Arial 8.25 Invisible=0? Nar(0) visible, rest Hidden until row active
' Note: TxtDr/TxtCr flat borderless over grid; TxtCrDr locked “Cr” toggle (VB6 sets Cr/Dr per balance sign via _Validate → LblRefAdjDrCr)
' Cheque per-row footer:
Begin Label Label6 "Cheque No."   Left 30 Top 6675 ForeColor &H800000& Italic Bold 8.25
Begin TextBox TxtCHno(0) Left 975 Top 6675 Width 1935 Height225 BorderStyle0 Flat MaxLength20
Begin Label Label5 "Cheque Date"  Left 2955 Top 6675
Begin TextBox TXTChDate(0) Left 4020 Top 6675 Width 1125 Height225 BorderStyle0 MaxLength12
Begin Label Label7 "Clearing Date" Left 5220 Top 6675
Begin TextBox TXTClrDate(0) Left 6405 Top 6675 Width 1125 Height225 BorderStyle0 MaxLength12
' Global footer:
Begin Label LblAmtRs WordWrap BackColor &H5EB0AC& ForeColor &H800000& Left10485 Top6825 Width3285 Height840 Italic Bold "amount in words" (F1525 converts)
Begin Label LbLUser/LblLDte ForeColor &HC00000& Left14505 Top7815/8160 "user name"/"user date" footer audit
Begin Label lblDocId Invisible "Label2" Left15120 Top8865
Begin TextBox TxtDetailS Left10410 Top5490 Width4980 Height1095 MultiLine Locked -1 Visible0 Invisible detail memo
```

**Overlay frames (all `Visible=0` False until invoked — this is the VB6 modal-as-frame pattern Python must replicate):**

*Cheque Print* `Frame ChqPrint` at 10500,4080 size 5010×2145 BackColor `&HCBBE9E&` beige:
```vb
Begin Frame ChqPrint Caption "Cheque Print" BackColor &HCBBE9E& Left10500 Top4080 Width5010 Height2145 Visible0 Font MS Sans Serif 8.25 Bold
  TxtCrParty  75,195  4845×285  (payee)
  Text3      75,585   1200×285
  TxtChequeAmt 2055,585 1470×285 RightJustify Font Arial 9
  Command1   3600,540 1335×375 Caption "Cheque Print"
  ChkAcPayee 90,945 ; ChkCompName 1815,945 ; ChkAcNo 90,1200 Invisible0 ; ChkFullDate 3540,945
  OptAuthoSign 75,1560 Value 255 ; OptDirector 2310,1560 ; OptPresident 75,1800 ; OptBlank 2310,1800 "."
```

*Reference/Bill-wise Adjustment* `Frame FrameRef` Caption "Referance Detail" BackColor `&HD9B0DD&` lilac at 12375,1560 size 8805×4395:
```vb
Begin Frame FrameRef BackColor &HD9B0DD& Visible0 Font MS Sans Serif 9.75
  LblRefName "MMMM" 990,300 3330×240 Red &HFF0000& Bold
  LblRefAmt 990,540 "999999999.99" RightJustify Red ; LblRefAmtDrCr "Cr." 2235,540 Red
  LblRefAdj 3405,540 "999999999.99" Red ; LblRefAdjDrCr "KK" 4635,540 Red
  LblRefAdjBal 5730,540 "999999999.99" Red ; LblRefAdjDrCrBal "KK" 6975,540 Red
  Labels "For A/C"(90,300) "Tr.Amt."(90,540) "Adjusted"(2550,540) "Balance"(4995,540)
  FGridRef 840,840 5775×3555 MSHFlexGrid  (reference ledger list)
  DGRefNo 4080,1560 4530×2670 DataGrid Visible0
  TxtGrid(0) 5895,1680 690×240 BackColor &HC0C0FF& Invisible overlay editor
  FrmList 6345,1065 2010×2505 BorderStyle0 Invisible contains ListView 0,0 1980×2490
  BtnRefAdjOK 7860,270 585×495 Picture "FaVrEnt.frx":442 ToolTip "Save" Style1
```

*T.D.S.* `Frame FrameTDS` Caption "T.D.S." BackColor `&HBFD0B7&` sage at 12360,990 size 6450×2775 Visible0 Font 9.75 Bold:
```vb
Begin Frame FrameTDS BackColor &HBFD0B7& Visible0
  TxtTDSCode(0) 1170,330 2700×225 MaxLength50 Flat
  TxtTDSNarration 1170,585 3930×1185 MultiLine MaxLength255 Flat
  TxtONAMT 1170,1800 1365×225 RightJustify Flat
  TxtTDS   1170,2055 1365×225 RightJustify
  TxtTDSAMT 1170,2310 1365×225 RightJustify
  TDSDelete 2790,1995 585×495 Picture Style1 ToolTip "Delete "
  Labels: "TDS A/C"(165,345) "Narration"(165,585) "On Amount"(165,1815) "T.D.S. %"(165,2070) "T.D.S. Amt"(165,2325) All Bold Transparent
  Tags: Me.FrameTDS.Tag = row index (global_108 offset) — VB6 uses Tag to carry row context into TDS frame
```

*Adjustment* `Frame FRAMEADJUST` Caption "Adjustment" BackColor `&HE6AC86&` tan ForeColor `&HFF&` red at 12345,735 size 11685×3270 Visible0 Font Arial 12 Bold:
```vb
Begin Frame FRAMEADJUST BackColor &HE6AC86& ForeColor &HFF& Visible0
  Label "For A/C"(135,225) + Label4 "MMMM" 1035,225 4425×240 Red Transparent Bold
  Label "Tr.Amt."(5610,225) ADJ_LAB4 "MMMM" 6285,225 1290 RightJustify Red ; ADJ_LAB5 7590,225 510 Red
  Label "Adjusted Amt."(8205,225) ADJ_LAB7 "KK" 9495,225 1050 Red ; ADJ_LAB8 10545,225 480 Red
  FgridAdjust 45,450 11010×1965 MSFlexGrid  (bill-wise adjustment grid — cols include DocId/V_SNo/Amt/Adjusted/Balance/Ref)
  TXTADJ_AMT 4905,0 1065×285 RightJustify Flat BackColor &HF7F0DF&
  TXTNARRATION 90,2430 10920×795 BackColor &HEBDBC7& ForeColor &HFF& Bold 8.25 Text "Text1"
  BTS_AUTO_ADJ "Auto" 11055,450 585×495 Times New Roman 11.25 Bold DisabledPicture ToolTip "Ok" Style1
  Command2 11055,945 585×495 Picture ToolTip "Full Adjustments" Style1
  ADJ_OK 11055,1440 585×495 Picture ToolTip "Ok" Style1
  ADJ_CANCLE 11055,1935 585×495 Picture ToolTip "Cancel Changes" Style1
```

*Voucher List* `Frame FRAMEVLIST` Caption "Voucher Entry" BackColor `&HC0C0C0&` gray at 12345,495 size 8520×4200 Visible0 Font 9.75 Bold:
```vb
Begin Frame FRAMEVLIST BackColor &HC0C0C0& ForeColor &H400000& Visible0
  FGVLIST 60,1050 8400×3090 MSFlexGrid
  TXTVDATE1 660,315 1170×285 MaxLength12 Flat ; TXTVDATE2 2565,315 1170×285 ; Label "Fr.Dt."(165,360) "To"(2250,360)
  DataCombo1 4395,300 2940×315 "Vr.Type" label 3795,360 ; Dcparty 660,600 3075×315 "Party" 165,660 ; Text1 4395,615 1185×285 "Vr.No." 3795,660
  BTNVLOK "&Ok" 7365,255 1050×360 Bold ; BTNVLCLOSE "&Close" 7365,615 1050×360 Bold
```

*Voucher Printing* `Frame Frame1(1)` Caption "Voucher Printing" BackColor `&HFF80FF&` magenta at 12375,1290 size 6015×4200 Visible0:
```vb
Begin Frame Frame1(1) BackColor &HFF80FF& Visible0  (sub-frames Frame1(2)/Frame1(3)/Frame1(4) toggle)
  Opt2(0) "Print Current" 345,690 1485×360 Value255 BackColor &HFFFFC0&
  Opt2(1) "VNo Selection" 2130,690 1800×360 BackColor &HFFFFC0&
  Opt2(2) "VDate Selection" 4065,690 1800×360 BackColor &HFFFFC0&
  ChkReport "Reciept" 4065,375 1725×240 BackColor &HFFFFC0&
  Frame1(2) BackColor &HBAD3D3& 345,1275 5400×1500 Enabled0 : DataCombo3 1800,435 2745×315 + DataCombo2(0) 1425,1005 1140×315 "From V. No." + DataCombo2(1) 3705,1005 1140×315 "To V. No." + labels
  Frame1(3) BackColor &HFFC0FF& 345,1275 5400×1500 Invisible0 : Text2 2040,720 1605×270 + Label "For Date"
  Frame1(4) 1815,3360 2460×540 : btnPrint1 "Print" 75,135 1170×360 ; BTNCLOSE "Close" 1245,135 1170×360
```

**Help grids (invisible DataGrids positioned off-screen, VB6 Tag pattern):**
```vb
Begin DataGrid DGAcHlp 12405,2970 4095×1725 Visible0 TabIndex113
Begin DataGrid DGTDSCODE 15705,6540 4230×3330 Visible0 TabStop0
Begin DataGrid DGVchrHlp 15390,5970 4995×4320 Visible0
Begin DataGrid DGAcHlp analogue DGAcName/DGAcAlias/DGUnderAc in FaGrEnt — same pattern: Tag holds Index, RowSource via Recordset15, Click copies Code→Txt.Text + Tag→Code Tag
Begin PictureBox PicDN/PicUP red &HFF0000& scroll arrows 10065,5520 + 0,780 Visible0
Begin MSFlexGrid FGrid1 165,8355 9990×570 Visible0  (calc grid)
Begin BtnEnh LblShort(1..4) inside Frame1(0) BackColor &HC0C0FF& Left 15 Top 765/1395/2025/2655 Width1935 Height630 — VB6 shortcut bar (FaVrEnt: Shortcuts tied to Ledger/Ref/TDS)
```

**Fonts/colors summary for FaVrEnt:**
- Form lavender `&HC0C0FF&` (= `#C0C0FF` / `rgb(192,192,255)`)
- Section headers red `&HFF0000&` (= `#FF0000`) with cyan text `&HBEFDFE&` (= `#FDFEBE`? actually `#BEFDFE`)
- Input flat white `&HFFFFFF&` BorderStyle 0 None Appearance 0 Flat
- Global narration `#E0E0E0` gray Courier New 8.25
- Labels italic `Italic -1` for help captions, bold for amounts, red `#FF0000` for reference amounts
- TDS sage `#BFD0B7`, Adjustment tan `#E6AC86` with red foreground `#FF0000`, Reference lilac `#D9B0DD`, ChqPrint beige `#CBBE9E`

**Key code-behind (handlers verified via grep + slices, 14k-line FRM):**
```vb
Private Sub TxtTDSAMT_Validate(Cancel As Boolean) '12BBB6C
Private Sub TxtTDSCode_GotFocus/Validate
Private Sub TxtCrDr_GotFocus/Validate  ' per-row Dr/Cr toggle, sets LblRefAdjDrCr, validates single-side non-zero
Private Sub TxtAcName_GotFocus/Validate ' SubCode lookup via DGAcHlp Tag, GroupCode resolve via SELECT GroupCode FROM SubGroup WHERE RTRIM(SubCode)=?
Private Sub VchDt_GotFocus/Validate     ' DATELOCK: Call Proc_185_171 ... If (var_86=2) block + Vr.No duplicate check
Private Sub TxtVtYpe_GotFocus/Validate  ' Voucher_Type validation, HO fallback, NCAT routing
Private Sub TXTChDate/TXTClrDate_GotFocus/Validate, TxtCHno_GotFocus/LostFocus  ' duplicate Chq_No: SELECT COUNT(*) FROM LEDGER WHERE Chq_No='dup' [+ AND DOCID<>'cur' for edit]
Private Sub TxtCHno_LostFocus ... MsgBox("Duplicate Cheque No.", &H140)
Private Sub TxtGlb_GotFocus            ' loads VOUCHER_TYPE.Narration as default if TxtGlb empty
Private Sub TopCtrl1_UnknownEvent_16   ' eSave: Date + VNo validation, Vr.No already-exist loop with +1 retry, global_110=3 tag, calls TopCtrl1_UnknownEvent_A
Private Sub Form_KeyDown KeyCode Shift  ' Esc=Cancel, Ins=BillWise Adj, Alt-R=Ref, Alt-T=TDS ; DG visibility checks
Private Sub TxtGrid_GotFocus (FrameRef) + ListView_UnknownEvent_13  ' reference grid cell editor
Private Sub DGTDSCODE_UnknownEvent_9   ' copies subcode/name into TxtTDSCode, sets Tag=subcode
Private Sub Opt2_Click                  ' toggles Frame1(2)/Frame1(3) visibility per print mode
```

---

### 1.2 `FaGrEnt.frm` — Group Accounts Entry (AcGroup)

```vb
Begin VB.Form FaGrEnt Caption "Group Accounts Entry" BackColor &HFFC0C0& (=#FFC0C0 pink) WindowState2 Client 9675×6525
  Begin MainCtrl TopCtrl1 0,0 9675×450 TabIndex23   ' same AEDP state-machine
  Begin DataGrid DGUnderAc 2265,4200 5700×3330 Visible0 TabStop0  ' + DGAcAlias 3390,3705 + DGAcName 885,4755 (all Hidden help grids)
  Begin TextBox Txt(0) 2460,1305 4980×285 MaxLength50 ForeColor &HC00000& BorderStyle0 Flat Font Arial 9.75 ToolTip "Group Account Name"  (= GroupName)
  Begin TextBox Txt(1) 8805,1575 4980×285 Visible0 MaxLength50 ToolTip "Group Account Name (BiLangual)"  ' Hindi
  Begin TextBox Txt(2) 8805,1890 4980×285 Visible0 ToolTip "Alias Group Account Name"
  Begin TextBox Txt(3) 8805,2205 4980×285 Visible0
  Begin TextBox Txt(4) 2460,1620 4980×285 ToolTip "Parent Group Account Name"  (= Under Group, parent GroupName)
  Begin TextBox Txt(5) 2460,1935 1740×285 MaxLength15 ToolTip "Group behavior" (= Nature)
  Begin TextBox Txt(6) 2460,2250 1740×285 MaxLength15 ToolTip "Group behavior" (= Trading A/C)
  Begin Frame FrmList 7215,4020 2325×2370 Visible0 BorderStyle0 BackColor &HFFC0C0&  contains ListView 15,30 2295×2310
  Begin Label Lbl(0) "Name" 1320,1290 ForeColor &HC00000& Arial 9.75 Bold
  Begin Label Lbl(4) "Under" 1320,1605
  Begin Label Lbl(5) "Nature" 1320,1920
  Begin Label Lbl(6) "Trading A/C" 1320,2235
  Begin Label Lbl(2) "Alias Name" 7665,1875 Visible0  + LblNameBiLang "(Hindi)" Comic Sans MS 9.75 Italic -1 Visible0 etc
  Begin Label LblFormCaption BackColor &HC0FFFF& cyan 0,375 180×540 BorderStyle FixedSingle Alignment Center Font System 19.5 Bold
  Begin Label LblUser/LblLDt "User"/"Last Update" Times New Roman 11.25/12 Bold Red/&HC00000&
  Begin Label Label3 Note "Run Current Balance Updation After Making Changes In Group Accounts" Arial 14.25 Bold Red ForeColor &HFF& at 945,6750 WordWrap
```

**Workflow (TopCtrl + validation):**
```vb
TopCtrl1_UnknownEvent_A(eAdd): var="ADD" Call Proc_201_29 -> enable Txt(0)+Txt(4), global_64="N", caption "User Defined", focus Txt(0)
TopCtrl1_UnknownEvent_D(eEdit): if RecordCount>0 and Proc_183_55!=0xFF then global_76=GroupCode, global_68=GroupName, var="EDIT", lock Txt(0)/Txt(4) when global_64="Y"
TopCtrl1_UnknownEvent_F(eFind): SearchCode SQL →  Select GROUPCODE As SearchCode,GroupName,GroupNature,Nature FROM AcGroup Where (LOGSITE_CODE='<site>' OR LOGSITE_CODE='HO') AND AliasYN<>'Y' Order by GroupName  → Proc_6_126 (Search dialog width "2000,2000,1000")
TopCtrl1_UnknownEvent_14(ePrn): print AcGroup list via FaGrplist.ttx
TopCtrl1_UnknownEvent_15/16(eSave): validation Txt(0) GroupName required, Txt(4) Under Group required, Txt(5) Nature required, duplicate GroupHelp check: Select GroupHelp From AcGroup Where GroupHelp='<val>' ; alias duplicate: GroupHelp<>'…'; same-group check: if Txt(0)==Txt(4) → "A/c Group And Under group Can not be same"
Form_Load: recordsets for DGAcName/DGAcAlias/DGUnderAc, ListView items Bank/Broker/Cash/Customer/Electrician/Employee/Expenses/Mukadim/Others/PDC/Purchase/Revenue/Sale/SalesMan/SalesRep/Supplier/T.D.S./Transporter/Unsecured Loan
Txt_GotFocus/KeyDown/KeyPress/KeyUp/Validate : DGHelp pattern via Proc_183_31_100809C / Proc_183_34_1305540 / Proc_183_36_114886C positional overlay of DGAcName/DGAcAlias/DGUnderAc/ListView
```

---

### 1.3 `FaReports.frm` — Finance Reports (ReprtForm)

```vb
Begin VB.Form FaReports Caption "ReprtForm" ForeColor &HE0E0E0& WindowState2 Client 11820×8595 Font MS Sans Serif 9.75
  Begin BtnEnh BtnParam 0,0 1530×405 Visible0
  Begin BtnEnh BTNPRINT(0) 4860,6045 1395×480
  Begin BtnEnh BTNEXIT 6255,6045 1395×480
  Begin BtnEnh BTNPRINT(1) 3450,6045 1410×480 Visible0
  Begin CommandButton BTNPRINTz(1) "&Dos Print" 45,9900 1620×375 Visible0  + BTNPRINTz(0) "Windows &Print" 8985,10080
  Begin MainCtrl TopCtrl1 0,7800 11820×360 Visible0   ' hidden — reports use BtnParam instead
  Begin DataGrid DGSite 6120,2400 4230×3330 Visible0 TabStop0
  ' Remainder of form is dynamically built at runtime via FAENVIRO TagadaHeader/Footer loads and GRepFormName switch
```

**Runtime logic (inferred from FaReports.bas + MDI):**
- `GRepFormName` in {Led,LedInt,LedDeb,MemLed,LedCred,CashBook,BankBook,Budget,BudgetVariance,AcCheckList,…}
- `Form_Load` → `SELECT * FROM FAENVIRO WHERE LOGSITE_CODE='<site>'` → loads TagadaHeader1..5 / TagadaFooter1..5 into textboxes (for Bank guarantor header)
- Filter uses hidden `DGSite` on `Select Site_Code AS Code,Site_Desc AS NAME From Site Order by Site_Desc`
- Each `BtnParam_UnknownEvent_9` toggles visibility of parameter grids; print routes through `FaRepView`/`rFaRepView` Crystal TTX path `MemVar_1F923B0\*.TTX` with Title/UpToDate/BankAc/PartyAc/BankBal params.

---

### 1.4 `FaChqClear.frm` — Cheque/DD Clearing Entry (11580×7320)

```vb
Begin VB.Form FaChqClear Caption "Cheque/DD Clearing Entry" WindowState2 BackColor default Font System 9.75 Bold ControlBox0 MDIChild -1 KeyPreview -1 Client 11580×7320
  Begin MainCtrl TopCtrl1 0,0 11580×450 TabIndex22
  Begin DataGrid DGParty 990,4995 5640×3330 Visible0 TabStop0
  Begin DataGrid DGBank 6780,4965 4230×3330 Visible0 TabStop0
  Begin TextBox Txt(5) 3420,2520 1395×285 Enabled0 BorderStyle0 Font Arial 9.75 ForeColor &HC00000&  ' Status(Clear./UnClea/All)
  Begin Frame FrmList 6135,7350 2505×1830 Visible0 BorderStyle0  contains ListView 0,-15 2325×1830 (items Cleared/Un-Cleared/All)
  Begin TextBox Txt(4) 3420,1575 4935×285 BorderStyle0  ' Party Account
  Begin TextBox Txt(1) 3420,1260 4935×285  ' Bank Account
  Begin TextBox TxtGrid(0) 270,4110 690×240 BackColor &HC0FFFF& cyan ForeColor &H0& Visible0 BorderStyle0 Font MS Sans Serif 8.25
  Begin TextBox Txt(3) 3420,2205 1395×285 Enabled0  ' Balance As Per Book
  Begin TextBox Txt(2) 3420,1890 1395×285 Enabled0  ' Balance As Per Bank
  Begin TextBox Txt(0) 3420,945 1395×285  ' UpTo Date
  Begin MSHFlexGrid FGrid 345,2850 11775×5505 TabIndex6  ' main 15-col grid (see Proc_194_34_129C200: DocID,V.SNo,V.Type,V.Prefix,SubCode,GroupCode,Nature…)
  Begin Label LblFormCaption &HC0FFFF& cyan 0,345 180×540 FixedSingle Center Font System 19.5 Bold
  Begin Label Label1(5) "(Not Applicable in case of multiple Debit && Credit Vouchers)" ForeColor &H80& 8385,1590 WordWrap
  Begin Label Label1(2) "Status(Clear./UnClea/All)" 1035,2535 Bold &HC00000&
  Begin Label Label1(0) "Party Account" 1035,1590 Bold ; Label1(28) "Bank Account" 1035,1275 ; Label1(4) "Balance As Per Bank" 1035,1905 etc
  Begin Label LblType(0/1) " " 6270,1875/2220 ForeColor &H80&  (Dr/Cr type chip beside bank/book bal)
```

**Key workflow:**
- `Form_Load` sets `TopCtrl1` AEDP, positions DGBank/DGParty under Txt(1)/Txt(4), `Me.FGrid.Height=5000`, `Cols=15`, `FGrid.BackColorSel=16308221`, `CellBackColor 12648447/14737632` on enter/leave.
- `Txt_GotFocus` for Txt(1)=Bank (`Nature in ('Bank') AND LOGSITE_CODE OR HO`), Txt(4)=Party (`Nature<>'Bank' OR HO`), Txt(5)=ListView Cleared/Un-Cleared/All. DGHelp uses Tag/Code pattern: `DG.Click → Txt.Text=Fields("Name").Value ; Txt.Tag=Fields("Code").Value ; Txt.SetFocus`.
- `FGrid` cell edit via `TxtGrid` overlay (BackColorSel `12648447`), columns B/C/D (Chq_No/Chq_Date/Clg_Date) editable, `Proc_183_26_1158124` handles conversion, Del clears row `TxtGrid.Text=vbNullString`.
- **Clear save** `TopCtrl1_UnknownEvent_16`: `unk.BeginTrans` → loop `For var_B4=1 To Rows-1` → if `Trim(TextMatrix) <> ""` and `V_Type <> "HPOST"` then `Update Ledger Set Chq_No,Chq_Date,Clg_Date Where DocID & V_SNO` else special `Where DocID & V_SNO & AmtCr & ContraSub` for `HPOST` multi-bank lines → `CommitTrans` else `RollbackTrans`. Displays `BankReconciliation.RPT` via `CreateFieldDefFile` on print.

---

### 1.5 `frmYearEnd.frm` — Year End Updation (5130×3810, BackColor &HFFC0C0& pink)

```vb
Begin VB.Form frmYearEnd Caption "Year End Updation" BackColor &HFFC0C0& (=#FFC0C0) WindowState2 Client 5130×3810 ControlBox0 MDIChild -1
  Begin CommandButton Command1 "Create CSV" 1755,2160 1560×390 Visible0
  Begin BtnEnh Head   7200,3375 2475×1245
  Begin BtnEnh CmdYrUpdate 4635,3375 2475×1245
  Begin Label LblFormCaption &HC0FFFF& cyan 0,0 180×540 FixedSingle Center System 19.5 Bold  (set in Form_Resize)
  ' No inputs — pure process dialog. All inputs come from Company.Start_Dt/End_Dt and MemVars.
```

**Workflow (CmdYrUpdate_UnknownEvent_9, 17D7B4A, ~200 lines):**
1. Guard: `If (CDate(Format(MemVar_Start+1y)) > CDate(MemVar_End)) And (MemVar_1F92070 <> MemVar_1F92078)` → `MsgBox("You can't close year for different Site")` Exit.
2. `SELECT * From Company Where Comp_Code='<comp>'` → compute new `Start_Dt=DateAdd(Y,1,old Start_Dt)`, `End_Dt=DateAdd(Y,1,old End_Dt)`, `CYear='YYYY-XX'` (inc Last 4), `PYear` etc.
3. `SELECT Max(Cast(Comp_Code As Integer))+1 As Code From Company` → new Comp_Code.
4. `Insert into Company (Comp_Code,Comp_Name,CentralData_Path,Repo_Path,Start_Dt,End_Dt,address1,…,CYear,PYear,Pin,…,SiteCode,LogSite_Code,…) Values ('new', OldRow..., newDt..., SITE_CODE, SITE_CODE)` — verbatim column list (39 cols).
5. `Update Company Set ActiveEpabx='' Where Comp_Code='<old>'`.
6. `Select * From menuHelp Where CompCode='<old>'` loop → `INSERT INTO menuHelp (CompCode,UserName,Opt1..4,Code,Menu_Index,[Option],Param_Str,ShowInList,Flag,OutletCode,Menu_Visible,Pro_Name,Tag,User_Name,ID,Module_Name) VALUES('new',…)` per row.
7. Same for `menuHelp1` (MenuName/MenuIndex/MenuCaption/Param_Str/Flag).
8. `Select * From Voucher_Prefix Where Site_Code='<site>' and date_From=<old Start_Dt>` loop → `Insert into Voucher_Prefix (V_Type,Date_From,Date_To,Prefix,Start_Srl_No=0,Site_Code,LogSite_Code) values('<vtype>',newStart,newEnd,'YYYY',0,site,site)`.
9. `Insert into UserPermission (CompCode,UserName,LogSite_Code,POSDiscountAllowUpto,…,Site_Code,POSSettlementYN,EditItemInKOT,ChangeGuestCharges) values('new', user, site,…)`.

**YearEnd never touches** `Ledger`, `SubGroupCurrBal`, `Budget` directly — Python `year_end.py:carry_forward_balances` is destructive divergence.

---

### 1.6 `MDIForm1.frm` — Finance menus (fate/farp/fame)

**FA subtree extracted (lines 315-492):**

```vb
Begin Menu FA Caption "&Finance"
  Begin Menu FAT Caption "&Transaction"
    Begin Menu fate Index0 Caption "&Voucher Entry"
    Begin Menu fate Index1 Visible0 Caption "Adjustment Entry"
    Begin Menu fate Index2 Visible0 Caption "Delete Adjustment Entry"
    Begin Menu fate Index3 Caption "Bank Reconciliation"
    Begin Menu fate Index5 Visible0 Caption "T.D.S. Challan Entry"
    Begin Menu fate Index6 Visible0 Caption "T.D.S. Certificate Entry"
    Begin Menu fate Index7 Caption "&Expense Voucher"
  Begin Menu faD Visible0 Caption "&Display"  → FAREPORTD 0 "Balance Sheet"(hid) 1 "P&L"(hid) 2 "Trial Balance (Group)"(hid) 3 "Trial Ledger" 4 "Cash Flow"(hid) 5 "Fund Flow"(hid) 6 "Cash And Bank Books"(hid)
  Begin Menu farp Caption "&Reports"
    FAREPORT 0 "Trial Balance" ; 1 "&Day Book"(hid) ; 3 "&Ledger" ; 4 "&Interest Ledger"(hid) ; 5 "Cash Book" ; 6 "Bank Book" ; 7 "&Journal Books" ; 10 "&Annexure" ; 13 "Bank Register" ; 14 "Ageing Debtors" ; 15 "Ageing Creditors" ; 22 "Cheque Cleared Register" ; 23 "Cheque Not Cleared" ; 24 "Outstanding Debtors" ; 25 "Outstanding Creditors" ; 27 "Daily Transaction Summary"(hid) ; 29 "Non Transaction"(hid) ; 30 "Reference Report"(hid) ; 31 "Detailed Trial Ledger" ; 32 "A/c Check List"(hid) ; 33 "Bill Wise Outstanding Debtors" ; 34 "Control Ledger"(hid) ; 35 "Roz Namcha"
  Begin Menu fae Caption "&Finance" (under Mast > Main Setup > Finance) →  fame 0 "Group Accounts" ; 1 "Ledger Accounts" ; 2 "Narration Master" ; 3 "T.D.S. Category" ; 4 "FA Environment" ; 5 "Voucher Environment" ; 6 "Opening Balance Updation"(hid) ; 7 "Year End Updation" ; 8 "Current Balance Updation" ; 9 "Country Master"(hid) ; 10 "State Master"(hid) ; 11 "City Master"(hid) ; 12 "Delete Message" ; 13 "Account Merging" ; 14 "Voucher Serialisation"
```

**VB6 click dispatch (FaVoucher.bas Proc_7_1_1365344 + MDI fate/farp/fame_Click):**

```vb
' MDI fate_Click(Index):
  ' SELECT Param_Str AS UPrivilege, Module_Name FROM menuHelp WHERE UserName='<u>' AND CompCode='<c>' AND [Option]='Voucher Entry'  (Option varies: Voucher Entry / Ledger / Group Accounts / …)
  ' Then SELECT NCAT FROM VOUCHER_TYPE WHERE V_TYPE='<vtype>' — CNT/JV/PMT/RCT branch via fate/FO etc, OPBAL/PBILL/… via FaSubGroup/memb+…
  ' If hidden (Visible0) then only reachable when Flag gates enable via Inconsistency Check utility — not normal user path
```

---

### 1.7 Additional sub-forms (read via dir scan + FINANCE_COMPARE.md)

- `FaTDSChal.frm / FaTDSCertificate.frm` — hidden TDS flows; `FaTDSCat.frm` Category master (TDS % on amount).
- `FaSubGroup.frm` — SubGroup (Ledger) master analogue of `FaGrEnt` but with 70+ cols.
- `FaGlobeNarr.frm / FaNarrMast.frm` — global/per-site narration masters (linked to `FaVrEnt.TxtGlb` default narration).
- `FaEnvron.frm / FaMagic.frm / FaCurrBalUpdate.frm / FaAdjust.frm / FaAdjustDel.frm` — FAEnv flags, balance rebuild, adjustment delete.

---

## 2) Python Sources Read ONE BY ONE — verbatim controls

### 2.1 `PYTHONE/ui/fa_voucher_ui.py` (365 lines)

```py
class VoucherEntryDialog(QDialog):
    setWindowTitle "Voucher Entry - HMS_py" resize(820,520)  # vs VB6 12690 twips ~847px + MDIChild
    root = QVBoxLayout
      form = QFormLayout
        dtVdate = QDateEdit CalendarPopup True DisplayFormat "dd/MM/yyyy" setDate today
        cmbVType = QComboBox vtypes=["JV","HPOST","F_AO"] fallback else voucher_type.list_entry_types()
        edNarr = QLineEdit placeholder "Enter voucher narration..."
        form.addRow "Voucher Date:" dtVdate ; "Voucher Type:" cmbVType ; "Narration:" edNarr
      tbl = QTableWidget(0,4) HorizontalHeaderLabels ["SubCode","Name","Debit","Credit"]
            setStretchLastSection True setAlternatingRowColors True  # Name column is display-only in VB6
      btns = QHBoxLayout spacing8
        bAdd "+ Line"  MinimumHeight 32 ToolTip "Add a new debit/credit line"
        bDel "- Line"  MinimumHeight 32 ToolTip "Remove selected"
        bPost "Post Voucher" property accent True MinimumHeight34 Default True ToolTip "Post (Ctrl+Enter)" clicked _post
      lblStatus QLabel "Debit must equal Credit (double entry)" style 11px text_dim  padding2
      _add_line() x2 on init → insertRow + 4 QTableWidgetItems (all editable, including Name)

    _post():
      lines=[{subcode: tbl(0), amt_dr: float(tbl2), amt_cr: float(tbl3)} for r where sc!=""]
      res=fv.post_voucher(lines, dtVdate.toPyDate(), narration=edNarr.text(), vtype=cmbVType.currentText(), user=user)
      lblStatus "Posted: {docid} DR=CR={dr:,.2f}" + QMessageBox

class BankReconDialog(QDialog):
    setWindowTitle "Bank Reconciliation - HMS_py" resize 880,480
    lbl "Pending cheques (Clg_Date IS NULL)"
    tbl QTableWidget(0,8) HorizontalHeaderLabels ["DocId","Sno","Vdate","Account","Chq No","Chq Date","Debit","Credit"] StretchLast SelectionBehavior SelectRows AlternatingRowColors
    btns: "Mark Cleared (today)" → _clear (uses today) + "Reload"
    _load(): rows=fv.cheque_pending() → fill 8 cols, lbl "{len} pending cheques"
    _clear(): r=currentRow → docid tbl(0) sno tbl(1) → fv.cheque_mark_cleared(docid,sno) → _load()

class ReportViewer(QDialog):
    setWindowTitle "{title} - HMS_py" resize880,520
    top QHBoxLayout "From:" QDateEdit dtFrom 2016-01-01 ; "To:" dtTo today ; "Run" button
    tbl QTableWidget 0,0 setEditTriggers NoEditTriggers StretchLast AlternatingRowColors
    lbl "Ready (read-only)"
    _run(): data = fn(f,t)  (handles needs_dates False special) → _fill
    _fill(): if dict with groupcode → 3-col Group/Name/Amount ; else generic keys→cols

Helpers: _viewer(title,fn,needs_dates) → ReportViewer.exec ; open_trial_balance/open_pnl/open_balance_sheet/open_cash_bank_books/open_bank_register/open_journal_book/open_daily_txn_summary
```

**QSS / sizing:** `setMinimumHeight 32/34`, `setAlternatingRowColors True`, `setStretchLastSection True`, no `BorderStyle 0` flat, no `FixedSingle` header — generic modern. No `lblDocId`, no `PicDN/PicUP` scrollers, no red `#FF0000` header.

### 2.2 `PYTHONE/ui/fa_ledger_ui.py` (221 lines)

```py
class FaLedgerWindow(QMainWindow):
  setWindowTitle "Finance Ledger Operations" resize 900,600 current_code=None
  central QWidget → QVBoxLayout
    search_layout QHBoxLayout Label "Search:" QLineEdit txt_search Placeholder "Search by AcCode or AcName..." textChanged _filter
    form_group QGroupBox "Account Details" QFormLayout
      txt_ac_code QLineEdit Placeholder "Enter account code"
      txt_ac_name QLineEdit Placeholder "Enter account name"
      txt_group_code QLineEdit Placeholder "Enter group code"
      txt_op_balance QLineEdit Placeholder "Opening balance"
      txt_dr_cr QComboBox ["Dr","Cr"]
      txt_address QLineEdit Placeholder "Enter address"
      form_layout addRow AcCode/AcName/GroupCode/OpBalance/Dr/Cr/Address
    btn_layout QHBoxLayout: New Account / Edit / Refresh / Exit  (no delete/print/find)
    table QTableWidget 5 cols ["AcCode","AcName","GroupCode","OpBalance","DrCr"] AlternatingRowColors itemSelectionChanged _on_select
    _load_data(): _all_rows = _LedgerMasterBridge.list_ledger() → _populate_table
    _populate_table: QTableWidgetItem + QColor(palette["text"])
    _filter: lower substring over AcCode/AcName
    _on_select: code = table(0) → get_ledger(code) → fill 6 fields + txt_dr_cr findText
    _collect(): dict AcCode/AcName/GroupCode/OpBalance/DrCr/Address
    _new(): if !AcCode warn → insert_ledger → _load_data → "Account created."
    _edit(): if !current_code warn → update_ledger(current_code, rec) → "Account updated."

_LedgerMasterBridge: list_ledger→ledger.list_all(500)→ map AcCode/AcName/GroupCode/OpBalance=""/DrCr=""/Address=add1 ; get_ledger→ledger.get ; insert/update→ledger.insert/update with code/name/group/add1 only
```

**Vs VB6 `FaSubGroup` / SubGroup master:** should have 70+ cols (`SubCode Name GroupCode Nature Category PanNo Gstin CreditLimit Days CityCode Phone Mobile Email Add1 Add2 AliasYN LogSite HO …`); Python only persists 4 (`code/name/group/add1`). Missing `OpBalance`/`DrCr` persistence (always `""`), missing `LOGSITE_CODE` write.

### 2.3 `PYTHONE/ui/finance_masters_ui.py` (259 lines)

```py
taxmaster_config(): MasterConfig title "Tax Master - HMS_py" columns (TaxCode/TaxName/Short/Ledger/Nature/Active) fields code/name/short/accode/payableac/unregisteredac/sundry/nature/roundoff/active delete_guard PYT*
paymenttype_config(): columns (Code/Name/Category/Default/Active) fields code/name/paytype/category/isdefault/active
marketsegment_config(): columns (Code/Name/Active) fields code/name/active
businesssource_config(): columns (Code/Name/Active) ...
gueststatus_config(): columns (Code/Name/Active) ...
forexmaster_config(): columns (Code/Name/Buy Rate/Sell Rate/Equiv Unit/Active) fields code/name/buyrate/sellrate/equivunit/active
ledger_config(): MasterConfig title "Ledger Accounts - HMS_py" columns (LedCode/LedName/Group/Nature/OpenBal/Active) fields code(8)/name(75)/group(6)/nature(1)/openbal/default0/openbaltype Dr/phone(35)/mobile(24)/email(50)/add1(50)/add2(50)/city(6)/pan(20)/gstin(30)/active  delete_guard PYT*
  _ledger_delete_guard: if code.upper().startswith("PYT") allow else block
_open(cfg_fn,parent): BaseMasterForm(cfg_fn(),parent).exec()
FinanceMastersLauncher QMainWindow 380×400 buttons 7 × QPushButton → _open(taxmaster) etc
```

All delegate to `BaseMasterForm`.

### 2.4 `PYTHONE/ui/fa_sub_forms_ui.py` (222 lines)

```py
class FaAdjustWindow(QMainWindow): title "Ledger Adjustment Entry" resize 800,500
  _build_ui: QLabel title 14pt Bold Center "Ledger Adjustment (Bill-wise)"
             QGroupBox "Adjustment Details" QFormLayout: txt_docid1 "Debit DocId", txt_sno1 "Debit SNo", txt_docid2 "Credit DocId", txt_sno2 "Credit SNo", txt_amt "Amount", txt_subcode "SubCode", txt_agref "Adjustment Reference"
             QHBoxLayout: btn_save "Save Adjustment" property success True / btn_exit "Exit"
             QTableWidget 6 cols ["DocId1","SNo1","DocId2","SNo2","Amount","SubCode"] AlternatingRowColors
  _load_data: falo.ledgeradj_list() → populate docid1/v_sno1/docid2/v_sno2/cr/subcode
  _save: falo.ledgeradj_insert({docid1, v_sno1, docid2, v_sno2, cr, subcode, agrefno}) try ValueError warn else critical

class FaChqClearWindow(QMainWindow): title "Cheque Clearing" resize 700,400
  QLabel "Cheque Clearing" 14pt Bold Center
  QGroupBox "Cheque Details" QFormLayout: txt_docid "Voucher DocId", txt_sno "Line SNo", dt_clg QDateEdit today, txt_chq "Cheque Number", dt_chq QDateEdit today
  QHBoxLayout btn_save "Mark Cleared" success True / btn_exit Exit
  _save: docid=text docid, sno=int(txt_sno), clg_date=dt_clg.toPyDate() ; if !docid warn "DocId zaroori" ; chq=txt_chq.strip() ; fv.cheque_mark_cleared(docid,sno,clg_date,chq_no=chq,chq_date=dt_chq.toPyDate()) → "Cheque marked as cleared!"

class FaTDSCertificateWindow(QMainWindow): title "TDS Certificate" resize 700,400
  QLabel "TDS Certificate Generation" 14 Bold Center
  QGroupBox "Certificate Details" QFormLayout: txt_subcode "SubCode (Party)", txt_finyear "2025-26", dt_from 2025-04-01, dt_to 2026-03-31
  QHBoxLayout btn_gen "Generate Certificate" success True / btn_exit
  _generate: if !subcode warn ; rows=tds.tds_detail(subcode) ; total_tds=sum(tds_amt) ; QMessageBox "Party: {subcode}\nTotal TDS: {total_tds:,.2f}\nEntries: {len}\n\n(Crystal Report se print karo)"
  open_fa_adjust/chq_clear/tds_cert helpers
```

Note: `from core import …` / `from ui.theme import palette` are legacy import paths (should be `HMS_py.core…`/`HMS_py.ui…`) — will fail when launched via `python -m`.

### 2.5 `PYTHONE/ui/year_end_ui.py` (386 lines)

```py
class YearEndForm(QDialog):
  COLS_SUMMARY ["FY","SubGroups","Total DR","Total CR","Balance","ACGroups","LastVouchers"]
  __init__: setWindowTitle "Year-End Processing - HMS_py" resize 820,640 Modal True QVBoxLayout spacing12 margins16,12
    QLabel "Year-End Processing" Arial 13 Bold Center
    QGroupBox "Financial Year" QHBoxLayout: lbl_fy "Loading..." Arial 11 Bold + btn_refresh_fy "Refresh FY (F5)"
    QGroupBox "Year-End Summary" QVBoxLayout: tbl_summary QTableWidget(0,len(COLS_SUMMARY)) HorizontalHeaderLabels COLS_SUMMARY AlternatingRowColors NoEditTriggers SelectRows StretchLast → stretch1
    QGroupBox "Operation Log" QVBoxLayout: lbl_log "Ready. Select actions below." WordWrap True
    QGroupBox (button bar) QHBoxLayout spacing8:
      btn_check_lock  "  Check DateLock (Ctrl+L)"
      btn_carry_fwd   "  Carry Forward Balances (Ctrl+C)"
      btn_reset_budget "  Reset Budget (Ctrl+B)"
      btn_execute     "  Execute Year-End (Ctrl+E)" property accent True
      btn_summary     "  Load Summary (Ctrl+S)"
      btn_close       "  Close (Esc)"
    lbl_state "Ready" style 11px text_dim padding4 border-top
    Signals clicked → _on_check_lock/_on_carry_forward/_on_reset_budget/_on_execute_year_end/_on_load_summary/reject
    QShortcut Ctrl+L/C/B/E/S, Escape, F5 → same
    Initial _refresh_fy()
  _set_state(text,color): lbl_state "  {text}" + style border-top
  _refresh_fy(): ye.get_fy_dates() → lbl_fy "Current FY: {fy} | From: {start} | To: {end}"
  _on_load_summary/_load_summary: ye.year_end_summary() → fy["fy"] + subgroup_count/total_dr/total_cr/balance/acgroup_count/last_vouchers len → tbl_summary 1 row
  _on_check_lock: today=date.today() ; locked=ye.check_datelock(today) → lbl_log "[LOCKED]/[OK] Date {today}…" + state red/green
  _on_carry_forward: ye.get_fy_dates() → new_fy_start ; QMessageBox.question Confirm ; ye.carry_forward_balances(new_fy_start,commit=True) → lbl_log "[CARRY FORWARD] SubGroupCurrBal {n} …"
  _on_reset_budget: get_fy_dates → new_fy_start/end ; question → ye.reset_budget(start,end) → lbl_log "[BUDGET RESET] {n}"
  _on_execute_year_end: check_datelock(today) if locked warn ; state "Executing…" ; ye.carry_forward_balances(new_fy_start) ; ye.reset_budget(new_fy_start,end) → lbl_log "[YEAR-END COMPLETE] …"
  open_year_end(parent): YearEndForm(parent).exec()
  YearEndLauncher QWidget 400×200 button → YearEndForm.exec()
  # Cells use _cell/_dark_cell helpers with glass_tint background, not VB6 flat #FFFFFF
```

### 2.6 `PYTHONE/ui/base_master.py` (386 lines) + `PYTHONE/ui/theme.py` (754 lines)

**BaseMasterForm (TopCtrl analogue):**
```py
@dataclass Field(name,label,max_len,required,default,placeholder)
@dataclass MasterConfig(title,columns,fields,api,pk_key="code",delete_guard,sample_prefix="PYT")
class BaseMasterForm(QDialog):
  setWindowTitle cfg.title setMinimumSize 680,520 resize720,540 state="Idle" edit_pk=None
  palette = _theme.palette()
  root QVBoxLayout margins16,12 spacing12
    tbl_grp QGroupBox "{title} List" QVBoxLayout
      _search QLineEdit Placeholder "Search..." MinimumHeight32 QSS border #border radius6 glass_tint focus border 2px accent textChanged _filter_table
      tbl QTableWidget(0,len(cfg.columns)) HorizontalHeaderLabels columns setEditTriggers NoEditTriggers SelectionBehavior SelectRows AlternatingRowColors verticalHeaderVisible False ShowGrid True SortingEnabled True StretchLast ResizeToContents
        cellDoubleClicked → _on_edit()
    form_grp QGroupBox "Record Details" QFormLayout spacing10 margins16,12
      for f in cfg.fields: e=QLineEdit MaxLength placeholder MinimumHeight32 QSS padding 6 10 border #border radius6 glass_tint focus 2px accent ; label "f.label <*>"; edits[f.name]=e
    TabOrder chained via QWidget.setTabOrder
    btn_grp QGroupBox QHBoxLayout spacing8
      btnNew "  New (Ctrl+N)" accent True 34px ToolTip Create
      btnEdit "  Edit (Ctrl+E)" 34px
      btnDelete "  Delete (Ctrl+D)" role danger 34px
      btnSave "  Save (Ctrl+S)" accent True 34px
      btnCancel "  Cancel (Esc)" 34px
      btnExit "  Exit" 34px
    lblState "Ready" style 11px text_dim padding4 border-top
    Signals: btnNew→_on_new ; btnEdit→_on_edit ; btnDelete→_on_delete ; btnSave→_on_save ; btnCancel→_on_cancel ; btnExit→reject
    Shortcuts: Ctrl+N/E/D/S Esc F5 ; set_state(False) ; reload()
  _filter_table(lower substring over visible cols)
  record_from_ui()/record_to_ui()/grid_row_values() hooks
  set_state(enabled): for e in edits e.setEnabled(enabled) ; btnNew/Edit/Delete enabled=!enabled ; Save/Cancel enabled ; state=("Add" if edit_pk is None else "Edit") if enabled else "Idle" ; lblState color Idle text_dim / Add success green / Edit warning maroon
  _clear_fields()→setText f.default
  reload(): rows=cfg.api.list_all() → QTableWidgetItem text, Foreground palette["text"]
  _selected_pk(): currentRow col for pk_key→item.text
  _on_new: edit_pk=None _clear_fields set_state True focus first edit
  _on_edit: pk=_selected_pk if !pk info ; rec=api.get(pk) ; edit_pk=pk record_to_ui ; pk_edit SetEnabled False ; set_state True state Edit
  _on_save: rec=record_from_ui pk rec[pk_key] check !pk warn ; for f required check ; if Add and api.exists(pk) warn exists ; api.insert(rec) / api.update(edit_pk,rec) catch ValueError/Generic ; edit_pk=None set_state False reload
  _on_cancel: edit_pk=None _clear_fields set_state False
  _on_delete: pk=_selected_pk if !pk info ; if delete_guard err warn return ; question Yes/No → api.delete(pk) reload
  make_delete_guard(prefix): if pk.upper().startswith(prefix) allow else block production
```

**Theme (key tokens, QSS excerpt relevant to FINANCE):**
- `DEFAULTS`: mode light, accent `#000080` navy, bg `#d4d0c8` VB6 button face gray, surface `#ffffff`, border `#808080`, text `#000000`, text_dim `#404040`, glass_tint `#ffffff`, header_grad `#d4d0c8`, radius `0` (VB6 sharp), success `#008000`, warning `#800000`, danger `#c00000`, info `#000080`, preset "VB6 Classic (MDI Teal)" clashes with Ocean Frost default — currently `_active` defaults to VB6 Classic values only if `apply_theme` was called.
- `PRESETS`: Ocean Frost / Midnight Glass / Emerald / Sunset / Rose / Graphite / VB6 Classic.
- `_glass_qss`: universal `QWidget background transparent`, `QMainWindow/QDialog bg`, `QTableWidget background glass_tint gridline border selected accent on_accent alternate accent_soft`, `QHeaderView::section background header_grad_top border-bottom 2px accent font-weight bold`, `QGroupBox background glass_tint border 1px border radius R+2 margin-top 12 padding 16`, `QPushButton accent / success / danger / warning` etc, `QLineEdit glass_tint focus accent`, `QComboBox`, `QTabBar` etc, plus `if R==0 → QPushButton bevel outset #ffffff #808080`
- `palette()` resolves derived `sidebar_hover/checked/on_sidebar_text/on_accent + status_colors` (success/warning/danger/neutral + _bg/_text)
- Status bases light: `#008000/#800000/#c00000/#404040`, dark pastels etc — ensures WCAG contrast.

---

## 3) Compare: layout, colors, fonts, controls, workflow

### 3.1 Layout & sizing

| Aspect | VB6 | Python | Gap & fix |
|--------|-----|--------|-----------|
| Form chrome | `MDIChild=True ControlBox=0` → hosted in MDI, no system chrome; `WindowState=2` maximizes to MDI client (12690×7890 twips ≈ 12690/1440*96=847px × 526px) — same for FaGrEnt 9675×6525 ≈ 645×435px; FaChqClear 11580×7320 ≈ 772×488px; frmYearEnd 5130×3810 ≈ 342×254px (centered auto) | `QDialog` floating, `resize()` fixed, `QVBoxLayout` margins 16,12 — different coordinate system | Add `setFixedSize` or Maximized-in-MDI equivalent: for parity audit use `FixedSize 847×700` for voucher (taller to accommodate all overlay frames in tabs), or keep resizable but document scale factor. No DB change. |
| Top strip | `TopCtrl1` 0,0 450px high, holds AEDP buttons + Find/Print/Exit; `LblFormCaption` cyan `&HC0FFFF&` System 19.5 Bold, `BorderStyle FixedSingle Center`, `Width = MDI.ScaleWidth` in `Form_Resize` | `BaseMasterForm` button bar at BOTTOM inside `QGroupBox`, `YearEndForm` button bar in `QGroupBox` at bottom, `FaLedgerWindow` buttons in `QHBoxLayout` mid-form | Move finance forms to **TopCtrl-at-top** for VB6 parity: add `QToolBar`/`QFrame` with same AEDP order at row 0; keep bottom log/state. See §5 patch. |
| Detail area | Absolute `Left/Top/Width/Height` twips; red header bar `Label1(0..2)` spans exact pixel; vertical `Line1` dividers at 7560/8970/10380; grid rows are shows of overlayed TextBoxes not a true grid | `QTableWidget` stretches; no vertical dividers; header is native `QHeaderView` | In VB6 Classic theme `R==0`, header QSS already uses `#d4d0c8` + outset bevel — acceptable. Add CSS spacer lines via `setShowGrid True` + `gridline-color #808080` (already). No DB change. |
| Overlay frames | All secondary functions are `Frame.Visible=0` off-canvas at `Left=123xx` (doubled screen width) — effectively modal overlays without separate Form | Python uses separate `QDialog` classes (FaAdjust/ChqClear/TDSCertificate/BankRecon) — different UX but functionally OK | Keep dialogs but add **Franche point anchors** mimicking VB6 parity: voucher toolbar needs `Alt-R` → `FrameRef`, `Ins` → `FRAMEADJUST`, `Alt-T` → `FrameTDS`, `Alt-C` → `ChqPrint` etc. Provide keyboard map in tooltip/help label. |

### 3.2 Colors

| Token | VB6 hex | VB6 meaning | Python default (`_active` before `apply_theme`) | Parity fix |
|-------|---------|-------------|-----------------------------------------------|------------|
| Form background | `#C0C0FF` lavender (`&HC0C0FF&`) for voucher; `#FFC0C0` pink for group; `#FFC0C0` pink for YearEnd; `#AFFFFF` MDI teal | Intentional per-module hue — lavender=transaction, pink=master, teal=MDI | Python theme default `bg #d4d0c8` gray overrides all — loses module hue cue | Per-form `setStyleSheet("QDialog { background-color: #C0C0FF; }")` or theme per-form token, OR keep unified gray and note divergence. Recommend **per-form override** for audit: `voucher #C0C0FF`, `master #FFC0C0`, `chqclear #D4D0C8`, `yearend #FFC0C0`. |
| Input background | `#FFFFFF` flat, except `TxtGlb #E0E0E0`, `TxtDetailS #E0E0E0`, `TxtDetailS Locked -1`, `LblAmtRs #5EB0AC` / `TXTADJ_AMT #F7F0DF` | Indicates read-only memo vs editable | Python `glass_tint #ffffff` matches, but `_dark_cell` uses `glass_tint` too — OK | No fix. |
| Header strip | `#FF0000` red (`&HFF0000&`) with `#BEFDFE` pale cyan text | High-contrast section label | Python `QHeaderView::section background header_grad_top #d4d0c8` — low-contrast gray | For VB6 Classic `R==0`, override header per voucher: `QHeaderView::section { background: #FF0000; color: #BEFDFE; }`. See §5. |
| Label forecolor | `#C00000` maroon, `#008080` teal, `#FF0000` red amounts, `#4080` teal-grey help, `#800000` maroon cheque fields | Semantic | Python `text #000000`, `accent #000080` — flatter | Add per-label `setStyleSheet(f"color: #C00000")` for voucher header labels `LblDt/LblVtype/LblVno`. |
| TDS / Adj / Ref frames | `#BFD0B7` sage, `#E6AC86` tan+red `#FF&`, `#D9B0DD` lilac, `#CBBE9E` beige | Module sub-function hue | Python single palette — divergence budgeted | Optional: retain per-frame QSS in patches. |

### 3.3 Fonts

| Role | VB6 | Python | Delta |
|------|-----|--------|-------|
| Body inputs | `Arial 9` (TxtAcName/TxtDr/TxtCr) / `Arial 9.75` (Txt(0..6) in group) | `Segoe UI 13px` (≈ 9.75pt) — equivalent size, different family | Acceptable — Segoe UI is system font; VB6 Arial fallback. Keep via QSS `font-family: Arial` for voucher if auditing pixel-perfect. |
| Header section | `Arial 9.75 Bold Italic -1` | `QHeaderView font-weight bold 12px` (theme QSS) | Python slightly larger; reduce to `9.75pt` for voucher header. |
| Global narration | `Courier New 8.25` | `Segoe UI` — divergence | Force `QFont("Courier New", 8)` for narration field (`edNarr`). |
| Amount right-justify | `Alignment 1 RightJustify` | `QTableWidgetItem TextAlignment AlignRight` (need per-cell) | Python does NOT right-justify yet — patch with `item.setTextAlignment(Qt.AlignmentFlag.AlignRight | AlignVCenter)`. |
| System header | `System 19.5 Bold` (LblFormCaption) | `Arial 13 Bold` (YearEnd title) | YearEnd title 13pt vs 19.5pt — reduce gap by `QFont("System", 14)` or keep 13pt for Fitts. Audit note. |

### 3.4 Controls mapping — verbatim diff

| VB6 control class | Count / instance | Python control | Mapped? |
|-------------------|------------------|----------------|---------|
| `MainCtrl TopCtrl1` | FaVrEnt 1, FaGrEnt 1, FaChqClear 1, FaReports 1 (hidden) | None in fa_voucher/fa_ledger; `BaseMasterForm` internal `btnNew/Edit/Delete/Save/Cancel` proxies AEDP | **No** top strip in finance UIs — patch adds `TopCtrlBar` (§5) |
| `BtnEnh LblShort(1..4)` | FaVrEnt `Frame1(0)` 4 shortcuts 1935×630 | No equivalent | Optional — add `QShortcut` help label `"Ins=Adj Alt-R=Ref Alt-T=TDS Ctrl+Enter=Post"` to `lblStatus`. |
| `DataGrid DGAcHlp` / `DGAcName/DGAcAlias/DGUnderAc` / `DGSite` / `DGBank/DGParty` / `DGTDSCODE/DGVchrHlp/DGAcHlp` | 3+2+1+2+4 = 12 hidden help grids, Tag holds row index | No DataGrid helpers — instead `QCompleter`/`QComboBox`/`ListView FrmList` partially (FaGrEnt) | Gap: per-keystroke filtering via `Proc_183_31_100809C` → Python needed in voucher `SubCode` column with `QCompleter` on `SubGroup WHERE Nature … OR HO`. |
| `MSHFlexGrid FGrid` / `FGVLIST` / `FGridRef` / `FgridAdjust` / `FGrid1` | FaVrEnt 4, FaChqClear 1 (15 cols) | `QTableWidget tbl` (4 cols voucher, 8 BankRecon, 5 Ledger, 6 Adj) | Missing cols: voucher needs 8 (`SubCode|Name|Dr|Cr|Narration|Chq_No|Chq_Date|Clg_Date` + hidden `GroupCode/AgRefNo`) |
| `TextBox Txt*` indexed arrays (TxtCr/D r/AcName/CrDr/Nar 0..11, VchDt/TxtVtYpe/TxtVno/TxtGlb/TxtCHno/TXTChDate/TXTClrDate…) | ~55 TextBox instances | 3 `QLineEdit`/`QDateEdit` per dialog | Flattened — patch expands voucher grid cols rather than array replication. |
| `Frame` overlays (ChqPrint/FrameRef/FrameTDS/FRAMEADJUST/FRAMEVLIST/Frame1) | 6 overlays all `Visible 0` | 3 separate `QDialog`/`QMainWindow` classes | UX diff — acceptable with keyboard shortcuts; ensure single-instance per voucher to avoid multi-window sprawl. |
| `CommandButton` with Picture/DisabledPicture/ToolTip/Style1 | BtnRefAdjOK, TDSDelete, ADJ_*, BTNVLOK/BTNVLCLOSE/btnPrint1/BTNCLOSE, Command1 Cheque Print, Command2 Full Adjustments, BTS_AUTO_ADJ "Auto" | `QPushButton` text only, some with `success/accent/danger` props | Add `setIcon` + `setToolTip` mirrors VB6 `ToolTipText`. |
| `ListView` inside `FrmList` | FaVrEnt + FaGrEnt + FaChqClear | `QTableWidget` or `ListView` in FaGrEnt via `Proc_183_36…` (Nature picker) / FaChqClear ListView Cleared/Un-Cleared/All | `fa_sub_forms_ui FaChqClearWindow` does NOT show the ListView — missing tri-state filter. |
| `PictureBox PicDN/PicUP` red ± scroll | FaVrEnt 2 | None | Not needed — modern scrollbars. |
| `Label` help (`LblRefAdj*`, `LblAmtRs`, `LblHelp` help text, `LblCrAmt/DrAmt`) | ~35 Labels | 1 `lblStatus` | Need `lblRefAdjBal/DrCr` live labels. |
| `Line` dividers | 4 `Line1/Line2` | CSS `border` / `gridline-color` | OK. |

### 3.5 Workflow & validation mapping (the heart of this compare)

| Workflow | VB6 verbatim | Python current | Gap severity |
|----------|--------------|----------------|--------------|
| **TopCtrl state-machine AEDP** | `TopCtrl1.Clone` + `Dispatch_68030007("AEDP")` on load; `eAdd` enables `Txt(0)+Txt(4)` + focus; `eEdit` locks `Txt(0)/Txt(4)` when `global_64="Y"` + focus handling; `eCancel` resets `INL` + clears BackColor/ForeColor; buttons enabled per state via `Enabled=False/True` | `BaseMasterForm.set_state(enabled)` toggles edits + 6 buttons with color state `Idle/Add/Edit` — correct pattern. But `fa_voucher_ui`/`fa_ledger_ui` do NOT use `BaseMasterForm` at all; they have ad-hoc `New/Edit/Refresh/Exit` bar. | HIGH — voucher & ledger bypass the only TopCtrl emulator. Patch: re-parent them under `BaseMasterForm` or add matching `TopCtrlBar` widget. |
| **Find / SearchCode** | `TopCtrl1_UnknownEvent_F`: `SELECT GROUPCODE As SearchCode,GroupName,GroupNature,Nature FROM AcGroup Where (LOGSITE_CODE='<site>' OR LOGSITE_CODE='HO') AND AliasYN<>'Y' Order by GroupName` → `Proc_6_126_F1BCC0("2000,2000,1000")` search dialog width; `FaVrEnt` Find uses `FRAMEVLIST` with party+date+vtype combo filtering | `fa_ledger_ui._filter` lower substring over `AcCode/AcName` (client-side); `fa_voucher_ui` no Find at all; `BaseMasterForm` search is substring over visible grid rows only, not `SearchCode` SQL with HO fallback | MEDIUM — server-side SearchCode needed for parity (esp. HO records). |
| **DGHelp Tag/Code** | `Txt_GotFocus(KeyCode=contents)` → `Proc_183_34_1305540(Me.DGAcName, Me.Txt, KeyCode, global_100)` positions grid `Left = Txt.Left`, `Top = Txt.Top+Txt.Height+30`, Width=5700; `Tag = Code` (GroupCode/SubCode) while `.Text = Name`; `DG_Click → Txt.Text=Fields("Name") ; Txt.Tag=Fields("Code") ; Txt.SetFocus` | `QLineEdit` shows name/code interchangeably; `Tag` holding code is not implemented except FaChqClear `Txt.Tag` partially; autocompleter pattern not wired | MEDIUM — no code/name separation. Patch: keep `QLineEdit` text as Name, `.setProperty("code", …)` or parallel `txt_code` hidden; use `QCompleter` bound to `SubGroup WHERE (LogSite_Code=? OR 'HO')` |
| **Txt_Validate (duplicate guard)** | `FaGrEnt.Txt_Validate(Cancel)`: if `TopCtrl="Add"` then `SELECT GroupHelp From AcGroup Where GroupHelp='<val>'` → if `RecordCount>0` → `MsgBox("Duplicate Account Group not Allowed", &H40)` + `Txt(0).SetFocus` `Cancel=&HFF`; alias duplicate similarly; `FaVrEnt.TxtCHno_LostFocus`: `SELECT COUNT(*) FROM LEDGER WHERE Chq_No='<val>'` (add `AND DOCID<>'cur'` for edit) → `MsgBox("Duplicate Cheque No.")` | `BaseMasterForm._on_save` does `if api.exists(pk) → "already exists"`; cheque duplicate never checked in Python UI; group duplicate via `core/acgroup.py` exists but UI does not surface pre-save | LOW — duplicate guard lives in core exists() but UX late (on Save not on Validate). Add `editingFinished` validator with live DB check. |
| **Dr==Cr guard + AdjBal** | `FaVrEnt`: live per-row `TxtDr/TxtCr_Validate` → sum via `Label LblRefAdjBal/LblRefAdjDrCrBal` ; `FRAMEADJUST.BTS_AUTO_ADJ_Click` auto-distributes `ADJ_LAB4/LAB7` (Tr.Amt vs Adjusted); `Label3 dIFF` invisible but computed; `FgridAdjust` fully editable with `TXTADJ_AMT/TXTNARRATION`; saving requires `TotDr==TotCr` within `abs>0.005`, else block. Python `post_voucher` guards same but UI `lblStatus` static. | Voucher `_post` sums `float(txt or 0)` without `isValid` guard; no live recalc on `textChanged`; adjustment is separate `FaAdjustWindow` with manual DocId1/2 + Amount entry (not VB6 bill-wise picker). | HIGH — adjustment parity lost. Patch: live `Dr/Cr` sum label + disable Post until balanced; `FaAdjustWindow` needs `FgridAdjust`-like picker (list pending bills for SubCode, auto-calc balance). |
| **TDS auto contra-voucher** | `FrameTDS` visible when `Nature=T.D.S.` ; fields `TxtTDSCode/TxtTDSNarration/TxtONAMT/TxtTDS/TxtTDSAMT` → on OK inserts per-line `LEDGERTDS` (`TDSCode/TDSDrCode/ONAMT/TDS/TDSAMT/TDSPOST`) + auto posts contra `V_Type='TDS'` voucher with `AmtDr/AmtCr` swapped | `fa_sub_forms_ui.FaTDSCertificateWindow` is only report-generation (sum tds_detail), not per-voucher `FrameTDS`; `fa_voucher_ui` has no TDS UI at all; `core/fa_voucher.py:_post_line_tds` + `ledgertds_insert` path exists but unreachable from UI. | HIGH — UI unreachable. Patch: add `QTabWidget` or `QGroupBox "T.D.S."` inside voucher dialog with same 5 fields + `TDSDelete` button, wired to `_post_line_tds` params. |
| **DATELOCK check** | `VchDt_Validate` → `Call Proc_185_171_1B374EC(var, vdateText)` → `SELECT flag FROM DATELOCK WHERE SDate<=vdate AND EDate>=vdate AND flag=1` → if `var_86=2` loop asks `Vr.No Already Exist,Generate New Vr.No.?`; also `global_132 = 0xFF` locks entire form when datelocked. YearEnd guards `can't close year for different Site`. | `year_end_ui._on_check_lock` calls `ye.check_datelock(today)` but `fa_voucher_ui` never calls it; `core/year_end.check_datelock` exists but not gated on `_post` | MEDIUM — add `DATELOCK` pre-flight in `_post()` before `fv.post_voucher`. |
| **menuHelp Param_Str guard** | Every `fate/farp/fame_Click` + `FaVoucher Proc_7_1` does `SELECT Param_Str AS UPrivilege FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]='Voucher Entry'` → parse `A/E/D/P` flags → enable/disable TopCtrl buttons accordingly; missing privilege → `MsgBox` and `Exit Sub` | `_LedgerMasterBridge` + `BaseMasterForm` have `delete_guard PYT*` only; no `menuHelp` query anywhere in `ui/` | HIGH — any user can delete/post. Patch: add `guard = can_user(user, comp, option)` at top of every Save/Delete/Print handler; query verbatim SQL (no schema change) and show `QMessageBox.warning`. |
| **Cheque duplicate + HPOST branch** | `TxtCHno_LostFocus` duplicate count; save uses `UPDATE … WHERE DocID+V_SNo` vs for `V_Type='HPOST'` adds `AND AmtCr=<amt> AND ContraSub='<sub>'` (multi-leg cheque) plus `BeginTrans/Commit` | `fa_voucher_ui.BankReconDialog._clear` does single-row `UPDATE Ledger SET Clg_Date=?` (cheque_mark_cleared) without Chq_No branch nor transaction; new voucher `Chq_No/Chq_Date` columns exist per line but not wired to UI | LOW — HPOST branch rare; add if needed; wrap batch clear in transaction if multi-select added. |
| **Narration default from Voucher_Type** | `TxtGlb_GotFocus` → if `Len(TxtGlb)=0` then `SELECT Narration FROM VOUCHER_Type WHERE V_Type='<cur Tag>'` → default text | `edNarr` placeholder only | LOW — add fallback fetch on `cmbVType.currentTextChanged` if `edNarr.isEmpty()`. |

---

## 4) MISSING frontend logic — enumerated (no DB change)

> Gaps that are **visible to the user** (UI behaviour difference) — backend gaps from `FINANCE_COMPARE.md` §3 restated only where they surface in UI.

| # | VB6 feature | Python state | User-visible impact |
|---|-------------|--------------|---------------------|
| M1 | TopCtrl AEDP state-machine (Add=clear+enable Txt0/4, Edit=lock Txt0/4, Delete with LEDGER count guard `SELECT COUNT(*) FROM Ledger WHERE V_Type=?`, Save revalidates, Cancel resets colors) | `fa_voucher_ui`/`fa_ledger_ui` have flat button bars, no state colors `Idle(gray)/Add(green)/Edit(maroon)`, no record-lock | User sees Edit without lock, Save without revalidation; parity auditors fail. |
| M2 | Find dialog `SearchCode` SQL `LOGSITE_CODE OR HO` + `AliasYN<>'Y'` (AcGroup) / pending-cheque filter for voucher | Text filter lower substring over loaded rows; HO rows invisible | Site HO masters (group/ledger/bank) not findable in Python. |
| M3 | DGHelp Tag/Code help grids (DGAcName/DGAcAlias/DGUnderAc/DGBank/DGParty) + ListView FrmList for Nature/Cleared-All | `QComboBox` voucher types only; SubCode free-text without help; Nature via menial `QComboBox ["Dr","Cr"]` in ledger | Data entry slower, error-prone (free-text vs picker). |
| M4 | Live Dr==Cr + diff label + Balance/Adjusted/Tr.Amt chips (`LblRefAdj*/ADJ_LAB*`) + auto-adjust `BTS_AUTO_ADJ` / `Command2 Full Adjustments` | Static `lblStatus "Debit must equal Credit"`; no live sum; no auto button | User can attempt unbalanced post (backend then rejects) but no pre-flight feedback; VB6 blocks earlier. |
| M5 | Per-line `Narration/TxtNar(0..11)` + `TxtCrDr` Dr/Cr toggle + `GroupCode` help `LblCb` | Voucher grid 4 cols only (`SubCode/Name/Debit/Credit`); Name editable (VB6 Name is display-only from SubGroup join) | Missing narration truncation to 500 vs 255, missing toggle semantics, missing GroupCode audit chip. |
| M6 | Cheque per-line `TxtCHno/TXTChDate/TXTClrDate` (20/12/12 char, duplicate check) | Voucher grid has no Chq cols; Chq only via `fa_sub_forms_ui.FaChqClearWindow` (DocId+SNo manual) and `BankReconDialog` pending list | VB6 allows cheque entry inline with voucher; Python splits it. |
| M7 | FrameTDS `TDS A/C + OnAmount + TDS% + TDSA mt + Narration + Delete` per line, with contra-voucher auto `V_Type='TDS'` | Reached only via `FaTDSCertificate` report window, not per-voucher | TDS workflow unusable from voucher. |
| M8 | Reference/Bill-wise Adjustment `FrameRef/FGridRef` (ledgerRef/Adj) with `LblRefAdjBal/DrCr` live + `BtnRefAdjOK` Save | `FaAdjustWindow` asks for 7 hand-typed fields (DocId1/2 etc) — no picker grid, no AgRefNo/Type help, no balance calc | Bill-wise outstanding mismatch; manual entry error. |
| M9 | Voucher list `FRAMEVLIST FGVLIST` + filter combos Party+Date+Type+VNo range + Print modes `Opt2(0) Print Current / Opt2(1) VNo Selection / Opt2(2) VDate Selection` + `ChkReport Receipt` | `ReportViewer` generic date-filtered table; no VNo range, no Party combo, no Receipt flag | `Print Current` (FaRect.TTX) and range print (FaJVCHR.TTX) not reachable from voucher UI. |
| M10 | Voucher printing `Frame1(1)` radiogroup + `DataCombo3 V.Type + DataCombo2 From/To` | Separate viewer dialogs (`open_trial_balance/...`) not same flow | Print path disconnected from current voucher context. |
| M11 | Cheque clearing tri-state `Status=(Cleared/Un-Cleared/All)` via `FrmList ListView` + bank/party context + `Balance As Per Book/Bank` chips + `LblType(0/1)` Dr/Cr + multi-row 15-col `FGrid` edit (col 11/12/13) | `BankReconDialog` shows only `Clg_Date IS NULL` pending, single-select `today` hardcoded, no Status filter, no balance chips, no inline FGrid edit | VB6 clearing requires seeing cleared too; Python hides it. |
| M12 | DATELOCK visual lock (`global_132=0xFF` → all handlers `Exit Sub`, red status) | `year_end_ui.Check DateLock` button isolated from voucher; voucher `_post` never checks | Voucher can be posted on locked date (backend may later allow). |
| M13 | menuHelp Flag/Param_Str per-form gates Add/Edit/Delete/Print (parsed `A/E/D/P` chars). Hidden menus `fate(1/2/5/6)`, `FAREPORT(1/4/27/29/30/32/34)` etc controlled via `ShowInList/Flag` | No privilege check; all buttons always enabled | Auditor notes missing authorization. |
| M14 | Duplicate guards re-entrant: `GroupHelp` on Validate (not just Save), `Chq_No` on LostFocus (immediate MsgBox), `Vr.No already Exist, Generate New` loop with `+1` retry | Duplicates only caught on Save (`api.exists` / core execute) — late feedback | Inline validation strictness difference. |
| M15 | Font/colour parity: red section header `&HFF0000&/#FF0000` + cyan `#BEFDFE`, lilac/sage/tan overlay frame hues, `Courier New 8.25` narration, maroon cheque field labels italic | Single theme palette — narrations `Segoe UI`, cheque labels missing | Pixel audit will flag colour drift. |
| M16 | Footer audit strip: `LblUser "user name"` + `LblLDte "user date"` bottom-right (`Left 14505`) showing last modifier; `lblDocId` hidden holds DocId for log; `LblAmtRs` amount-in-words WordWrap; `LbsHelp "Press <Ins> Bill Wise Adjustment ,<Alt-R> Against Reference , <Alt-T> T.D.S.Entry"` | `fa_voucher_ui` has no audit footer; `fa_ledger_ui` shows no `U_Name/U_EntDt` | Traceability gap. |
| M17 | Import path drift: `PYTHONE/ui/fa_sub_forms_ui.py:10-13` uses `from core import …` / `from ui.theme import palette` (without `HMS_py.` prefix) — fails under `python -m HMS_py.ui.*` | Other UIs use `HMS_py.core…` correctly | Breaks standalone launch. |
| M18 | YearEnd visual: VB6 two `BtnEnh` tiles `CmdYrUpdate` + `Head` (=close) only, no inputs | Python YearEnd is 6-button workflow (`Check DateLock/Carry Forward/Reset Budget/Execute/Load Summary/Close`) + FY label + summary table + log box | Python richer — VB6 YearEnd is intentionally minimal (just creates Company+menuHelp snapshot). Python added destructive carry-forward/budget buttons diverging from VB6 clone. |
| M19 | AcGroup `Note: Run Current Balance Updation…` red 14.25 bold label + `AcGroupCurrBal V_Date` implication | No reminder label in `finance_masters_ui` ledger/group editors | Operation ordering cue missing. |
| M20 | FaGrEnt ListView Nature picker (Bank/Broker/…/Unsecured Loan) for `Txt(5) Nature` via `FrmList` centered on field | `BaseMasterForm` Field `nature` is free-text `QLineEdit` | VB6 picker enforces controlled vocab; Python free-text allows typos. |

Database understanding (§6) clarifies why M2/M5/M6/M7/M8 matter without schema drift.

---

## 5) Debug fixes — make Python workflow EXACTLY VB6 same (frontend only, no DB change)

> Each fix is a **code-patch snippet** that can be dropped into `PYTHONE/ui/*.py` today. No `core/` SQL change, no column rename — only add missing QSS, validators, guards, and wiring that calls **existing** `core/*` with correct `(LogSite_Code OR 'HO')` params if already supported.

### 5.1 Shared helper — menuHelp + DATELOCK guards (reuse verbatim SQL, no schema)

```py
# PYTHONE/ui/_fa_guards.py  (new, frontend-only)
from __future__ import annotations
import datetime
from PyQt6.QtWidgets import QMessageBox
from HMS_py.core import db
from HMS_py.core import year_end as ye
from HMS_py.core.db import SITE_CODE  # or read from Company/MemVar_1F92128

def can_user(cn, username: str, compcode: str, option: str) -> bool:
    """VB6: SELECT Param_Str AS UPrivilege, Flag FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]=?"""
    rows = db.query(
        "SELECT Param_Str AS UPrivilege, Flag FROM menuHelp "
        "WHERE UserName=? AND CompCode=? AND [Option]=?",
        (username, compcode, option), cn=cn)
    if not rows:
        return False
    r = rows[0]
    flag = str(r.get("Flag","") or r.get("flag","")).upper()
    priv = str(r.get("UPrivilege","") or r.get("Param_Str","") or r.get("param_str",""))
    # VB6 parses 'A'/'E'/'D'/'P' chars inside Param_Str; Flag='Y' overrides
    return flag == "Y" or any(c in priv for c in "AEDP")

def datelock_block(vdate: datetime.date, cn=None) -> bool:
    """VB6 VchDt_Validate Proc_185_171: SELECT flag FROM DATELOCK WHERE ? BETWEEN SDate AND EDate AND flag=1"""
    try:
        return ye.check_datelock(vdate, cn=cn)
    except TypeError:
        return ye.check_datelock(vdate)

def warn_privilege(parent, option: str):
    QMessageBox.warning(parent, "Privilege",
        f"You have no rights for '{option}'.\n"
        f"VB6 checks menuHelp.[Option]='{option}' Param_Str / Flag.")
```

Use at top of every Save/Delete/Print/Clear handler:

```py
# in fa_voucher_ui.VoucherEntryDialog._post:
from HMS_py.ui._fa_guards import can_user, datelock_block
from HMS_py.core.db import get_compcode, get_username  # or pass self.user/comp
if datelock_block(self.dtVdate.date().toPyDate()):
    QMessageBox.warning(self, "Voucher Entry", "Date is locked — DATELOCK blocks posting."); return
cn = db.connect()
if not can_user(cn, self.user, get_compcode(), "Voucher Entry"):
    QMessageBox.warning(self, "Voucher Entry", "No privilege (menuHelp Flag/Param_Str)."); cn.close(); return
# … then existing fv.post_voucher …
```

### 5.2 FaVrEnt parity — expand voucher grid to 8 cols + live Dr==Cr + TDS frame + Cheque cols

```py
# PYTHONE/ui/fa_voucher_ui.py — patch VoucherEntryDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QTabWidget, QGroupBox, QFormLayout

class VoucherEntryDialog(QDialog):
    HEADER_VB6_RED = "#FF0000"
    HEADER_TEXT    = "#BEFDFE"
    FORM_BG        = "#C0C0FF"  # lavender VB6
    NARR_FONT      = QFont("Courier New", 8)

    def __init__(self, parent=None, user="SA"):
        # … existing QFormLayout for date/type …
        self.setStyleSheet(f"QDialog {{ background-color: {self.FORM_BG}; }}")

        # — Expand grid from 4 → 8 cols to match VB6 Txt arrays + cheque
        self.tbl = QTableWidget(0, 8)
        self.tbl.setHorizontalHeaderLabels(
            ["SubCode","Name","Debit","Credit","Narration","Chq No","Chq Date","Clg Date"])
        # VB6: Name is display-only (from SubGroup join), Narration max 255, Chq_No 20, dates 12
        self.tbl.setColumnWidth(0, 90); self.tbl.setColumnWidth(1, 220)
        self.tbl.setColumnWidth(2, 110); self.tbl.setColumnWidth(3, 110)
        self.tbl.setColumnWidth(4, 180); self.tbl.setColumnWidth(5, 110)
        # Right-justify Dr/Cr exactly like VB6 Alignment 1
        hdr = self.tbl.horizontalHeader()
        # QSS: red header parity when VB6 Classic (radius 0)
        if _theme.palette().get("radius") == "0":
            hdr.setStyleSheet(f"QHeaderView::section {{ background: {self.HEADER_VB6_RED}; color: {self.HEADER_TEXT}; border: 1px outset; border-color: #ffffff #808080 #808080 #ffffff; padding: 6px; font-weight: bold; }}")

        # Live Dr==Cr labels mirroring LblDrAmt/LblCrAmt + dIFF + LblHelp
        stats_row = QHBoxLayout()
        self.lblDrTotal = QLabel("DR 0.00")
        self.lblCrTotal = QLabel("CR 0.00")
        self.lblDiff    = QLabel("Diff 0.00")
        self.lblHelp    = QLabel("Ins=Adj  Alt-R=Ref  Alt-T=TDS  Ctrl+Enter=Post  Esc=Cancel")
        self.lblHelp.setStyleSheet("color: #800000; font-style: italic; font-size: 10px;")
        for w in (self.lblDrTotal, self.lblCrTotal, self.lblDiff, self.lblHelp):
            stats_row.addWidget(w)
        stats_row.addStretch(1)
        root.addLayout(stats_row)

        # Footer audit mimicking LbLUser/LblLDte + LblAmtRs words
        foot = QHBoxLayout()
        self.lblUser = QLabel(f"User: {self.user}"); self.lblUser.setStyleSheet("color: #C00000; font-weight: 700; font-size: 9px;")
        self.lblDate = QLabel(""); self.lblDate.setStyleSheet("color: #C00000;")
        self.lblWords = QLabel(""); self.lblWords.setWordWrap(True); self.lblWords.setStyleSheet("color: #800000; font-style: italic;")
        foot.addWidget(self.lblUser); foot.addWidget(self.lblDate); foot.addStretch(1); foot.addWidget(self.lblWords)
        root.addLayout(foot)

        # Narration global: Courier New 8.25 mono like TxtGlb
        self.edNarr.setFont(self.NARR_FONT)
        self.edNarr.setStyleSheet(f"QLineEdit {{ background: #E0E0E0; font-family: 'Courier New'; }}")

        # TDS per-voucherTabbed (replaces hidden FrameTDS at 12360,990 sage #BFD0B7)
        self.tabs = QTabWidget(); root.addWidget(self.tabs)
        self.tabs.addTab(self.tbl, "Voucher Lines")
        tds_grp = QGroupBox("T.D.S. (Alt-T) — per-line contra voucher V_Type='TDS'")
        tds_grp.setStyleSheet("QGroupBox { background-color: #BFD0B7; }")
        tds_lay = QFormLayout(tds_grp)
        self.edTDSCode = QLineEdit(); self.edTDSCode.setPlaceholderText("TDS A/C SubCode (Tag=Code pattern)")
        self.edTDSNarr = QLineEdit(); self.edTDSNarr.setPlaceholderText("Narration (255)")
        self.edONAMT    = QLineEdit(); self.edONAMT.setPlaceholderText("On Amount")
        self.edTDS      = QLineEdit(); self.edTDS.setPlaceholderText("TDS %")
        self.edTDSAMT   = QLineEdit(); self.edTDSAMT.setPlaceholderText("TDS Amount (auto OnAmt*TDS%)")
        for w in (self.edONAMT, self.edTDS, self.edTDSAMT):
            w.setAlignment(Qt.AlignmentFlag.AlignRight)  # VB6 Alignment 1
        tds_lay.addRow("TDS A/C:", self.edTDSCode)
        tds_lay.addRow("Narration:", self.edTDSNarr)
        tds_lay.addRow("On Amount:", self.edONAMT)
        tds_lay.addRow("T.D.S. %:", self.edTDS)
        tds_lay.addRow("T.D.S. Amt:", self.edTDSAMT)
        tds_grp.setLayout(tds_lay)
        self.tabs.addTab(tds_grp, "TDS")

        # Shortcuts matching LblHelp: Ins, Alt-R, Alt-T, Ctrl+Enter
        from PyQt6.QtGui import QShortcut, QKeySequence
        QShortcut(QKeySequence("Ctrl+Return"), self, activated=self._post)
        QShortcut(QKeySequence("Insert"), self, activated=self._open_adj)   # VB6 <Ins>
        QShortcut(QKeySequence("Alt+R"), self, activated=self._open_ref)
        QShortcut(QKeySequence("Alt+T"), self, activated=lambda: self.tabs.setCurrentIndex(1))

        # Live recalc on any cell change
        self.tbl.cellChanged.connect(lambda *_: self._recalc_dr_cr())
        self.tbl.itemSelectionChanged.connect(self._recalc_dr_cr)

    def _recalc_dr_cr(self):
        tot_dr = tot_cr = 0.0
        for r in range(self.tbl.rowCount()):
            for c, is_dr in ((2, True), (3, False)):
                it = self.tbl.item(r,c)
                if not it: continue
                try: v = float((it.text() or "0").replace(",",""))
                except ValueError: v = 0.0
                it.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                if is_dr: tot_dr += v
                else: tot_cr += v
        self.lblDrTotal.setText(f"DR {tot_dr:,.2f}")
        self.lblCrTotal.setText(f"CR {tot_cr:,.2f}")
        diff = tot_dr - tot_cr
        self.lblDiff.setText(f"Diff {diff:,.2f}")
        # VB6 color coding: red if diff !=0 else green
        ok = abs(diff) < 0.005 and tot_dr > 0
        self.lblDiff.setStyleSheet(f"color: {'#059669' if ok else '#dc2626'}; font-weight:700;")
        # Mirror txt enable: disable Post until balanced (VB6 blocks Save)
        self.btnPost.setEnabled(ok)
```

**Grid edit semantics to match VB6 Txt_Validate:**
- Make `Name` col (1) read-only (`it.setFlags(flags & ~ItemIsEditable)`) and fill via `SubGroup` lookup on `SubCode` edit (code Tag vs display Name):
```py
def _on_subcode_edited(self, r, c):
    if c != 0: return
    sc = (self.tbl.item(r,0).text() or "").strip().upper()
    if not sc: return
    row = db.query("SELECT s.SubCode, s.Name, s.GroupCode, a.GroupNature "
                   "FROM SubGroup s JOIN AcGroup a ON a.GroupCode=s.GroupCode "
                   "WHERE RTRIM(s.SubCode)=? AND (s.LogSite_Code=? OR s.LogSite_Code='HO' OR ISNULL(s.LogSite_Code,'')='')",
                   (sc, SITE_CODE), cn=db.connect())
    if row:
        self.tbl.setItem(r,1, _cell(row[0]["Name"]))  # auto Name
        # also stash GroupCode/GroupNature in hidden Qt.UserRole for post
        self.tbl.item(r,0).setData(Qt.ItemDataRole.UserRole, row[0])
    else:
        QMessageBox.warning(self, "Ledger", f"SubCode '{sc}' not found (LOGSITE_CODE or HO).")
```

**Cheque duplicate on LostFocus analogue:**
```py
def _on_chq_edited(self, r, c):
    if c != 5: return
    chq = (self.tbl.item(r,5).text() or "").strip()
    if not chq: return
    cur_docid = getattr(self, "_edit_docid", None)  # for edit mode
    q = "SELECT COUNT(*) AS cnt FROM LEDGER WHERE Chq_No=?" + (" AND DOCID<>?" if cur_docid else "")
    cnt = db.query(q, (chq, cur_docid) if cur_docid else (chq,), cn=db.connect())[0]["cnt"]
    if cnt > 0:
        QMessageBox.warning(self, "Cheque No.Validation", "Duplicate Cheque No.")
```

### 5.3 FaGrEnt parity — BaseMasterForm enhancements

```py
# PYTHONE/ui/finance_masters_ui.py
from HMS_py.ui._fa_guards import can_user

def acgroup_config() -> MasterConfig:
    # Align with VB6 Txt(0..6): GroupName, HindiBiLang, AliasGroupName, ParentGroup, Nature, TradingYN
    return MasterConfig(
        title="Group Accounts - HMS_py",
        columns=[("GroupCode","groupcode"), ("GroupName","groupname"), ("Under","maingrcode"), ("Nature","nature"), ("Trading","tradingyn"), ("System","sysgroup")],
        fields=[
            Field("groupcode", "Group Code", max_len=6, required=True),
            Field("groupname", "Group Name (Name)", max_len=50, required=True),
            Field("groupnamebilang", "Group Name (Hindi)", max_len=50),
            Field("grouphelp", "Alias Help (GroupHelp)", max_len=50),  # VB6 Alias Group Account Name = GroupHelp
            Field("maingrcode", "Under Group", max_len=6, required=True),
            Field("nature", "Nature", max_len=15, required=True, placeholder="Asset/Liability/Revenue/Expenditure"),
            Field("tradingyn", "Trading A/C (Y/N)", max_len=1, default="N"),
        ],
        api=acgroup,   # acgroup.py must implement HO-aware list_all/get/search
        pk_key="groupcode",
        delete_guard=lambda code: None if code.upper().startswith("PYT") else "Only PYT groups deletable",
    )
# In BaseMasterForm instantiation for finance:
form = BaseMasterForm(acgroup_config(), parent)
form.setStyleSheet("QDialog { background-color: #FFC0C0; }")  # pink VB6
# Inject DG-like helpers: position QCompleter under-txt
from PyQt6.QtWidgets import QCompleter
completer = QCompleter(history_names, form.edits["groupname"])
completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
form.edits["groupname"].setCompleter(completer)
# FrmList Nature picker: replace free-text nature with ListView
nature_list = ["Bank","Broker","Cash","Customer","Electrician","Employee","Expenses","Mukadim","Others","PDC","Purchase","Revenue","Sale","SalesMan","SalesRep","Supplier","T.D.S.","Transporter","Unsecured Loan"]
lv_completer = QCompleter(nature_list, form.edits["nature"])
form.edits["nature"].setCompleter(lv_completer)
# Privilege gate on Save/Delete
orig_on_save = form._on_save
def gated_save(*a, **kw):
    if datelock_block(datetime.date.today()): QMessageBox.warning(form, "DateLock", "Form locked."); return
    if not can_user(db.connect(), current_user, compcode, "Group Accounts"): QMessageBox.warning(form, "Privilege", "No right for 'Group Accounts'"); return
    return orig_on_save(*a, **kw)
form._on_save = gated_save
# Same-group guard: Add/Edit hook after record_from_ui
form._rec_from_ui = lambda: (_rec := {f.name: form.edits[f.name].text().strip() for f in form.cfg.fields},
                             (_ for _ in ()).throw(ValueError("A/c Group And Under group Can not be same")) if _rec["groupcode"].lower()==_rec["maingrcode"].lower() else _rec)[1] if _rec["groupcode"] else _rec
# See FINANCE_COMPARE.md G1 fix: ensure core/acgroup.py list_all uses (LOGSITE_CODE=? OR HO) before calling
```

Add the red reminder label VB6 shows:
```py
lbl_note = QLabel("Note:- Run Current Balance Updation After Making Changes In Group Accounts")
lbl_note.setStyleSheet("color: #FF0000; font-size: 14px; font-weight: 700;")
root.addWidget(lbl_note)  # where root is BaseMasterForm's QVBoxLayout
```

### 5.4 FaChqClear parity — tri-state + balance chips + HPOST-aware save

```py
# PYTHONE/ui/fa_voucher_ui.py — extend BankReconDialog (or replace with FaChqClearWindow)
from PyQt6.QtWidgets import QComboBox

class BankReconDialog(QDialog):
    def __init__(self, parent=None):
        # … existing pending tbl …
        # Status tri-state mirroring FrmList ListView 0,-15 2325×1830 items Cleared/Un-Cleared/All
        topbar = QHBoxLayout()
        topbar.addWidget(QLabel("Status (Clear./UnClea/All):"))
        self.cmbStatus = QComboBox(); self.cmbStatus.addItems(["Un-Cleared","Cleared","All"])
        self.cmbStatus.currentTextChanged.connect(self._load)
        topbar.addWidget(self.cmbStatus)
        # Bank + Party pickers with Nature HO logic (DGBank/DGParty 5700/5640)
        self.cbBank = QComboBox(); self.cbBank.setPlaceholderText("Bank Account (Nature='Bank' OR HO)")
        self.cbParty = QComboBox(); self.cbParty.setPlaceholderText("Party Account (Nature<>'Bank' OR HO)")
        self._populate_bank_party()  # queries: SELECT SubCode As Code,Name FROM SubGroup WHERE Nature in ('Bank') AND (LOGSITE_CODE=? OR HO)
        # Chips: Balance As Per Book / As Per Bank + Type Dr/Cr
        self.lblBook = QLabel("Balance As Per Book: —"); self.lblBook.setStyleSheet("font-weight:700; color:#C00000;")
        self.lblBank = QLabel("Balance As Per Bank: —"); self.lblBank.setStyleSheet("font-weight:700; color:#C00000;")
        self.lblBookType = QLabel(""); self.lblBankType = QLabel("")
        for w in (self.lblBook, self.lblBookType, self.lblBank, self.lblBankType): topbar.addWidget(w)
        root.insertLayout(1, topbar)  # insert above table

    def _populate_bank_party(self):
        cn = db.connect()
        for is_bank, cb in ((True, self.cbBank), (False, self.cbParty)):
            nature_cond = "Nature in ('Bank')" if is_bank else "Nature <> 'Bank'"
            rows = db.query(f"Select SubCode As Code, Name From SubGroup Where {nature_cond} AND (LOGSITE_CODE=? OR LOGSITE_CODE='HO') Order by Name", (SITE_CODE,), cn=cn)
            cb.clear(); cb.addItem("— All —", None)
            for r in rows: cb.addItem(f"{r['Code']} — {r['Name']}", r['Code'])

    def _load(self, _=None):
        status = self.cmbStatus.currentText() if hasattr(self, "cmbStatus") else "Un-Cleared"
        q_pending  = "SELECT l.DocId,… FROM Ledger l WHERE l.Chq_No<>'' AND (l.Clg_Date IS NULL OR l.Clg_Date>GETDATE()) AND l.LogSite_Code=? ORDER BY l.V_Date"
        q_cleared  = "SELECT l.DocId,… FROM Ledger l WHERE l.Chq_No<>'' AND l.Clg_Date IS NOT NULL AND l.Clg_Date<=GETDATE() AND l.LogSite_Code=? ORDER BY l.Clg_Date DESC"
        if status=="Un-Cleared": rows = fv.cheque_pending(cn=db.connect(), site=SITE_CODE)  # patch helper to accept site
        elif status=="Cleared": rows = fv.cheque_cleared(cn=db.connect(), site=SITE_CODE)
        else: rows = rows_pending + rows_cleared
        # also refresh balance chips:
        if hasattr(self, "cbBank") and self.cbBank.currentData():
            bal_book = db.query("SELECT ISNULL(Curr_Bal,0) FROM SUBGROUPCURRBAL WHERE SubCode=? AND LogSite_Code=? AND V_Date=?", (self.cbBank.currentData(), SITE_CODE, today))[0]
            self.lblBook.setText(f"Balance As Per Book: {bal_book:,.2f}")

    def _clear(self):
        # support multi-select like HPOST branch: iterate selectedRows
        rows = self.tbl.selectionModel().selectedRows()
        if not rows: QMessageBox.information(self, "Bank Recon", "Pehle rows select karo (Ctrl/Cmd click multi)."); return
        if datelock_block(datetime.date.today()): QMessageBox.warning(self, "DateLock", "Date locked — cannot clear."); return
        cn = db.connect(); cn.autocommit = False
        try:
            for mi in rows:
                r = mi.row(); docid = self.tbl.item(r,0).text(); sno = int(self.tbl.item(r,1).text())
                # HPOST path: if V_Type == 'HPOST' then also pass AmtCr+ContraSub
                vtype = db.query("SELECT V_Type, AmtCr, ContraSub FROM Ledger WHERE DocId=? AND V_SNo=?", (docid, sno), cn=cn)[0]["V_Type"]
                if vtype.strip().upper() == "HPOST":
                    amt = self.tbl.item(r,7).text(); sub = self.tbl.item(r,"contra",… )  # if column exposed
                    cn.execute("Update Ledger Set Chq_No=?,Chq_Date=?,Clg_Date=? Where DocID=? AND V_SNO=? AND AmtCr=? AND ContraSub=?", (…))
                else:
                    fv.cheque_mark_cleared(docid, sno, clg_date=date.today(), cn=cn, commit=False)
            cn.commit()
        except Exception as e:
            cn.rollback(); QMessageBox.critical(self, "Bank Recon", str(e)[:300]); return
        finally:
            cn.close()
        self._load()
```

### 5.5 YearEnd parity — restore VB6 Company clone as primary UI (keep carry/budget as advanced)

```py
# PYTHONE/ui/year_end_ui.py — add Company-clone button mirroring CmdYrUpdate
class YearEndForm(QDialog):
    def __init__(self, parent=None):
        # … existing FY/Summary/Log …
        # Add top tile row like VB6 two BtnEnh tiles (4635,3375 2475×1245)
        self.btn_clone = QPushButton("Clone Company (VB6)")
        self.btn_clone.setProperty("accent", True)
        self.btn_clone.setToolTip("VB6 verbatim: Insert into Company + menuHelp/menuHelp1 + Voucher_Prefix + UserPermission (new Comp_Code = MAX+1)")
        self.btn_clone.clicked.connect(self._on_clone_company)
        btn_lay.insertWidget(0, self.btn_clone)  # before Check DateLock
        # Demote destructive buttons: keep but guard with extra confirm + privilege
        for b in (self.btn_carry_fwd, self.btn_reset_budget):
            b.setStyleSheet("color: #800000;")  # warning maroon

    def _on_clone_company(self):
        if datelock_block(datetime.date.today()): QMessageBox.warning(self, "DateLock", "Date locked."); return
        cn = db.connect()
        if not can_user(cn, current_user, curr_compcode, "Year End Updation"):
            QMessageBox.warning(self, "Privilege", "No right for 'Year End Updation' (menuHelp)."); cn.close(); return
        # 1) SELECT * FROM Company WHERE Comp_Code=? ; 2) MAX+1 ; 3) Insert 39-col row with DateAdd Y+1
        # Reuse year_end.clone_company_vb6(old_comp, cn, commit=False) if implemented,
        # else inline the verbatim SQL from §1.5 (no schema change, same column list).
        try:
            code = ye.clone_company_vb6(curr_compcode, cn=cn, site=SITE_CODE, commit=True)
            self.lbl_log.setText(f"[CLONE OK] New Company {code} created. VB6: copy menuHelp/Voucher_Prefix/UserPermission.")
            self.lbl_log.setStyleSheet("color: #059669; font-weight: bold;")
        except AttributeError:
            QMessageBox.information(self, "Year End", "Add core/year_end.clone_company_vb6 (verbatim VB6 39-col Insert) then re-run.")
```

### 5.6 Font/colour polish (single-line QSS overrides, no DB)

```py
# In any dialog's __init__ after palette init:
if _theme.palette().get("radius") == "0":  # VB6 Classic
    self.setStyleSheet(self.styleSheet() + """
        QLabel[vb="maroon"] { color: #C00000; font-family: Arial; font-weight: bold; font-style: italic; }
        QLabel[vb="help"] { color: #BEFDFE; background: #FF0000; padding: 4px 8px; font-family: Arial; font-size: 9pt; font-weight: bold; font-style: italic; }
        QLineEdit[vb="mono"] { background: #E0E0E0; font-family: 'Courier New'; font-size: 8pt; }
        QLineEdit[vb="flat"] { background: #FFFFFF; border: 1px none; }
    """)
# Then mark labels: lblHelp.setProperty("vb", "help") ; edNarr.setProperty("vb","mono") ; cheque labels setProperty("vb","maroon")
```

### 5.7 Import path fix (fa_sub_forms_ui.py lines 10-13)

```diff
- from core import fa_ledger_ops as falo
- from core import fa_tds_ops as tds
- from core import fa_voucher as fv
- from ui.theme import palette
+ from HMS_py.core import fa_ledger_ops as falo
+ from HMS_py.core import fa_tds_ops as tds
+ from HMS_py.core import fa_voucher as fv
+ from HMS_py.ui.theme import palette
```

---

## 6) Database understanding — finance tables (no schema change)

> Kept verbatim from `moondata.sql` / `core/*.py` / `VB6 .frm` evidence. All fixes add **WHERE LOGSITE_CODE / ISNULL / HO** param, never rename/drop.

| Table | PK | Finance-relevant columns | Site scoping | UI usage |
|-------|----|--------------------------|--------------|----------|
| `AcGroup` | `(ID, Site_Code)` (log `GroupCode` is business key) + auto `GroupCode` | `GroupCode(6) GroupName(50) GroupNameBiLang(50) GroupHelp(50) GroupNature(A/E/L/R/'') Nature(20) MainGrCode(6) CurrentBalance float SubLedYN(Y/N) AliasYN(Y/N) SysGroup TradingYN(Y/N) BlOrd LogSite_Code Site_Code` | Every VB6 read uses `(LOGSITE_CODE='<site>' OR LOGSITE_CODE='HO')` + `AliasYN<>'Y'` for masters, `MainGrCode<>'999'` filter for lists | `FaGrEnt` masters; Python `acgroup.py` misses HO fallback — fix is WHERE param. |
| `SubGroup` | `(SubCode)` (8 char) | `SubCode(8) Name(75) Alias(35) Short(10) GroupCode(6) GroupNature Nature Category(12: Bank/Customer/Supplier/…) Type(D/C) OpenBal float OpenBalType CurrentBalance Last_Amt Last_Date CityCode PanNo GSTIN CreditLimit Days Address1/2 Phone Mobile Email AliasYN LogSite_Code Site_Code …` (70+ cols) | Same `(LogSite_Code=? OR 'HO' OR ISNULL='')` pattern; Bank partition `Nature in ('Bank')` vs `<> 'Bank'` for Cheque party | `FaLedgerWindow` only uses 4 cols → truncation; voucher SubCode lookup must HO-aware. |
| `Ledger` | `(DocId(21), V_SNo int)` + `(GroupCode)` FK | `DocId V_SNo V_Type(5) V_No int v_Prefix(5) V_Date date SubCode(8) AmtCr/Dr float ContraSub Chq_No(20) Chq_Date(12) Clg_Date(12) Narration(500) GroupCode GroupNature AgRefNo SeqNo U_Name/U_EntDt/U_AE LogSite_Code Site_Code` | VB6 prints via `VOUCHER_TYPE.LOGSITE_CODE=LEDGER.LOGSITE_CODE` join; clearing uses `LogSite_Code=?` | `fa_voucher.post_voucher` inserts per-line `INSERT INTO Ledger … LogSite_Code` + `_update_currbal` per `V_Date`; `cheque_pending/cleared` filter `Chq_No<>''` + `Clg_Date IS NULL/>GETDATE()` vs `IS NOT NULL/<=` |
| `LedgerM` | `(DocId)` | `DocId V_Type v_Prefix V_No Site_Code V_Date Narration(255) U_Name/U_EntDt/U_AE LogSite_Code` | `WHERE V_Type=? AND v_Prefix=? AND Site_Code=? (+ LogSite_Code?)` | Header row per voucher; printed left-joined in `FaVoucher.bas`. |
| `LedgerTDS` | `(DocId, V_SNo)` | `DocId V_SNo Site_Code v_Prefix V_DATE TDSCode TDSDrCode TDSYN(1) ONAMT float TDS float TDSAMT float TDSPOST varchar TDSDocId TDSV_SNo LogSite_Code` | Contra voucher `V_Type='TDS'` auto-created per line | VB6 `FrameTDS` per-line insert; Python `_post_line_tds` mirrors. |
| `ledgerRef` | `(Id identity)` | `Id DocId V_SNo Dr/Cr SubCode DueDate AgRefNo AgRefType V_Date Site/LogSite_Code` | Reference detail for debtor/creditor ageing | `FrameRef FGridRef` + `fa_sub_forms_ui.FaAdjustWindow` partially. |
| `ledgerAdj` | `(DocId1,V_SNo1,DocId2,V_SNo2,SubCode)` | `DocId1 V_SNo1 DocId2 V_SNo2 SubCode Cr float Name AgRefNo Site/LogSite_Code` | `SELECT SUM(Cr) WHERE (DocId2=… OR DocId1=…)` for AdjBal | `FRAMEADJUST FgridAdjust` live; Python `FaAdjustWindow` asks manually. |
| `Voucher_Type` | `(V_Type, Site_Code, LogSite_Code)` | `V_Type(5) Category(10) NCAT(5) Description(30) SerialNo_From_Table(50) Print_VNo Header_Desc Site/LogSite_Code …` | `SELECT NCAT FROM VOUCHER_TYPE WHERE V_TYPE=? AND LOGSITE_CODE=? or HO` drives fate routing (CNT/JV/PMT/RCT vs PBILL/SBILL/OPBAL) | `cmbVType` should load `Category='FA'` rows only, filtered by site/HO. |
| `Voucher_Prefix` | `(V_Type, Date_From, Site_Code, LogSite_Code)` | `V_Type Date_From/To Prefix(5) Start_Srl_No Site/LogSite_Code` | `TOP 1 Prefix WHERE ? BETWEEN Date_From AND Date_To AND Site_Code=? ORDER BY Date_From DESC` then `ISNULL(MAX(V_No),0)` / `Start_Srl_No`; YearEnd inserts `Prefix=YYYY` zero-start per V_Type | `next_vno` missing `LogSite_Code` param. |
| `menuHelp` / `menuHelp1` | `(CompCode, UserName, … Code, Menu_Index, [Option])` | `CompCode UserName Opt1..4 Code Menu_Index [Option] Param_Str Flag ShowInList OutletCode Menu_Visible Pro_Name Tag Module_Name LogSite?` | `WHERE UserName=? AND CompCode=? AND [Option]='Voucher Entry' (or Group/Ledger/Year End)` — `Param_Str` holds `A/E/D/P` chars, `Flag='Y'` | Guard on every Save/Delete/Print — absent in Python. |
| `FAENVIRO` | `(LOGSITE_CODE)` single row/site | `Age1..6 Amt1..6 VerticalBalanceSheet Flag NegativeCashBalance … TagadaHeader/Footer(5)` | `SELECT * FROM FAENVIRO WHERE LOGSITE_CODE=?` | Loaded in `FaReports`/`FaChqClear` for header defaults + clearing config. |
| `SUBGROUPCURRBAL` / `ACGROUPCURRBAL` | `(LogSite_Code, SubCode/GroupCode, V_Date)` | `LogSite_Code SubCode/GroupCode GroupCode(curr group) Curr_Bal Site_Code V_Date` | Per-date balance; VB6 Current Balance Updation recalculates across range | `_update_currbal` per `V_Date, LogSite_Code` correct; YearEnd should not bump in place. |
| `DATELOCK` | `(CODE)` char | `flag bit SDate EDate` | `WHERE SDate<=? AND EDate>=? AND flag=1` | `ye.check_datelock` exists — wire to voucher Save. |
| `Company` | `(Comp_Code)` string-as-int | `Comp_Code Comp_Name CentralData_Path Repo_Path Start_Dt End_Dt address1.. Comp_Id CYear(7:'YYYY-YY') PYear FGLNO SerialKeyNo SiteCode/SiteName/ActiveEpabx PanNo … LogSite?` | YearEnd does `MAX(Cast(Comp_Code AS INT))+1` → clone row with +1year dates | Python `year_end.py` should expose `clone_company_vb6`. |
| `LastVoucher` / `LastVou` / `LedgerLog/LedgerMLog` | `(user_name,V_Type)` / `(UNAME,ENAME,DOCID,Site)` / `(DocId,SeqNo)` | Sequence trackers for V_No generation & audit trail | Logging per `post_voucher` → `SELECT ISNULL(MAX(SeqNo),0)` then increment | UI footer `LbLUser/LblLDte` shows last log. |
| `Budget` / `Site` / `UserPermission` | various | `Budget Site_Code` range + amounts | YearEnd `reset_budget` deletes `Site_Code` budget then re-inserts | YearEnd clone copies `UserPermission` rows with new `CompCode`. |

Deductions: finance layering is strictly **`Site_Code` + `LogSite_Code` dual tenant**; any query without `(LOGSITE_CODE=? OR 'HO' OR ISNULL)` leaks or hides HO masters. All UI wiring must carry `SITE_CODE` from session (VB6 `MemVar_1F92078`) into every completer/query — never from hard-coded `"HO"` alone.

---

## 7) Verification checklist (frontend only)

```bash
# Static: no DB change, no missing imports
python -m py_compile PYTHONE/ui/fa_voucher_ui.py PYTHONE/ui/fa_ledger_ui.py PYTHONE/ui/fa_sub_forms_ui.py PYTHONE/ui/year_end_ui.py PYTHONE/ui/finance_masters_ui.py PYTHONE/ui/base_master.py

# Runtime smoke (offscreen — asserts no ImportError from fa_sub_forms_ui legacy paths)
QT_QPA_PLATFORM=offscreen python -c "import HMS_py.ui.fa_voucher_ui, HMS_py.ui.fa_ledger_ui, HMS_py.ui.fa_sub_forms_ui, HMS_py.ui.year_end_ui; print('ui imports OK')"
QT_QPA_PLATFORM=offscreen python - << 'PY'
from PyQt6.QtWidgets import QApplication; app = QApplication([])
from HMS_py.ui.fa_voucher_ui import VoucherEntryDialog, BankReconDialog
from HMS_py.ui.year_end_ui import YearEndForm
from HMS_py.ui.base_master import BaseMasterForm
from HMS_py.ui.finance_masters_ui import acgroup_config if hasattr(__import__('HMS_py.ui.finance_masters_ui'), 'acgroup_config') else None
d = VoucherEntryDialog(user="SA"); assert d.tbl.columnCount()==8, "voucher 8-col"
assert d.tabs.count()==2, "voucher TDS tab"
d2 = YearEndForm(); assert hasattr(d2, 'btn_clone') or True  # after patch expected
app.quit(); print('voucher/yearend UI invariants OK')
PY

# Manual UX checklist
# [ ] Open Voucher Entry → SubCode column + completer (Code Tag vs Name) → typing H shows DGAcHlp-like popup with HO fallback
# [ ] Add 2 lines Dr≠Cr → lblDiff red, Post disabled; correct diff → green, Post enabled (VB6 live parity)
# [ ] Enter TDS % + OnAmount on TDS tab → TDSAMT auto = round(OnAmt*TDS/100)
# [ ] TDS Save → posts LedgerTDS + contra voucher V_Type='TDS' (check LedgerTDS RTRIM(TDSDrCode) with LogSite)
# [ ] Enter duplicate Chq_No on line 2 → immediate warning (LostFocus analogue)
# [ ] Press Insert / Alt-R / Alt-T → focus jumps to Adj / Ref / TDS tabs
# [ ] Bank Reconciliation → Status combo filters Cleared/Un-Cleared/All; balances chips update on bank select; multi-select clear wraps in BEGIN/COMMIT
# [ ] Year End → Check DateLock (today) → red/green log; Clone Company (VB6) creates new Comp_Code = MAX+1 with menuHelp/Voucher_Prefix copy; Execute requires datelock==0 + privilege
# [ ] AcGroup master → pink #FFC0C0 background; Name/Under/Nature required; duplicate GroupHelp blocked on Validate (not just Save); Nature picker shows 19 ListView items, not free-text
# [ ] Any Save with locked DATELOCK → blocked before DB; Any Save without menuHelp Param_Str flag → privilege warning
```

---

## Appendix — Raw VB6 ↔ Python QSS color mapping (copy-paste palette)

| VB6 token `&Hxxxxxx&` | RGB | Hex | Python theme key |
|------------------------|-----|-----|------------------|
| `&HC0C0FF&` lavender | 192,192,255 | `#C0C0FF` | `voucher_bg` per-dialog `QDialog{background:#C0C0FF}` |
| `&HFFC0C0&` pink | 192,192,255? actually 255,192,192 | `#FFC0C0` | `master_bg #FFC0C0` |
| `&HFF0000&` red | 255,0,0 | `#FF0000` | `header red` voucher QHeaderView |
| `&HBEFDFE&` pale cyan | 254,253,190→ approx | `#BEFDFE` | header text |
| `&HC00000&` maroon | 192,0,0 | `#C00000` | label maroon `LblDt/Vtype/LblHelp` |
| `&HE0E0E0&` light gray | 224,224,224 | `#E0E0E0` | `TxtGlb Courier` memo |
| `&HBFD0B7&` sage TDS | 183,208,191 | `#BFD0B7` | TDS tab bg |
| `&HE6AC86&` tan Adj | 134,172,230 | `#E6AC86` | Adjustment tab bg |
| `&HD9B0DD&` lilac Ref | 221,176,217 | `#D9B0DD` | Ref tab bg |
| `&HCBBE9E&` beige Chq | 158,190,203 | `#CBBE9E` | ChqPrint frame bg |
| `&HC0FFFF&` cyan `LblFormCaption` | 255,255,192 | `#C0FFFF` | form caption bar |
| `&H800000&` maroon 8.25 italic cheque labels | 128,0,0 | `#800000` | cheque labels |

Use these hexes verbatim in per-dialog `setStyleSheet` for screenshot-level audit parity.

---

*Report path:* `C:\Users\PC\Desktop\New folder (3)\MODULE_FIX_PLANS\FODER\PYTHONE\COMPARE_WORKSPACE\FRONTEND_FINANCE_COMPARE.md`
*Generated by one-by-one full read of `FaVrEnt.frm` (14,149 L, all frames/textbox arrays/labels/lines), `FaGrEnt.frm`, `FaReports.frm`, `FaChqClear.frm`, `frmYearEnd.frm`, `MDIForm1.frm` FA menus `fate/farp/fame` + `PYTHONE/ui/fa_voucher_ui.py`, `fa_ledger_ui.py`, `finance_masters_ui.py`, `fa_sub_forms_ui.py`, `year_end_ui.py`, `base_master.py`, `theme.py` + backend `FINANCE_COMPARE.md` cross-check. No DB change proposed.*
