"""Guest Profile master CRUD (VB6: Guest Profile - Front Office).

Schema evidence (live): GuestProf 67 cols, 7215 rows.
Core cols (VB6 sample 'KK000002/SUBHASH SINHA' se):
  Code varchar(8) PK, Name varchar(50), Add1 varchar(50), Add2 varchar(50),
  City varchar(6) FK, Type varchar(7) (India/Foreign), CreditCardNo(25),
  CreditLimit float, PhoneNo varchar(35), FaxNo varchar(24),
  MobileNo varchar(24), EmailId varchar(50), Nationality varchar(6).
Audit cols end me: Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code.
Audit pattern VB6 jaisa: U_Name + U_EntDt(getdate()) + U_AE ('A'/'E').
Code pattern live: 'KK' + 6 digits (KK000002...).
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
LIMITS = {"code": 8, "name": 50, "add1": 50, "add2": 50, "city": 6,
          "type": 7, "phone": 35, "mobile": 24, "email": 50,
          "nationality": 6}
SELECT_COLS = ("Code, Name, Add1, Add2, City, Type, PhoneNo, MobileNo, "
               "EmailId, Nationality, U_Name, U_EntDt, U_AE")


def _map(r) -> dict:
    return {"code": r.Code, "name": (r.Name or "").strip(),
            "add1": (r.Add1 or "").strip(), "add2": (r.Add2 or "").strip(),
            "city": r.City or "", "type": r.Type or "",
            "phone": (r.PhoneNo or "").strip(),
            "mobile": (r.MobileNo or "").strip(),
            "email": (r.EmailId or "").strip(),
            "nationality": r.Nationality or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}


def _validate(rec: dict, cn=None, check_duplicates: bool = True):
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if len(rec["code"]) > LIMITS["code"]:
        raise ValueError(f"Code max {LIMITS['code']} chars")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    if len(rec["name"]) > LIMITS["name"]:
        raise ValueError(f"Name max {LIMITS['name']} chars")
    for k, lim in (("add1", "add1"), ("add2", "add2"), ("city", "city"),
                   ("type", "type"), ("phone", "phone"),
                   ("mobile", "mobile"), ("email", "email"),
                   ("nationality", "nationality")):
        if len(rec.get(k, "")) > LIMITS[lim]:
            raise ValueError(f"{k} max {LIMITS[lim]} chars")
    
    # Check for duplicate mobile/phone/email (if provided and not empty)
    if check_duplicates and cn is not None:
        code = rec.get("code", "").strip()
        mobile = rec.get("mobile", "").strip()
        phone = rec.get("phone", "").strip()
        email = rec.get("email", "").strip()
        
        if mobile:
            dup = db.query(
                "SELECT Code FROM GuestProf WHERE MobileNo = ? AND Code <> ?",
                (mobile, code), cn=cn)
            if dup:
                raise ValueError(f"Mobile {mobile} already exists for guest {dup[0][0]}")
        
        if phone:
            dup = db.query(
                "SELECT Code FROM GuestProf WHERE PhoneNo = ? AND Code <> ?",
                (phone, code), cn=cn)
            if dup:
                raise ValueError(f"Phone {phone} already exists for guest {dup[0][0]}")
        
        if email:
            dup = db.query(
                "SELECT Code FROM GuestProf WHERE EmailId = ? AND Code <> ?",
                (email, code), cn=cn)
            if dup:
                raise ValueError(f"Email {email} already exists for guest {dup[0][0]}")


def list_all(cn=None, top: int = 500) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(top)} {SELECT_COLS} FROM GuestProf "
        "ORDER BY Code", cn=cn)
    return [_map(r) for r in rows]


def search(name_part: str, cn=None, top: int = 100) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(top)} {SELECT_COLS} FROM GuestProf "
        "WHERE Name LIKE ? ORDER BY Name", (f"%{name_part}%",), cn=cn)
    return [_map(r) for r in rows]


def get(code: str, cn=None) -> dict | None:
    rows = db.query(f"SELECT {SELECT_COLS} FROM GuestProf WHERE Code = ?",
                    (code,), cn=cn)
    return _map(rows[0]) if rows else None


def exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM GuestProf WHERE Code = ?", (code,),
                         cn=cn))


def next_code(cn=None) -> str:
    """VB6 pattern: 'KK' + max-numeric-suffix + 1 (live: KK000002...)."""
    rows = db.query(
        "SELECT MAX(Code) FROM GuestProf WHERE Code LIKE 'KK%' AND "
        "LEN(Code) = 8", cn=cn)
    mx = rows[0][0] if rows and rows[0][0] else "KK000000"
    return f"KK{int(mx[2:]) + 1:06d}"


def insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec, cn=cn, check_duplicates=True)
    return db.execute(
        "INSERT INTO GuestProf (Code, Name, Add1, Add2, City, Type, "
        "PhoneNo, MobileNo, EmailId, Nationality, "
        "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["code"], rec["name"], rec.get("add1", ""), rec.get("add2", ""),
         rec.get("city", ""), rec.get("type", ""), rec.get("phone", ""),
         rec.get("mobile", ""), rec.get("email", ""),
         rec.get("nationality", ""), SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def update(code: str, rec: dict, cn=None, commit: bool = True) -> int:
    _validate(rec, cn=cn, check_duplicates=True)

    # VB6 cascade (GuestProfile.frm:6863-6871): guest profile change propagates
    # to denormalized copies in GuestFolio (GuestProf/Name/city) and
    # RoomOcc (GuestProf). Same transaction, single commit at end.
    own = cn is None
    cn_use = cn or db.connect()
    try:
        n = db.execute(
            "UPDATE GuestProf SET Name = ?, Add1 = ?, Add2 = ?, City = ?, "
            "Type = ?, PhoneNo = ?, MobileNo = ?, EmailId = ?, "
            "Nationality = ?, U_Name = ?, U_EntDt = getdate(), U_AE = 'E' "
            "WHERE Code = ?",
            (rec["name"], rec.get("add1", ""), rec.get("add2", ""),
             rec.get("city", ""), rec.get("type", ""), rec.get("phone", ""),
             rec.get("mobile", ""), rec.get("email", ""),
             rec.get("nationality", ""), USER, code),
            cn=cn_use, commit=False)
        db.execute(
            "UPDATE GuestFolio SET GuestProf = ?, Name = ?, city = ?, "
            "U_EntDt = getdate() WHERE RTRIM(GuestProf) = ?",
            (code, rec["name"], rec.get("city", ""), code),
            cn=cn_use, commit=False)
        db.execute(
            "UPDATE RoomOcc SET GuestProf = ?, U_EntDt = getdate() "
            "WHERE RTRIM(GuestProf) = ?",
            (code, code), cn=cn_use, commit=False)
        if commit:
            cn_use.commit()
        return n
    except Exception:
        if own:
            try:
                cn_use.rollback()
            except Exception:
                pass
        raise
    finally:
        if own:
            cn_use.close()


def delete(code: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM GuestProf WHERE Code = ?", (code,),
                      cn=cn, commit=commit)
