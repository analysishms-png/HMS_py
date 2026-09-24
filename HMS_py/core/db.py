"""HMS_py core: config + database layer.
Config source: same Analysis.ini jo VB6 HMS padhta hai (section [HMS]).
  keys: 1=Server, 6=Database, 2=Reports path, 3=Temp path...
Rules: sirf parameterized queries; schema me ZERO change.
"""
import configparser
import os

import pyodbc

DEFAULT_CONFIG = {
    "server": "Localhost",
    # Live Analysis.ini (HMS_py/Analysis.ini) = Moondata2627 (KY 2026-27).
    # Fallback only — load_config() Analysis.ini key 6 padhta hai.
    "database": "Moondata2627",
    "reports": r"C:\Drive\HMS2526\Reports",
    "temp": r"C:\Drive\HMS2526\Temp",
    "company": "KK",
    "site": "Kanpur",
    "modules": None,
}


def _candidate_ini_paths() -> list[str]:
    """Return the search order for Analysis.ini, preferring the project-local file."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    candidates = []
    env_path = os.environ.get("HMS_ANALYSIS_INI")
    if env_path:
        candidates.append(env_path)
    candidates.extend([
        os.path.join(project_root, "Analysis.ini"),
        os.path.join(os.getcwd(), "Analysis.ini"),
        r"C:\Drive\HMS2526\Analysis.ini",
        os.path.join(project_root, "HMS_py", "Analysis.ini"),
    ])
    seen = set()
    ordered = []
    for p in candidates:
        norm = os.path.normpath(p)
        if norm and norm not in seen:
            ordered.append(norm)
            seen.add(norm)
    return ordered


def find_analysis_ini() -> str | None:
    """Locate the Analysis.ini used by VB6/HMS, preferring the repo-local copy."""
    for path in _candidate_ini_paths():
        if os.path.isfile(path):
            return path
    return None


def load_config(ini_path: str | None = None) -> dict:
    """Analysis.ini -> {server, database, reports, temp} (VB6 jaisa)."""
    ini_path = ini_path or find_analysis_ini() or os.environ.get("HMS_ANALYSIS_INI") or r"C:\Drive\HMS2526\Analysis.ini"
    cp = configparser.ConfigParser()
    read = cp.read(ini_path, encoding="latin-1")
    if not read or not cp.has_section("HMS"):
        # fallback: VB6 jaisa default, but prefer local project config when present
        return dict(DEFAULT_CONFIG)
    hms = cp["HMS"]
    # VB6 numbered keys (evidence: Analysis.ini decoded):
    #   1=server, 2=reports path, 3=temp path, 6=database,
    #   7=company code (KK), 8=site (Kanpur), 9=sidebar modules (#-list)
    def g(i):
        return hms.get(str(i), "").strip()
    modules = [m.strip() for m in g(9).split("#") if m.strip()]
    return {"server": g(1) or DEFAULT_CONFIG["server"],
            "database": g(6) or DEFAULT_CONFIG["database"],
            "reports": g(2) or DEFAULT_CONFIG["reports"],
            "temp": g(3) or DEFAULT_CONFIG["temp"],
            "printer": g(4) or "Prn",
            "company": g(7) or DEFAULT_CONFIG["company"],
            "site": g(8) or DEFAULT_CONFIG["site"],
            "modules": modules or None}


CONN_STR = None


def _project_ini_path() -> str:
    """Package-local Analysis.ini (repo-local config priority)."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(project_root, "Analysis.ini")


def save_config(server: str | None = None, database: str | None = None,
                ini_path: str | None = None) -> str:
    """[HMS] keys update + Analysis.ini save (1=server, 6=database).

    Pehle existing ini write hota hai (find_analysis_ini priority);
    koi ini nahi to package-local file create hoti hai.
    Returns: written ini path."""
    ini_path = ini_path or find_analysis_ini() or _project_ini_path()
    cp = configparser.ConfigParser()
    cp.read(ini_path, encoding="latin-1")
    if not cp.has_section("HMS"):
        cp.add_section("HMS")
    if server is not None:
        cp.set("HMS", "1", str(server).strip())
    if database is not None:
        cp.set("HMS", "6", str(database).strip())
    with open(ini_path, "w", encoding="latin-1") as f:
        cp.write(f)
    return ini_path


def ensure_paths(cfg: dict | None = None) -> dict:
    """Analysis.ini keys 2/3 (reports/temp) folders create-if-missing.

    VB6 evidence: report export/PDF + Temp.Mdb in these paths (live:
    C:\\Drive\\HMS2526\\Reports + \\Temp, and package-local Reports/Temp).
    Best-effort: permission errors swallowed (production path may be
    read-only) - startup must not fail because of a folder.
    """
    cfg = cfg or load_config()
    made = {"reports": False, "temp": False}
    for key in ("reports", "temp"):
        p = cfg.get(key)
        if p and not os.path.isdir(p):
            try:
                os.makedirs(p, exist_ok=True)
                made[key] = True
            except OSError:
                pass
    return made


def connect(cfg: dict | None = None) -> pyodbc.Connection:
    """Same DB jisme VB6 HMS.exe judta hai (trusted connection).
    Driver: SQL Server Native Client 10.0 (VB6 wahi use karta hai -
    varchar codepage differences se bachne ke liye; fallback SQL Server)."""
    global CONN_STR
    cfg = cfg or load_config()
    for drv in ("SQL Server Native Client 10.0", "SQL Server"):
        try:
            CONN_STR = (f"DRIVER={{{drv}}};SERVER={cfg['server']};"
                        f"DATABASE={cfg['database']};"
                        f"Trusted_Connection=yes;")
            cn = pyodbc.connect(CONN_STR, timeout=5)
            # B017 fix: dead-process orphan transactions DB ko block kar
            # rahe the (GodownMast LCK). Query timeout + lock-timeout se
            # kabhi bhi hamesha-ke-liye block nahi honge.
            cn.timeout = 30
            try:
                cur = cn.cursor()
                cur.execute("SET LOCK_TIMEOUT 5000")
                cur.close()
            except pyodbc.Error:
                pass
            return cn
        except pyodbc.Error:
            continue
    raise RuntimeError("Koi SQL Server ODBC driver nahi mila")


_SAFE_IDENTIFIER_RE = None


def _validate_identifier(name: str, kind: str = "identifier") -> str:
    """Reject SQL injection in table/column names. Only allow [a-zA-Z0-9_]."""
    import re
    global _SAFE_IDENTIFIER_RE
    if _SAFE_IDENTIFIER_RE is None:
        _SAFE_IDENTIFIER_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
    if not _SAFE_IDENTIFIER_RE.match(name):
        raise ValueError(f"Invalid {kind}: '{name}' — only alphanumeric/underscore allowed")
    return name


def require_absent(table: str, pk_col: str, pk_val, label: str = "Code",
                   cn: pyodbc.Connection | None = None) -> None:
    """Duplicate-code guard (VB6 CompMast.frm:3830 'A/c Code Already
    Exists'). Raises before INSERT when the PK already exists."""
    _validate_identifier(table, "table")
    _validate_identifier(pk_col, "column")
    rows = query(
        f"SELECT 1 FROM [{table}] WHERE RTRIM([{pk_col}]) = ?",
        (str(pk_val).strip(),), cn=cn)
    if rows:
        raise ValueError(f"{label} '{pk_val}' Already Exists")


def query(sql: str, params=(), cn: pyodbc.Connection | None = None):
    """SELECT -> list[pyodbc.Row]. Apna cursor band karta hai."""
    own = cn is None
    cn = cn or connect()
    try:
        cur = cn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        return rows
    finally:
        if own:
            cn.close()


def execute(sql: str, params=(), cn: pyodbc.Connection | None = None,
            commit: bool = True) -> int:
    """INSERT/UPDATE/DELETE -> rows affected.
    commit=False: transaction khula rehta hai (test/rollback ke liye) —
    PAR apna (cn=None) connection pass karo to rollback ho jayega close
    se pehle (B017: orphan transaction se DB-wide lock bleed nahi hogi).
    Rollback-pattern ke liye apna cn bana ke pass karo."""
    own = cn is None
    cn = cn or connect()
    try:
        cur = cn.cursor()
        cur.execute(sql, params)
        n = cur.rowcount
        if commit:
            cn.commit()
        return n
    finally:
        if own:
            try:
                cn.rollback()
            except pyodbc.Error:
                pass
            cn.close()


# ============================================================
# BUG-014 fix: central site/user/year context (enviro/ini-driven)
# ============================================================

def get_site_code(cfg: dict | None = None) -> str:
    """Site code (2 char) - Analysis.ini key 7 (company), env override HMS_SITE_CODE.

    83 core modules me hardcoded SITE_CODE="KK" tha; ab yahan se aata hai.
    VB6 HMS.bas bhi Analysis.ini key 7 padhta hai (live-verified).
    """
    env = os.environ.get("HMS_SITE_CODE", "").strip()
    if env:
        return env[:2].upper()
    cfg = cfg or load_config()
    return (cfg.get("company") or "KK")[:2].upper()


def get_user() -> str:
    """Current user for audit columns - env override HMS_USER, default PYADMIN.

    VB6 UserMast login ke baad global User$ set karta tha; CLI/headless runs
    me PYADMIN (test/audit identity) fallback hai.
    """
    env = os.environ.get("HMS_USER", "").strip()
    return env[:10].upper() if env else "PYADMIN"


def get_comp_code(cfg: dict | None = None) -> str:
    """menuHelp CompCode - Analysis.ini key 7 (company), env HMS_COMP_CODE.

    menuHelp/menuHelp1 PK ka part; default '2' (live DB evidence).
    """
    env = os.environ.get("HMS_COMP_CODE", "").strip()
    if env:
        return env
    cfg = cfg or load_config()
    # Company code 'KK' nahi - CompCode numeric string chahiye ('2').
    # Analysis.ini me alag key nahi; live DB default '2'.
    return "2"


def get_vprefix(cfg: dict | None = None) -> str:
    """Current financial year prefix (e.g. '2026') - env HMS_VPREFIX override.

    VB6 Enviro table me Year field hota hai; ini se FY nikaal sakte to wo,
    warna hardcode-free fallback: current calendar year (jab tak live Enviro
    schema-verified read add na ho).
    """
    env = os.environ.get("HMS_VPREFIX", "").strip()
    if env:
        return env[:4]
    import datetime
    return str(datetime.date.today().year)


def get_logsite(cfg: dict | None = None) -> str:
    """Login site (LOGSITE_CODE) — env HMS_LOGSITE, fallback Analysis.ini site/company.

    VB6: login ke baad MemVar LogSite (LoginSite, e.g. 'RR'/'SS'/'KK').
    Masters: (LOGSITE_CODE='cur' OR 'HO'), Transactions: LogSite_Code='cur' strict.
    Default env HMS_LOGSITE > HMS_SITE_CODE > ini company/site.
    """
    env = os.environ.get("HMS_LOGSITE", "").strip()
    if env:
        return env[:2].upper()
    # HMS_SITE_CODE legacy env (LogSite ke roop me use hota tha)
    env2 = os.environ.get("HMS_SITE_CODE", "").strip()
    if env2:
        return env2[:2].upper()
    cfg = cfg or load_config()
    # Analysis.ini key 8=site name ('Kanpur'), key 7=company ('KK') — use site first letter fallback
    site_name = (cfg.get("site") or "").strip()
    if site_name and len(site_name) >= 2:
        # Site names like 'Kanpur' -> not 2-char code; prefer company code as site code
        pass
    return (cfg.get("company") or "KK")[:2].upper()


def get_context(cn=None) -> dict:
    """{site, user, vprefix} ek hi call me - naye code isse use kare.

    Modules apne module-level SITE_CODE/USER constants ko is function se
    replace karte hain (BUG-014): site/company Analysis.ini-driven ho gaya.
    """
    return {
        "site": get_site_code(),
        "logsite": get_logsite(),
        "user": get_user(),
        "vprefix": get_vprefix(),
    }


# ============================================================
# P0 helpers: DateLock / menuHelp / Voucher_Prefix (VB6-verbatim, no schema change)
# ============================================================

def check_datelock(name: str, vdate, cn=None, logsite: str | None = None) -> None:
    """VB6 DateLock guard: block posting if VDate inside a locked period (flag=1).

    VB6 SQL: SELECT Name,Srno,IsNull(SDate,''),IsNull(EDate,'') FROM DateLock
             WHERE Name='<EntryName>'  and python guard:
             SELECT TOP 1 flag FROM DATELOCK WHERE SDate<=? AND EDate>=? AND flag=1
    Raises ValueError with VB6 wording if locked. No-op if table missing.
    """
    if not name or vdate is None:
        return
    try:
        rows = query(
            "SELECT TOP 1 flag FROM DATELOCK WHERE SDate <= ? AND EDate >= ? AND flag = 1",
            (vdate, vdate), cn=cn)
    except Exception:
        return  # table absent or other — do not block
    if rows and rows[0][0] is not None and int(rows[0][0] or 0) == 1:
        raise ValueError(f"Date locked for '{name}' — posting not allowed on {vdate}")

    # VB6 name-specific window check (SDate/EDate per entry type)
    try:
        rows2 = query(
            "SELECT TOP 1 SDate, EDate FROM DateLock WHERE Name = ? AND flag = 1 AND SDate <= ? AND EDate >= ?",
            (name, vdate, vdate), cn=cn)
        if rows2:
            raise ValueError(f"Date locked for '{name}' — posting not allowed on {vdate}")
    except ValueError:
        raise
    except Exception:
        pass


def check_menuhelp(option: str, cn=None, user: str | None = None, compcode: str | None = None) -> None:
    """VB6 menuHelp gating: SELECT Param_Str FROM menuHelp WHERE [Option]=? and user/comp.

    Raises PermissionError if no row — caller should block Insert before any write.
    No-op if table missing or option empty (schema-compat).
    """
    if not option:
        return
    user = (user or get_user()).strip()
    compcode = (compcode or get_comp_code()).strip()
    try:
        rows = query(
            "SELECT Param_Str FROM menuHelp WHERE [Option] = ? AND UserName = ? AND CompCode = ?",
            (option, user, compcode), cn=cn)
    except Exception:
        return
    if not rows:
        # Fallback: try without CompCode (some DBs have CompCode='' )
        try:
            rows2 = query(
                "SELECT Param_Str FROM menuHelp WHERE [Option] = ? AND UserName = ?",
                (option, user), cn=cn)
            if rows2:
                return
        except Exception:
            pass
        raise PermissionError(f"Access denied for '{option}' — menuHelp entry missing for user '{user}'")


def get_voucher_prefix(vtype: str, vdate, cn=None, logsite: str | None = None, site: str | None = None) -> tuple[str, int, str]:
    """VB6 canonical Voucher_Prefix lookup (no schema change).

    SQL: SELECT VT.Number_Method,VP.V_Type,VP.Date_From,VP.Prefix,VP.Start_Srl_No
         FROM Voucher_Type VT INNER JOIN Voucher_Prefix VP
           ON (VT.V_Type=VP.V_Type AND VT.SITE_CODE=VP.SITE_CODE AND VP.LOGSITE_CODE=VP.LOGSITE_CODE)
         WHERE (VP.SITE_CODE=? AND VP.LOGSITE_CODE=? AND VP.V_Type=? AND ? BETWEEN VP.Date_From AND VP.Date_To)
    Returns (prefix, start_no, number_method) or fallback (str(year),1,'Auto').
    """
    if not vtype or vdate is None:
        return (get_vprefix()[:4], 1, "Auto")
    logsite = (logsite or get_logsite())[:2].upper()
    site = (site or get_site_code())[:2].upper()
    try:
        rows = query(
            "SELECT VP.Prefix, VP.Start_Srl_No, VT.Number_Method "
            "FROM Voucher_Prefix VP INNER JOIN Voucher_Type VT "
            " ON VT.V_Type = VP.V_Type AND VT.SITE_CODE = VP.SITE_CODE AND VP.LOGSITE_CODE = VP.LOGSITE_CODE "
            "WHERE VP.V_Type = ? AND VP.SITE_CODE = ? AND VP.LOGSITE_CODE = ? AND ? BETWEEN VP.Date_From AND VP.Date_To",
            (vtype, site, logsite, vdate), cn=cn)
        if rows and rows[0][0] is not None:
            prefix = str(rows[0][0] or "").strip() or str(vdate.year) if hasattr(vdate, 'year') else get_vprefix()
            start_no = int(rows[0][1] or 1)
            method = str(rows[0][2] or "Auto").strip() or "Auto"
            return (prefix[:4], start_no, method)
    except Exception:
        pass
    # Fallback: year based
    y = str(getattr(vdate, 'year', get_vprefix()))[:4]
    return (y, 1, "Auto")


# ============================================================
# BUG-015 fix: race-safe next document number (UPDLOCK/HOLDLOCK)
# ============================================================

def next_vno(table: str, vtype: str, vprefix: str, site: str | None = None,
            vtype_col: str = "Vtype", cn: pyodbc.Connection | None = None,
            commit: bool = False, vdate=None, logsite: str | None = None) -> int:
    """Race-safe MAX(VNo)+1 with VB6 Voucher_Prefix window + LogSite_Code (P0 #3).

    VB6 canonical: SELECT VP.Prefix,VP.Start_Srl_No FROM Voucher_Prefix+Voucher_Type
      WHERE VP.V_Type=? AND SITE_CODE=? AND LOGSITE_CODE=? AND ? BETWEEN Date_From AND Date_To
    Then: SELECT MAX(VNo) FROM [table] WITH (UPDLOCK,HOLDLOCK)
          WHERE [Vtype]=? AND Vprefix=? AND Site_Code=? AND LogSite_Code=?  -> max(..., Start_Srl_No)

    Keeps backward compat: if vdate is None, uses passed vprefix as-is but still filters
    on LogSite_Code (no DB change — column already exists in moondata.sql).
    """
    from HMS_py.core.db import _validate_identifier
    _validate_identifier(table, "table")
    _validate_identifier(vtype_col, "column")
    site = (site or get_site_code())[:2].upper()
    logsite = (logsite or get_logsite())[:2].upper()
    # Resolve prefix/start via Voucher_Prefix when vdate supplied (VB6 window)
    start_no = 1
    effective_prefix = vprefix
    if vdate is not None:
        try:
            eff_pref, s_no, _method = get_voucher_prefix(vtype, vdate, cn=cn, logsite=logsite, site=site)
            effective_prefix = eff_pref
            start_no = s_no
        except Exception:
            pass
    else:
        # No vdate — try to honor Start_Srl_No from Voucher_Prefix for current vprefix if available
        try:
            # Lookup by prefix equality if window not date-based fallback
            rows = query(
                "SELECT TOP 1 VP.Start_Srl_No FROM Voucher_Prefix VP WHERE VP.V_Type=? AND VP.SITE_CODE=? AND VP.LOGSITE_CODE=? AND VP.Prefix=?",
                (vtype, site, logsite, vprefix), cn=cn)
            if rows and rows[0][0] is not None:
                start_no = int(rows[0][0] or 1)
        except Exception:
            pass
    own = cn is None
    cn = cn or connect()
    try:
        cur = cn.cursor()
        # VB6 verbatim: Site_Code + LogSite_Code + Vprefix window, UPDLOCK/HOLDLOCK
        cur.execute(
            f"SELECT MAX(VNo) FROM [{table}] WITH (UPDLOCK, HOLDLOCK) "
            f"WHERE [{vtype_col}] = ? AND Vprefix = ? AND Site_Code = ? AND LogSite_Code = ?",
            (vtype, effective_prefix, site, logsite))
        row = cur.fetchone()
        vno = int(row[0] or 0) + 1 if row and row[0] is not None else 1
        if vno < start_no:
            vno = start_no
        if commit:
            cn.commit()
        return vno
    finally:
        if own:
            try:
                cn.rollback()
            except pyodbc.Error:
                pass
            cn.close()


def vb6_next_vno(table: str, vtype: str, vdate, cn=None, logsite: str | None = None, site: str | None = None) -> tuple[int, str]:
    """VB6 next_vno that also returns effective Vprefix (prefix window)."""
    eff_pref, start_no, _ = get_voucher_prefix(vtype, vdate, cn=cn, logsite=logsite, site=site)
    vtype_col = "Vtype" if table in ("Stock", "KClStk") else ("VType" if table in ("Purch1", "POrder", "GIN", "Indent") else "Vtype")
    vno = next_vno(table, vtype, eff_pref, site=site, vtype_col=vtype_col, cn=cn, vdate=vdate, logsite=logsite)
    return vno, eff_pref
