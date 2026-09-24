"""Main Setup plan (02_MAIN_SETUP_FIX_PLAN.txt) ke required tests.

Run: C:/Python314/python.exe HMS_py/tests/database/test_main_setup_plan.py
Covers:
  T1 duplicate code rejection (naye guards: ItemMast/ItemGrp/FixedCharge/TelCall*)
  T2 read-only finance setting protection (enviro)
  T3 valid printer/temp/report path loading (Analysis.ini)
  T4 safe no-op for missing table
  T5 UI shell screens open without crashing (offscreen, no-rows config)
READ-ONLY: T1 sirf exists-check + live sample code reject karta hai (insert hota hi nahi).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))

from HMS_py.core import db, enviro

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(("PASS " if cond else "FAIL ") + name + (" | " + detail if detail else ""))


def main():
    # T1: duplicate-code rejection — har guarded master pe live PK sample
    dup_targets = [
        ("ItemMast", "Code", "Item Code", "HMS_py.core.item", "insert"),
        ("ItemGrp", "Code", "Item Group Code", "HMS_py.core.item", "itemgrp_insert"),
        ("FixedCharge", "Code", "Fixed Charge Code", "HMS_py.core.fixcharge", "insert"),
        ("TelCallType", "Code", "Call Type Code", "HMS_py.core.epabx_masters",
         "calltype_insert"),
        ("TelCallCode", "STDCode", "STD Code", "HMS_py.core.epabx_masters",
         "callcode_insert"),
        ("TelExt", "Code", "Extension Code", "HMS_py.core.epabx_masters",
         "telext_insert"),
    ]
    for table, pk, label, modname, fn in dup_targets:
        try:
            mod = __import__(modname, fromlist=[fn])
            f = getattr(mod, fn)
            rows = db.query(f"SELECT TOP 1 RTRIM({pk}) FROM {table} "
                            f"WHERE {pk} IS NOT NULL AND {pk} <> ''")
            if not rows:
                check(f"T1 {table} (no live rows - guard skipped)", True,
                      "table empty")
                continue
            live_code = rows[0][0]
            rec = {pk.lower(): live_code, "code": live_code,
                   "stdcode": live_code, "name": "X", "desc": "X",
                   "calltype": "X"}
            try:
                f(rec, commit=False)
                check(f"T1 {label} reject", False,
                      f"insert allowed duplicate {live_code!r}")
            except ValueError as e:
                check(f"T1 {label} reject", "Already Exists" in str(e),
                      f"code={live_code!r}: {e}")
            except Exception as e:
                check(f"T1 {label} reject", False, repr(e)[:120])
        except Exception as e:
            check(f"T1 {label}", False, repr(e)[:120])

    # T2: read-only finance setting protection
    try:
        fin = [c for c in enviro.READ_ONLY]
        check("T2 READ_ONLY non-empty", len(fin) >= 5, f"{len(fin)} cols")
        try:
            enviro.update_settings({fin[0]: "X"})
            check("T2 finance reject", False, "update allowed on READ_ONLY")
        except ValueError:
            check("T2 finance reject", True, f"{fin[0]} blocked")
        # editable setting read path (no guessing: pehli EDITABLE key hi lo)
        key0 = list(enviro.EDITABLE)[0]
        val = enviro.get_setting(key0)
        check("T2 get_setting works", True, f"{key0}={val!r}")
    except Exception as e:
        check("T2 enviro", False, repr(e)[:120])

    # T3: Analysis.ini paths
    try:
        cfg = db.load_config()
        check("T3 config keys", all(k in cfg for k in
                                    ("server", "database", "reports", "temp")),
              f"db={cfg.get('database')}")
        check("T3 paths resolve", bool(cfg.get("reports")) and
              bool(cfg.get("temp")),
              f"reports={cfg.get('reports')}")
        made = db.ensure_paths(cfg)
        check("T3 ensure_paths", set(made) == {"reports", "temp"})
        ini = db.find_analysis_ini()
        check("T3 ini found", ini is not None, str(ini))
    except Exception as e:
        check("T3 paths", False, repr(e)[:120])

    # T4: safe no-op for missing table (query raises clean, no crash)
    try:
        try:
            db.query("SELECT 1 FROM NoSuchTable_XYZ")
            check("T4 missing-table raises", False)
        except Exception as e:
            check("T4 missing-table raises", "42S02" in str(e) or
                  "Invalid object" in str(e), repr(e)[:90])
        # require_absent on missing table also raises cleanly
        try:
            db.require_absent("NoSuchTable_XYZ", "Code", "X")
            check("T4 require_absent missing-table", False)
        except Exception as e:
            check("T4 require_absent missing-table", True, repr(e)[:80])
    except Exception as e:
        check("T4", False, repr(e)[:120])

    # T5: UI screens offscreen probe (subprocess, per-screen hard timeout —
    # in-process Qt timers offscreen me return nahi karte, app bug nahi hai)
    try:
        import subprocess
        root = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))))
        probe = os.path.join(root, "tools", "_ui_probe.py")
        opens = [("pm", "open_city"), ("pm", "open_area"),
                 ("pm", "open_depart"), ("pm", "open_item"),
                 ("gs", "open_godown"), ("gs", "open_roomfeature")]
        n_open = 0
        detail = ""
        for m, fn in opens:
            try:
                p = subprocess.run(
                    [sys.executable, probe, m, fn], capture_output=True,
                    text=True, timeout=40, cwd=root)
                ok = p.returncode == 0 and "RETURNED" in (p.stdout or "")
                n_open += 1 if ok else 0
                if not ok and not detail:
                    detail = f"{fn}: rc={p.returncode} " \
                             f"{(p.stderr or '')[-100:]}"
            except subprocess.TimeoutExpired:
                if not detail:
                    detail = f"{fn}: timeout"
        check("T5 ui screens open", n_open == 6,
              f"{n_open}/6" + (f" | {detail}" if detail else ""))
    except Exception as e:
        check("T5 ui", False, repr(e)[:120])

    fails = [r for r in RESULTS if not r[1]]
    print(f"\n{len(RESULTS) - len(fails)}/{len(RESULTS)} PASS")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
