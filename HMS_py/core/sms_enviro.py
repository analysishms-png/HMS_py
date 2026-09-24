"""SMS/Email Environment & Operations (VB6: SMS/Email setup + messaging).

Tables:
- SMSEnviro: SMS settings (32 cols, single-row)
- EmailSMSForward: Email/SMS forwarding rules (13 cols)
- DBSendSMS: SMS send queue (25 cols)
- JobSchedule: Job schedule header (27 cols)
- JobScheduledDetail: Job schedule detail (17 cols)

Schema: verified from live KailashData2526 DB.
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()


# ============================================================
# SMSEnviro - SMS Settings (single-row)
# PK: LogSite_Code + Site_Code
# ============================================================
SMS_FIELDS = [
    "SmsCenterUserName", "SmsCenterPassword", "SmsDisplayName",
    "SmsURL", "SmsPurchase", "SmsSend", "SmsBal",
    "TUser", "TPassword", "TFromSend", "TMessage", "TExtra",
    "LogSite_Code", "CheckInMsg", "CheckOutMsg", "SmsPhoneNoPrefix",
    "TPhNo", "ReservationMsg", "Site_Code", "SendingMessageText",
    "ReservationCancelMsg", "OutStandingMsg", "CashReceiptMsg",
    "BankReceiptMsg", "MemberBillMsg", "BanqBookingMsg",
    "BanqBookingCancelMsg", "GuestRegistrationMsg", "RewardPointMsg",
    "RedeemPointMsg", "POSBillMsg", "AssignDeliveryMsg",
]


def _map_smsenviro(r) -> dict:
    try:
        return {k.lower(): (getattr(r, k) or "").strip()
                for k in SMS_FIELDS}
    except AttributeError:
        vals = [str(v or "").strip() if isinstance(v, str) else v
                for v in r]
        return {k.lower(): v for k, v in zip(SMS_FIELDS, vals)}


def smsenviro_get(cn=None) -> dict:
    """Read SMS settings (single-row)."""
    cols = ", ".join(SMS_FIELDS)
    rows = db.query(
        f"SELECT {cols} FROM SMSEnviro WHERE LogSite_Code = ? "
        "OR LogSite_Code = 'HO'",
        (SITE_CODE,), cn=cn)
    if not rows:
        raise ValueError("SMSEnviro row hi nahi mila")
    r = rows[0]
    if hasattr(r, "keys"):
        return {k.lower(): (r[k] or "").strip() if isinstance(r[k], str) else r[k]
                for k in r.keys()}
    return {k.lower(): v for k, v in zip(SMS_FIELDS, r)}


def smsenviro_update(changes: dict, user: str = USER, cn=None,
                     commit: bool = True) -> int:
    """Update SMS settings."""
    if not changes:
        raise ValueError("Khaali changes")
    own = cn is None
    cn = cn or db.connect()
    try:
        sets = ", ".join(f"[{k}] = ?" for k in changes)
        params = tuple(changes.values()) + (SITE_CODE,)
        n = db.execute(
            f"UPDATE SMSEnviro SET {sets} WHERE LogSite_Code = ? "
            "OR Site_Code = ?",
            params + (SITE_CODE,), cn=cn, commit=False)
        if commit:
            cn.commit()
        return n
    finally:
        if own:
            cn.close()


class _SMSEnviroAPI:
    @staticmethod
    def get(cn=None): return smsenviro_get(cn)
    @staticmethod
    def update(changes, user=USER, cn=None, commit=True):
        return smsenviro_update(changes, user, cn, commit)

SMSEnviroAPI = _SMSEnviroAPI()


# ============================================================
# EmailSMSForward - Email/SMS Forwarding Rules
# PK: Id (identity)
# ============================================================
def _map_emailforward(r) -> dict:
    try:
        return {
            "id": r.Id, "type": r.Type or "",
            "mobile_no": r.MobileNo or "", "email_id": r.EmailId or "",
            "site_code": r.Site_Code or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
            "txt_msg": r.TxtMsg or "", "flag_type": r.FlagType or "",
            "dept_code": r.DepartCode or "",
            "guest_msg": r.GuestMsg or "",
        }
    except AttributeError:
        i, t, mn, ei, site, un, _, uae, txt, ft, dp, gm = r
        return {
            "id": i, "type": t or "",
            "mobile_no": mn or "", "email_id": ei or "",
            "site_code": site or "",
            "u_name": un or "", "u_ae": uae or "",
            "txt_msg": txt or "", "flag_type": ft or "",
            "dept_code": dp or "",
            "guest_msg": gm or "",
        }


def emailforward_list(cn=None, limit: int = 500) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} Id, Type, MobileNo, EmailId, Site_Code, "
        "U_Name, U_EntDt, U_AE, LogSite_Code, TxtMsg, FlagType, "
        "DepartCode, GuestMsg "
        "FROM EmailSMSForward ORDER BY Id", cn=cn)
    return [_map_emailforward(r) for r in rows]


def emailforward_get(id: int, cn=None) -> dict | None:
    rows = db.query(
        "SELECT Id, Type, MobileNo, EmailId, Site_Code, U_Name, U_EntDt, "
        "U_AE, LogSite_Code, TxtMsg, FlagType, DepartCode, GuestMsg "
        "FROM EmailSMSForward WHERE Id = ?", (id,), cn=cn)
    return _map_emailforward(rows[0]) if rows else None


def emailforward_insert(rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "INSERT INTO EmailSMSForward (Type, MobileNo, EmailId, Site_Code, "
        "U_Name, U_EntDt, U_AE, LogSite_Code, TxtMsg, FlagType, "
        "DepartCode, GuestMsg) "
        "VALUES (?, ?, ?, ?, ?, getdate(), 'A', ?, ?, ?, ?, ?)",
        (rec.get("type", ""), rec.get("mobile_no", ""),
         rec.get("email_id", ""), SITE_CODE, USER, SITE_CODE,
         rec.get("txt_msg", ""), rec.get("flag_type", ""),
         rec.get("dept_code", ""), rec.get("guest_msg", "")),
        cn=cn, commit=commit)


def emailforward_update(id: int, rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "UPDATE EmailSMSForward SET Type = ?, MobileNo = ?, EmailId = ?, "
        "TxtMsg = ?, FlagType = ?, DepartCode = ?, GuestMsg = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Id = ?",
        (rec.get("type", ""), rec.get("mobile_no", ""),
         rec.get("email_id", ""), rec.get("txt_msg", ""),
         rec.get("flag_type", ""), rec.get("dept_code", ""),
         rec.get("guest_msg", ""), USER, id),
        cn=cn, commit=commit)


def emailforward_delete(id: int, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM EmailSMSForward WHERE Id = ?", (id,),
        cn=cn, commit=commit)


class _EmailSMSForwardAPI:
    @staticmethod
    def list_all(cn=None, limit=500): return emailforward_list(cn, limit)
    @staticmethod
    def get(id, cn=None): return emailforward_get(id, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return emailforward_insert(rec, cn, commit)
    @staticmethod
    def update(id, rec, cn=None, commit=True): return emailforward_update(id, rec, cn, commit)
    @staticmethod
    def delete(id, cn=None, commit=True): return emailforward_delete(id, cn, commit)

EmailSMSForwardAPI = _EmailSMSForwardAPI()


# ============================================================
# DBSendSMS - SMS Send Queue
# PK: DocId + SNo (composite)
# ============================================================
def _map_dbsendsms(r) -> dict:
    try:
        return {
            "docid": r.DocId or "", "vtype": r.Vtype or "",
            "vdate": r.Vdate, "vno": r.VNo or 0,
            "subcode": r.SubCode or "",
            "mobile1": r.Mobile1 or "", "mobile2": r.Mobile2 or "",
            "txt_msg": r.TxtMsg or "",
            "sms_dt": r.SMSDt, "sms_tm": r.SMSTm or "",
            "delv_dt": r.DelvDt, "delv_tm": r.DelvTm or "",
            "sender_name": (r.SenderName or "").strip(),
            "party_name": (r.PartyName or "").strip(),
            "room_no": r.RoomNo or "",
            "bill_amount": float(r.BillAmount or 0),
            "send_tf": r.SendTF or "",
            "comp_code": r.Comp_Code or "",
            "msg_type": r.MsgType or "",
            "sno": r.SNo or 0,
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        d, vt, vd, vn, sc, m1, m2, txt, sd, st, dd, dt, sn, pn, \
            uae, un, _, site, lgs, rm, ba, stf, cc, mt, sno = r
        return {
            "docid": d or "", "vtype": vt or "",
            "vdate": vd, "vno": vn or 0,
            "subcode": sc or "",
            "mobile1": m1 or "", "mobile2": m2 or "",
            "txt_msg": txt or "",
            "sms_dt": sd, "sms_tm": st or "",
            "delv_dt": dd, "delv_tm": dt or "",
            "sender_name": (sn or "").strip(),
            "party_name": (pn or "").strip(),
            "room_no": rm or "",
            "bill_amount": float(ba or 0),
            "send_tf": stf or "",
            "comp_code": cc or "",
            "msg_type": mt or "",
            "sno": sno or 0,
            "u_name": un or "", "u_ae": uae or "",
        }


def dbsendsms_list(cn=None, limit: int = 500) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} DocId, Vtype, Vdate, VNo, SubCode, "
        "Mobile1, Mobile2, TxtMsg, SMSDt, SMSTm, DelvDt, DelvTm, "
        "SenderName, PartyName, U_AE, U_Name, U_EntDt, Site_Code, "
        "LogSite_Code, RoomNo, BillAmount, SendTF, Comp_Code, MsgType, SNo "
        "FROM DBSendSMS ORDER BY SNo DESC", cn=cn)
    return [_map_dbsendsms(r) for r in rows]


def dbsendsms_get(docid: str, sno: int, cn=None) -> dict | None:
    rows = db.query(
        "SELECT DocId, Vtype, Vdate, VNo, SubCode, Mobile1, Mobile2, "
        "TxtMsg, SMSDt, SMSTm, DelvDt, DelvTm, SenderName, PartyName, "
        "U_AE, U_Name, U_EntDt, Site_Code, LogSite_Code, RoomNo, "
        "BillAmount, SendTF, Comp_Code, MsgType, SNo "
        "FROM DBSendSMS WHERE DocId = ? AND SNo = ?",
        (docid, sno), cn=cn)
    return _map_dbsendsms(rows[0]) if rows else None


def dbsendsms_insert(rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "INSERT INTO DBSendSMS (DocId, Vtype, Vdate, VNo, SubCode, "
        "Mobile1, Mobile2, TxtMsg, SMSDt, SMSTm, DelvDt, DelvTm, "
        "SenderName, PartyName, U_AE, U_Name, U_EntDt, Site_Code, "
        "LogSite_Code, RoomNo, BillAmount, SendTF, Comp_Code, MsgType, SNo) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'A', ?, getdate(), ?, ?, ?, ?, ?, ?, ?, ?)",
        (rec.get("docid", ""), rec.get("vtype", ""), rec.get("vdate"),
         rec.get("vno", 0), rec.get("subcode", ""),
         rec.get("mobile1", ""), rec.get("mobile2", ""),
         rec.get("txt_msg", ""), rec.get("sms_dt"),
         rec.get("sms_tm", ""), rec.get("delv_dt"),
         rec.get("delv_tm", ""), rec.get("sender_name", ""),
         rec.get("party_name", ""), USER, SITE_CODE, SITE_CODE,
         rec.get("room_no", ""), float(rec.get("bill_amount") or 0),
         rec.get("send_tf", ""), rec.get("comp_code", ""),
         rec.get("msg_type", ""), rec.get("sno", 0)),
        cn=cn, commit=commit)


def dbsendsms_update(docid: str, sno: int, rec: dict,
                     cn=None, commit: bool = True) -> int:
    return db.execute(
        "UPDATE DBSendSMS SET TxtMsg = ?, SMSDt = ?, SMSTm = ?, "
        "DelvDt = ?, DelvTm = ?, SendTF = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' "
        "WHERE DocId = ? AND SNo = ?",
        (rec.get("txt_msg", ""), rec.get("sms_dt"),
         rec.get("sms_tm", ""), rec.get("delv_dt"),
         rec.get("delv_tm", ""), rec.get("send_tf", ""),
         USER, docid, sno),
        cn=cn, commit=commit)


def dbsendsms_delete(docid: str, sno: int, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM DBSendSMS WHERE DocId = ? AND SNo = ?",
        (docid, sno), cn=cn, commit=commit)


class _DBSendSMSAPI:
    @staticmethod
    def list_all(cn=None, limit=500): return dbsendsms_list(cn, limit)
    @staticmethod
    def get(docid, sno, cn=None): return dbsendsms_get(docid, sno, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return dbsendsms_insert(rec, cn, commit)
    @staticmethod
    def update(docid, sno, rec, cn=None, commit=True): return dbsendsms_update(docid, sno, rec, cn, commit)
    @staticmethod
    def delete(docid, sno, cn=None, commit=True): return dbsendsms_delete(docid, sno, cn, commit)

DBSendSMSAPI = _DBSendSMSAPI()


# ============================================================
# JobSchedule - Job Schedule Header
# PK: Schedule_Id
# ============================================================
def _map_jobschedule(r) -> dict:
    try:
        return {
            "schedule_id": r.Schedule_Id or "",
            "schedule_name": (r.ScheduleName or "").strip(),
            "schedule_type": r.ScheduleType or "",
            "enabled": r.ScheduleEnabled,
            "start_date": r.ScheduleStartDate,
            "end_date": r.ScheduleEndDate,
            "one_time_occur": r.OneTimeOccur,
            "freq_occurs": r.FreqOccurs or "",
            "freq_recurs": r.FreqRecurs or 0,
            "freq_weekdays": r.FreqWeekdays or 0,
            "freq_month": r.FreqMonth or 0,
            "freq_month_day": r.FreqMonthDay or 0,
            "freq_month_day_every": r.FreqMonthDayOfEveryMonth or 0,
            "freq_month_the": r.FreqMonthThe or "",
            "freq_month_the_day": r.FreqMonthTheDay or "",
            "freq_month_the_day_every": r.FreqMonthTheDayOfEveryMonth or 0,
            "dfreq": r.DFreq or 0,
            "dfreq_once": r.DFreqOccursOnce,
            "dfreq_every": r.DFreqOccursEvery or 0,
            "dfreq_type": r.DFreqOccursType or "",
            "dfreq_start": r.DFreqOccursStartTime,
            "dfreq_end": r.DFreqOccursEndTime,
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        sid, sn, st, se, ssd, sed, oto, fo, fr, fw, fm, fmd, fmde, \
            fmt, fmtd, fmdt, df, dfo, dfe, dft, dfst, dfet, un, _, uae, lgs = r
        return {
            "schedule_id": sid or "",
            "schedule_name": (sn or "").strip(),
            "schedule_type": st or "",
            "enabled": se,
            "start_date": ssd, "end_date": sed,
            "one_time_occur": oto,
            "freq_occurs": fo or "", "freq_recurs": fr or 0,
            "freq_weekdays": fw or 0,
            "freq_month": fm or 0, "freq_month_day": fmd or 0,
            "freq_month_day_every": fmde or 0,
            "freq_month_the": fmt or "", "freq_month_the_day": fmtd or "",
            "freq_month_the_day_every": fmdt or 0,
            "dfreq": df or 0,
            "dfreq_once": dfo, "dfreq_every": dfe or 0,
            "dfreq_type": dft or "",
            "dfreq_start": dfst, "dfreq_end": dfet,
            "u_name": un or "", "u_ae": uae or "",
        }


def _validate_jobschedule(rec: dict):
    if not rec.get("schedule_id", "").strip():
        raise ValueError("Schedule_Id zaroori hai")


def jobschedule_list(cn=None, limit: int = 500) -> list[dict]:
    cols = ("Schedule_Id, ScheduleName, ScheduleType, ScheduleEnabled, "
            "ScheduleStartDate, ScheduleEndDate, OneTimeOccur, "
            "FreqOccurs, FreqRecurs, FreqWeekdays, FreqMonth, "
            "FreqMonthDay, FreqMonthDayOfEveryMonth, FreqMonthThe, "
            "FreqMonthTheDay, FreqMonthTheDayOfEveryMonth, "
            "DFreq, DFreqOccursOnce, DFreqOccursEvery, DFreqOccursType, "
            "DFreqOccursStartTime, DFreqOccursEndTime, "
            "U_Name, U_EntDt, U_AE, Site_Code, LogSite_Code")
    rows = db.query(
        f"SELECT TOP {int(limit)} {cols} FROM JobSchedule ORDER BY Schedule_Id",
        cn=cn)
    return [_map_jobschedule(r) for r in rows]


def jobschedule_get(schedule_id: str, cn=None) -> dict | None:
    cols = ("Schedule_Id, ScheduleName, ScheduleType, ScheduleEnabled, "
            "ScheduleStartDate, ScheduleEndDate, OneTimeOccur, "
            "FreqOccurs, FreqRecurs, FreqWeekdays, FreqMonth, "
            "FreqMonthDay, FreqMonthDayOfEveryMonth, FreqMonthThe, "
            "FreqMonthTheDay, FreqMonthTheDayOfEveryMonth, "
            "DFreq, DFreqOccursOnce, DFreqOccursEvery, DFreqOccursType, "
            "DFreqOccursStartTime, DFreqOccursEndTime, "
            "U_Name, U_EntDt, U_AE, Site_Code, LogSite_Code")
    rows = db.query(
        f"SELECT {cols} FROM JobSchedule WHERE Schedule_Id = ?",
        (schedule_id,), cn=cn)
    return _map_jobschedule(rows[0]) if rows else None


def jobschedule_insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate_jobschedule(rec)
    cols = ("Schedule_Id, ScheduleName, ScheduleType, ScheduleEnabled, "
            "ScheduleStartDate, ScheduleEndDate, OneTimeOccur, "
            "FreqOccurs, FreqRecurs, FreqWeekdays, FreqMonth, "
            "FreqMonthDay, FreqMonthDayOfEveryMonth, FreqMonthThe, "
            "FreqMonthTheDay, FreqMonthTheDayOfEveryMonth, "
            "DFreq, DFreqOccursOnce, DFreqOccursEvery, DFreqOccursType, "
            "DFreqOccursStartTime, DFreqOccursEndTime, "
            "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code")
    return db.execute(
        f"INSERT INTO JobSchedule ({cols}) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["schedule_id"], rec.get("schedule_name", ""),
         rec.get("schedule_type", ""), rec.get("enabled", 1),
         rec.get("start_date"), rec.get("end_date"),
         rec.get("one_time_occur"),
         rec.get("freq_occurs", ""), rec.get("freq_recurs", 0),
         rec.get("freq_weekdays", 0), rec.get("freq_month", 0),
         rec.get("freq_month_day", 0), rec.get("freq_month_day_every", 0),
         rec.get("freq_month_the", ""), rec.get("freq_month_the_day", ""),
         rec.get("freq_month_the_day_every", 0),
         rec.get("dfreq", 0), rec.get("dfreq_once"),
         rec.get("dfreq_every", 0), rec.get("dfreq_type", ""),
         rec.get("dfreq_start"), rec.get("dfreq_end"),
         SITE_CODE, USER, SITE_CODE),
        cn=cn, commit=commit)


def jobschedule_update(schedule_id: str, rec: dict,
                       cn=None, commit: bool = True) -> int:
    _validate_jobschedule(rec)
    return db.execute(
        "UPDATE JobSchedule SET ScheduleName = ?, ScheduleType = ?, "
        "ScheduleEnabled = ?, ScheduleStartDate = ?, ScheduleEndDate = ?, "
        "OneTimeOccur = ?, FreqOccurs = ?, FreqRecurs = ?, "
        "FreqWeekdays = ?, FreqMonth = ?, FreqMonthDay = ?, "
        "FreqMonthDayOfEveryMonth = ?, FreqMonthThe = ?, "
        "FreqMonthTheDay = ?, FreqMonthTheDayOfEveryMonth = ?, "
        "DFreq = ?, DFreqOccursOnce = ?, DFreqOccursEvery = ?, "
        "DFreqOccursType = ?, DFreqOccursStartTime = ?, "
        "DFreqOccursEndTime = ?, U_Name = ?, U_EntDt = getdate(), "
        "U_AE = 'E' WHERE Schedule_Id = ?",
        (rec.get("schedule_name", ""), rec.get("schedule_type", ""),
         rec.get("enabled", 1), rec.get("start_date"),
         rec.get("end_date"), rec.get("one_time_occur"),
         rec.get("freq_occurs", ""), rec.get("freq_recurs", 0),
         rec.get("freq_weekdays", 0), rec.get("freq_month", 0),
         rec.get("freq_month_day", 0), rec.get("freq_month_day_every", 0),
         rec.get("freq_month_the", ""), rec.get("freq_month_the_day", ""),
         rec.get("freq_month_the_day_every", 0),
         rec.get("dfreq", 0), rec.get("dfreq_once"),
         rec.get("dfreq_every", 0), rec.get("dfreq_type", ""),
         rec.get("dfreq_start"), rec.get("dfreq_end"),
         USER, schedule_id),
        cn=cn, commit=commit)


def jobschedule_delete(schedule_id: str, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM JobSchedule WHERE Schedule_Id = ?",
        (schedule_id,), cn=cn, commit=commit)


class _JobScheduleAPI:
    @staticmethod
    def list_all(cn=None, limit=500): return jobschedule_list(cn, limit)
    @staticmethod
    def get(schedule_id, cn=None): return jobschedule_get(schedule_id, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return jobschedule_insert(rec, cn, commit)
    @staticmethod
    def update(schedule_id, rec, cn=None, commit=True): return jobschedule_update(schedule_id, rec, cn, commit)
    @staticmethod
    def delete(schedule_id, cn=None, commit=True): return jobschedule_delete(schedule_id, cn, commit)

JobScheduleAPI = _JobScheduleAPI()


# ============================================================
# JobScheduledDetail - Job Schedule Detail
# PK: Job_Id
# ============================================================
def _map_jobscheddetail(r) -> dict:
    try:
        return {
            "job_id": r.Job_Id or "",
            "job_name": (r.JobName or "").strip(),
            "schedule_id": r.Schedule_Id or "",
            "event": r.Event or "",
            "scheduled_job": r.ScheduledJob or "",
            "mobile_no": r.MobileNo or "",
            "enabled": r.JobEnabled,
            "scheduled_on": r.JobScheduledOn,
            "mark": r.Mark or "",
            "msg_header": r.MsgHeader or "",
            "template_id": r.TemplateId or "",
            "msg_footer": r.MsgFooter or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        jid, jn, sid, ev, sj, mn, je, jo, mk, un, _, uae, lgs, mh, ti, mf = r
        return {
            "job_id": jid or "",
            "job_name": (jn or "").strip(),
            "schedule_id": sid or "",
            "event": ev or "",
            "scheduled_job": sj or "",
            "mobile_no": mn or "",
            "enabled": je,
            "scheduled_on": jo,
            "mark": mk or "",
            "msg_header": mh or "",
            "template_id": ti or "",
            "msg_footer": mf or "",
            "u_name": un or "", "u_ae": uae or "",
        }


def _validate_jobscheddetail(rec: dict):
    if not rec.get("job_id", "").strip():
        raise ValueError("Job_Id zaroori hai")


def jobscheddetail_list(cn=None, limit: int = 500) -> list[dict]:
    cols = ("Job_Id, JobName, Schedule_Id, Event, ScheduledJob, "
            "MobileNo, JobEnabled, JobScheduledOn, Mark, "
            "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code, "
            "MsgHeader, TemplateId, MsgFooter")
    rows = db.query(
        f"SELECT TOP {int(limit)} {cols} FROM JobScheduledDetail ORDER BY Job_Id",
        cn=cn)
    return [_map_jobscheddetail(r) for r in rows]


def jobscheddetail_get(job_id: str, cn=None) -> dict | None:
    cols = ("Job_Id, JobName, Schedule_Id, Event, ScheduledJob, "
            "MobileNo, JobEnabled, JobScheduledOn, Mark, "
            "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code, "
            "MsgHeader, TemplateId, MsgFooter")
    rows = db.query(
        f"SELECT {cols} FROM JobScheduledDetail WHERE Job_Id = ?",
        (job_id,), cn=cn)
    return _map_jobscheddetail(rows[0]) if rows else None


def jobscheddetail_insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate_jobscheddetail(rec)
    cols = ("Job_Id, JobName, Schedule_Id, Event, ScheduledJob, "
            "MobileNo, JobEnabled, JobScheduledOn, Mark, "
            "Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code, "
            "MsgHeader, TemplateId, MsgFooter")
    return db.execute(
        f"INSERT INTO JobScheduledDetail ({cols}) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?, ?, ?, ?)",
        (rec["job_id"], rec.get("job_name", ""),
         rec.get("schedule_id", ""), rec.get("event", ""),
         rec.get("scheduled_job", ""), rec.get("mobile_no", ""),
         rec.get("enabled", 1), rec.get("scheduled_on"),
         rec.get("mark", ""), SITE_CODE, USER, SITE_CODE,
         rec.get("msg_header", ""), rec.get("template_id", ""),
         rec.get("msg_footer", "")),
        cn=cn, commit=commit)


def jobscheddetail_update(job_id: str, rec: dict,
                          cn=None, commit: bool = True) -> int:
    _validate_jobscheddetail(rec)
    return db.execute(
        "UPDATE JobScheduledDetail SET JobName = ?, Schedule_Id = ?, "
        "Event = ?, ScheduledJob = ?, MobileNo = ?, JobEnabled = ?, "
        "JobScheduledOn = ?, Mark = ?, MsgHeader = ?, TemplateId = ?, "
        "MsgFooter = ?, U_Name = ?, U_EntDt = getdate(), U_AE = 'E' "
        "WHERE Job_Id = ?",
        (rec.get("job_name", ""), rec.get("schedule_id", ""),
         rec.get("event", ""), rec.get("scheduled_job", ""),
         rec.get("mobile_no", ""), rec.get("enabled", 1),
         rec.get("scheduled_on"), rec.get("mark", ""),
         rec.get("msg_header", ""), rec.get("template_id", ""),
         rec.get("msg_footer", ""), USER, job_id),
        cn=cn, commit=commit)


def jobscheddetail_delete(job_id: str, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM JobScheduledDetail WHERE Job_Id = ?",
        (job_id,), cn=cn, commit=commit)


class _JobScheduledDetailAPI:
    @staticmethod
    def list_all(cn=None, limit=500): return jobscheddetail_list(cn, limit)
    @staticmethod
    def get(job_id, cn=None): return jobscheddetail_get(job_id, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return jobscheddetail_insert(rec, cn, commit)
    @staticmethod
    def update(job_id, rec, cn=None, commit=True): return jobscheddetail_update(job_id, rec, cn, commit)
    @staticmethod
    def delete(job_id, cn=None, commit=True): return jobscheddetail_delete(job_id, cn, commit)

JobScheduledDetailAPI = _JobScheduledDetailAPI()
