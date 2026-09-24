"""Authentication - ORIGINAL VB6 HMS logic ka exact port.

EVIDENCE (decompiled UserMast.frm):
1. Encrypt (Proc_153_30_EEFAD0):
     seed = Int(Rnd * 99) + 1                ' 1..99
     stored = Chr(seed + 27)                 ' pehla char seed carrier
     for each ch: stored &= Chr(Asc(ch) + 27 + seed)
2. Decrypt (Proc_153_31_EFEE54):
     seed = Asc(first_char) - 27
     for ch in rest: plain &= Chr(Asc(ch) - 27 - seed)
3. Login comparison: UCase(Trim(typed)) = UCase(Trim(stored_decrypted))
   (frmPassword.frm: Ucase(Trim(...)) pattern)
4. User table: UserMast (USER_NAME, PASSWD encrypted, LABEL, ShortName,
   ActiveYN 'Y'/'N'). SA default password '\' (frmCompany.frm line 2415).

SECURITY: VB6-compatible reversible encryption retained for DB compat.
Brute-force protection added (max 5 attempts per 15 min per user).
"""
from __future__ import annotations

import json
import os
import random
import tempfile
import time
from collections import defaultdict

SHIFT = 0x1B   # 27 - VB6 &H1B

# Brute-force protection: {username: [(timestamp, success), ...]}
_login_attempts: dict[str, list[tuple[float, bool]]] = defaultdict(list)
_MAX_ATTEMPTS = 5
_LOCKOUT_SECONDS = 900  # 15 minutes
# BUG-LOCKOUT-NOT-PERSISTENT: restart pe lockout na gire — temp file me
# attempts persist karo (process restart safe; multi-user same machine OK).
_LOCKOUT_PATH = os.path.join(
    tempfile.gettempdir(), "hms_py_login_attempts.json")


def _load_attempts() -> None:
    """Best-effort load of persisted attempts (ignore corrupt file)."""
    try:
        if not os.path.isfile(_LOCKOUT_PATH):
            return
        with open(_LOCKOUT_PATH, encoding="utf-8") as f:
            raw = json.load(f)
        now = time.time()
        for user, items in (raw or {}).items():
            kept = [(float(t), bool(s)) for t, s in items
                    if now - float(t) < _LOCKOUT_SECONDS]
            if kept:
                _login_attempts[user] = kept
    except Exception:
        pass


def _save_attempts() -> None:
    """Best-effort persist (never raise into login path)."""
    try:
        now = time.time()
        out = {u: [[t, s] for t, s in items if now - t < _LOCKOUT_SECONDS]
               for u, items in _login_attempts.items()}
        out = {u: items for u, items in out.items() if items}
        tmp = _LOCKOUT_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(out, f)
        os.replace(tmp, _LOCKOUT_PATH)
    except Exception:
        pass


_load_attempts()


def _is_locked_out(username: str) -> bool:
    """Check if user has exceeded max failed attempts in lockout window."""
    _load_attempts()  # aur process (restart) se aaye attempts bhi dekho
    now = time.time()
    attempts = _login_attempts[username]
    # Prune old attempts
    _login_attempts[username] = [
        (t, s) for t, s in attempts if now - t < _LOCKOUT_SECONDS
    ]
    failed = sum(1 for _, s in _login_attempts[username] if not s)
    return failed >= _MAX_ATTEMPTS


def _record_attempt(username: str, success: bool):
    """Record a login attempt."""
    _login_attempts[username].append((time.time(), success))
    if success:
        # Clear failed attempts on successful login
        _login_attempts[username] = [
            (t, s) for t, s in _login_attempts[username] if s
        ]
    _save_attempts()


def encrypt(plain: str, seed: int | None = None) -> str:
    """VB6 Proc_153_30_EEFAD0 ka port."""
    if seed is None:
        seed = random.randint(1, 99)
    out = chr(seed + SHIFT)
    for ch in plain:
        out += chr(ord(ch) + SHIFT + seed)
    return out


def decrypt(stored: str) -> str:
    """VB6 Proc_153_31_EFEE54 ka port."""
    if not stored:
        return ""
    seed = ord(stored[0]) - SHIFT
    out = ""
    for i in range(1, len(stored)):
        out += chr(ord(stored[i]) - SHIFT - seed)
    return out


def enc_bytes(plain: str, seed: int | None = None) -> bytes:
    """encrypt() ka byte-exact form — UserMast.PASSWD writes ke liye.

    VB6 char-math (ord(ch)+SHIFT+seed) se chars >127 ban sakte hain;
    SQL varchar param me wo Native Client codepage conversion se
    lossy ho jaate hain (e.g. 'e'->'?' 0x3F) aur decrypt toot jaata hai
    (E2E 2026-09-23: seed 95 pe 'e2etest123' corrupt hua). Pyodbc ko
    latin-1 bytes bind karne se VB6 ke ANSI bytes byte-exact store hote
    hain; _stored_passwd() CAST(varbinary) side already byte-exact hai.
    """
    return encrypt(plain, seed=seed).encode("latin-1")


def _stored_passwd(username: str, cn=None) -> str | None:
    """PASSWD raw bytes (latin-1) - driver-agnostic.

    BUGFIX (P0): pichhla SELECT list-driver pe PASSWD ko unicode-expand
    kar deta tha (Native Client 10: varchar 'A' -> 'A\x00'). CAST se
    raw bytes milte hain (VB6 ke jo ansi bytes hain wahi).
    Evidence: SA raw=3c877d8a8c918e -> decrypt 'KANPUR' (seed=33).
    """
    from HMS_py.core import db
    rows = db.query(
        "SELECT CAST(PASSWD AS varbinary(max)) FROM UserMast "
        "WHERE USER_NAME = ?", (username,), cn=cn)
    if not rows or rows[0][0] is None:
        return None
    b = rows[0][0]
    return b.decode("latin-1") if isinstance(b, (bytes, bytearray)) else str(b)


def check_login(username: str, password: str, cn=None) -> tuple[bool, str]:
    """frmPassword/frmCompany ka login pattern:
    UCase(Trim(typed)) vs decrypted stored (bhi UCase/Trim).
    Returns (ok, message).
    SECURITY: brute-force protection (5 attempts / 15 min)."""
    from HMS_py.core import db
    username = (username or "").strip()
    if _is_locked_out(username):
        remaining = int(_LOCKOUT_SECONDS - (time.time() - _login_attempts[username][0][0]))
        return False, f"Account locked. Try again in {max(60, remaining)}s"
    rows = db.query(
        "SELECT ActiveYN, LABEL, ShortName FROM UserMast "
        "WHERE USER_NAME = ?", (username,), cn=cn)
    if not rows:
        _record_attempt(username, False)
        return False, "Invalid User Name"
    row = rows[0]
    # SELECT order: ActiveYN, LABEL, ShortName
    active, _label, short = row[0], row[1], row[2]
    if (active or "Y").upper() != "Y":
        return False, "User is INACTIVE - admin se contact karein"
    stored = _stored_passwd(username, cn=cn)
    real = decrypt(stored) if stored else ""
    typed = (password or "").strip()
    if typed.upper() == real.upper():
        _record_attempt(username, True)
        return True, f"Welcome {short or username}"
    _record_attempt(username, False)
    attempts_left = _MAX_ATTEMPTS - sum(1 for _, s in _login_attempts[username] if not s)
    if attempts_left <= 2:
        return False, f"Invalid Password ({attempts_left} attempts left)"
    return False, "Invalid Password"


if __name__ == "__main__":
    # self-test: encrypt->decrypt roundtrip + SA check
    for pwd in ("India12", "SApass1", "x"):
        e = encrypt(pwd, seed=42)
        d = decrypt(e)
        assert d == pwd, f"roundtrip fail {pwd!r} -> {d!r}"
    print("roundtrip OK: encrypt/decrypt VB6-compatible")
    ok, msg = check_login("SA", "")
    print(f"SA login (empty pass - DB me stored '.' = ''): {ok} - {msg}")
    ok2, msg2 = check_login("SA", "wrongpass")
    print(f"SA wrong pass: {ok2} - {msg2}")
    ok3, msg3 = check_login("PANKAJ", "1234")
    print(f"PANKAJ/1234 (decoded from DB): {ok3} - {msg3}")
    ok4, msg4 = check_login("PANKAJ", "9999")
    print(f"PANKAJ wrong: {ok4} - {msg4}")
    ok5, msg5 = check_login("AKHILESH", "x")
    print(f"AKHILESH (inactive): {ok5} - {msg5}")
