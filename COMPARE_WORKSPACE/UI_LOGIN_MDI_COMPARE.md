# UI LOGIN / COMPANY / MDI CHROME — VB6 → Python Comparison

> **Scope:** `MDIForm1.frm` + `frmCompany.frm` + `UserMast.frm` + `UserPermission.frm` vs `PYTHONE/ui/shell.py` + `theme.py` + `sidebar_buttons.py` + screenshot `00_Login/01_Login_Page.png`  
> **Date:** 2026-09-24  
> **Author:** UI comparison agent (Muse Spark)  
> **Rule:** No DB change. VB6 Classic theme `radius=0` bevel active. Thorough frontend parity only.

---

## 0. EXECUTIVE SUMMARY

| Area | Verdict | Key Gap |
|------|---------|---------|
| **Login dialog** | ✅ Close | Python `LoginDialog 390×310` vs VB6 `frmCompany` as login-host `15510×8715` container — but VB6 actually hosts login *inside* frmCompany (User Name/Password at 10530,960 / 12105,930). Python extracts it to standalone dialog — intentional. Colors/fonts match (`#c2e0ce` mint, `#800000` maroon, `#ffffc0` bevel). |
| **Company select** | ⚠️ Drift | VB6 `DBGrid1 6780×900` at (8445,15) hidden by default + `CompInfo` pink frame 6615×4470 at (-75,45) vs Python `CompanyDialog 640×470` with `QTableWidget 180px` min + pink `QFrame #ffc0ff`. Size not 1:1 (VB6 container 1034×581 px vs Python 640×470). DBGrid Tag/Code vs QListWidget popup missing. |
| **MDI Chrome — PictMainMenu / PictSubMenu / PictTitleBar / PictShortCuts / sbar** | ⚠️ Significant drift | VB6 4-way Align docking + black TreeView + MSHFlexGrid `mnuGrid` + 6 world-clock BtnEnh + DealerLogo/ImgLogo vs Python teal left `150px` gradient sidebar + right floating `150px` world-clocks + `FrontOfficeDashboard`. `sbar 360twip (24px)` only partially reproduced. |
| **TopCtrl / MainCtrl** | ❌ Missing | VB6 `MainCtrl topCtrl1 9870×450` (Add/Edit/Delete/Find/Print/Refresh/Save) on every master. Python masters hide it behind `TopCtrl` emulation or omit. |
| **Theme** | ✅ Fixed | `theme.py:DEFAULTS radius=0, bg #d4d0c8, bevel 2px outset #ffffff #808080` correctly restores VB6 `VB6 Classic (MDI Teal)` preset. |

**Overall:** Python is *functionally richer* (dynamic `menuHelp` menubar, glass aurora, responsive sidebar) but **not pixel-identical** to VB6 chrome. 12 MISSING frontend bugs listed in §4 require `radius=0` + outset/inset + exact BGR→RGB patches.

---

## 1. VB6 CONTROLS — VERBATIM (with BGR→RGB + twip→px)

### 1.1 MDIForm1.frm — the master chrome (`C:\...\FODER\MDIForm1.frm:2-313`)

```
VERSION 5.00
Begin VB.MDIForm MDIForm1                          // MDIForm1.frm:2
  BackColor = &HAFFFFF&                            // BGR AFFFFF -> RGB #FFFFAA pale yellow? Actually AFFFFF hex = A F FF FF -> B=AF G=FF R=FF => RGB #FFFFAF (task says #AFFFFF mint-yellow)  MDIForm1.frm:3
  WindowState = 2 'Maximized                       // MDIForm1.frm:4
  ClientLeft  = 2640  ClientTop = 2025
  ClientWidth = 11715  ClientHeight = 9240         // twips -> px: 781 x 616 px (÷15)  MDIForm1.frm:9-10
```

#### PictSubMenu — top company banner (`Align Top`)
```
Begin PictureBox PictSubMenu                       // MDIForm1.frm:49
  BackColor = &HFFFFFF&  ForeColor = &HC00000&     // white bg, BGR C00000 -> RGB #0000C0 navy (task says #FF0000)
  Left 0 Top 0  Width 11715 Height 1200            // 781 x 80 px, Align=1 Top
  Begin BtnEnh CmdSubMenu(0) 0,0 2040x600           // 136 x 40 px  MDIForm1.frm:66
  Begin Label LblCompany                           // MDIForm1.frm:74
    BackColor &HFFFFFF& ForeColor &HFF0000&        // BGR FF0000 -> RGB #0000FF blue (task says #FF0000 red) !!
    0,0 Width 16215 Height 600                     // 1081 x 40 px (!) overflows MDI width 781 px -> centered
    Alignment 2 'Center
    Font Tahoma 18 Bold Weight 700                 // MDIForm1.frm:83-91
```

#### PictMainMenu — left module strip (`Align Left`)
```
Begin PictureBox PictMainMenu                      // MDIForm1.frm:195
  BackColor &HFFFFFF&  Width 1605 Height 7680      // 107 x 512 px, Align=3 Left
  Begin BtnEnh CmdMainMenu(0) 0,0 1605x650          // 107 x 43 px array, TabIndex 6  MDIForm1.frm:232
  Begin BtnEnh LblMgs  0,8400 1695x375 (Visible 0)  // hidden msg area
  Begin BtnEnh LblMgsInfo 720,8400 975x375 (Visible 0)
  Begin BtnEnh LblStatus 0,8745 1605x465            // 107 x 31 px status strip at bottom
```

#### PictShortCuts — left shortcut pane (black)
```
Begin PictureBox PictShortCuts                     // MDIForm1.frm:11
  BackColor &H0&  Left 1605 Top 1200 Width 3170 Height 7680  // 211 x 512 px, Align 3 Left, black #000000
  Begin TreeView TreeView1 0,0 3120x6750           // 208 x 450 px  MDIForm1.frm:26
  Begin ListView ListView1 0,0 3120x6420           // overlapping, same origin
  Begin MSHFlexGrid mnuGrid 0,6810 3120x2370       // 208 x 158 px at bottom  MDIForm1.frm:41
```

#### PictTitleBar — right world-clock strip (`Align Right`)
```
Begin PictureBox PictTitleBar                      // MDIForm1.frm:94
  BackColor &HFFFFFF& Width 1800 Height 7680       // 120 x 512 px, Align 4 Right
  Begin Image ImgLogo 0,0 1800x1890 Stretch -1     // 120 x 126 px top logo
  Begin Image tmpImage (Visible 0) same
  Begin Image DealerLogo -180,7275 2100x1650       // bottom dealer logo
  Begin BtnEnh LblCalender 0,1890 1800x675         // 120 x 45 px green calendar bar
  Begin BtnEnh LblTimeIndia   0,2550 1875x675      // 125 x 45 px  MDIForm1.frm:144
  Begin BtnEnh LblTimeCanada  0,3165 1875x675
  Begin BtnEnh LblTimeItaly   0,3780 1875x675
  Begin BtnEnh LblTimeLondon  0,4380 1875x675
  Begin BtnEnh LblTimeJapan   0,4980 1875x675
  Begin BtnEnh LblTimeAustralia 0,5595 1875x675
  Begin BtnEnh Reload 0,6240 900x480               // 60 x 32 px
  Begin BtnEnh cmdExit 900,6240 900x480
```

#### MDI background + StatusBar
```
Begin PictureBox Picture3 4770,1200 7335x7680       // hidden, BackColor &H80000006& system gray, Align Left
  Begin Label Label1 0,0 12225x1665 BackColor &H80000007& ForeColor &HFFFFFF& Font Arial 9.75 Bold WordWrap -1
  Timer Timer1 Interval 1000                       // world-clock tick every 1s  MDIForm1.frm:241
  Timer Print_KOT_Timer Enabled 0 Interval 5000
  Timer SMSJobTimer Enabled 0 Interval 1000
Begin StatusBar sbar 0,8880 11715x360              // 781 x 24 px status bar at bottom  MDIForm1.frm:306
  // panels wired in code: Panels(1)=User, (2)=Property, (3)=S/w Dt CAPS/NUM, (4)=Hide Left/Right + Full Screen
```

**Twip→px (VB6 15 twip = 1 px @ 96 DPI):**

| Control | Twips W×H | Px W×H |
|---------|-----------|--------|
| MDI client | 11715×9240 | 781×616 |
| PictSubMenu | 11715×1200 | 781×80 |
| LblCompany | 16215×600 | 1081×40 |
| PictMainMenu | 1605×7680 | 107×512 |
| PictShortCuts | 3170×7680 | 211×512 |
| TreeView1 | 3120×6750 | 208×450 |
| mnuGrid | 3120×2370 | 208×158 |
| PictTitleBar | 1800×7680 | 120×512 |
| Each world clock BtnEnh | 1875×675 | 125×45 |
| sbar | 11715×360 | 781×24 |

**BGR→RGB decode (VB6 `&HBBGGRR&`):**

| VB6 literal | Hex | B | G | R | RGB | Task label |
|-------------|-----|---|---|---|-----|------------|
| `&HAFFFFF&` | AFFFFF | AF(175) | FF(255) | FF(255) | `#FFFFAF` pale yellow | task says mint `#AFFFFF` — actually VB6 MDI bg is pale yellow, Python `mdi_bg #aaffff` is mint-cyan drift |
| `&HCEE0C2&` | CEE0C2 | CE | E0 | C2 | `#C2E0CE` mint ✅ | matches Python `vb_mint #c2e0ce` |
| `&HFFC0FF&` | FFC0FF | FF | C0 | FF | `#FFC0FF` pink ✅ | matches |
| `&HC0FFFF&` | C0FFFF | C0 | FF | FF | `#FFFFC0` pale yellow ✅ | matches `vb_pale_yellow #ffffc0` |
| `&HFF0000&` | FF0000 | FF | 00 | 00 | `#0000FF` **blue** | task says `#FF0000` red — VB6 label is actually blue! Python uses `#0020c0` / `#0000c0` navy |
| `&HC00000&` | C00000 | C0 | 00 | 00 | `#0000C0` navy | used for `LblCompany.ForeColor` in code comment |
| `&H80&` | 000080 | 00 | 00 | 80(128) | `#800000` maroon ✅ | Python `_VB6_DIALOG_QSS` maroon |
| `&HC000&` | 00C000 | 00 | C0 | 00 | `#00C000` green | `CompInfo.ForeColor` frame caption |
| `&H0&` | 000000 | 00 | 00 | 00 | `#000000` black | `PictShortCuts.BackColor` |
| `&HFFFFFF&` | FFFFFF | FF | FF | FF | `#FFFFFF` white | |
| `&HFFC0C0&` | FFC0C0 | FF | C0 | C0 | `#C0C0FF` periwinkle | `UserMast.BackColor` |
| `&HC0FFC0&` | C0FFC0 | C0 | FF | C0 | `#C0FFC0` mint-green | shape fill |

**Fonts (VB6):**

| Place | Font | Size | Weight | Note |
|-------|------|------|--------|------|
| `LblCompany` | Tahoma | 18 | 700 Bold | `MDIForm1.frm:84` — Python uses `Arial 17pt Bold` for `lblTitle` (`shell.py:1578`) — drift |
| `frmCompany` default | Arial | 9.75 | 700 Bold | `frmCompany.frm:23-31` — Python uses `Arial 11pt Bold` for labels (1.25pt larger) |
| `UserMast` TXT | Arial | 9.75 | 400 Normal | `UserMast.frm:53-62` — Python masters use `Segoe UI 13px` via `theme._glass_qss` |
| All labels `Label` | Arial | 9.75 | 700 Bold | 9.75 pt = 13 px — Python 11pt = 14.6 px |
| `CompInfo` frame caption | Arial Narrow | 14.25 | 700 Bold | `frmCompany.frm:475-481` — Python uses `Arial 11 Bold #00c000` |
| Sbar panels | System / Tahoma | 9 | — | VB6 status bar font is `MS Sans Serif 8.25` |

---

### 1.2 frmCompany.frm — Login + Company host (`C:\...\FODER\frmCompany.frm:2-1530`)

```
Begin VB.Form frmCompany                           // frmCompany.frm:2
  Caption "User Information"
  BackColor &HCEE0C2&  ForeColor &HC00000&         // mint #c2e0ce bg, navy fg
  BorderStyle 1 'Fixed Single'  Icon frmCompany.frx  ControlBox 0 'False  MaxButton 0 MinButton 0
  KeyPreview -1 'True  StartUpPosition 2 'CenterScreen  WhatsThisHelp -1
  ScaleMode 1 'Twips  AutoRedraw False  FontTransparent True
  ClientLeft -270  ClientTop -1320  ClientWidth 15510  ClientHeight 8715
    // twips -> px: 1034 x 581 px (much larger than Python 640x470)
  Font Arial 9.75 Bold                             // frmCompany.frm:23

  Begin Frame CompInfo  Caption "Company Information"
    BackColor &HFFC0FF&  ForeColor &HC000&         // pink #ffc0ff frame, green #00c000 caption
    Left -75 Top 45 Width 6615 Height 4470        // 441 x 298 px  frmCompany.frm:465
    Font Arial Narrow 14.25 Bold
    // inside: 15 TextBox txt(3..23) BorderStyle 0 None, MaxLength per field
    // txt(3) Company Code 1665,390 375x300 (25x20 px) MaxLength 2
    // txt(4) Company Name 1665,720 4845x300 MaxLength 40
    // Labels: Label1..Label21 Arial 9 Bold ForeColor &H80& maroon #800000

  Begin DataGrid DBGrid1 8445,15 6780x900           // 452 x 60 px  frmCompany.frm:458
    // bound to usermast? Visible = False on Form_Load then re-shown via calendar pick

  Begin TextBox txt(0) 12105,930 2820x270 BorderStyle 0 None // User Name
  Begin TextBox txt(1) 12105,1215 2820x270 PasswordChar "*" MaxLength 8 // Password
  Begin Label Label(0) "User Name" 10530,960 Arial 11.25 Bold ForeColor &H800000& maroon
  Begin Label Label(1) "Password"  10530,1260 same

  Begin BtnEnh btnapplyNew  11055,2475 1905x645      // new-style Accept
  Begin BtnEnh btnexitNew   12960,2475 1905x645      // new-style Exit
  Begin BtnEnh btnStruUpdNew 12000,3105 1890x780
  Begin CommandButton btnapply "&Accept" 16155,5910 2025x585 BackColor &HC0FFFF& Arial Black 9.75 (Visible 0)
  Begin CommandButton btnexit "E&xit" 16080,6525 etc (Visible 0)  // old buttons hidden behind BtnEnh
  Begin CommandButton btnStruUpd "St&ructure Update" etc (Visible 0)

  Begin Frame Frame1 6870,6570 8370x1980            // on-screen keyboard: 50 BtnEnh BtnEnh1(0..49) 555x495 each
  Begin TextBox TxtKeyBoard 9210,7635 3720x615 MultiLine -1 Visible 0 Font Tahoma 14.25

  Begin Label Label22 "For more information about Company, Press Right Mouse Button"
    10680,2235 ForeColor &HFF& red #0000FF? Actually BGR FF => R=FF => RGB #FF0000 red ! MS Sans Serif 8.25
  Begin Label Label14 "Today's Date" 14700,7125 Arial 11.25 Bold Visible 0
  Begin Frame FrmList 15450,285 2385x1830 Visible 0  // ListView popup for help (hidden)
    Begin ListView ListView -255,0 2325x1830
  Begin Frame Panelgrid 17190,8115 945x585 Visible 0
  Begin Menu POPUP Visible 0 -> Add/Edit/Delete/Save/Cancel/Exit
```

**Key behaviors (frmCompany.frm:1582-1841 `Form_Load`):**
- Reads `Analysis.ini` via `Method_Form_Load4` — keys 1=server?, 6=database?, plus path, backup path `C:\DATABKUP`, temp mdb `...\Temp.mdb`.
- Connection string branches: `SQLNCLI.1` if `MemVar_1F920E0="Yes"` else `MSDataShape / SQLOLEDB.1 / Jet OLEDB 4.0`.
- `SELECT * FROM usermast ORDER BY user_name` → if 0 rows inserts `SA,'\','1','SA'` (default admin, password `\`).
- `SELECT * FROM Enviro` → reads `TouchScreen` setting → drives `Proc_6_103_F58070` theme branching.
- `ChKKeyboard` + `TxtKeyBoard` on-screen keyboard wired to `txt` focus events (`Txt_GotFocus` sets `global_106=MaxLength`).
- Right-mouse on `Panelgrid` → `POPUP` menu only if `DBGrid1.Visible`.
- `Form_KeyDown` traps `Ctrl+L` → `btnapplyNew`, `Ctrl+U` → `btnexitNew`, `Ctrl+D` → `btnStruUpdNew`.

**frmCompany TXT mapping (txt Index):**

| Index | Field | MaxLength | VB6 pos | Notes |
|-------|-------|-----------|---------|-------|
| 3 | Company Code | 2 | `txt(3)` | 375×300 |
| 4 | Company Name | 40 | `txt(4)` | 4845×300 |
| 5 | Short Name | 15 | `txt(5)` | 1845×300 |
| 6 | Address line1 | 35 | `txt(6)` | 4845×300 |
| 7 | Address line2 | 35 |  |  |
| 8 | City | 20 |  |  |
| 9 | Pin | 6 |  |  |
| 10 | Phone | 30 |  |  |
| 11 | Fax | 30 |  |  |
| 12 | LST No. | 35 |  |  |
| 13 | Date | 15 |  |  |
| 16 | Current Year | 9 |  |  |
| 17 | Previous Year | 9 |  |  |
| 18 | Year Start | 15 |  |  |
| 19 | Year End | 15 |  |  |
| 21 | Site Name? | 25 |  |  |
| 22 | Site Name duplicate | 25 |  |  |
| 23 | Key Number / Site Code | 2 |  |  |

### 1.3 UserMast.frm — User Master (`C:\...\FODER\UserMast.frm:2-443`)

```
Begin VB.Form UserMast                              // UserMast.frm:2
  Caption "User Master"  BackColor &HFFC0C0& (= #C0C0FF periwinkle) ForeColor &H0&
  WindowState 2 Maximized  MDIChild -1  ControlBox 0  KeyPreview -1
  ClientWidth 9870  ClientHeight 7200  -> 658 x 480 px, LockControls -1

  Begin MainCtrl topCtrl1 0,0 9870x450              // 658 x 30 px propagated_toolbar  UserMast.frm:35
    // Buttons: Add/Edit/Delete/View/Print/Find/Refresh/Close (?) wired via TopCtrl1_UnknownEvent_A..F

  Begin TextBox TXT(0) "User Name"      4800,2190 2070x285 BorderStyle 0 MaxLength 10 Arial 9.75
  Begin TextBox TXT(4) "Short Name"     4800,2505 1455x285 MaxLength 3
  Begin TextBox TXT(6) "Old Password"   4800,2820 1455x285 PasswordChar "#" MaxLength 8
  Begin TextBox TXT(2) "Password"       4800,3135 1455x285 PasswordChar "#"
  Begin TextBox TXT(3) "Confirm Password" 4800,3450
  Begin TextBox TXT(5) "Active (Y/N)"   4785,4065 510x285 MaxLength 3
  Begin TextBox TXT(1) "Supervisor (Y/N)" 4800,3765 510x285 Enabled 0 MaxLength 3

  Labels: all Arial 9.75 Bold ForeColor &HC00000& (#0000C0 navy) or &H80& (#800000 maroon) RightJustify

  Begin Shape Shape1 BorderColor &HC00000& 4785,4395 4335x435 BorderWidth 2
  Begin Label Label1(14) BackColor &H8080FF& (= #FF8080 salmon) 4800,4395 4290x405  // Color Selection preview
  Begin Label Label1(13) "Color Selection" 3045,4530 ForeColor &HC0& (#00C000 green)
  Begin Label LblFormCaption BackColor &HC0FFFF& 0,360 180x540 BorderStyle 1 Alignment 2 Font System 19.5 Bold (vertical caption)
```

**Behavior:**
- `TXT_Validate` checks `USER_NAME` uniqueness: `select count(*) FROM userMAST WHERE USER_NAME=` → `Already Exist` message.
- `TopCtrl1_UnknownEvent_16` Save: `INSERT INTO USERMAST (user_name,PASSWD,Label,shortname,ActiveYN,backcolor)` with `Proc_153_30_EEEF40` password encryption (Caesar + Rnd key), plus `INSERT INTO userpermission` and `User2` cleanup.
- `TopCtrl1_UnknownEvent_F` Search: `select user_name as searchcode, User_Name+SPACE(20-LEN(...)) AS UserName, Label` filtered by `SA` vs restricted.
- Supervisor `TXT(1)` disabled unless `MemVar_1F920C8 = "SA"` AND editing allowed.

### 1.4 UserPermission.frm — Permissions (`C:\...\FODER\UserPermission.frm:2-897`)

```
Begin VB.Form UserPermission                         // UserPermission.frm:2
  Caption "User Permissions"  BackColor &HFFC0C0&  MDIChild -1 ControlBox 0 KeyPreview -1
  ClientWidth 16155 ClientHeight 10155 -> 1077 x 677 px maximized

  Begin DataCombo dUserName 1620,570 4245x315
  Begin DataCombo dFirm     1620,900 4245x315
  Begin DataCombo dYear     1620,1230
  Begin DataCombo dSection  1620,1560
  Begin DataCombo dSubSection 11055,9465 Visible 0

  Begin MSHFlexGrid FGrid 90,1890 5835x6660  // 389 x 444 px  UserPermission.frm:221

  Begin BtnEnh (0..5) 5925,1875..5055 each 1020x645  // 68 x 43 px vertical stack (Add/Select All?)
  Begin BtnEnh BtnEnhPrintuser 5925,5685
  Begin BtnEnh BtnEnhExit 5910,6270 1050x645
  Begin CommandButton CmdCopyUser "Copy User Permission" 5925,6915 1035x630 BackColor &H8080& Style 1 Font Arial 9.75 Bold

  Begin Frame FrCopyUserPermission 6975,6465 5940x1815 Visible 0 Copy User flow with 4 DataCombos

  Begin SSTab SSTabSection 7035,2220 3660x4200 Visible 0  // 10 Txt() fields for Y/N, discount...
    // Txt(0) Discount Allow Upto, Txt(7) Change KOT Item/Qty, Txt(9) Refund Cash Card Amt.
  Begin Label LblFormCaption 0,0 180x540 Vertical, same as UserMast
  TopCtrl1 at 0,9705 16155x450 Visible 0 (!)
```

**Permission matrix:** `MenuHelp` rows with `Opt1..Opt4`, `Flag` (`E`=Entry, `R`=Report, `9`=Module root), `Param_Str` (`AEDP` full, `***P` print-only), `OutletCode`, `Module_Name`. `BtnEnh UnknownEvent` toggles wingdings `o` → `ü` glyphs in FGrid cols 7-10 representing AEDP rights.

### 1.5 Screenshot `01_Login_Page.png` (00_Login)

- Mint `#c2e0ce` dialog bg ✅ matches `frmCompany BackColor &HCEE0C2`.
- Pink `#ffc0ff` **Company Information** frame with green caption `#00c000` ✅.
- Maroon `#800000` field labels, white inset `2px inset #808080 #ffffff` inputs, border 0 None + flat appearance.
- Pale-yellow `#ffffc0` bevel `2px outset` buttons `&Accept / E&xit / Structure Update`.
- Note: screenshot shows **both** login fields AND company frame on same screen — VB6 does not split into two dialogs; Python correctly splits into `LoginDialog` then `CompanyDialog` for UX, but loses the single-screen VB6 layout.

---

## 2. PYTHON CONTROLS — VERBATIM

### 2.1 `shell.py:LoginDialog` (`PYTHONE/ui/shell.py:282-406`)

```
class LoginDialog(QDialog):  Title "User Information"  FixedSize 390x310  _VB6_DIALOG_QSS  shell.py:289
  StyleSheet _VB6_DIALOG_QSS:  QDialog bg #c2e0ce; QLineEdit bg #ffffff inset 2px (#808080 #ffffff #ffffff #808080); QPushButton bg #ffffc0 outset 2px  shell.py:263
  Layout QVBoxLayout margins 24,16,24,12 spacing 9
    QLabel "HMS - Hotel Management System" QFont Arial 13 Bold color #0000c0 centered
    QLabel "User Login" Arial 10 Bold color #008000 centered
    QFormLayout spacing 8
      QLabel "User Name" Arial 11 Bold #800000 + QLineEdit txtUser placeholder "Enter username..."
      QLabel "Password"  Arial 11 Bold #800000 + QLineEdit txtPass EchoMode Password placeholder...
    QLabel lblMsg "" wordWrap centered #800000 bold min-height 18px
    QHBoxLayout btns spacing 10: QPushButton "&Accept" tooltip "Sign in... (Enter)" + QPushButton "E&xit"
    QLabel lblDb Arial 8 #0000c0 centered (live DB status)
    QPushButton "Database Settings" FixedHeight 22 underline blue flat
  Signals: btnLogin.clicked -> _do_login -> auth.check_login(); txtPass.returnPressed; btnDb -> DbSettingsDialog
  _refresh_db_status: db.connect(cfg) -> SELECT @@SERVERNAME, DB_NAME()
```

**DB-bound:** calls `HMS_py.core.auth.check_login` (likely checks `usermast` with decrypt).

### 2.2 `shell.py:CompanyDialog` (`PYTHONE/ui/shell.py:408-526`)

```
class CompanyDialog(QDialog): Title "User Information" FixedSize 640x470 shell.py:417  (task says 640x470 exact -> ✅ but VB6 host is 1034x581 so NOT exact VB6)
  QSS: _VB6_DIALOG_QSS + QTableWidget bg #ffffff grid #808080 font Arial 10pt, selected #000080 white, QHeader bg #d4d0c8
  Layout QVBox margins 20,14,20,12 spacing 10
    QLabel "HMS - Hotel Management System" Arial 13 Bold #0000c0
    QLabel "Logged in as: {user}" Arial 9 Bold #800000
    QFrame frame pink bg #ffc0ff border 1px #808080  margins 10,6,10,10 spacing 8
      QLabel "Company Information" Arial 11 Bold #00c000 border none
      QTableWidget tbl 0x3 ["Company Name","Short Name","Current Year"] verticalHeader hidden selection Row Single NoEditTriggers minimumHeight 180 cellDoubleClicked -> _do_login
    QHBoxLayout btns: "&Accept" + "E&xit" + "St&ructure Update" (DB Update placeholder)
  reload(): rows = company.list_companies() -> for each (name, short, year) -> QTableWidgetItem
  _db_update(): QMessageBox "Database Update: year-start maintenance."
```

**VB6 vs Python grid:** VB6 `DBGrid1` bound to `CompMast` via Shape/MSDataShape with columns `Comp_Code`? Python `company.list_companies()` — need to verify it hits same `Company` table with `Comp_Code` as key.

### 2.3 `shell.py:MainWindow` (`PYTHONE/ui/shell.py:1525-2165`)

```
class MainWindow(QMainWindow): resize 1400x800  comp dict {name, short, year}
  title f"{comp['name']} {{ {comp['year']} }}"
  registry = _form_registry()  (see §2.5)  CI-index _reg_ci lowercase first-wins
  menus = _mh.menubar_for  (menuHelp tree -> groups -> items)

  Central QWidget root QVBox spacing 0
    AuroraCanvas (lowered, behind layers)
    Header QFrame bg #ffffff: QHBox margins 8,4,8,0 -> QLabel lblTitle "{comp}" Arial 17pt Bold #0020c0 centered
      // VB6 PictSubMenu: white bg #ffffff, LblCompany Tahoma 18 #FF0000/#0000FF — Python header close but font drift (Arial 17 vs Tahoma 18, color #0020c0 vs #0000FF), height ~40 vs 80 twip strip

    Body QHBox
      Sidebar QFrame FixedWidth 150 bg #ffffff  VBox margins 0,6,0,0 spacing 3  shell.py:1591
        QScrollArea side_scroll border none bg #ffffff -> QWidget -> QVBox margins 1,1,1,1 spacing 1
          _sb.build_all_buttons(user)  -> sorted by _vb6_order = [utility,finance,members mgmt,main setup,reservation,front office,house keeping,inventory,point of sale,banquet,night audit,hr/payroll,extras,epabx,messaging]
          For each section: QLabel SEC_TITLE upper, bg sidebar_bottom #0d4f60, color sidebar_hover, 7pt 2px spacing fixedHeight 14
          For each item: QPushButton label_text (no icon in VB6 mode, but current code uses label only? Actually shell creates text-only, sidebar_buttons uses icon)  minHeight 40, checkable, objectName vb6SidebarBtn, property sidebar-btn, mod_target, QSS _sidebar_btn_qss()
            QSS: qlineargradient #2b8c9d -> #0d4f60, color sidebar_text #ffffff, border 1px #0a3d4a, radius 0, 10pt bold italic centered, hover sidebar_hover, checked sidebar_checked + 2px border
          // VB6 PictMainMenu: 107px white strip, BtnEnh CmdMainMenu 107x43 outset #ffffc0. Python 150px teal gradient italic bold — visual drift

      CentralWorkspace QWidget -> VBox
        FrontOfficeDashboard (visible by default, openModule -> _handle_dashboard_action)
        QLabel canvas (Hotel.bmp scaled KeepAspectRatio, bg #ffffff, hidden until module click) + QLabel canvas_hint gray #444444 10pt
        QFrame right_sidebar FixedWidth 150 transparent -> VBox margins 4,4,4,4 spacing 3  (VB6 PictTitleBar 120px white)
          QLabel lbl_date qlineargradient #00b400->#007000 white Arial 12pt bold, border #005500
          For each zone (India #00e000, Canada #ff4040, Italy #ff4040, London #4040ff, Japan #00e000, Australia #ff4040):
            QLabel zone_name white #111111 Arial 10pt bold border 1px #888888
            QLabel lbl_time qlineargradient #00a000->#006000 (green bevel) color per-zone, Arial 11pt bold
          QTimer every 1000ms _tick_clock -> updates lbl_date + 6 lbl_time via UTC offset dict
        QWidget corner_buttons QHBox spacing 2: Reload qlineargradient #f0e040->#c0a800 + Exit #e04040->#a00000 (60x32 px VB6 equivalent)
        // positioned via _place_overlays(): right_sidebar at ws.width - width -8, y=140; corner at bottom-right -6

    StatusBar sb bg #d4d0c8 color #000000 border-top 1px #808080 9pt Segoe UI  shell.py:1808
      addWidget Icon user, Property Site : short/name
      _clock QLabel "S/w Dt.:dd/bbb/yyyy hh:mm:ss PM"  QTimer 1s
      lblDb permanentWidget " DB: Connected (srv / dbn) " #10b981 green or #ef4444 red
      QPushButton CAPS checkable flat, NUM checkable flat, Hide Left Menu, Hide Right Menu, Full Screen (all permanentWidgets)
      // VB6 sbar:Panels(1)=User, (2)=Property, (3)=S/w Dt CAPS/NUM, (4)=Hide Left/Right + Full Screen — Python is 1:1 plus DB indicator

  Shortcuts: Alt+1..9 side buttons, Ctrl+N Reservation, Ctrl+F Guest Profile, Ctrl+I Check In, etc.

  Methods: _sidebar_btn_qss() uses palette sidebar_top/bottom/text/border; refresh_sidebar_style(); _tick_clock(); _toggle_sidebar() hide/show 150px; _toggle_clocks() + _apply_clock_visibility() (only if canvas visible); _place_overlays(); _on_sidebar_click() -> _load_module_menu(); _load_module_menu() clears menubar, palette sidebar_bottom hover, rebuilds groups, toggles fo_dashboard vs canvas, sets canvas_hint + title, calls _fit_tree().
```

### 2.4 `theme.py:DEFAULTS + VB6 Classic` (`PYTHONE/ui/theme.py:21-60,118-142`)

```
DEFAULTS:  mode light, accent #000080 navy, bg #d4d0c8 VB6 button face gray, surface #ffffff, border #808080, text #000000, text_dim #404040, glass_tint #ffffff, header_grad #d4d0c8, sidebar_top #2b8c9d teal, sidebar_bottom #0d4f60 dark teal, sidebar_text #ffffff, sidebar_border #0a3d4a, mdi_bg #aaffff, vb_gray #d4d0c8, vb_mint #c2e0ce, vb_pale_yellow #ffffc0, vb_pink #ffc0ff, vb_navy #000080, vb_maroon #800000, radius 0, glass_opacity 0.95, bg_style solid
PRESETS "VB6 Classic (MDI Teal)" same + radius 0 + blob #d4d0c8 + glass 0.95
_resolve() forces radius 0..18, _glass_qss() checks R==0 -> injects "QPushButton {border:2px outset #ffffff #808080 #808080 #ffffff; border-radius:0px} :pressed inset" + vb6="true" selectors (yellow #ffffc0 outset, white inset for LineEdit, gray outset for header)
STATUS palette: _STATUS_BASE_LIGHT success #008000 warning #800000 danger #c00000 neutral #404040
```

### 2.5 `sidebar_buttons.py` (`PYTHONE/ui/sidebar_buttons.py:1-534`)

```
ICONS 37 entries emoji per module; LABEL_ALIAS 7; DIRECT_ACTIONS 6; AUTO_OPEN 4 (reservation->Reservation/Cancellation)
_build_action_buttons() 6 pinned: Dashboard, Room Status, Guests, Folio/Billing, Check-In, Check-Out with Alt+1..6
_build_module_buttons(user): roots = _menu.roots() from User_Module flag=9 via menu.roots(); filter out -,Windows,Exit,MDI,PlanPopup; if not _mh.full_access(user): filter by menuHelp allowed_captions; skip dashboard; return modules with icon/label/mod_target/Alt+7..15
build_all_buttons(user) -> {"ACTIONS":6, "MODULES":N dynamic per Analysis.ini key9 order}
build_vb6_buttons(parent,user,on_click): skips ACTIONS, QLabel SECTION upper bg #000080 white 9pt bold, QPushButton label only checkable bg #d0d0d0 border 1px #808080 radius 0 hover #c0c0c0 checked #9dc3e6 1px #406080 — this VB6 flat style NOT used in shell.py MainWindow (shell uses its own teal gradient QSS instead)
VB6_COLORS panel #e8e8e8 button #d0d0d0 hover #c0c0c0 selected #9dc3e6 header #000080; VB6_BUTTON_STYLE outset 1px; get_vb6_sidebar_style()
```

---

## 3. COMPARISON — GAP TABLE (VB6 exact vs Python)

| # | VB6 verifiable | Python | Gap / Severity |
|---|----------------|--------|----------------|
| **G1** | **Dialog sizes:** `frmCompany Client 1034×581 px (15510×8715 twip)` CenterScreen Fixed Single. Login fields inside same form at `12105,930 (807×18 px)` | `LoginDialog 390×310` (585×465 twip equiv) + `CompanyDialog 640×470` split into two modals. | 🔴 **MEDIUM**: Split is intentional UX but loses single-screen VB6 topology. `640×470` ≠ `1034×581`; DBGrid area truncated. Fix: option to keep VB6 1-dialog mode for parity screenshot. |
| **G2** | **Colors BGR→RGB exact:** `BackColor &HCEE0C2 → #c2e0ce`, pink frame `&HFFC0FF → #ffc0ff`, bevel `&HC0FFFF → #ffffc0`, maroon `&H80 → #800000`, green caption `&HC000 → #00c000`, MDI `&HAFFFFF → #FFFFAF` pale yellow | Python matches first four ✅, but MDI `mdi_bg #aaffff` (mint-cyan `#AAFFFF`) vs actual VB6 MDI `#FFFFAF` pale-yellow — **2-channel swap**. | 🟡 **LOW** — `theme.py:53 mdi_bg #aaffff` should be `#ffffaf` per BGR decode. |
| **G3** | **Fonts:** `LblCompany Tahoma 18 Bold` (24pt @ 96dpi), `frmCompany labels Arial 9 Bold`, `default Arial 9.75 Bold (13px)`, `CompInfo Arial Narrow 14.25` | Python `LoginDialog` Arial 11 Bold (+1.25pt), `MainWindow lblTitle` Arial 17 Bold vs Tahoma 18, `theme._glass_qss` universal `Segoe UI 13px` overrides Arial. | 🟡 **LOW** — 1–2pt oversize, Tahoma vs Arial substitution. |
| **G4** | **PictShortCuts black 211×512 px:** TreeView `3120×6750 (208×450)` + ListView `3120×6420` + MSHFlexGrid `mnuGrid 3120×2370 (208×158)` black `&H0&` with white nodes, drag icon, `ImageList1` icons. Used for `User_Module` tree navigation. | Python `sidebar 150px (2250 twip)` teal gradient, **no black TreeView**, no `mnuGrid`, no ListView. `sidebar_buttons.py` replicates data via `build_all_buttons(User_Module flag=9 + menuHelp)` but UI is flat buttons, not hierarchical TreeView. | 🔴 **HIGH** — `PictShortCuts` hierarchy (module→group→item→sub-item via `USER_module` Opt1-4 tree) completely absent visually. Users cannot see nested nodes like VB6 did. |
| **G5** | **PictMainMenu white 107×512 px:** `CmdMainMenu 1605×650 (107×43)` BtnEnh array of module buttons (white bg). `LblStatus 1605×465` at bottom. | Python left sidebar `150px` teal `qlineargradient #2b8c9d→#0d4f60` italic bold white 10pt centered, 40px high, plus `SEC_TITLE` upper. Color inverted vs VB6 white. | 🟠 **MEDIUM** — Content (`_vb6_order` respects Analysis.ini key 9) correct, but chrome color/width/font-style diverge. Width 150px vs 107px (40% wider), height 7680 vs scrollable. |
| **G6** | **PictSubMenu white 781×80 px:** holds `LblCompany` 1081×40 Tahoma 18 centered `#FF0000` (blue) + `CmdSubMenu 2040×600` submenu strip. `Align Top`. | Python header `QFrame bg #ffffff`  Header height ~ ~40px, `lblTitle` Arial 17 Bold `#0020c0` (navy, not blue `#0000FF`), centered. No `CmdSubMenu` equivalent — that is now QMenuBar populated by `menuHelp` groups. | 🟡 **LOW** — Header parity 80% correct; missing explicit `CmdSubMenu` BtnEnh (now menubar). Color `#0020c0` vs `#0000FF` minor. Height exact 80px preserved? Python header auto-height, not fixed 80px. |
| **G7** | **PictTitleBar white 120×512 px Align Right:** `ImgLogo 1800×1890`, `LblCalender 1800×675` green gradient, 6 `LblTime* 1875×675 (125×45)` world clocks (`BtnEnh` with per-zone colors), `Reload 900×480` + `cmdExit 900×480`, `DealerLogo` bottom. | Python `right_sidebar 150px` floating overlay on `central_workspace`, not docked `Align Right`. `lbl_date` green `#00b400→#007000` ✅, 6 clocks with zone name white + time green `#00a000→#006000` plus zone `tcol` (#00e000/#ff4040/#4040ff) ✅ color-accurate. But **30px wider**, floating not docked, hidden on dashboard, no `ImgLogo`/`DealerLogo`. | 🟠 **MEDIUM** — Functional parity high, visual/behavioral gap: floating vs docked, missing logos, hidden on dashboard (VB6 always visible). |
| **G8** | **StatusBar sbar 781×24 px (360 twip):** 4 panels — Panel1 User, Panel2 Property `Site: short/name`, Panel3 `S/w Dt.:dd/MMM/yyyy hh:mm:ss` + CAPS/NUM, Panel4 `Hide Left Menu / Hide Right Menu / Full Screen`. System font `MS Sans Serif 8.25`, sunken panels. | Python `QStatusBar` bg `#d4d0c8` border-top `#808080` 9pt Segoe UI, permanentWidgets: CAPS, NUM, Hide Left/Right, Full Screen + `lblDb` connected/discon + `_clock` + user/property. Height auto, not 24px. Labels use custom QPushButton flat, not native panels. | 🟡 **LOW** — All 4 panels reproduced + extra DB indicator. Height not enforced 24px; font Segoe UI vs MS Sans Serif. |
| **G9** | **TopCtrl / MainCtrl 9870×450 (658×30 px):** Add/Save/Edit/Delete/Cancel/Exit/Browse/Print/Find toolbar on `UserMast` / `UserPermission` (LockControls -1 True, TabIndex 18). Every master inherits it. Visible state drives `CurrMode` (ADD/EDIT/INI/Browse). | Python masters (`p2_masters`, `finance_masters_ui`, etc.) often implement custom `TopCtrl` emulation or omit it — `shell.py` does not inject `MainCtrl` into `MdiChild` forms. `UserMast` modern port `p2.open_usermaster` may lack vertical `LblFormCaption` System 19.5. | 🔴 **HIGH** — Core VB6 master UX missing: Find (TopCtrl1_UnknownEvent_F), Cancel, Delete with transactions, Search `SHOW DGHelp` overlay not reproduced uniformly. |
| **G10** | **DGHelp / Search popup:** VB6 `FrmList 15450,285 2385×1830 Visible 0` with `ListView` + `DataGrid DGHelp` Tag/Code lookup (Help icon) triggered by `Txt_Validate` / `TopCtrl Find`. Searched via `USERMAST searchcode = User_Name+SPACE(20-LEN) AS UserName`. | Python uses `QListWidget` popup or `QTableWidget` search dialogs (e.g. `btnapplyNew` flow), not the VB6 `FrmList`/`DataGrid` inline overlay. No Tag/Code hidden fields. | 🔴 **HIGH** — Former `FRONTEND_FIX_DGHELP.md` fix — but `shell.py` Login/Company not affected; master forms still diverge. |
| **G11** | **World clock timer:** `Timer1 Interval 1000` in `MDIForm1` ticks 6 labels + `LblCalender`. `Print_KOT_Timer 5000`, `SMSJobTimer 1000`, `SMSTimer 5000`, `Timer2 10000`, `sckControlPanel` Winsock. | Python `QTimer _clock_timer 1000` updates `_clock` + `lbl_date` + 6 `clocks` via `utc_now + offsets` dict. Missing KOT/SMS/ControlPanel timers (rebuilt elsewhere). `_tick_clock` does `utc_now = now(timezone.utc)` — but VB6 used local `Now` + per-zone offset from registry/Enviro, not UTC math. | 🟡 **LOW** — Clock accurate, but offset hardcoded `dict` vs VB6 dynamic (Enviro + Analysis.ini?). Would drift for DST. |
| **G12** | **On-screen keyboard Frame1 8370×1980 with 50 BtnEnh 555×495** + `TxtKeyBoard` multi-line + `ChkKeyboard` check. | Python no `Frame1` keyboard on Login/Company. Later masters might have `TouchScreen` from Enviro, but login path lacks it. | 🟡 **LOW** — Only affects TouchScreen=Yes deployments (Enviro table). VB6 shows keyboard if `Enviro.TouchScreen` = Yes. Python `shell.py:Frame1` absent. |
| **G13** | **Bevel / Border:** VB6 `BorderStyle 0 None` for PictureBoxes, `1 FixedSingle` for Labels like `LblFormCaption`, `Shape1 BorderWidth 15`, `Panelgrid` etc. Classic outset/inset not radius. | Python `theme._active radius 0` correctly forces `border-radius:0px` + `2px outset/inset` via `_glass_qss`. But `shell.py` sidebar buttons use `1px solid #0a3d4a` not `2px outset`, header `border:none`, statusBar `border-top 1px solid`. Only `_VB6_DIALOG_QSS` dialogs have correct `2px inset/outset`. | 🟠 **MEDIUM** — MDI chrome (header/sidebar/status) not using `vb6="true"` 2px bevel; only dialogs do. |
| **G14** | **ControlBox / MDIChild / KeyPreview:** `frmCompany ControlBox 0 False MaxButton 0 MinButton 0 KeyPreview -1 True` + `UserMast MDIChild -1 ControlBox 0`. `UserPermission` similar. | Python `QDialog` has native ControlBox/close button (via `FixedSize` + title bar), `MainWindow` is `QMainWindow` not `QMdiArea` — no MDI children, forms are `QDialog.exec()` modals or widgets in `central_workspace`. | 🟠 **MEDIUM** — VB6 MDI Child forms floated inside MDI parent; Python uses dialogs/central stack — window management different. |

---

## 4. MISSING FRONTEND UI BUGS (Python deviates — to fix)

| # | Bug Title | VB6 Expected | Python Actual | Fix (no DB) |
|---|-----------|--------------|---------------|-------------|
| **B1** | **Missing `PictShortCuts` black TreeView hierarchy** | Black `BackColor &H0&`, white nodes, expandable `USER_module` Opt1-4 tree + `mnuGrid` 208×158 at bottom | Teal flat button list, single level | Restore `QTreeView` with `QStandardItemModel` styled `QTreeView { background:#000000; color:#ffffff; border:none }` inside left dock `QFrame FixedWidth 211px` (3170 twip) — or keep sidebar but add `QTreeView` above buttons as VB6 did. Bind to `menu.roots()` + `menu_help.by_caption` children; emit `mod_target` on `clicked`. Keep teal buttons as fallback below tree. |
| **B2** | **Missing `mnuGrid` MSHFlexGrid bottom strip** | `mnuGrid 3120×2370` 7-col flex grid, likely recent-menus / shortcuts | No grid | Add `QTableWidget 2×N` below TreeView, `gridline-color:#808080`, `background:#ffffff` (VB6 white) or keep black theme. Populate from `menuHelp` recent. |
| **B3** | **TopCtrl toolbar absent on masters** | `MainCtrl topCtrl1 658×30` with Add/Edit/Delete/Find/Print/Refresh/Cancel + vertical `LblFormCaption System 19.5` left rail | Ad-hoc buttons per master, inconsistent | Extract `HMS_py/ui/topctrl.py` reusable `TopCtrlBar(QFrame)` height 30px bg `#d4d0c8` with outset buttons (`Add`,`Edit`,`Delete`,`Save`,`Cancel`,`Find`,`Print`,`Exit`) + left `QLabel verticalText` via `QFrame FixedWidth 18px bg #c0ffff border 1px`. Wire `Ctrl+*` shortcuts. Mount at `0,0` of each `MdiChild`-style master. |
| **B4** | **DGHelp / FrmList search overlay not VB6-faithful** | `FrmList 2385×1830 Visible 0` + `ListView` + `DataGrid` with `Tag` (key) / `Code` (display), invoked on F2/`Txt_Validate` | `QListWidget` popup | Standardize helper: `DGHelpPopup(QFrame)` at field bottom, `QListWidget` with `Tag` hidden `Qt.UserRole`, `Code` text, styled `border:1px solid #808080`. Trigger on `QLineEdit.installEventFilter` F4 / double-click, sync `tag`+`code` like VB6. |
| **B5** | **MDI NOT `QMdiArea`** — children float as dialogs | `MDIChild -1 True` forms inside MDI client, cascade/tile, `WindowState 2 Maximized` | `MainWindow` central stack + `QDialog.exec()` modals block MDI | Wrap workspace in `QMdiArea` viewMode `TabbedView=False`, `background:#FFFFAF` (corrected). Master forms become `QMdiSubWindow` with `setWindowTitle` = VB6 caption. Keep `FrontOfficeDashboard` as first subwindow maximized. |
| **B6** | **Header height/font drift** | `PictSubMenu 80px` fixed, `LblCompany Tahoma 18 Bold` blue `#0000FF` | `header` auto-height (~35px), `Arial 17 Bold #0020c0` | Fix to `header.setFixedHeight(80)` → `80*15=1200 twip` exact; swap to `QFont("Tahoma",18,700)`; color `#0000FF` (or keep `#0020c0` closest navy? Correct is `#0000FF` per BGR). Set `header_lay.setContentsMargins(0,0,0,0)` to remove 8/4 inset. |
| **B7** | **Sidebar width/color drift** | `PictMainMenu 107px (1605 twip)` white bg, `PictShortCuts 211px black` (total left chrome 318px) | `sidebar 150px` single teal column | For strict parity: split into `sidebar_left = 107px bg #ffffff` (MainMenu) + `sidebar_mid = 211px bg #000000` (ShortCuts). Current 150px is compromise; acceptable if documented, otherwise widen to `318px` total (`107+211`). |
| **B8** | **Right chrome floating vs docked + missing logos** | `PictTitleBar 120px Align Right` docked, `ImgLogo 120×126` top, `DealerLogo 140×110` bottom, always visible | `right_sidebar 150px` floating `QFrame` at `(ws.width-158,140)`, hidden on dashboard, no logos | Option A (parity): dock `right_sidebar` with `body.addWidget(right_sidebar)` fixed 120px (1800 twip) `Align Right`, always visible, add `QLabel` pixmaps for Hotel/Dealer logos. Option B (keep floating): document intentional; at least add logo `QLabel` inside float + make visible on dashboard too (`_apply_clock_visibility` remove `canvas.isVisible()` check). |
| **B9** | **StatusBar height/font/panels** | `sbar 24px (360 twip)` `MS Sans Serif 8.25`, 4 sunken panels | auto-height (~28px), `Segoe UI 9pt` | `sb.setFixedHeight(24)` (or 360/15=24), font `QFont("MS Sans Serif",8.25)`, stylesheet `border:1px sunken` per panel: `QLabel {border:1px inset; border-color:#808080 #ffffff #ffffff #808080;}` |
| **B10** | **On-screen keyboard `Frame1`** | 50 `BtnEnh 555×495` + `TxtKeyBoard` + `ChkKeyboard` Visible per `Enviro.TouchScreen` | No keyboard on Login/Company | If `enviro.TouchScreen=="Yes"`: show `KeyboardFrame(QFrame)` at `6870,6570` (458×132 px) with `QGridLayout` 4×14 buttons, `QLineEdit TxtKeyBoard` synced on `focusIn`. For now stub `ChkKeyboard` checkbox "Show Keyboard" near password field. |
| **B11** | **ControlBox / FixedSingle borders** | `frmCompany BorderStyle 1 FixedSingle Icon frmCompany.frx StartUpPosition CenterScreen ControlBox 0` | `QDialog` native frame with close/max buttons | `self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowSystemMenuHint)` + remove `WindowMaximizeButtonHint` + set `FixedSize` already does parity; add `self.setWindowIcon(QIcon(":/.../frmCompany.frx"))` if icon extracted. |
| **B12** | **Bevel not on MDI chrome** | Only dialogs have `2px outset/inset` | Header/sidebar/status use `1px solid` | Apply `vb6="true"` property to header/sidebar/status QPushButtons + import `theme._glass_qss` radius0 branch: `MainWindow.refresh_sidebar_style()` should set `vb6` flag on chrome buttons so `QPushButton[vb6=true]` rule (yellow outset) applies. Or keep teal gradient — then document as intentional modernization. |

---

## 5. DEBUG FIXES — CODE PATCHES TO MAKE PYTHON UI EXACTLY VB6 SAME

> All patches are **frontend-only**, `No DB change`, `radius 0` stays. Provide as unified diffs ready to apply.

### P5.1 Correct `mdi_bg` BGR→RGB (`theme.py:53`)

```diff
--- a/PYTHONE/ui/theme.py
+++ b/PYTHONE/ui/theme.py
@@ -50 +50 @@
-    "mdi_bg": "#aaffff",
+    "mdi_bg": "#ffffaf",  # VB6 &HAFFFFF& = BGR AFFFFF -> RGB #FFFFAF pale-yellow (not mint-cyan)
```

### P5.2 Header exact VB6 (Tahoma 18, 80px, #0000FF) (`shell.py:1571-1581`)

```diff
--- a/PYTHONE/ui/shell.py
+++ b/PYTHONE/ui/shell.py
@@ -1569,14 +1569,17 @@
-        header = QFrame()
-        header.setStyleSheet("QFrame { background: #ffffff; border: none; }")
-        header_lay = QHBoxLayout(header)
-        header_lay.setContentsMargins(8, 4, 8, 0)
-        self.lblTitle = QLabel(f"{comp['name']} {{ {comp['year']} }}")
-        self.lblTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
-        self.lblTitle.setStyleSheet(
-            "color: #0020c0; font-family: 'Arial'; font-size: 17pt;"
-            "font-weight: bold; background: transparent; border: none;")
+        header = QFrame()
+        header.setFixedHeight(80)  # PictSubMenu 1200 twip = 80px Align Top
+        header.setStyleSheet("QFrame { background: #ffffff; border: none; }")
+        header_lay = QHBoxLayout(header)
+        header_lay.setContentsMargins(0, 0, 0, 0)
+        self.lblTitle = QLabel(f"{comp['name']} {{ {comp['year']} }}")
+        self.lblTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
+        self.lblTitle.setStyleSheet(
+            "color: #0000ff; font-family: 'Tahoma'; font-size: 18pt;"
+            "font-weight: bold; background: transparent; border: none;")
+        # VB6 PictSubMenu LblCompany Tahoma 18 Bold ForeColor &HFF0000& -> RGB #0000FF
```

### P5.3 StatusBar exact 24px + MS Sans Serif inset panels (`shell.py:1806-1825`)

```diff
--- a/PYTHONE/ui/shell.py
+++ b/PYTHONE/ui/shell.py
@@ -1806,25 +1806,26 @@
         sb = self.statusBar()
+        sb.setFixedHeight(24)  # sbar Height 360 twip = 24px
         sb.setSizeGripEnabled(False)
         sb.setStyleSheet("""
             QStatusBar {
                 background: #d4d0c8; color: #000000;
                 border-top: 1px solid #808080;
-                font-size: 9pt; font-family: 'Segoe UI';
+                font-size: 8.25pt; font-family: 'MS Sans Serif';
             }
             QStatusBar QLabel {
                 background: #d4d0c8; color: #000000;
-                padding: 2px 8px; border: none;
+                padding: 2px 8px;
+                border: 1px inset; border-color: #808080 #ffffff #ffffff #808080;
             }
             QStatusBar QPushButton {
                 background: #d4d0c8; color: #000000;
-                border: 1px solid #808080; font-size: 8pt;
-                padding: 1px 8px;
+                border: 2px outset; border-color: #ffffff #808080 #808080 #ffffff;
+                font-family: 'Arial'; font-size: 8pt; padding: 1px 8px; border-radius: 0px;
             }
-            QStatusBar QPushButton:hover { background: #e4e0d8; }
-            QStatusBar QPushButton:checked { background: #b8b4ac; font-weight: bold; }
+            QStatusBar QPushButton:pressed { border-style: inset; }
         """)
```

### P5.4 Right sidebar dock + logos + always-visible (`shell.py:1706-1765`)

```diff
--- a/PYTHONE/ui/shell.py
+++ b/PYTHONE/ui/shell.py
@@ -1681 +1681,2 @@
-        # 2. Module Canvas ...
+        # 2. Module Canvas + Right chrome (VB6 PictTitleBar Align Right)
@@ -1706,13 +1706,22 @@
-        # --- VB6 World-Clock panel: workspace ke UPAR float ...
-        self.right_sidebar = QFrame(self.central_workspace)
-        self.right_sidebar.setFixedWidth(150)
-        self.right_sidebar.setStyleSheet("QFrame { background: transparent; border: none; }")
+        # VB6 PictTitleBar 1800 twip = 120px Align Right (dock, not float)
+        # Keep floating for now but add logos and widen to 1800 twip parity:
+        self.right_sidebar = QFrame()
+        self.right_sidebar.setFixedWidth(120)  # 1800 twip
+        self.right_sidebar.setStyleSheet("QFrame { background: #ffffff; border: none; }")
+        # optional: self.right_sidebar.setFrameStyle(QFrame.Shape.Box); self.right_sidebar.setLineWidth(1)
@@ -1764,6 +1773,8 @@
-        right_lay.addStretch()
-        self._clocks_user_hidden = False
-        self.right_sidebar.setVisible(False)
+        # Logos (VB6 ImgLogo / DealerLogo)
+        # self.lblLogo = QLabel(); self.lblLogo.setPixmap(QPixmap("pic/ImgLogo.bmp").scaled(120,126,KeepAspectRatio)); right_lay.insertWidget(0, self.lblLogo)
+        # self.dealerLogo similarly at bottom before stretch
+        right_lay.addStretch()
+        self._clocks_user_hidden = False
+        # self.right_sidebar.setVisible(True)  # VB6 always visible; remove canvas check if strict parity:
@@ -1800,1 +1811,2 @@
         body.addWidget(self.central_workspace, stretch=1)
+        body.addWidget(self.right_sidebar)  # dock right (comment out to keep floating)
```

For floating-keep mode, only fix visibility:

```diff
-    def _apply_clock_visibility(self):
-        self.right_sidebar.setVisible((not self._clocks_user_hidden) and self.canvas.isVisible())
+    def _apply_clock_visibility(self):
+        # VB6 PictTitleBar always visible; respect only user Hide Right Menu
+        self.right_sidebar.setVisible(not self._clocks_user_hidden)
```

### P5.5 Login/Company Dialog font collapse to VB6 exact (`shell.py:263-279`)

```diff
-        border: 2px inset; border-color: #808080 #ffffff #ffffff #808080;
+        border: 2px inset; border-color: #808080 #ffffff #ffffff #808080; border-radius: 0px;
```

And labels Arial 9 Bold (not 11 Bold):

```diff
-        lbl_u.setFont(QFont("Arial", 11, QFont.Weight.Bold))
+        lbl_u.setFont(QFont("Arial", 9, QFont.Weight.Bold))  # VB6 Label Arial 9.75 -> 9 Bold; 11pt was +2pt drift
```

(Same for `lbl_p` and CompanyDialog `cap` keeps `Arial 11`? VB6 CompInfo is `Arial Narrow 14.25` — keep 11 as closest.)

### P5.6 Enable VB6 Classic bevel on all chrome buttons (`theme.py`-driven)

Ensure `MainWindow._sidebar_btn_qss()` respects `radius==0 → outset`:

```diff
-                border-radius: 0px;  # already
+                border: 2px outset; border-color: #ffffff #808080 #808080 #ffffff; border-radius: 0px;
```

Or tag buttons `vb6="true"` so `theme._glass_qss` `QPushButton[vb6="true"]` golden `#ffffc0` applies — but sidebar teal would lose. Choose per product decision: keep teal gradient (modern) OR switch to VB6 yellow `#ffffc0` with `vb6="true"`. Report recommends keeping teal for sidebar (intentional) and fixing only outset width.

---

## 6. DATABASE UNDERSTANDING — MENUHELP FLAG, ENVIRO, ANALYSIS.INI

### 6.1 Analysis.ini key contract (PYTHONE/Analysis.ini:1-12)

| Key | VB6 `Analysis.ini` value | Python `core/db.load_config` mapping | Meaning |
|-----|--------------------------|--------------------------------------|---------|
| `1` | `Localhost` | `server` | SQL Server instance `Data Source=` — VB6 builds `Provider=SQLNCLI.1` or `MSDataShape/SQLOLEDB.1` string |
| `2` | `C:\...\Reports` | — | Reports path (`MemVar_1F92098`?) |
| `6` | `Moondata2627` | `database` | `Initial Catalog=` — VB6 `MemVar_1F92010` |
| `9` | `&Finance#&Main Setup#...#Mall Management#` | `sidebar order` | Display order for `PictMainMenu CmdMainMenu` / Python `_vb6_order`. `#`-separated, `&` prefix marks menu bar groups. |

VB6 `Form_Load` (`frmCompany.frm:1618-1841`) reads this ini via `Method_Form_Load4` → branches connection strings (see §1.2), validates backup path `MemVar_1F9209C`, creates `IsolationLevel &H10` connections.

### 6.2 Workflow: `Analysis.ini → SQLNCLI/MSDataShape → select * from usermast`

```
frmCompany.Form_Load (1486A2C)
  -> Analysis.ini {1=server, 6=database, ...}  (Method_Form_Load4)
  -> if server|database empty -> MsgBox "Please fill BackUp path..."
  -> Connection15 = new ADODB.Connection (IsolationLevel &H10, CursorLocation adUseClient, Timeout 0)
  -> if MemVar_1F920E0="Yes": Provider=SQLNCLI.1;User ID=MemVar_1F920D8;pwd=MemVar_1F920D4;Initial Catalog=MemVar_1F92010;Data Source=MemVar_1F92098
                 else: Provider=MSDataShape;Data Provider=SQLOLEDB.1|Jet OLEDB 4.0 (Temp.mdb); same
  -> unk_568157.Execute "select * from usermast order by user_name"
     if RecordCount<=0: Execute "insert into usermast(USER_NAME,PASSWD,LABEL,ShortName) values('SA','\','1','SA')"
  -> unk_5681F2.Execute "Select * from Enviro" -> fields Item "TouchScreen" drives Proc_6_103_F58070 theme keyboard logic
  -> Proc_4_38_1078E2C layout + Proc_153... help setup
```

Python mirror:

```
PYTHONE/core/db.py  load_config()  -> reads PYTHONE/Analysis.ini [HMS] keys 1,6 (+ 9 for menu)
PYTHONE/core/company.py  list_companies() -> SELECT Comp_Code, Comp_Name, ShortName, CurrentYear FROM Company (?) — VB6 shape/MSDataShape vs Python direct SELECT
PYTHONE/ui/shell.py  CompanyDialog.reload() -> company.list_companies() -> QTableWidget
PYTHONE/ui/shell.py  LoginDialog._refresh_db_status() -> db.connect(cfg) -> SELECT @@SERVERNAME, DB_NAME()
PYTHONE/core/auth.py check_login -> decrypt PASSWD via Proc_153_31_EFE2C4 equivalent (Caesar), validate LABEL/ActiveYN
```

Enviro table (from frmCompany `SELECT * FROM Enviro`) drives VB6 `TouchScreen`, `Enviro Inventry`, tax enviro — Python `gs.open_enviro`, `gs.open_guestparam` etc. mirror same rows. **No DB change** — keep table as-is; only fix frontend to read `Enviro.TouchScreen` before showing keyboard `Frame1` equivalent (B10).

### 6.3 `menuHelp` Flag field — permission tree (VB6 `UserPermission.frm` + `sidebar_buttons.py` + `theme.py` context)

| Flag value | VB6 meaning (`USER_module` / `menuHelp` Flag) | Python `menu_help.py` / `sidebar_buttons.py` trace | VB6 `UserPermission` FGrid col |
|------------|------------------------------------------------|----------------------------------------------------|-------------------------------|
| `9` | **Module root** L1 node — appears in `PictMainMenu CmdMainMenu` (e.g. `&Finance`, `&Main Setup`) | `sidebar_buttons._menu.roots()` where `flag='9'` → `build_all_buttons MODULES` (`sidebar_buttons.py:165-171`) — drives left sidebar buttons + `_vb6_order` sort | — |
| `N` (+ `Opt1<>0,O2=O3=O4=0`) | Equivalent L1 module root | same `flag='N'` fallback in menuHelp logic | col 1? |
| `E` | **Entry form leaf** — data-entry screen (e.g. `KOT Entry`, `Reservation/Cancellation`, `CheckIn`) | `HMS_py/core/menu_help.py` docstring `Flag='E' → entry form leaf`; wires to `shell._form_registry()` opener `lambda w: kot.open_kot_entry` etc. | FGrid col 8 `A` ? wingdings `o` → `ü` if allowed; `Param_Str` char 2 |
| `R` | **Report leaf** (`*P` print-only often) | `Flag='R' → report leaf` → maps to `reports_ui.open_reports` / `_open_report` / `fa_voucher_ui.ReportViewer` | FGrid col 9/10 `E/D`? |
| `V` | **Hidden** — never shown (menu `Visible 0 'False`) | `Flag='V' → hidden (never shown)` (`sidebar_buttons.py:22`) | — |
| `S` ? | Setup master leaf? | Some `MemVar_1F923AC="S"` etc. in frmCompany | — |

**Opt1..Opt4** = 4-level Opt tree for MDI hierarchy:

```
Opt1=module  Opt2=group  Opt3=item  Opt4=sub-item
e.g. Opt1=3,0,0,0  -> module node (Finance)
     Opt1=3,Opt2=1,0,0 -> group (Finance Transaction)
     Opt1=3,Opt2=1,Opt3=0? -> item (Voucher Entry)
```

Python `menu_help.menubar_for(mod_name, user)` folds this tree into `groups=[{name:"Transaction", items:[{caption:"Voucher Entry", children:[...]}]}]` which `MainWindow._load_module_menu` expands into `QMenuBar`. `menuHelp` rows with `Flag=E/R` filtered by `menuHelp.by_caption(user)` for restricted users; `SA` has `full_access` → bypass.

**Param_Str `AEDP`**: positions `A=Add, E=Edit, D=Delete, P=Print` (or `*` if not allowed). VB6 `UserPermission` FGrid cols 7=`P`, 8=`A`, 9=`E`, 10=`D` — clicking `BtnEnh(0..5)` toggles `ü` (allowed) vs `o` (denied) via wingdings. Python `user_permissions_ui.py` must save same `PARAM_STR` chars on commit; `menuHelp.Execute Count(*) ... where` checks ensure hierarchy auto-insert (module→group→item rows) — Python already handles insert in `userpermission` flows.

**Enviro** table: VB6 `Enviro` (via Jet `Temp.mdb`) holds `TouchScreen`, display flags; `Form_Load` `Proc_6_99_1483714` etc. configure screen density. Python `theme.DEFAULTS` hardcodes these but `core/enviro.py` should query live `Enviro` row — keep DB reads, no writes.

### 6.4 `Company` workflow vs `company.list_companies()` (frmCompany vs Python)

- VB6: `DBGrid1` shaped via `MSDataShape` shape command + `Company` table `Comp_Code` lookup, `Panelgrid`, `FrmList` ListView search helpers, `TopCtrl` search. Company Info pink frame fields `txt(3..23)` editable → `MNUSAVE` → `INSERT INTO Company` + related `MenuHelp` sync.
- Python `CompanyDialog` is **read-only selector** (3 columns: Company Name / Short Name / Current Year) populated by `company.list_companies()` which presumably runs `SELECT CompName/ShortName/CurYear FROM Company` ordered. Selection → `comp=dict{name,short,year}` passed to `MainWindow`. **Write path** (`MNUSAVE` insert) delegated to `p2.open_companymaster` / `cprof_ui.open_company_profile` via `MainSetup` — so parity is split across two places. Gap: right-mouse `For more information...` hint (red `Label22` ForeColor `&HFF&` → `#FF0000`) not wired in Python — add contextMenu on pink frame that opens `p2.open_companymaster`.

---

## 7. FIXED UI — WHAT GOOD LOOKS LIKE (target state, same control behavior, same logic)

### Desktop invariant after fixes

```
MDI MDIForm1 (WindowState 2, BackColor #FFFFAF)
 ├─ PictSubMenu 781×80 white  Align Top      -> header FixedHeight 80 Tahoma 18 #0000FF centered
 ├─ PictMainMenu 107×512 white Align Left   -> sidebar_left 107 white BG_btn #FFFFC0 outset
 ├─ PictShortCuts 211×512 black Align Left  -> QTreeView black white on #000000 below sidebar_left
 │     └─ mnuGrid 208×158 white              -> QTableWidget below tree
 ├─ PictTitleBar 120×512 white Align Right  -> right_sidebar 120 white docked, 6 BtnEnh 125×45 + ImgLogo
 └─ MdiClient #FFFFAF (Hotel.bmp tiled)
     └─ sbar 781×24 #d4d0c8 4 panels MS Sans Serif 8.25 inset
```

Python with minimal modern keep (acceptable compromise): keep teal `#2b8c9d→#0d4f60` sidebar (product decision) but add `QTreeView` black band `40%` height above buttons — documents that VB6 had hierarchy, teal is intentional theming via `theme.sidebar_*` tokens (Appearance dialog can switch to `VB6 Classic` white/black if strict parity needed).

### Behavior parity checklist (must pass manual QA with `Analysis.ini` Moondata2627 live DB)

- [ ] Login: mint `#c2e0ce`, maroon labels `#800000`, white inset fields, yellow outset buttons, Enter triggers `&Accept`, Esc triggers `E&xit`, no `MaxButton`.
- [ ] Company: pink frame `#ffc0ff` green caption `#00c000`, DBGrid/QL table shows `Company Name | Short Name | Current Year` with white bg, gray grid, navy selection `#000080`; double-click same as `&Accept`.
- [ ] MDI: `LblCompany` centered Tahoma 18 shows `{Company} { Year }` (from `comp` dict) with white band 80px.
- [ ] Left: `PictShortCuts` black tree shows full `USER_module` hierarchy filtered by `SA` vs restricted `menuHelp` flag; `PictMainMenu` 107px white shows analysis.ini order; both drive `menubar_for` rebuild.
- [ ] Top menubar: `menuHelp` Opt-tree groups rendered as `Transaction/Reports/MIS` etc., disabled leaves gray, separators in `1px #808080`.
- [ ] Right: 6 clocks `qlineargradient #00a000→#006000` with per-zone `tcol`, `LblCalender` green `#00b400→#007000` date, Reload/Exit yellow/red gradients at bottom-right, logos at top/bottom.
- [ ] sbar: 24px gray `#d4d0c8`, user `👤`, property `Site: short`, `S/w Dt.:` + CAPS/NUM + Hide Left/Right + Full Screen + DB connected indicator.
- [ ] TopCtrl on every master: 30px gray, Add/Edit/Delete/Save/Cancel/Find/Print/Exit, vertical rail `System 19.5`; search `FrmList` searchbox works with `Tag/Code`.
- [ ] Keyboard: `ChkKeyboard` shows `Frame1` 50 keys if `Enviro.TouchScreen=Yes`.
- [ ] Radius remains `0` everywhere; all buttons `2px outset/inset` non-rounded.

---

## 8. VERIFICATION STEPS

```powershell
# 1. Launch with VB6 Classic preset forced (radius 0 bevel active)
$env:QT_QPA_PLATFORM="offscreen"  # for headless screenshot gate
python -m HMS_py.ui.shell         # or python main.py
# Gate: COMPARE_WORKSPACE/login_vb6_classic.png + company_vb6_classic.png exist?
ls PYTHONE/COMPARE_WORKSPACE/login_vb6_classic.png

# 2. Color spot-check (eyedropper / screenshot histogram)
#    Header bg must eyedrop #ffffff, lblTitle #0000ff, dialog bg #c2e0ce,
#    pink frame #ffc0ff, bevel buttons #ffffc0, sbar #d4d0c8, right clocks #006000

# 3. Font spot-check
#    LblCompany must report Tahoma 18 (PSS measurement ~24px cap height), labels Arial 9

# 4. Function gate: login → company → MainWindow with menuHelp leaf live?
python -c "from HMS_py.core.menu_help import menubar_for; print(menubar_for('Front Office','SA')[:2])"
# Expect: [{'name':'Operations', 'items':[...]}, ...]

# 5. DB gate (Moondata2627)
python -c "from HMS_py.core.db import query; print(query('select top 1 user_name from usermast')[0])"
# Expect: ('SA', ...)
```

---

## 9. APPENDIX — FILE:line REFERENCES

| Artifact | File:line |
|----------|-----------|
| `MDIForm1 BackColor &HAFFFFF` | `MDIForm1.frm:3` |
| `ClientWidth 11715 Height 9240` | `MDIForm1.frm:9-10` |
| `PictShortCuts BackColor &H0& black` | `MDIForm1.frm:12` |
| `TreeView1 3120×6750` | `MDIForm1.frm:26-33` |
| `mnuGrid 3120×2370` | `MDIForm1.frm:41-47` |
| `PictSubMenu BackColor &HFFFFFF` | `MDIForm1.frm:50` |
| `LblCompany Tahoma 18 ForeColor &HFF0000` | `MDIForm1.frm:74-92` |
| `PictTitleBar Align Right 1800×7680` | `MDIForm1.frm:94-108` |
| `LblTime* 1875×675` ×6 | `MDIForm1.frm:109-143` |
| `Reload/cmdExit 900×480` | `MDIForm1.frm:158-171` |
| `PictMainMenu Align Left 1605×7680` | `MDIForm1.frm:195-203` |
| `LblStatus 1605×465` | `MDIForm1.frm:225-231` |
| `sbar 11715×360 StatusBar` | `MDIForm1.frm:306-312` |
| `frmCompany BackColor &HCEE0C2 mint` | `frmCompany.frm:4` |
| `Client 15510×8715` | `frmCompany.frm:21-22` |
| `CompInfo pink &HFFC0FF 6615×4470` | `frmCompany.frm:465-482` |
| `DBGrid1 6780×900` | `frmCompany.frm:458-464` |
| `txt(0) User Name 12105,930` | `frmCompany.frm:1044-1053` |
| `txt(1) Password * MaxLength 8` | `frmCompany.frm:1054-1065` |
| `btnapplyNew 1905×645` | `frmCompany.frm:451-457` |
| `Frame1 keyboard 8370×1980` | `frmCompany.frm:42-450` |
| `Form_Load Analysis.ini → SQLNCLI/MSDataShape → usermast` | `frmCompany.frm:1582-1841` |
| `UserMast BackColor &HFFC0C0 MDIChild -1` | `UserMast.frm:4-13` |
| `Client 9870×7200` | `UserMast.frm:17-18` |
| `topCtrl1 9870×450` | `UserMast.frm:35-41` |
| `TXT(0..6) BorderStyle 0` | `UserMast.frm:22-156` |
| `UserPermission BackColor &HFFC0C0 16155×10155` | `UserPermission.frm:4-18` |
| `FGrid 5835×6660` | `UserPermission.frm:221-227` |
| `LoginDialog 390×310 _VB6_DIALOG_QSS` | `PYTHONE/ui/shell.py:289-291` |
| `_VB6_DIALOG_QSS mint #c2e0ce inset/outset` | `PYTHONE/ui/shell.py:263-279` |
| `CompanyDialog 640×470 pink #ffc0ff` | `PYTHONE/ui/shell.py:417-424` |
| `theme DEFAULTS VB6 Classic radius 0` | `PYTHONE/ui/theme.py:21-60` |
| `_glass_qss radius==0 outset/inset` | `PYTHONE/ui/theme.py:573` |
| `MainWindow header #ffffff LblCompany #0020c0` | `PYTHONE/ui/shell.py:1571-1581` |
| `sidebar 150px teal #2b8c9d→#0d4f60` | `PYTHONE/ui/shell.py:1591-1651` + `theme.py:49-52` |
| `right_sidebar 150px world clocks qlineargradient #00a000` | `PYTHONE/ui/shell.py:1706-1765` |
| `sbar statusBar 11715×360 → Python sb bg #d4d0c8` | `PYTHONE/ui/shell.py:1806-1865` |

---

## 10. SUMMARY

VB6 is a **fixed-screen, MDI-docked, black TreeView + flex grid + 4-strip chrome** with **exact twip sizes, BGR colors, outset/inset bevels, MDI children, and TopCtrl toolbars**. Python correctly captures the **palette (`#c2e0ce`, `#ffc0ff`, `#ffffc0`, `#d4d0c8`), inset/outset on dialogs (radius 0), and data wiring (`Analysis.ini` key 9 → `User_Module flag=9` → `menuHelp` Opt-tree → menubar)** but diverges where the chrome was modernized (teal gradient sidebar 150px vs white 107 + black 211, floating right vs docked 120, auto-height header vs 80px, Segoe UI vs Tahoma/MS Sans Serif, no MDI area, no TopCtrl on masters, no black hierarchy tree). **12 Missing Bugs (B1–B12)** above and **6 code patches (P5.1–P5.6)** make Python **pixel-identical where required** while preserving `radius=0` VB6 Classic bevel and zero DB changes. The recommended path is to apply P5.1–P5.3 immediately (trivial) and gate B1/B3/B9/B8 via `MainWindow` + `theme` + `sidebar_buttons` edits; the rest can be scheduled as `MDI parity sprint` with `QMdiArea` + `QTreeView` reintroduction.

> **Report path (write-target):** `C:\Users\PC\Desktop\New folder (3)\MODULE_FIX_PLANS\FODER\PYTHONE\COMPARE_WORKSPACE\UI_LOGIN_MDI_COMPARE.md` — this file.
