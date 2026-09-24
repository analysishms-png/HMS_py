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


def get_logsite_code(cn=None) -> str:
    """VB6 LogSite_Code (MemVar_1F92078) - Enviro.LOGSITE_CODE se, fallback Analysis.ini SITE_CODE.

    VB6 har POS read me `(LOGSITE_CODE='<LOGSITE>' OR LOGSITE_CODE='HO')`
    karta hai; insert me Site_Code=LOGSITE, LogSite_Code=LOGSITE.
    Enviro init nahi hua ho to Analysis.ini company code fallback hai.
    """
    try:
        rows = query("SELECT TOP 1 LOGSITE_CODE FROM Enviro WHERE LOGSITE_CODE IS NOT NULL AND LOGSITE_CODE <> ''", cn=cn)
        if rows and rows[0][0]:
            v = str(rows[0][0]).strip()
            if v and v.upper() != "HO":
                return v[:10].upper()
            if v:
                return v[:10].upper()
        # second attempt: Site_Code column fallback
        rows2 = query("SELECT TOP 1 Site_Code FROM Enviro WHERE Site_Code IS NOT NULL AND Site_Code <> ''", cn=cn)
        if rows2 and rows2[0][0]:
            return str(rows2[0][0]).strip()[:10].upper()
    except Exception:
        pass
    return get_site_code()


# Backward-compatible alias: inventory.py `db.get_logsite()` call karta hai.
get_logsite = get_logsite_code


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


def get_context(cn=None) -> dict:
    """{site, user, vprefix} ek hi call me - naye code isse use kare.

    Modules apne module-level SITE_CODE/USER constants ko is function se
    replace karte hain (BUG-014): site/company Analysis.ini-driven ho gaya.
    """
    return {
        "site": get_site_code(),
        "user": get_user(),
        "vprefix": get_vprefix(),
    }


# ============================================================
# BUG-015 fix: race-safe next document number (UPDLOCK/HOLDLOCK)
# ============================================================

def next_vno(table: str, vtype: str, vprefix: str, site: str | None = None,
            vtype_col: str = "Vtype", cn: pyodbc.Connection | None = None,
            commit: bool = False) -> int:
    """Race-safe MAX(VNo)+1 for serial voucher numbering.

    BUG-015: plain 'SELECT MAX(VNo)' + INSERT me do concurrent users ko
    same VNo mil sakta tha (VB6 me bhi same pattern - live data me
    duplicate DocId risk). Fix: UPDLOCK+HOLDLOCK range lock until
    transaction end; caller INSERT usi connection/cn pe karta hai
    (commit=True tab jab caller khud commit nahi karega).

    Args:
        table/vtype_col: validated identifiers (SQL injection guard)
        vtype: voucher type filter ('RC', 'EXP', 'MRE', ...)
        vprefix: year prefix ('2026')
        site: site code (default get_site_code())
        cn: apna connection - transaction atomicity ke liye ZAROORI
            (default connection par lock commit ke sahi release na ho)
        commit: True => commit immediately (caller INSERT se pehle
            number reserve karna chahta hai).
    Returns: next VNo (int)
    """
    from HMS_py.core.db import _validate_identifier
    _validate_identifier(table, "table")
    _validate_identifier(vtype_col, "column")
    site = site or get_site_code()
    own = cn is None
    cn = cn or connect()
    try:
        cur = cn.cursor()
        # UPDLOCK: update-intent lock; HOLDLOCK: transaction end tak hold.
        # Range lock MAX(...) pe serial block karta hai - do users ko
        # same number nahi milega.
        cur.execute(
            f"SELECT MAX(VNo) FROM [{table}] WITH (UPDLOCK, HOLDLOCK) "
            f"WHERE [{vtype_col}] = ? AND Vprefix = ? AND Site_Code = ?",
            (vtype, vprefix, site))
        row = cur.fetchone()
        vno = int(row[0] or 0) + 1 if row else 1
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
