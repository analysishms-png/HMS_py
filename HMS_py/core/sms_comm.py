"""SMS/Communication - EmailSMSForward, SMSEnviro, DBSendSMS, GuestReward,
AssignDelivery, DeliveryBoy, JobSchedule, JobScheduledDetail CRUD."""
from __future__ import annotations
from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()

# === EmailSMSForward ===
def _map_email(r) -> dict:
    try:
        return {"id": r.Id or 0, "type": r.Type or "", "mobileno": r.MobileNo or "",
                "emailid": r.EmailId or "", "txtmsg": r.TxtMsg or "",
                "site_code": r.Site_Code or "", "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"id": r[0] or 0, "type": str(r[1] or "")}


def list_email_forward(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM EmailSMSForward WHERE Site_Code = ? ORDER BY Id DESC",
                    (SITE_CODE,), cn=cn)
    return [_map_email(r) for r in rows]


def insert_email_forward(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    id_rows = db.query("SELECT MAX(Id) FROM EmailSMSForward", cn=cn)
    new_id = (id_rows[0][0] or 0) + 1 if id_rows and id_rows[0][0] else 1
    db.execute(
        "INSERT INTO EmailSMSForward (Id,Type,MobileNo,EmailId,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code,TxtMsg,FlagType)"
        " VALUES (?,?,?,?,?,?,getdate(),'A',?,?,?)",
        (new_id, rec.get("type",""), rec.get("mobileno",""), rec.get("emailid",""),
         site, user, site, rec.get("txtmsg",""), rec.get("flagtype","")),
        cn=cn, commit=commit)
    return {"id": new_id}


def delete_email_forward(id_val, cn=None, commit=True):
    return db.execute("DELETE FROM EmailSMSForward WHERE Id = ?", (id_val,), cn=cn, commit=commit)


# === DBSendSMS ===
def _map_dbsms(r) -> dict:
    try:
        return {"docid": r.DocId or "", "vtype": r.Vtype or "", "vdate": r.Vdate,
                "vno": r.VNo or 0, "subcode": r.SubCode or "", "mobileno": r.Mobile1 or "",
                "txtmsg": r.TxtMsg or "", "sendername": r.SenderName or "",
                "partyname": r.PartyName or "", "msgtype": r.MsgType or "",
                "site_code": r.Site_Code or "", "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"docid": str(r[0] or ""), "txtmsg": str(r[6] or "")}


def list_dbsms(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM DBSendSMS WHERE Site_Code = ? ORDER BY DocId DESC",
                    (SITE_CODE,), cn=cn)
    return [_map_dbsms(r) for r in rows]


def insert_dbsms(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    db.execute(
        "INSERT INTO DBSendSMS (DocId,Vtype,Vdate,VNo,SubCode,Mobile1,TxtMsg,SMSDt,SMSTm,SenderName,PartyName,U_AE,U_Name,U_EntDt,Site_Code,LogSite_Code,MsgType)"
        " VALUES (?,'SMS',getdate(),?,?,?,?,getdate(),getdate(),?,?,'A',getdate(),?,?,?)",
        (rec.get("docid",""), rec.get("vno",0), rec.get("subcode",""),
         rec.get("mobileno",""), rec.get("txtmsg",""),
         rec.get("sendername",""), rec.get("partyname",""),
         site, site, rec.get("msgtype","")),
        cn=cn, commit=commit)
    return rec


# === GuestReward ===
def _map_reward(r) -> dict:
    try:
        return {"docid": r.DocId or "", "custcode": r.CustCode or "", "vdate": r.Vdate,
                "billno": r.BillNo or "", "billamt": r.BillAmt or 0.0,
                "rewardpoint": r.RewardPoint or 0.0, "redeempoint": r.RedemPoint or 0.0,
                "mobileno": r.MobileNo or "", "site_code": r.Site_code or "",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"docid": str(r[0] or ""), "custcode": str(r[1] or "")}


def list_reward(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM GuestReward WHERE Site_code = ? ORDER BY DocId DESC",
                    (SITE_CODE,), cn=cn)
    return [_map_reward(r) for r in rows]


def insert_reward(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    db.execute(
        "INSERT INTO GuestReward (DocId,CustCode,Vdate,BillNo,BillAmt,RewardPoint,RedemPoint,MobileNo,Site_code,LogSite_Code,U_Name,U_AE,U_EntDt)"
        " VALUES (?,?,getdate(),?,?,?,?,?,?,?,?,?,getdate())",
        (rec.get("docid",""), rec.get("custcode",""), rec.get("billno",""),
         rec.get("billamt",0.0), rec.get("rewardpoint",0.0), rec.get("redeempoint",0.0),
         rec.get("mobileno",""), site, site, user, "A"),
        cn=cn, commit=commit)
    return rec


# === AssignDelivery ===
def _map_delivery(r) -> dict:
    try:
        return {"docid": r.DocId or "", "vtype": r.Vtype or "", "vno": r.VNo or 0,
                "vdate": r.Vdate, "ddate": r.Ddate, "restcode": r.RestCode or "",
                "deliboy": r.DeliBoy or "", "billamt": r.BillAmt or 0.0,
                "remark": r.Remark or "", "site_code": r.Site_Code or "",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"docid": str(r[0] or ""), "vno": r[2] or 0}


def list_delivery(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM AssignDelivery WHERE Site_Code = ? ORDER BY DocId DESC",
                    (SITE_CODE,), cn=cn)
    return [_map_delivery(r) for r in rows]


def insert_delivery(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    # BUG-015: race-safe VNo (UPDLOCK/HOLDLOCK)
    vno_rows = db.query(
        "SELECT MAX(VNo) FROM AssignDelivery WITH (UPDLOCK, HOLDLOCK) "
        "WHERE Site_Code = ?", (site,), cn=cn)
    vno = (vno_rows[0][0] or 0) + 1 if vno_rows and vno_rows[0][0] else 1
    vprefix = rec.get("vprefix", "2026")
    docid = ("D" + site.ljust(2) + "AD".ljust(6) + str(vprefix).ljust(4) + str(vno).rjust(8))[:21]
    db.execute(
        "INSERT INTO AssignDelivery (DocId,Vtype,VNo,Vprefix,Vdate,Ddate,RestCode,DeliBoy,BillAmt,Remark,Site_Code,U_Name,U_AE,U_EntDt,LogSite_Code)"
        " VALUES (?,'AD',?,?,getdate(),?,?,?,?,?,?,?,?,getdate(),?)",
        (docid, vno, vprefix, rec.get("ddate"), rec.get("restcode",""),
         rec.get("deliboy",""), rec.get("billamt",0.0), rec.get("remark",""),
         site, user, "A", site),
        cn=cn, commit=commit)
    return {"docid": docid, "vno": vno}


def delete_delivery(docid, cn=None, commit=True):
    return db.execute("DELETE FROM AssignDelivery WHERE DocId = ?", (docid,), cn=cn, commit=commit)


# === DeliveryBoy ===
def _map_dboy(r) -> dict:
    try:
        return {"code": r.Code or "", "name": (r.Name or "").strip(),
                "site_code": r.Site_Code or "", "activeyn": r.ActiveYN or "",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"code": str(r[0] or ""), "name": str(r[1] or "")}


def list_dboy(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM DeliveryBoy WHERE Site_Code = ? ORDER BY Code",
                    (SITE_CODE,), cn=cn)
    return [_map_dboy(r) for r in rows]


def insert_dboy(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    db.execute(
        "INSERT INTO DeliveryBoy (Code,Name,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code,ActiveYN)"
        " VALUES (?,?,?,?,getdate(),?, ?,?)",
        (rec.get("code",""), rec.get("name",""), site, user, "A", site, rec.get("activeyn","Y")),
        cn=cn, commit=commit)
    return rec


def delete_dboy(code, cn=None, commit=True):
    return db.execute("DELETE FROM DeliveryBoy WHERE Code = ?", (code,), cn=cn, commit=commit)


# === JobSchedule ===
def _map_jobschedule(r) -> dict:
    try:
        return {"schedule_id": r.Schedule_Id or 0, "schedulename": r.ScheduleName or "",
                "scheduletype": r.ScheduleType or "", "scheduleenabled": r.ScheduleEnabled or "",
                "site_code": r.Site_Code or "", "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"schedule_id": r[0] or 0, "schedulename": str(r[1] or "")}


def list_jobschedule(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM JobSchedule WHERE Site_Code = ? ORDER BY Schedule_Id DESC",
                    (SITE_CODE,), cn=cn)
    return [_map_jobschedule(r) for r in rows]


def insert_jobschedule(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    id_rows = db.query("SELECT MAX(Schedule_Id) FROM JobSchedule", cn=cn)
    new_id = (id_rows[0][0] or 0) + 1 if id_rows and id_rows[0][0] else 1
    db.execute(
        "INSERT INTO JobSchedule (Schedule_Id,ScheduleName,ScheduleType,ScheduleEnabled,ScheduleStartDate,ScheduleEndDate,OneTimeOccur,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code)"
        " VALUES (?,?,?,?,?,?,?,?,?,getdate(),'A',?)",
        (new_id, rec.get("schedulename",""), rec.get("scheduletype",""),
         rec.get("scheduleenabled","N"), rec.get("startdate"), rec.get("enddate"),
         rec.get("onetimeoccur",""), site, user, site),
        cn=cn, commit=commit)
    return {"schedule_id": new_id}


def delete_jobschedule(schedule_id, cn=None, commit=True):
    return db.execute("DELETE FROM JobSchedule WHERE Schedule_Id = ?", (schedule_id,), cn=cn, commit=commit)


# === JobScheduledDetail ===
def _map_jobschdetail(r) -> dict:
    try:
        return {"job_id": r.Job_Id or 0, "jobname": r.JobName or "",
                "schedule_id": r.Schedule_Id or 0, "event": r.Event or "",
                "jobenabled": r.JobEnabled or "", "mobile": r.MobileNo or "",
                "site_code": r.Site_Code or "", "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"job_id": r[0] or 0, "jobname": str(r[1] or "")}


def list_jobschdetail(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM JobScheduledDetail WHERE Site_Code = ? ORDER BY Job_Id DESC",
                    (SITE_CODE,), cn=cn)
    return [_map_jobschdetail(r) for r in rows]


def insert_jobschdetail(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    id_rows = db.query("SELECT MAX(Job_Id) FROM JobScheduledDetail", cn=cn)
    new_id = (id_rows[0][0] or 0) + 1 if id_rows and id_rows[0][0] else 1
    db.execute(
        "INSERT INTO JobScheduledDetail (Job_Id,JobName,Schedule_Id,Event,ScheduledJob,MobileNo,JobEnabled,JobScheduledOn,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,getdate(),'A',?)",
        (new_id, rec.get("jobname",""), rec.get("schedule_id",0),
         rec.get("event",""), rec.get("scheduledjob",""), rec.get("mobile",""),
         rec.get("jobenabled","Y"), rec.get("jobscheduledon"),
         site, user, site),
        cn=cn, commit=commit)
    return {"job_id": new_id}


def delete_jobschdetail(job_id, cn=None, commit=True):
    return db.execute("DELETE FROM JobScheduledDetail WHERE Job_Id = ?", (job_id,), cn=cn, commit=commit)


class SMSCommAPI:
    def list_email_forward(self, cn=None, limit=500): return list_email_forward(cn, limit)
    def insert_email_forward(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_email_forward(rec, cn, commit, site, user)
    def delete_email_forward(self, id_val, cn=None, commit=True): return delete_email_forward(id_val, cn, commit)
    def list_dbsms(self, cn=None, limit=500): return list_dbsms(cn, limit)
    def insert_dbsms(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_dbsms(rec, cn, commit, site, user)
    def list_reward(self, cn=None, limit=500): return list_reward(cn, limit)
    def insert_reward(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_reward(rec, cn, commit, site, user)
    def list_delivery(self, cn=None, limit=500): return list_delivery(cn, limit)
    def insert_delivery(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_delivery(rec, cn, commit, site, user)
    def delete_delivery(self, docid, cn=None, commit=True): return delete_delivery(docid, cn, commit)
    def list_dboy(self, cn=None, limit=500): return list_dboy(cn, limit)
    def insert_dboy(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_dboy(rec, cn, commit, site, user)
    def delete_dboy(self, code, cn=None, commit=True): return delete_dboy(code, cn, commit)
    def list_jobschedule(self, cn=None, limit=500): return list_jobschedule(cn, limit)
    def insert_jobschedule(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_jobschedule(rec, cn, commit, site, user)
    def delete_jobschedule(self, schedule_id, cn=None, commit=True): return delete_jobschedule(schedule_id, cn, commit)
    def list_jobschdetail(self, cn=None, limit=500): return list_jobschdetail(cn, limit)
    def insert_jobschdetail(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_jobschdetail(rec, cn, commit, site, user)
    def delete_jobschdetail(self, job_id, cn=None, commit=True): return delete_jobschdetail(job_id, cn, commit)