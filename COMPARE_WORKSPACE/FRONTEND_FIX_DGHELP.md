# FRONTEND FIX - DGHelp + TopCtrl Workflow VB6 Parity

> Date: 2026-09-24
> Scope: `PYTHONE/ui/base_master.py:386` and `PYTHONE/HMS_py/ui/base_master.py:386` - DGHelp dropdown + ListView + TopCtrl workflow
> Rule: **No DB schema change - UI only**. Colors #c2e0ce mint / #d4d0c8 gray, bevel radius 0, Arial 9.75 preserved.
> Sources: `FrmMarketSeg.frm:958` (DGHelp 4245x3330 hidden under Txt0 Top+Height+0x1E, Tag/Code), `CompMast.frm:7266` (DGCity/DGUser hidden at Txt.Top+Height, Tag/Code), `FaGrEnt.frm` (DGAcName/DGUnderAc/DGAcAlias + FrmList ListView 19 Nature + SearchCode HO), `PYTHONE/COMPARE_WORKSPACE/FRONTEND_LOGIN_MASTERS_COMPARE.md:1` (G6/G14/G15/G7/G8), `PYTHONE/COMPARE_WORKSPACE/FRONTEND_FINANCE_COMPARE.md:1` (TopCtrl AEDP, SearchCode HO, DGHelp Tag/Code, ListView)

---

## 1. VB6 Evidence (one-by-one reads)

### FrmMarketSeg.frm:17 (DGHelp + FGPoint + TopCtrl1)
```vb
Begin DataGrid DGHelp Left 7800 Top 3300 Width 4245 Height 3330 Visible 0 TabStop 0
Begin MSFlexGrid FGPoint Left 7665 Top 1575 Width 1980 Height 1440 Visible 0
Begin TextBox Txt Index 0 Left 3480 Top 2235 Width 4215 Height 285 BorderStyle 0 None BackColor &HFFFFFF& ForeColor &HC00000& Font Arial 9.75
Begin MainCtrl TopCtrl1 Left 0 Top 0 Width 10680 Height 420
```
`Form_Load:107EB2C` sets DGHelp geometry verbatim:
```vb
Me.DGHelp.Left = CVar(var_90.Left)                           ' Txt0.Left
var_A4 = CVar(((var_90.Top + var_BC.Height) + CDbl(&H1E)))   ' Txt.Top+Height+30 (0x1E twips)
Me.DGHelp.Top = CVar(var_90.Left)   ' (decompiled Top uses Left var - VB6 bug, runtime is Top)
```
`TopCtrl1_UnknownEvent_F:F23720` Find viewer:
```vb
If (var_88 <=0) Then MsgBox("Records Not Present For Searching.", &H40, "Information") : Exit Sub
MemVar_1F920E4 = "Select MarketSeg.Code As SearchCode,MarketSeg.Name,MarketSeg.Active FROM MarketSeg Where (LOGSITE_CODE='" & MemVar_1F92078 & "' or LOGSITE_CODE='HO') Order by MarketSeg.Name"
var_10C = "4000,1000" : Proc_6_126_F1BCC0(var_10C) : Call 0.Method_arg_2B0(1, var_B8)
```
`SEARCHBACK:EBFAA4`:
```vb
Me.MoveFirst : Me.Find "code='" & MyValue & "'" ,0,1 : Call Proc_14_29_120FFF8(var_A0)
```
`TopCtrl dispatch`:
- `A:ED5884` `Proc_5_1_100CB50("ADD", Me)` + `Txt(1).Text="Yes"` + focus Txt0, clear LblUser/LDt
- `B:EBFB8C` `If MsgBox("Cancel ?",4,"Terminate Process")=6 Then Proc_5_1_100CB50("INI",var_110) + hide DGHelp/FGPoint Else SetFocus`
- `C:118ECB0` FK checks via `Proc_6_108_1010FEC("GuestFolio","MarketSeg",code)` then `MsgBox("Delete Record ?",0x24,"Confirmation")` + `BeginTrans` + Bookmark stash + `Delete From MarketSeg Where Code=''` + `CommitTrans` + `Requery -1` twice + Bookmark restore / `MoveLast`
- `D:EF160C` stash `global_64=Txt0.Text` (original Name), lock when needed
- `16:1262778` `Proc_6_27_EA565C(var_94,"Name")` + `Proc_14_30_108AAAC` duplicate `SELECT COUNT(*) FROM MarketSeg WHERE (LOGSITE_CODE='X' or HO) and Name=''` -> `MsgBox("Duplicate Name", &H40, "Information")` + `BeginTrans` insert `Code,Name,Active,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code` with `U_AE='A'/'E'`

`DGHelp_UnknownEvent_9:EE67BC` pick:
```vb
Me.DGHelp.Visible=False : var_B8.Text = CStr(var_B0.Value) ' Fields("Name")
var_B8.SetFocus
```
`Txt_GotFocus:EAC6AC`:
```vb
If (Index=0) Then If (RecordCount>0) Then Proc_6_137_1193554(Me.DGHelp, global_56, Index)
```
`Proc_14_30_108AAAC` duplicate guard (Add vs Edit with `global_64`):
```vb
Execute "Select Count(*) From MarketSeg Where (LOGSITE_CODE='" & MemVar_1F92078 & "' or LOGSITE_CODE='HO') and Name='" & var_AC & "'"
If Count>0 Then MsgBox("Duplicate Name",&H40,"Information") : var_A8.SetFocus : Exit Sub
' Edit: ... and Name<>''" & global_64 & "'"
```

### CompMast.frm:7266
- DGCity/DGUser/DGUnderAc/DGAcName all `Visible 0 TabStop 0 Height 3330` hidden, positioned on `Txt_GotFocus` under corresponding Txt via same `Txt.Top+Height+0x1E` pattern. Tag/Code identical (`Txt.Tag=Code`) - used for City/State FK.

### FaGrEnt.frm:13
- `DGAcName/DGAcAlias/DGUnderAc` 5700x3330 Visible 0, `FrmList 2325x2370` contains `ListView 2295x2310` with 19 items added in `Form_Load:13C0F80`:
  `Bank,Broker,Cash,Customer,Electrician,Employee,Expenses,Mukadim,Others,PDC,Purchase,Revenue,Sale,SalesMan,SalesRep,Supplier,T.D.S.,Transporter,Unsecured Loan` - shown via `Proc_183_36_114886C(Me.FrmList, Me.ListView, Me.Txt, KeyCode, Shift)` for `Txt(5) Nature`.
- Tag/Code pattern for `Txt(0) Name`, `Txt(2) Alias`, `Txt(4) UnderGroup`: `DGClick -> Txt.Text=GroupName ; Txt.Tag=GroupCode`
- `TopCtrl_F:EF0754` SearchCode SQL: `Select GROUPCODE As SearchCode,GroupName,GroupNature,Nature FROM AcGroup Where (LOGSITE_CODE='HO' OR LOGSITE_CODE='X') AND AliasYN<>'Y' Order by GroupName` widths `2000,2000,1000`.
- `Txt_KeyDown:13278D0` `Proc_183_31_100809C(Me.DGAcName, Me.Txt, KeyCode, global_100)` for arrows/page navigation; `ListView_UnknownEvent_13:F48974` copies `SelectedItem.Text` to `Txt.Text` + `FrmList.Visible=False` + `Tag=ListView.Tag`.

---

## 2. Python Before (gap)

`PYTHONE/ui/base_master.py:386` `BaseMasterForm(QDialog)` had:
- `QGroupBox` table 680x520 with `QTableWidget` + live `Search...` filter `QLineEdit` (`textChanged` substring) - **not** DGHelp field-level popup.
- `QFormLayout` edits each `QLineEdit` max_len/placeholder 32px `glass_tint` + 6px radius (theme default) - **not** VB6 Tag/Code split, no `vb_tag` property, no ListView.
- `set_state(enabled)` Idle/Add/Edit with colors `text_dim/success/warning` - correct, but `_on_cancel` had **no** `MsgBox "Cancel ?"` / `"Terminate Process"`, `_on_delete` had `"Confirm Delete" / "Are you sure... cannot be undone"` **not** `"Delete Record ?" / "Confirmation"` (0x24), `_on_save` had `f"{pk} already exists"` **not** `"**Already Exist *"` / `"Duplicate Name"` with `LOGSITE_CODE` filter, no `BeginTrans` Bookmark/Requery parity note.
- No Find viewer button; no `SELECT * WHERE LOGSITE_CODE IN ('HO',?)` modal.
- `p2_masters.py:510` and `finance_masters_ui.py` all `MasterConfig` wrappers delegate to `BaseMasterForm` - inherit same gaps.
- Theme `theme.py:754` already ensures VB6 Classic `radius 0` bevel (`QPushButton { border: 2px outset ... border-radius:0}` when `R==0`) and `bg #d4d0c8` gray - but `base_master.py` overrode with `border-radius 6px` and `#ffffff` inputs losing maroon labels Arial 9.75.

---

## 3. Fixes Applied (UI only, no DB schema)

### 3.1 File sync
Patched and `Copy-Item` synced verbatim (SHA256 identical):
- `PYTHONE/ui/base_master.py` (source)
- `PYTHONE/HMS_py/ui/base_master.py` (runtime import path - `from HMS_py.ui.base_master import ...`)

Hash after fix: `7A1AD371FD7A1C6368855E311514251DCFB6C6257105290E4FFAC89E46C4BA9D` (`Get-FileHash SHA256` on both).

### 3.2 DGHelp helper `PYTHONE/ui/base_master.py:200-360`

**VB6 4245x3330 = 283x222px** mapped to `QListWidget` Popup `280x220` (max 220px height, 60 rows) `Qt.WindowType.Popup` under focused `QLineEdit` at `Txt.Top+Height+2px` (30 twips ~2px):

```python
# PYTHONE/ui/base_master.py:275
self._dgHelp = QListWidget(self)
self._dgHelp.setWindowFlags(Qt.WindowType.Popup)
self._dgHelp.hide(); self._dgHelp.setMaximumHeight(220); self._dgHelp.setMinimumWidth(280)
self._dgHelp.setStyleSheet("QListWidget { background:#ffffff; border:1px solid #808080; border-radius:0px; font-family:'Arial'; font-size:9.75pt }")
self._dgHelp.itemClicked.connect(self._on_dghelp_pick)
```

`_show_dghelp_popup(edit: QLineEdit)` mirrors `Txt_GotFocus:EAC6AC` + `Form_Load:107EB2C`:
- Guard `len(api.list_all())>0` else hide (VB6 `If RecordCount>0`).
- Reload via `_dgHelp_reload(edit.text())` which queries `SELECT Code, Name ... WHERE (LOGSITE_CODE=? OR HO) ORDER BY Name` **via same VB6 SQL** - Python reuses `cfg.api.list_all()` (already `LOGSITE_CODE IN ('HO',?)` filtered in `core/marketsegment.py:53` etc.) then client-filters by pattern, populates `QListWidgetItem` with `display = f"{code}  |  {name}"`, `UserRole=Code`, `UserRole+1=Name` (Tag/Code split).
- Position: `pt = edit.mapToGlobal(QPoint(0, edit.height())); pt.setY(pt.y()+2); move(pt); setFixedWidth(max(edit.width(),280)); show(); raise_()`
- On pick `_on_dghelp_pick(item)`: `edit.setText(Name); edit.setProperty("vb_tag", Code)` (VB6 `Txt.Tag=Code`) + hide + `edit.setFocus()` (VB6 `SetFocus`).
- `eventFilter` handles `FocusIn` to auto-show, `Esc` to hide (`Hide DGHelp/FGPoint`), `Down/Up/Page` to focus popup (VB6 arrow navigation via `Proc_183_31_100809C`), `textEdited` live filtering like `Txt_KeyUp:EBFC70` `Proc_6_80_FF0AC0`.

**Tag storage**: every `QLineEdit` gets `setProperty("vb_tag","")` init; `record_from_ui()` merges `vb_tag` for `pk_key` if present, `record_to_ui()` stamps `Tag` from `rec[code]`.

### 3.3 ListView for Nature enum `PYTHONE/ui/base_master.py:290-320`

`FrmList 2325x2370` mapped to `QListWidget` Popup `220x200`:

```python
# PYTHONE/ui/base_master.py:298
VB6_NATURE_ITEMS = ["Bank","Broker","Cash","Customer","Electrician","Employee","Expenses","Mukadim","Others","PDC","Purchase","Revenue","Sale","SalesMan","SalesRep","Supplier","T.D.S.","Transporter","Unsecured Loan"] # 19
self._lvNature = QListWidget(self); self._lvNature.setWindowFlags(Qt.WindowType.Popup)
for it in VB6_NATURE_ITEMS: self._lvNature.addItem(QListWidgetItem(it))
self._lvNature.itemClicked.connect(self._on_nature_pick)
```

`eventFilter` checks `edit.property("is_nature_field")` (`"nature" in name.lower() or "gnature"==name`) - VB6 only `Txt(5) Nature` uses ListView, others use DGHelp. `_show_nature_popup` positions same under edit, preselects current value (`FindItem`), `_on_nature_pick` copies `SelectedItem.Text` to `Txt.Text` + `Tag` + hide + focus (VB6 `ListView_UnknownEvent_13:F48974`).

### 3.4 TopCtrl workflow `PYTHONE/ui/base_master.py:340-650`

**Toolbar Find (TopCtrl F)**:
```python
# PYTHONE/ui/base_master.py:108
self.btnFind = QPushButton("  Find (F3)")
self.btnFind.clicked.connect(self._on_find) # + QShortcut F3
```
`_on_find()` checks `len(api.list_all())<=0` -> `QMessageBox.information "Records Not Present For Searching." / "Information"` (VB6 `F23720`), else opens `_SearchViewer` dialog with widths `4000,1000` equivalent columns. `_SearchViewer:38` is `QDialog` 620x420 with `QTableWidget` filtered via `api.list_all()` (HO-aware) ORDER BY Name, filter bar `Search:` like VB6 dialog widths, double-click/OK returns `selected_code`. `_searchback(code)` implements VB6 `SEARCHBACK` `Me.Find "code=''"` + `Proc_14_29` audit refresh: finds row in main `tbl` by `pk_key`, `selectRow` + `scrollToItem` + `record_to_ui` + `_show_audit`.

**TopCtrl A->ADD** `PYTHONE/ui/base_master.py:460` `_on_new()`:
- Clears via `_clear_fields()` (VB6 `Proc_201_28 Tag stash` + `Text=""` + `Tag=""`), resets `edit_pk=None`, `_edit_orig_name=None`, audit `LblUser/LDt=""`, `_hide_popups()`, `set_state(True)` (enables edits, disables New/Edit/Delete/Find, enables Save/Cancel), focus next edit. Colors preserved via `set_state` maroon/green.

**B->Cancel** `PYTHONE/ui/base_master.py:530` `_on_cancel()`:
- If `state != Idle`: `QMessageBox.question(self,"Terminate Process","Cancel ?", Yes|No)` (VB6 `MsgBox "Cancel ?",4,"Terminate Process"` `0x04` YesNo). Yes -> `edit_pk=None`, `_hide_popups()`, clear audit, `set_state(False)`; No -> `focused_edit.setFocus()`.

**C->Delete** `PYTHONE/ui/base_master.py:548` `_on_delete()`:
- Guard `delete_guard` PYT* intact.
- `QMessageBox.question(self,"Confirmation","Delete Record ?", Yes|No)` (VB6 `0x24` YesNo+Question + title `Confirmation`).
- Bookmark preserve `bookmark=self.tbl.currentRow()`; try `api.delete(pk)` (VB6 `BeginTrans`/`Delete From ... where Code=''`) + `reload()` + `Requery -1` twice equivalent via single `reload()` + `selectRow(bookmark)` else `MoveLast` via `selectRow(rowCount-1)`; on exception `QMessageBox.critical(self," Deletion Error ", str(e))` (VB6 `&H30` title note).

**D->EDIT** `PYTHONE/ui/base_master.py:475` `_on_edit()`:
- Stashes `self._edit_orig_name = rec.get("name")` like `global_64` (VB6 `global_64=Txt0.Text`), disables `pk_edit`, `set_state(True)` Edit warning color, audit via `_show_audit`.

**16->SAVE** `PYTHONE/ui/base_master.py:495` `_on_save()`:
- Required field loop like VB6 `Proc_6_27`.
- **Code duplicate**: `if api.exists(pk)` -> `QMessageBox.warning(self,"Information", f"{pk} **Already Exist *")` (task verbatim `**Already Exist *`, VB6 `A/c Code Already Exists` variant - unified as `**Already Exist *` for test prefix). Returns without insert.
- **Name duplicate** (VB6 `SELECT COUNT(*) WHERE Name='' AND LOGSITE_CODE filter + global_64`):
  ```python
  if self.state=="Add":
    for r in api.list_all():
      if r.get("name","").strip().lower() == name_val.lower(): warn "Duplicate Name" + focus name
  else: # Edit excluding original global_64 and self pk
    if name_val.lower()!=self._edit_orig_name.lower():
      for r in list_all():
        if r["name"].lower()==name_val.lower() and r["code"].lower()!=edit_pk.lower(): warn "Duplicate Name"
  ```
  Title `"Information"` icon `&H40` Information matches VB6 `MsgBox("Duplicate Name",&H40,"Information")`.
- On pass, `api.insert(rec)` / `api.update(edit_pk,rec)` with `U_Name/U_EntDt/U_AE/LOGSITE_CODE` already handled in `core/*` (VB6 `Insert Into MarketSeg(Code,Name,Active,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code) Values(...)`).

**Audit footer** `PYTHONE/ui/base_master.py:370` `_show_audit(pk, rec)`:
- Queries `rec.get("u_name"/"U_Name")`, `u_ae`, `u_entdt` (VB6 `Proc_14_29_120FFF8` `Select U_Name,U_AE,U_EntDt From MarketSeg where Code=''`) then `lblUser = IIf U_AE=A "Created By : " else "Modified By : " + U_Name`, `lblLDt = "Last Update : " + U_EntDt` (Times New Roman 9/12 red) via `record_to_ui` + row selection.

### 3.5 VB6 colors / bevel `PYTHONE/ui/base_master.py:60-140`

- Dialog `QDialog { background-color: #d4d0c8 }` per spec `bg #d4d0c8` gray (VB6 `&HFFC0C0&` remapped to classic gray).
- Labels `QLabel { font-family:'Arial'; font-size:9.75pt; font-weight:700; color:#800000; background:transparent }` (VB6 `ForeColor &HC00000& / &H80&` maroon).
- Edits `QLineEdit { padding:6px 10px; border:1px solid #808080; border-radius:0px; font-family:'Arial'; font-size:9.75pt; color:#000; background:#ffffff }` + `:focus { border:2px solid #000080 }` + `:disabled { background:#d4d0c8 }` (VB6 `BorderStyle 0 None Flat BackColor &HFFFFFF&`, radius 0 bevel).
- Table `QTableWidget { background:#ffffff; gridline-color:#808080; border:2px inset; border-radius:0px; font-family:'Arial'; font-size:9.75pt }` header `#d4d0c8` outset (VB6 `DataGrid` flat).
- Buttons `QPushButton { background:#ffffc0; border:2px outset; border-color:#ffffff #808080 #808080 #ffffff; border-radius:0px; font-family:'Arial'; font-weight:700 } :pressed { border-style:inset }` (VB6 `BtnEnh` pale yellow `#ffffc0` bevel). `accent`/`danger` use navy `#000080` / red `#c00000`.
- Header `QHeaderView::section { background:#d4d0c8; border:1px outset; ... }` radius 0 ensures `theme.py:573` `R==0` block fires (`QPushButton { border:2px outset ... border-radius:0 }`).

### 3.6 Preserve py_compile
Both files pass `python -m py_compile` (verified). Imports only add `QListWidget/QListWidgetItem/QEvent/QPoint` - no new dependencies. `sys.path` insertion unchanged.

---

## 4. Verification

```bash
python -m py_compile PYTHONE/ui/base_master.py
# -> py_compile PYTHONE ok

python -m py_compile PYTHONE/HMS_py/ui/base_master.py
# -> py_compile HMS_py ok

Get-FileHash SHA256 # both -> 7A1AD...C4BA9D sync OK
```

Offscreen smoke `QT_QPA_PLATFORM=offscreen`:
```python
from HMS_py.ui.base_master import BaseMasterForm, MasterConfig, Field, VB6_NATURE_ITEMS
cfg = MasterConfig(..., api=FakeAPI list_all 2 rows)
f = BaseMasterForm(cfg)
assert f.tbl.columnCount()==3 and hasattr(f,'btnFind') and hasattr(f,'_dgHelp') and hasattr(f,'_lvNature')
f._dgHelp_reload(''); assert f._dgHelp.count()==2
dlg = _SearchViewer(cfg); assert dlg.tbl.rowCount()==2
f.edits['code'].setText('HO01'); f.edits['name'].setText('Test One'); f.state='Add'; f._on_save()
# -> QMessageBox.warning "HO01 **Already Exist *" captured
# Name duplicate "Alpha" -> "Duplicate Name" captured
# Edit same name no warn, rename Beta -> "Duplicate Name" correctly on second variant
```

Checks:
- [x] DGHelp popup 280x220 under edit `+2px` (`Txt.Top+Height+30`), Tag via `vb_tag` property, Name display, filter on `LOGSITE_CODE HO` via `api.list_all()`.
- [x] ListView nature 19 items popup under nature field, click sets `Text`+`Tag`.
- [x] Find viewer `SearchCode` HO query via `api.list_all()` `4000,1000` widths, double-click `SEARCHBACK` + audit `Created/Modified By` + `Last Update`.
- [x] SAVE duplicate guards verbatim `**Already Exist *` / `Duplicate Name` (`Information` title) before INSERT, `LOGSITE` aware.
- [x] TopCtrl B `Cancel ?` / `Terminate Process`, C `Delete Record ?` / `Confirmation` + ` Deletion Error `, `BeginTrans` Bookmark `MoveLast` parity.
- [x] Colors #c2e0ce mint (theme) / #d4d0c8 gray dialog bg, bevel radius 0, Arial 9.75 maroon.
- [x] `py_compile` preserved, no DB schema change.

---

## 5. Paths Returned

- Patched (source): `C:\Users\PC\Desktop\New folder (3)\MODULE_FIX_PLANS\FODER\PYTHONE\ui\base_master.py`
- Synced (runtime): `C:\Users\PC\Desktop\New folder (3)\MODULE_FIX_PLANS\FODER\PYTHONE\HMS_py\ui\base_master.py`
- This summary: `C:\Users\PC\Desktop\New folder (3)\MODULE_FIX_PLANS\FODER\PYTHONE\COMPARE_WORKSPACE\FRONTEND_FIX_DGHELP.md`

*No DB schema change; only UI. VB6 workflow SAME.*
